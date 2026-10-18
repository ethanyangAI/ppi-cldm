"""Pure CPU acceptance of actual new design before independent refolding."""
import argparse,json,os,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
ACCEPTED="REFERENCE_FREE_E2E_ACTUAL_DESIGN_CPU_CONTENT_ACCEPTED"

def validate_design_chain(pre,pre_descriptor,result,design):
    if pre.get("status")!="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED" or pre["qualified_prediction"]["status"]!="POSE_ACCEPTED":
        raise ValueError("Actual CPU-qualified pose required")
    if result.get("status")!="ACTUAL_MODEL_STAGE_COMPLETE" or result.get("stage")!="design":raise ValueError("Actual design stage incomplete")
    if result["CPU_preflight"]!=pre_descriptor or result["source_manifest"]!=pre["source_manifest"]:
        raise ValueError("Design source or qualification differs")
    if result["upstream"]!=pre["qualified_prediction"]["manifest"] or design["inputs"]!=[pre["qualified_prediction"]["manifest"]]:
        raise ValueError("Actual design not from exact new qualified pose")
    if design["status"]!="DESIGNS_GENERATED" or design["candidate_count"]!=1:raise ValueError("Fixed actual proposal count differs")

def validate_fasta_candidate(candidates,records):
    if len(candidates)!=1 or len(records)!=2:raise ValueError("One original plus exactly one designed MPNN sequence required")
    if "designed_chains=['B']" not in records[0][0]:raise ValueError("ProteinMPNN must design binder B only")
    candidate=candidates[0];seq=records[1][1]
    if seq!=candidate["sequence"] or len(seq)!=65 or set(seq)-set("ADEFGHIKLMNPQRSTVWY"):raise ValueError("Actual canonical65aa C/X-omitted MPNN sequence differs")
    return seq

