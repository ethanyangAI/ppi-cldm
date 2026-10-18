"""Root-owned true model-stage entry; explicit source/qualification/upstream only."""
from __future__ import annotations
import argparse, json, os, sys, time, traceback
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
EXPECTED="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",required=True,choices=["design","evaluate"])
    p.add_argument("--preflight-acceptance",required=True)
    p.add_argument("--upstream",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--design-stage-result")
    p.add_argument("--design-audit-acceptance")
    a=p.parse_args()
    if not os.environ.get("SLURM_JOB_ID") or not os.environ.get("CUDA_VISIBLE_DEVICES"):
        raise RuntimeError("Actual Slurm GPU model-stage allocation required")
    if os.environ.get("SLURM_GPUS_ON_NODE") not in {"1","1(x1)"}:
        raise RuntimeError("Exactly one actual allocated GPU required")
    inputs=[Path(a.preflight_acceptance).resolve(),Path(a.upstream).resolve(),Path(a.output_dir).resolve()]
    if a.design_stage_result:inputs.append(Path(a.design_stage_result).resolve())
    if a.design_audit_acceptance:inputs.append(Path(a.design_audit_acceptance).resolve())
    if any(not x.is_relative_to(ROOT) for x in inputs):raise RuntimeError("All inputs/outputs must belong to authoritative test9 root")
    out=Path(a.output_dir).resolve();out.mkdir(parents=True,exist_ok=False)
    pre=json.loads(Path(a.preflight_acceptance).read_text())
    if pre.get("status")!=EXPECTED or pre.get("GPU_allocated")!=0 or pre.get("native_inference_performed") is not False:
        raise RuntimeError("Actual accepted pure CPU requalification is required")
    descriptor=pre["source_manifest"];source_manifest_path=Path(descriptor["path"])
    if source_manifest_path.parent!=Path(__file__).resolve().parent:
        raise RuntimeError("Launcher and accepted frozen source package differ")
    sys.path.insert(0,str(source_manifest_path.parent/"source/src"))
    from ppiblocker import common,pipeline
    common.verify_file(descriptor)
    snapshot=common.read_json(source_manifest_path)
    for item in snapshot["files"]+snapshot["external_dependencies"]:common.verify_file(item)
    for item in common.file_references(pre):common.verify_file(item)
    from patch_common_runtime_selector import qualification_contract
    qualification_contract(pre,snapshot,common.read_json(pre["software_contracts"]["path"]),common.read_json(pre["runtime_override_inputs"]["path"]))
    package_sha=snapshot["patched_python_source_sha256"]
    qualified=pre["qualified_prediction"]
    if qualified["status"]!="POSE_ACCEPTED":raise RuntimeError("Declared requalification rejected; do not force generation")
    common.verify_file(qualified["manifest"])
    exact_preflight=common.record_file(a.preflight_acceptance)
    status=dict(schema="reference_free_e2e_actual_model_stage.v1",stage=a.stage,status="RUNNING",
        slurm_job_id=os.environ["SLURM_JOB_ID"],allocated_gpus=os.environ.get("SLURM_GPUS_ON_NODE"),
        node=os.environ.get("SLURM_JOB_NODELIST"),cuda_visible_devices_before=os.environ.get("CUDA_VISIBLE_DEVICES"),
        source_manifest=descriptor,CPU_preflight=exact_preflight,upstream=common.record_file(a.upstream),
        started_epoch=time.time(),evidence_scope="ENGINEERING_E2E_COMPLEMENT_NOT_FORMAL_BENCHMARK",
        fixed_design_settings=dict(backbones=1,sequences_per_backbone=1,binder_length=65,seed=42,temperature=.1),
        fixed_refold_settings=dict(samples=3,seed=1042,recycles=3,allow_external_msa=False,allow_single_sequence=True),
        CPU_bookkeeping_inside_true_model_allocation=True,no_dedicated_GPU_diagnostic=True,
        experimental_binding=False,experimental_blockade=False,formal13260_modified=False)
    common.atomic_json(out/"stage_result.json",status)
    try:
        from e2e_resource_policy import model_guard,child_backend_environment
        from ppiblocker import backends
        original_backend_environment=backends.backend_env
        backends.backend_env=lambda root,component="boltz":child_backend_environment(original_backend_environment(root,component))
        resource=model_guard("rfd" if a.stage=="design" else "boltz",ROOT,backends.backend_env,snapshot["frozen_epoch"])
        status["actual_owned_resource"]=resource;status["cuda_visible_devices"]=os.environ["CUDA_VISIBLE_DEVICES"]
        child_env=backends.backend_env(ROOT,"rfd" if a.stage=="design" else "boltz")
        status["backend_child_environment"]={k:child_env.get(k) for k in ("CUDA_VISIBLE_DEVICES","OMP_NUM_THREADS","SLURM_CPUS_PER_TASK","SLURM_JOB_ID")}
        common.atomic_json(out/"stage_result.json",status)
        if a.stage=="design":
            if str(Path(a.upstream).resolve())!=qualified["manifest"]["path"] or status["upstream"]["sha256"]!=qualified["manifest"]["sha256"]:
                raise RuntimeError("Design must consume the exact new CPU-qualified pose manifest, never old model0")
            upstream=common.load_run(a.upstream,{"POSE_ACCEPTED"})
            if upstream["source"]["python_source_sha256"]!=package_sha or upstream.get("native_inference_performed") is not False:
                raise RuntimeError("Qualified pose source/replay identity mismatch")
            if upstream.get("old_inference_runtime_reference",{}).get("sha256")!=pre["original_prediction"]["sha256"]:
                raise RuntimeError("Original native inference lineage mismatch")
            config,pose,_=pipeline.validate_design_pose(upstream)
        else:
            if not a.design_stage_result or not a.design_audit_acceptance:raise RuntimeError("Evaluation requires exact actual design-stage result AND independent pure CPU design acceptance")
            design_result=common.read_json(a.design_stage_result)
            if design_result.get("stage")!="design" or design_result.get("status")!="ACTUAL_MODEL_STAGE_COMPLETE":
                raise RuntimeError("Actual design stage result not accepted")
            if design_result["upstream"]!=qualified["manifest"]:raise RuntimeError("Actual design-stage upstream is not the exact new qualified pose")
            if design_result["CPU_preflight"]!=exact_preflight or design_result["source_manifest"]!=descriptor:
                raise RuntimeError("Design and evaluation source/CPU qualification differ")
            if design_result["result_manifest"]["path"]!=str(Path(a.upstream).resolve()) or design_result["result_manifest"]["sha256"]!=status["upstream"]["sha256"]:
                raise RuntimeError("Evaluation requires exact new actual design manifest")
            common.verify_file(design_result["result_manifest"])
            from e2e_design_audit_cpu import validate_design_cpu_gate
            design_audit=common.read_json(a.design_audit_acceptance)
            for item in common.file_references(design_audit):common.verify_file(item)
            validate_design_cpu_gate(design_audit,exact_preflight,descriptor,design_result["result_manifest"],common.record_file(a.design_stage_result))
            status["actual_design_audit_acceptance"]=common.record_file(a.design_audit_acceptance)
            upstream=common.load_run(a.upstream,{"DESIGNS_GENERATED"})
            if upstream["source"]["python_source_sha256"]!=package_sha:
                raise RuntimeError("Design source differs from declared physical-gate snapshot")
            if upstream["inputs"][0]["path"]!=qualified["manifest"]["path"] or upstream["inputs"][0]["sha256"]!=qualified["manifest"]["sha256"]:
                raise RuntimeError("New design not derived from exact CPU-qualified pose")
            config=common.read_json(upstream["outputs"]["config"]["path"])
            status["actual_design_stage_result"]=common.record_file(a.design_stage_result)
        if config["design"]!=status["fixed_design_settings"] or config["refold"]!=status["fixed_refold_settings"]:
            raise RuntimeError("Fixed engineering settings changed")
        # Runtime/source/output hashes here are CPU bookkeeping of the real model stage,
        # never CUDA scoring, and all wall time remains in this separate stage allocation.
        manifest=(pipeline.design if a.stage=="design" else pipeline.evaluate)(ROOT,a.upstream)
        result=common.read_json(manifest)
        expected="DESIGNS_GENERATED" if a.stage=="design" else "EVALUATION_COMPLETE"
        status.update(status="ACTUAL_MODEL_STAGE_COMPLETE" if result["status"]==expected else "ACTUAL_MODEL_STAGE_INCOMPLETE",
                      result_manifest=common.record_file(manifest),result_status=result["status"],
                      actual_native_prediction_repeated=False,completed_epoch=time.time())
        common.atomic_json(out/"stage_result.json",status)
        print(json.dumps(status,sort_keys=True))
        return 0 if status["status"]=="ACTUAL_MODEL_STAGE_COMPLETE" else 2
    except Exception as e:
        status.update(status="ACTUAL_MODEL_STAGE_FAILED",error=str(e),traceback=traceback.format_exc(),completed_epoch=time.time())
        common.atomic_json(out/"stage_result.json",status);print(json.dumps(status),file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
