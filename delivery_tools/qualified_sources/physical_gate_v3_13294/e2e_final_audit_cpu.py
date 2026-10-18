"""CPU-only independent read-back of actual qualified-pose -> design -> blind refold."""
import argparse,json,math,os,subprocess,sys,time,traceback
from pathlib import Path
import numpy as np
ROOT=Path("/lustre/users/u21111210118/projects/test9")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight-acceptance",required=True);p.add_argument("--design-stage-result",required=True)
    p.add_argument("--evaluate-stage-result",required=True);p.add_argument("--output-dir",required=True)
    p.add_argument("--design-audit-acceptance",required=True)
    a=p.parse_args()
    if not os.environ.get("SLURM_JOB_ID") or os.environ.get("CUDA_VISIBLE_DEVICES")!="" or os.environ.get("SLURM_JOB_GPUS"):
        raise RuntimeError("Independent audit requires actual pure Slurm CPU allocation")
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    pre=json.loads(Path(a.preflight_acceptance).read_text())
    source_manifest=Path(pre["source_manifest"]["path"])
    if source_manifest.parent!=Path(__file__).resolve().parent:raise RuntimeError("Audit source package differs from accepted snapshot")
    sys.path.insert(0,str(source_manifest.parent/"source/src"))
    from ppiblocker import common,pipeline
    from ppiblocker.structure import read_structure,competition
    from e2e_resource_policy import load_guard,validate_owned_record
    from physical_preflight_cpu import independent_atoms
    from e2e_design_audit_cpu import validate_design_cpu_gate
    source=common.read_json(common.verify_file(pre["source_manifest"]))
    for item in source["files"]+source["external_dependencies"]:common.verify_file(item)
    if pre.get("status")!="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED":raise RuntimeError("CPU qualification incomplete")
    if pre["qualified_prediction"]["status"]!="POSE_ACCEPTED":raise RuntimeError("Real physical/ensemble rejection: cannot audit a fabricated design continuation")
    for artifact in common.file_references(pre):common.verify_file(artifact)
    from patch_common_runtime_selector import qualification_contract
    qualification_contract(pre,source,common.read_json(pre["software_contracts"]["path"]),common.read_json(pre["runtime_override_inputs"]["path"]))
    descriptors=[common.record_file(a.preflight_acceptance),common.record_file(a.design_stage_result),common.record_file(a.evaluate_stage_result)]
    designs=common.read_json(a.design_stage_result);evaluated=common.read_json(a.evaluate_stage_result)
    all_jobs=[designs["slurm_job_id"],evaluated["slurm_job_id"]]
    if len(set(all_jobs))!=2:raise RuntimeError("Design and refold require distinct actual allocations")
    g=load_guard()
    proc=subprocess.run(["sacct","-X","-j",",".join(all_jobs),"--noheader","--parsable2",
        "--format=JobIDRaw,JobID,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"],capture_output=True,text=True,check=True)
    (out/"actual_model_sacct.txt").write_text(proc.stdout);(out/"actual_model_sacct.stderr.txt").write_text(proc.stderr)
    rows,excluded=g.parse_sacct(proc.stdout)
    costs=[]
    for result in (designs,evaluated):
        job=result["slurm_job_id"]
        if job not in rows:raise RuntimeError("Actual allocated model-stage sacct row missing")
        row=rows[job]
        if row["state"] in {"RUNNING","PENDING","COMPLETING"}:raise RuntimeError("Model allocation not terminal")
        if row["gpu_count"]!=1:raise RuntimeError("Actual model GPU allocation differs")
        tres=dict(x.split("=",1) for x in row["alloc_tres"].split(",") if "=" in x)
        if tres.get("cpu")!="3":raise RuntimeError("Actual final CPU allocation differs")
        costs.append(dict(stage=result["stage"],allocation=row,actual_GPU_seconds=row["gpu_count"]*row["elapsed_seconds"],
                          includes_failed_and_rejected_computation=True,formal_generation_cost=False))
    common.atomic_json(out/"actual_model_costs.json",dict(allocations=costs,total_new_GPU_seconds=sum(x["actual_GPU_seconds"] for x in costs),
        native_prediction_new_GPU_seconds=0,old_native_inference_job="11801",excluded_sacct_steps=excluded))
    try:
        if designs["status"]!="ACTUAL_MODEL_STAGE_COMPLETE" or evaluated["status"]!="ACTUAL_MODEL_STAGE_COMPLETE":
            raise RuntimeError("Actual generation/refold stage incomplete; costs retained")
        if designs["stage"]!="design" or evaluated["stage"]!="evaluate":raise RuntimeError("Wrong stage identities")
        preflight=descriptors[0]
        design_gate=common.read_json(a.design_audit_acceptance)
        for artifact in common.file_references(design_gate):common.verify_file(artifact)
        validate_design_cpu_gate(design_gate,preflight,pre["source_manifest"],designs["result_manifest"],descriptors[1])
        if evaluated["actual_design_audit_acceptance"]!=common.record_file(a.design_audit_acceptance):raise RuntimeError("Evaluation did not pin exact independent CPU design gate")
        for result in (designs,evaluated):
            if result["CPU_preflight"]!=preflight or result["source_manifest"]!=pre["source_manifest"]:raise RuntimeError("Stage source or qualification identity differs")
            owned=result["actual_owned_resource"]["owned_guard"]
            env=dict(SLURM_JOB_ID=result["slurm_job_id"],SLURM_CPUS_PER_TASK="3",OMP_NUM_THREADS="4")
            validate_owned_record(owned,env,source["frozen_epoch"])
            if result["actual_owned_resource"]["owned_GPU_UUID"]!=owned["child_cuda_visible_devices"]:raise RuntimeError("Owned UUID proof mismatch")
            if result["backend_child_environment"]["CUDA_VISIBLE_DEVICES"]!=owned["child_cuda_visible_devices"] or result["backend_child_environment"]["OMP_NUM_THREADS"]!="4":
                raise RuntimeError("Actual captured child environment does not preserve owned UUID and OMP4")
        if designs["upstream"]!=pre["qualified_prediction"]["manifest"]:raise RuntimeError("Actual design did not consume exact new qualified pose")
        if evaluated["upstream"]!=designs["result_manifest"]:raise RuntimeError("Actual refold did not consume exact new design")
        for result in (designs,evaluated):common.verify_file(result["result_manifest"])
        pose_m=common.load_run(pre["qualified_prediction"]["manifest"]["path"],{"POSE_ACCEPTED"})
        config,pose,native=pipeline.validate_design_pose(pose_m)
        design=common.load_run(designs["result_manifest"]["path"],{"DESIGNS_GENERATED"})
        evaluation=common.load_run(evaluated["result_manifest"]["path"],{"EVALUATION_COMPLETE"})
        if design["source"]["python_source_sha256"]!=source["patched_python_source_sha256"] or evaluation["source"]["python_source_sha256"]!=source["patched_python_source_sha256"]:
            raise RuntimeError("Actual source changed between the declared generic stages")
        if design["inputs"][0]!=pre["qualified_prediction"]["manifest"] or evaluation["inputs"][0]!=designs["result_manifest"]:
            raise RuntimeError("Exact stage-manifest edges differ")
        candidates=common.read_json(design["outputs"]["candidates"]["path"]);accepted=common.read_json(evaluation["outputs"]["evaluation"]["path"])
        if len(candidates)!=1 or len(accepted["candidates"])!=1:raise RuntimeError("Fixed engineering proposal universe must be one backbone/one MPNN sequence")
        cand=candidates[0];row=accepted["candidates"][0]
        if (row["id"],row["sequence"])!=(cand["id"],cand["sequence"]) or len(cand["sequence"])!=65:
            raise RuntimeError("Candidate identity differs")
        target,partner=read_structure(native)[0]
        fixed,backbone_binder=read_structure(common.verify_file(cand["backbone"]))[0]
        if target["sequence"]!=cand["target_sequence"] or cand["target_sequence"]!=fixed["sequence"]:raise RuntimeError("Target identity not preserved")
        if len(backbone_binder["sequence"])!=65:raise RuntimeError("Actual backbone length differs")
        predicted_proteins=[dict(sequence=target["sequence"],canonical_start=1),dict(sequence=cand["sequence"],canonical_start=1,de_novo=True)]
        if len(row["models"])!=3:raise RuntimeError("All three independent blind refolds required")
        checks=[]
        for idx,stored in enumerate(row["models"]):
            model=dict(model_index=idx,**{k:evaluation["outputs"][f"{cand['id']}_{idx}_{k}"] for k in ("structure","confidence","pae")})
            independent=independent_atoms(model["structure"]["path"])
            aa,bb,pair,metrics=pipeline.model_pair(model,predicted_proteins,config.get("gates",{}))
            geom=competition(target,partner,fixed,backbone_binder,aa,bb,cutoff=config.get("gates",{}).get("contact_cutoff",5))
            reasons=pipeline.confidence_reasons(metrics,config.get("gates",{}))
            if geom["predicted_complex_interface"]["minimum_distance"]<1.5:reasons.append("SEVERE_TARGET_BINDER_CLASH")
            gates=config.get("gates",{})
            if geom["binder_ca_rmsd_after_target_alignment"]>gates.get("max_binder_rmsd",2):reasons.append("DESIGNED_POSE_NOT_RECOVERED")
            if geom["target_ca_rmsd"]>gates.get("max_target_rmsd",2):reasons.append("TARGET_DISTORTED")
            if geom["native_interface_coverage"]<gates.get("min_interface_overlap",.5):reasons.append("INSUFFICIENT_NATIVE_INTERFACE_OVERLAP")
            if geom["partner_overlap_atom_count_2A"]<gates.get("min_partner_overlap_atoms",5):reasons.append("NO_STERIC_COMPETITION_SUPPORT")
            if reasons!=stored["reasons"] or metrics!=stored["metrics"] or geom!=stored["geometry"]:raise RuntimeError("CPU raw recomputation differs from model-stage evidence")
            if abs(independent["minimum_distance_angstrom"]-pair["interface"]["minimum_distance"])>1e-4:raise RuntimeError("Independent raw atom distance does not match production")
            if (independent["minimum_distance_angstrom"]<1.5)!=(pair["interface"]["minimum_distance"]<1.5):raise RuntimeError("Independent severe-clash classification mismatch")
            checks.append(dict(model=idx,raw_artifacts=model,independent_heavy_atom_audit=independent,confidence=metrics,geometry=geom,reasons=reasons))
        passes=sum(not c["reasons"] for c in checks)
        expected="COMPUTATIONAL_COMPETITION_CANDIDATE" if passes>=2 else "REJECTED"
        if row["status"]!=expected or row["passing_samples"]!=passes or evaluation["accepted_count"]!=int(passes>=2):raise RuntimeError("Actual evaluation terminal classification differs")
        common.atomic_json(out/"raw_model_independent_readback.json",dict(models=checks,passed_refolds=passes,candidate_status=expected,
            native_pose_inference_reused_not_repeated=True,formal_benchmark=False))
        result=dict(schema="reference_free_e2e_independent_actual_closure.v1",status="REFERENCE_FREE_E2E_COMPUTATIONAL_CHAIN_CONTENT_ACCEPTED",
            inputs=descriptors+[common.record_file(a.design_audit_acceptance)],source_manifest=pre["source_manifest"],qualified_pose=pre["qualified_prediction"]["manifest"],
            actual_design_manifest=designs["result_manifest"],actual_evaluation_manifest=evaluated["result_manifest"],
            actual_costs=common.record_file(out/"actual_model_costs.json"),
            raw_model_independent_readback=common.record_file(out/"raw_model_independent_readback.json"),
            new_native_inference_GPU_jobs=0,new_design_GPU_jobs=1,new_refold_GPU_jobs=1,
            proposal_count=1,refold_count=3,accepted_computational_candidates=int(passes>=2),
            classification=expected,engineering_only=True,experimental_binding=False,experimental_blockade=False,
            generic_arbitrary_pair_success_rate_established=False,formal13260_changed=False,
            slurm_CPU_job_id=os.environ["SLURM_JOB_ID"],GPU_allocated=0,completed_epoch=time.time())
        common.atomic_json(out/"acceptance.json",result);print(json.dumps(result));return 0
    except Exception as error:
        common.atomic_json(out/"typed_incomplete.json",dict(status="REFERENCE_FREE_E2E_ACTUAL_CLOSURE_INCOMPLETE",
            error=str(error),traceback=traceback.format_exc(),costs=common.record_file(out/"actual_model_costs.json"),
            accepted_computational_candidate_count=None,completed_epoch=time.time()))
        raise
if __name__=="__main__":raise SystemExit(main())
