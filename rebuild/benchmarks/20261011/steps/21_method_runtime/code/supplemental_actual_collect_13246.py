import os,json,hashlib,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";job=os.environ["SLURM_JOB_ID"];out=S/"runs"/("supplemental_actual_current_"+job)/"outputs"
source=S/"frozen/supplemental_content_collector_13244/audit_supplemental_bindcraft_v1.py"
result=subprocess.run(["python",str(source),"--gpu-output",str(S/"runs/bindcraft_supplemental_gpu_13246/outputs"),"--output-dir",str(out)])
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
history={"status":"SUPERSEDED_SUPPLEMENTAL_API_CONTENT_VERIFIED_PYTHON_KEY_RNG_UNRESOLVED_ENGINEERING_HISTORY_ONLY",
"historical_gpu_job":"13234","historical_cpu_content_audit":rec(S/"runs/supplemental_actual_content_13235/outputs/acceptance.json"),
"historical_source":rec(S/"frozen/supplemental_bindcraft_13224/bindcraft_supplemental_stage_coverage.py"),
"rng_limitation_proof":rec(S/"runs/native_rng_semantics_13242/outputs/acceptance.json"),
"current_corrected_gpu_job":"13246","current_actual_acceptance":rec(out/"acceptance.json") if (out/"acceptance.json").exists() else None,
"hist_allocation_accounting":subprocess.check_output(["sacct","-j","13234","-n","-P","--format=JobIDRaw,JobID,State,ElapsedRaw,AllocTRES,ExitCode"],text=True),
"scope":"Old20 pool/two nativeAF2/modelmetrics are actual API content but do not establish root-seed MPnn replay; no current seeded/positive/formal claim. Old bytes unchanged and all extra costs retained."}
out.mkdir(parents=True,exist_ok=True);p=out/"old_supplemental_rng_history_disposition.json"
if p.exists():raise FileExistsError(p)
p.write_text(json.dumps(history,indent=2)+"\n")
raise SystemExit(result.returncode)
