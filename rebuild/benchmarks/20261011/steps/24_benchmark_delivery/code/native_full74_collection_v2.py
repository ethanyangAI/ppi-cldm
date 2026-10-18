#!/usr/bin/env python3
"""Three-source full native74 CPU collection using the original scientific scorer."""
import argparse,importlib.util,json,os,subprocess,sys
from pathlib import Path
import native_resource_closure_v2 as n
R=n.R
PIPELINE=R/"steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py"
PIPELINE_SHA="56648b7f905abfc393526fcba04dcd5e7ecc9cb4437db796b3b58047292b77fa"
PLAN=R/"steps/23_common_review/runs/native_controls_frozen_13051/inference_plan.json"
ANALYSIS=PLAN.with_name("analysis_plan.json")
MEMBERSHIP=PLAN.with_name("membership.json")
ROOTS=(
R/"steps/23_common_review/runs/native_controls_frozen_13051/raw",
R/"steps/23_common_review/runs/allocation_v2_13106/native_index19/raw",
R/"steps/23_common_review/engineering_history/native_index18_20261011/raw",
)
def original_pipeline():
    if n.checksum(PIPELINE)["sha256"]!=PIPELINE_SHA:raise ValueError("Original scientific CPU pipeline bytes changed")
    spec=importlib.util.spec_from_file_location("frozen_native_scientific_pipeline_13119",PIPELINE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def final_native_status(assembly,raw):
    return ("NATIVE74_FULL_RAW_AND_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY"
            if assembly["n_jobs_copied"]==20 and raw["n_raw_confidence_accepted"]==74 and raw["n_raw_unresolved"]==0
            else "NATIVE74_CURRENT_COLLECTION_TYPED_UNRESOLVED_NOT_FULL74_ACCEPTED")
def independent_af2_msa(plan,assembled,out):
    module=plan["runtime_locks"]["msa_roundtrip_module"];source=n.checksum(module["path"])
    if source["sha256"]!=module["sha256"] or source["bytes"]!=module["bytes"]:raise ValueError("Retained actual MSA validator changed")
    entities={e["blind_id"]:e for e in plan["entities"]};rows=[]
    helper="import json,sys;sys.path.insert(0,sys.argv[1]);from control_msa_check import verify_roundtrip;print(json.dumps(verify_roundtrip(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]),sort_keys=True))"
    env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",PYTHONNOUSERSITE="1");env.pop("PYTHONPATH",None)
    for j in plan["jobs"]:
        if j["engine"]!="af2":continue
        e=entities[j["blind_id"]];actual=Path(assembled)/j["job_key"]/"af2/complex.a3m"
        if not actual.exists():
            rows.append(dict(job_key=j["job_key"],status="ACTUAL_AF2_MSA_MISSING_TYPED_UNRESOLVED"));continue
        original=n.checksum(j["input"]["path"])
        if original!=j["input"]:raise ValueError("Declared MSA input bytes changed")
        pr=subprocess.run([str(R/"env/colabfold/bin/python"),"-c",helper,str(Path(module["path"]).parent),j["input"]["path"],str(actual),e["target_sequence"],e["binder_sequence"]],
                          check=True,capture_output=True,text=True,env=env)
        verified=json.loads(pr.stdout)
        if verified["status"]!="EXACT_CHAIN_QUERY_PAIRED_UNPAIRED_ORDER_AND_DELETION_MATRICES_VERIFIED":raise ValueError("MSA semantic roundtrip not accepted")
        rows.append(dict(job_key=j["job_key"],status="INDEPENDENT_CURRENT_AF2_MSA_QUERY_FEATURES_ACCEPTED",input=original,actual=n.checksum(actual),retained_validator=module,semantic_features=verified))
    result=dict(status="AF2_ACTUAL_QUERY_MSA_FEATURES_REVALIDATED_WITH_RETAINED_CURRENT_SOURCE",source=n.checksum(__file__),retained_validator=module,
                n_jobs_expected=sum(j["engine"]=="af2" for j in plan["jobs"]),n_jobs_accepted=sum(r["status"]=="INDEPENDENT_CURRENT_AF2_MSA_QUERY_FEATURES_ACCEPTED" for r in rows),
                rows=rows,CUDA_visible_devices="",old_MSA_derivation_sources_executed=False,missing_MSA_derivation_sources_recovered=False)
    n.dump(out,result);return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--out-dir",required=True);p.add_argument("--history-policy",required=True);a=p.parse_args()
    cpu=n.cpu_allocation();source=original_pipeline();plan=source.read(PLAN)
    if plan["settings"]!=source.c.SETTINGS or len(plan["jobs"])!=20 or sum(j["expected_models"] for j in plan["jobs"])!=74:raise ValueError("Original native20/74 protocol changed")
    if plan["source"]["sha256"]!="876d29f9b8a20cf3f8bbf526262de96b1071a30b47590b632e5d31f97c362391":raise ValueError("Actual native original immutable scientific source changed")
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=False);science=out/"scored";science.mkdir()
    assembly=source.assemble(plan,ROOTS,science/"assembled_raw");source.dump(science/"assembly.json",assembly)
    source.score_with_metadata_receipt_correction(PLAN,ANALYSIS,science/"assembled_raw",science/"score.json")
    raw=source.independent_audit(plan,science/"assembled_raw",source.read(science/"score.json"));source.dump(science/"raw_audit.json",raw)
    source.c.verify_result(science/"score.json",MEMBERSHIP,science/"score_acceptance.json")
    msa_audit=independent_af2_msa(plan,science/"assembled_raw",science/"independent_current_msa_audit.json")
    # The closure archives/rehashes original and assembled evidence before independent readback.
    command=[sys.executable,str(Path(n.__file__)),"--old-run",str(science),"--out-dir",str(out/"closure"),
             "--prior-run-role","CURRENT_THREE_SOURCE_NATIVE_COLLECTION","--history-policy",a.history_policy,
             "--extra-source",str(Path(__file__)),"--extra-source",str(science/"independent_current_msa_audit.json")]
    subprocess.run(command,check=True)
    closed=n.read(out/"closure/acceptance.json");accepted=n.read(science/"score_acceptance.json")
    status=final_native_status(assembly,raw)
    if msa_audit["n_jobs_accepted"]!=msa_audit["n_jobs_expected"]:status="NATIVE74_CURRENT_COLLECTION_TYPED_UNRESOLVED_NOT_FULL74_ACCEPTED"
    result=dict(schema="native74-three-source-collection.v2",status=status,CPU_allocation=cpu,source=n.checksum(__file__),
        original_scientific_pipeline=n.checksum(PIPELINE),original_scientific_source=plan["source"],plan=n.checksum(PLAN),analysis=n.checksum(ANALYSIS),membership=n.checksum(MEMBERSHIP),
        raw_source_roots=[str(r) for r in ROOTS],expected_jobs=20,expected_models=74,actual_original_workers_copied=assembly["n_jobs_copied"],
        models_raw_confidence_accepted=raw["n_raw_confidence_accepted"],models_raw_typed_unresolved=raw["n_raw_unresolved"],
        models_contact_valid=accepted["n_models_valid"],models_no_interface_or_unresolved=accepted["n_unresolved_or_no_interface"],
        assembly=n.checksum(science/"assembly.json"),canonical_score=n.checksum(science/"score.json"),original_engine_score=n.checksum(science/"score_engine_original.json"),
        metadata_only_repair=n.checksum(science/"score_metadata_repair.json"),independent_raw_audit=n.checksum(science/"raw_audit.json"),
        independent_current_MSA_audit=n.checksum(science/"independent_current_msa_audit.json"),score_acceptance=n.checksum(science/"score_acceptance.json"),closure_supplement_acceptance=n.checksum(out/"closure/acceptance.json"),
        resource_closure=closed["resource_closure"],resource_aliases=closed["resource_aliases"],independent_closure_acceptance=closed["independent_closure_acceptance"],
        preserved_engineering_history=["native74_review_13124 typed71/74 and FAILED closure","native74_closure_v2_13169/13171/13172 diagnostics"],
        original_GPU_worker_bytes_modified=False,original_scientific_source_or_settings_modified=False,new_GPU_inference_submitted_by_this_CPU_collector=False,
        derived_CPU_scoring_only=True,engines_summarized_separately=True,experimental_probability=None,independent_experimental_validation=False,
        formal_RF_vs_BindCraft_benchmark_complete=False,ACTIVE_changed=False,offline_GPU_recompute_guaranteed=False,
        current_operative_scientific_resources_closed=True,complete_historical_generator_source_closure=False,
        historical_MSA_derivation_missing_n=closed["historical_unresolved_n"],historical_MSA_disposition=n.checksum(a.history_policy))
    n.dump(out/"acceptance.json",result);print(json.dumps({k:v for k,v in result.items() if k!="CPU_allocation"},indent=2),flush=True)
    if status!="NATIVE74_FULL_RAW_AND_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY":raise RuntimeError("Full74 collection not accepted; typed missing evidence retained")
if __name__=="__main__":main()

