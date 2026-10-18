import os,subprocess,shutil,json,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";job=os.environ["SLURM_JOB_ID"]
out=S/"runs"/("actual_bc_v8_identity_"+job);out.mkdir(parents=True,exist_ok=True);frozen=S/"frozen"/("bc_native_collector_v2_"+job);frozen.mkdir()
source=frozen/"audit_actual_bc_native_v8.py";shutil.copyfile(S/"code/audit_actual_bc_native_v8_v2.py",source)
subprocess.run(["python","-m","py_compile",str(source)],check=True)
args=["python",str(source),"--attempt-dir",str(R/"steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_1/attempts/000000"),
 "--target-manifest",str(R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json"),
 "--config",str(R/"steps/22_matched_benchmark/settings/pilot_v8/bindcraft.json"),"--config-sha256","ede838ddf98e459aceb1175c682df47439dc38f2125afd3c9c328c286e70c29f",
 "--runtime-source",str(R/"steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py"),
 "--confidence-collector-source",str(S/"runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py"),
 "--plan",str(R/"steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json"),
 "--run-receipt",str(R/"steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_1/run_receipt.json"),"--output-dir",str(out/"outputs")]
subprocess.run(args,check=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
summary={"source":rec(source),"bc_base_acceptance":rec(out/"outputs/acceptance.json"),"bc_trajectory":rec(out/"outputs/native_bindcraft_trajectory.json"),
 "rf_acceptance":rec(S/"runs/actual_native_v8_13213/outputs/rf/acceptance.json"),"identity_diagnostic":rec(S/"runs/bc_native_identity_13217/outputs/identity.json")}
(out/"summary_receipts.json").write_text(json.dumps(summary,indent=2)+"\n")
source.chmod(0o444);frozen.chmod(0o555);print(json.dumps(summary,indent=2))
