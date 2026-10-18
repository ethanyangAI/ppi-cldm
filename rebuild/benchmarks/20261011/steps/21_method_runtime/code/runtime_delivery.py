#!/usr/bin/env python3
import hashlib,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/delivery_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def verify(p):
 value=json.loads(p.read_text())
 for key in ["sources","configs"]:
  for r in value.get(key,{}).values():assert rec(Path(r["path"]))==r
 return value
settings=S/"runs/rf_feature_reaudit_13058/outputs/pilot_settings_receipt.json";verify(settings)
features=S/"runs/bbf_features_13057/outputs/feature_manifest.json";v=json.loads(features.read_text())
assert v["status"]=="ALL22_JOBS_110_LITERAL_MODEL_INPUTS_CPU_VERIFIED"
assert v["source"]==rec(S/"frozen/bbf_backend_v2/bbf_feature_backend.py")
assert len(v["jobs"])==22 and sum(len(x["actual_validated_model_slots"]) for x in v["jobs"])==110
for j in v["jobs"]:assert rec(Path(j["features"]["path"]))==j["features"]
paths=[settings,features,S/"RUNTIME_AUDIT.md",S/"README.md",S/"runs/bcf_feature_audit_13039/outputs/acceptance.json",S/"runs/readiness_12980/outputs/acceptance.json",S/"runs/repair_12993/outputs/acceptance.json",S/"runs/finalize_13021/outputs/acceptance.json",S/"runs/rf_feature_reaudit_13058/outputs/acceptance.json",S/"frozen/bbf_backend_v2/bindcraft_env.sh"]
jobs="12946,12947,12948,12962,12967,12974,12977,12980,12982,12990,12993,13011,13013,13020,13021,13026,13028,13030,13032,13034,13039,13046,13048,13050,13055,13057,13058"
sacct=subprocess.check_output(["sacct","-j",jobs,"--format=JobID,JobName,State,Elapsed,AllocTRES","-P"],text=True);(O/"cpu_job_history.tsv").write_text(sacct)
result={"status":"PRIVATE_METHOD_RUNTIMES_AND_IMMUTABLE_BBF_BACKEND_CPU_VERIFIED_GPU_PILOT_PENDING","cpu_only":True,"gpu_jobs_submitted_by_runtime_agent":[],"required_user_credentials":[],"settings":rec(settings),"bbf_features":rec(features),"records":[rec(p) for p in paths]+[rec(O/"cpu_job_history.tsv")],"unresolved":["root-controlled complete GPU engineering attempt per method","root-controlled independent BBF110 GPU inference","formal matched-budget benchmark/common evaluator and scientific report"]}
(O/"acceptance.json").write_text(json.dumps(result,indent=2)+"\n")
(S/"RUNTIME_CPU_CURRENT.json").write_text(json.dumps({"status":result["status"],"acceptance":rec(O/"acceptance.json"),"pilot_settings":rec(settings),"bbf_feature_manifest":rec(features)},indent=2)+"\n")
print(result["status"],flush=True)

