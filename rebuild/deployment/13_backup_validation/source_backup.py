import ast,datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"source"
def receipt(p):
 b=Path(p).read_bytes();return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
out=S/"rebuild/deployment";out.mkdir(parents=True,exist_ok=True);records=[]
for name in ["05_design_restore","09_boltz_restore","11_physics_restore","12_physics_reassessment"]:
 for p in sorted((R/"steps"/name/"code").glob("*")):
  if p.suffix not in [".py",".sh",".sbatch"] or not p.is_file():continue
  d=out/name/p.name;d.parent.mkdir(parents=True,exist_ok=True)
  content=p.read_text()
  if p.suffix in [".sh",".sbatch"] and 'source /opt/app/conda' in content and 'export PS1=' not in content:
   content=content.replace('source /opt/app/conda', 'export PS1="${PS1:-}"\nsource /opt/app/conda')
  d.write_text(content);records.append(dict(source=receipt(p),archived=receipt(d),changed=content!=p.read_text()))
  if p.suffix==".py":ast.parse(content,filename=str(d))
  else:subprocess.run(["bash","-n",str(d)],check=True)
frozen=S/"environment/rebuild-freezes";frozen.mkdir(exist_ok=True)
for p in sorted((R/"env").glob("*.txt")):
 if p.stat().st_size<1000000:
  d=frozen/p.name;shutil.copy2(p,d);records.append(dict(source=receipt(p),archived=receipt(d),changed=False))
for p in sorted((R/"assets").rglob("*receipt.json")):
 if "mols/" in str(p) or p.stat().st_size>2000000:continue
 d=S/"environment/rebuild-assets"/p.relative_to(R/"assets");d.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(p,d);records.append(dict(source=receipt(p),archived=receipt(d),changed=False))
(out/"README.md").write_text("""# Deployment reconstruction records
These small files record the explicit reconstruction steps on public_cluster_2.
Use ../../scripts/submit_public.sh for routine workflow execution.
Installation and acceptance scripts retain fixed run paths for audit and require reviewed inputs for a new deployment.
Shell copies include a PS1 guard where necessary; original execution hashes are preserved in MANIFEST.json.
No model weights, environments, structure data or credentials are committed here.
""")
(out/"MANIFEST.json").write_text(json.dumps(dict(status="ARCHIVED_RECONSTRUCTION_CODE_AND_VERSION_RECEIPTS",files=records),indent=2)+"\n")
# Refuse unexpectedly large untracked files or common credential token patterns.
untracked=subprocess.check_output(["git","ls-files","--others","--exclude-standard"],cwd=S,text=True).splitlines()
oversized=[p for p in untracked if (S/p).is_file() and (S/p).stat().st_size>5000000]
assert not oversized, oversized
subprocess.run(["git","-c","core.whitespace=-blank-at-eof","diff","--check"],cwd=S,check=True)
subprocess.run(["git","add","--all"],cwd=S,check=True)
subprocess.run(["git","-c","core.whitespace=-blank-at-eof","diff","--cached","--check"],cwd=S,check=True)
print("STAGED_FILE_COUNT",len(subprocess.check_output(["git","-c","core.whitespace=-blank-at-eof","diff","--cached","--name-only"],cwd=S,text=True).splitlines()))
subprocess.run(["git","-c","user.name=PPI Reconstruction","-c","user.email=u21111210118@localhost","commit","-m","Reconstruct audited PPI blocker workflow on public cluster"],cwd=S,check=True)
commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=S,text=True).strip()
bundle=R/"archive/source_reconstruction_20261002.bundle"
assert not bundle.exists()
subprocess.run(["git","bundle","create",str(bundle),"--all"],cwd=S,check=True)
subprocess.run(["git","bundle","verify",str(bundle)],cwd=S,check=True)
restore=R/"steps/13_backup_validation/runs"/("source_"+os.environ["SLURM_JOB_ID"])
restore.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(["git","clone",str(bundle),str(restore)],check=True)
assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=restore,text=True).strip()==commit
files=subprocess.check_output(["git","ls-files"],cwd=S,text=True).splitlines()
assert all(receipt(S/p)["sha256"]==receipt(restore/p)["sha256"] for p in files)
env=os.environ.copy();env["PYTHONPATH"]=str(restore/"src");env["OPENBLAS_NUM_THREADS"]="1"
subprocess.run([str(R/"env/core/bin/python"),"-m","pytest","-q"],cwd=restore,env=env,check=True)
result=dict(status="SOURCE_BUNDLE_RESTORED_HASHES_AND_TESTS_VERIFIED",commit=commit,branch="rebuild/public-cluster-20261002",
 bundle=receipt(bundle),tracked_files=len(files),restore_path=str(restore),restored_pytest="PASSED",
 archive_records=len(records),offsite_backup=False,github_push=False)
dest=R/"steps/13_backup_validation/source_acceptance.json";dest.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))