def validate_design_cpu_gate(audit,pre_descriptor,source_descriptor,design_descriptor,design_result_descriptor):
    if audit.get("status")!=ACCEPTED or audit.get("GPU_allocated")!=0:raise ValueError("Actual pure CPU design acceptance required")
    if audit["preflight_acceptance"]!=pre_descriptor or audit["source_manifest"]!=source_descriptor:
        raise ValueError("CPU design gate source/qualification mismatch")
    if audit["actual_design_manifest"]!=design_descriptor or audit["actual_design_stage_result"]!=design_result_descriptor:
        raise ValueError("CPU design gate does not bind exact actual design")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight-acceptance",required=True);p.add_argument("--design-stage-result",required=True);p.add_argument("--output-dir",required=True)
    a=p.parse_args()
    if not os.environ.get("SLURM_JOB_ID") or os.environ.get("CUDA_VISIBLE_DEVICES")!="" or os.environ.get("SLURM_JOB_GPUS"):
        raise RuntimeError("Actual pure Slurm CPU allocation required")
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    pre=json.loads(Path(a.preflight_acceptance).read_text());frozen=Path(pre["source_manifest"]["path"]).parent
    if frozen!=Path(__file__).resolve().parent:raise RuntimeError("CPU design audit package differs")
    sys.path.insert(0,str(frozen/"source/src"))
    from ppiblocker import common,pipeline
    from ppiblocker.structure import read_structure,interface,superpose
    from e2e_resource_policy import load_guard,validate_owned_record
    from Bio import SeqIO
    source=common.read_json(common.verify_file(pre["source_manifest"]))
    for artifact in source["files"]+source["external_dependencies"]:common.verify_file(artifact)
    for artifact in common.file_references(pre):common.verify_file(artifact)
    from patch_common_runtime_selector import qualification_contract
    qualification_contract(pre,source,common.read_json(pre["software_contracts"]["path"]),common.read_json(pre["runtime_override_inputs"]["path"]))
    result=common.read_json(a.design_stage_result);g=load_guard();job=result["slurm_job_id"]
    proc=subprocess.run(["sacct","-X","-j",job,"--noheader","--parsable2",
       "--format=JobIDRaw,JobID,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"],capture_output=True,text=True,check=True)
    (out/"actual_design_sacct.txt").write_text(proc.stdout);(out/"actual_design_sacct.stderr.txt").write_text(proc.stderr)
    rows,excluded=g.parse_sacct(proc.stdout)
    if job not in rows:raise RuntimeError("Actual design allocation absent from sacct")
    row=rows[job]
    if row["state"] in {"RUNNING","PENDING","COMPLETING"}:raise RuntimeError("Actual design allocation not terminal")
    cost=dict(actual_allocation=row,actual_GPU_seconds=row["gpu_count"]*row["elapsed_seconds"],formal_benchmark_cost=False,
              includes_failure_and_rejection=True,excluded_steps=excluded)
    common.atomic_json(out/"actual_design_cost.json",cost)
    try:
        if row["gpu_count"]!=1:raise RuntimeError("Actual design GPU count differs")
        tres=dict(x.split("=",1) for x in row["alloc_tres"].split(",") if "=" in x)
        if tres.get("cpu")!="3":raise RuntimeError("Actual design CPU count differs")
        owned=result["actual_owned_resource"]["owned_guard"]
        validate_owned_record(owned,dict(SLURM_JOB_ID=job,SLURM_CPUS_PER_TASK="3",OMP_NUM_THREADS="4"),source["frozen_epoch"])
        child=result["backend_child_environment"]
        if child["CUDA_VISIBLE_DEVICES"]!=owned["child_cuda_visible_devices"] or child["OMP_NUM_THREADS"]!="4":raise RuntimeError("Actual child environment differs")
        pre_descriptor=common.record_file(a.preflight_acceptance);result_descriptor=common.record_file(a.design_stage_result)
        common.verify_file(result["result_manifest"])
        design=common.load_run(result["result_manifest"]["path"],{"DESIGNS_GENERATED"})
        validate_design_chain(pre,pre_descriptor,result,design)
        if design["source"]["python_source_sha256"]!=source["patched_python_source_sha256"]:raise RuntimeError("Actual design source differs")
        pose=common.load_run(pre["qualified_prediction"]["manifest"]["path"],{"POSE_ACCEPTED"})
        config,pose_data,native_path=pipeline.validate_design_pose(pose)
        if config["design"]!=dict(backbones=1,sequences_per_backbone=1,binder_length=65,seed=42,temperature=.1):
            raise RuntimeError("Fixed design config changed")
        if common.read_json(design["outputs"]["config"]["path"])!=config:raise RuntimeError("Design config differs from qualified pose")
        if design["outputs"]["native"]["sha256"]!=pose["outputs"]["native"]["sha256"]:raise RuntimeError("Design native input copy changed")
        candidates=common.read_json(design["outputs"]["candidates"]["path"])
        if len(candidates)!=1:raise RuntimeError("Fixed actual proposal universe not one")
        candidate=candidates[0]
        for key in ("raw_backbone","backbone","mpnn_fasta"):common.verify_file(candidate[key])
        records=[(r.description,str(r.seq)) for r in SeqIO.parse(candidate["mpnn_fasta"]["path"],"fasta")]
        sequence=validate_fasta_candidate(candidates,records)
        nat,_=read_structure(native_path);normalized,ctx=read_structure(candidate["backbone"]["path"])
        if [c["id"] for c in normalized]!=["A","B"] or ctx or normalized[0]["sequence"]!=nat[0]["sequence"] or len(normalized[1]["sequence"])!=65:
            raise RuntimeError("Actual normalized backbone chains/query differ")
        raw,_=read_structure(candidate["raw_backbone"]["path"])
        target_matches=[c for c in raw if c["sequence"]==nat[0]["sequence"]]
        if len(raw)!=2 or len(target_matches)!=1:raise RuntimeError("Actual raw RF target not uniquely recovered")
        if len(next(c for c in raw if c["id"]!=target_matches[0]["id"])["sequence"])!=65:raise RuntimeError("Raw RF binder length differs")
        contacts=interface(nat[0],nat[1],config.get("gates",{}).get("contact_cutoff",5))
        counts={}
        for aa,bb in contacts["residue_pairs"]:counts[aa]=counts.get(aa,0)+1
        anchors=sorted(counts,key=lambda aa:(-counts[aa],aa))[:3]
        if candidate["interface_anchors"]!=anchors:raise RuntimeError("Geometric anchors differ from exact qualified pose")
        logs=Path(result["result_manifest"]["path"]).parent/"logs"
        rf=common.read_json(logs/"rfd.command.json");mpnn=common.read_json(logs/"mpnn_42.command.json")
        rf_args=set(rf["argv"])
        expected={"inference.num_designs=1","inference.design_startnum=42","inference.deterministic=True","contigmap.contigs=[A1-85/0 65-65]",
                  "inference.input_pdb="+str(native_path),"ppi.hotspot_res=["+",".join("A"+str(x) for x in anchors)+"]"}
        if not expected<=rf_args:raise RuntimeError("Actual RF command settings/input differ")
        args=mpnn["argv"]
        for key,value in {"--pdb_path_chains":"B","--num_seq_per_target":"1","--batch_size":"1","--sampling_temp":"0.1","--seed":"42","--omit_AAs":"CX"}.items():
            if args.count(key)!=1 or args[args.index(key)+1]!=value:raise RuntimeError("Actual MPNN command differs: "+key)
        for name in ("rfd","mpnn_42"):
            resources=common.read_json(logs/(name+".resources.json"))
            if resources["status"]!="COMPLETE" or resources["returncode"]!=0 or resources["slurm_job_id"]!=job:raise RuntimeError("Actual backend command receipt not complete in the owned job")
        import numpy as np
        ca=lambda c:np.array([r["ca"] for r in c["residues"]])
        _,_,target_rmsd=superpose(ca(normalized[0]),ca(nat[0]))
        readback=dict(candidate_id=candidate["id"],sequence=sequence,backbone=candidate["backbone"],raw_backbone=candidate["raw_backbone"],
                      mpnn_fasta=candidate["mpnn_fasta"],geometric_anchors=anchors,target_CA_RMSD_after_alignment_angstrom=target_rmsd,
                      RF_command=common.record_file(logs/"rfd.command.json"),MPNN_command=common.record_file(logs/"mpnn_42.command.json"),
                      actual_native_pose_gate=pose_data["design_entry_physical_gate"],formal_benchmark=False)
        common.atomic_json(out/"actual_design_readback.json",readback)
        acceptance=dict(schema="reference_free_e2e_design_cpu_gate.v1",status=ACCEPTED,GPU_allocated=0,
             slurm_CPU_job_id=os.environ["SLURM_JOB_ID"],source_manifest=pre["source_manifest"],preflight_acceptance=pre_descriptor,
             actual_design_stage_result=result_descriptor,actual_design_manifest=result["result_manifest"],
             actual_design_cost=common.record_file(out/"actual_design_cost.json"),actual_design_readback=common.record_file(out/"actual_design_readback.json"),
             exact_qualified_pose=pre["qualified_prediction"]["manifest"],proposal_count=1,experimental_binding=False,experimental_blockade=False,
             completed_epoch=time.time())
        common.atomic_json(out/"acceptance.json",acceptance);print(json.dumps(acceptance));return 0
    except Exception as error:
        common.atomic_json(out/"typed_incomplete.json",dict(status="REFERENCE_FREE_E2E_DESIGN_CPU_AUDIT_INCOMPLETE",error=str(error),
              traceback=traceback.format_exc(),actual_cost=common.record_file(out/"actual_design_cost.json"),completed_epoch=time.time()))
        raise
if __name__=="__main__":raise SystemExit(main())
