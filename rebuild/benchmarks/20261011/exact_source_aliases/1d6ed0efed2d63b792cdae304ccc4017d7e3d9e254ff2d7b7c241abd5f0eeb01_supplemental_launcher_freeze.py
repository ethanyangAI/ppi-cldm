import os,json,hashlib,shutil,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";job=os.environ["SLURM_JOB_ID"]
root=S/"runs/supplemental_stage_prepare_13219/outputs";frozen=S/"frozen"/("supplemental_launcher_"+job);frozen.mkdir()
p=frozen/"gpu_launcher.sh";shutil.copyfile(S/"code/bc_supplemental_gpu_launcher.sh",p);subprocess.run(["bash","-n",str(p)],check=True);p.chmod(0o444);frozen.chmod(0o555)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
out=S/"runs"/("supplemental_launcher_"+job)/"outputs";out.mkdir(parents=True)
doc={"status":"SUPPLEMENTAL_FIXED_INPUT_CALLS_SOURCE_AND_LAUNCHER_CPU_ACCEPTED_NOT_GPU_EXECUTED","config":rec(root/"config.json"),"fixed_pose":rec(root/"fixed_pose.json"),"prepare_acceptance":rec(root/"acceptance.json"),
"source":rec(S/"frozen/supplemental_bindcraft_13219/bindcraft_supplemental_stage_coverage.py"),"test_source":rec(S/"frozen/supplemental_bindcraft_13219/test_bindcraft_supplemental_stage_coverage.py"),
"contracts_stdout":rec(S/"logs/supplemental_stage_prepare_13219.out"),"contracts_stderr":rec(S/"logs/supplemental_stage_prepare_13219.err"),
"launcher":rec(p),"budget_gpu_seconds":3600,"scientific_scope":"ENGINEERING_STAGE_COVERAGE_ONLY_NOT_NATIVE_ACCEPTED_NOT_FORMAL","actual_fixed_pose_identity":rec(S/"runs/bc_native_identity_13217/outputs/identity.json"),"cpu_job":job,"scheduler":subprocess.check_output(["scontrol","show","job","-o",job],text=True)}
(out/"acceptance.json").write_text(json.dumps(doc,indent=2)+"\n");print(json.dumps(doc,indent=2))
