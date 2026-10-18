#!/usr/bin/env python3
import ast,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
V=S/f"frozen/native_workflow_collectors_{os.environ['SLURM_JOB_ID']}";V.mkdir(parents=True)
O=S/f"runs/native_workflow_collectors_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
raw=subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True);assert "gres/gpu=" not in raw
receipts={};help_checks={}
for name in ["audit_actual_rf_native_v8.py","audit_actual_bc_native_v8.py"]:
 source=S/"code"/name;out=V/name;shutil.copyfile(source,out);ast.parse(out.read_text())
 compile(out.read_text(),str(out),"exec")
 p=subprocess.run([sys.executable,str(out),"--help"],text=True,capture_output=True)
 assert p.returncode==0 and "--plan" in p.stdout and "--run-receipt" in p.stdout and "--confidence-collector-source" in p.stdout
 receipts[name]=rec(out);help_checks[name]={"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr};out.chmod(0o444)
confidence=S/"runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py"
proof=S/"runs/native_collector_contracts_13166/outputs/acceptance.json"
assert json.loads(proof.read_text())["status"]=="NATIVE_RAW_CONFIDENCE_CPU_COLLECTOR_CONTRACTS_PASS"
settings=R/"steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py"
report={"status":"NATIVE_METHOD_CONTENT_COLLECTORS_CPU_SYNTAX_READBACK_PASS_ACTUAL_GPU_PENDING",
 "collectors":receipts,"confidence_collector_source":rec(confidence),"confidence_collector_contracts":rec(proof),"runtime_source":rec(settings),
 "cli_help":help_checks,"cpu_job":os.environ["SLURM_JOB_ID"],"scheduler_record":raw,
 "scientific_scope":"ENGINEERING_ONLY","no_model_inference":True,
 "scope":"Frozen collector syntax/API and9 confidence core contracts; not actual native GPU stage acceptance"}
path=O/"acceptance.json";path.write_text(json.dumps(report,indent=2)+"\n")
for p in O.iterdir():p.chmod(0o444)
O.chmod(0o555);V.chmod(0o555)
print(json.dumps({"acceptance":rec(path),"collectors":receipts,"confidence_collector":rec(confidence)},indent=2))

