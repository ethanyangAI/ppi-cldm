import datetime, hashlib, json, os, shutil, subprocess
from pathlib import Path
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9"); step=R/"steps/12_physics_reassessment"
def receipt(p):
 p=Path(p); b=p.read_bytes()
 return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
native=R/"steps/06_native_diagnostics/runs/20261002T114000Z_11716/outputs"
items=[("native_4CH9",native/"4CH9_B_D_normalized.pdb"),
 ("native_6TTK",native/"6TTK_A_H_normalized.pdb"),
 ("native_2FLU",R/"steps/06_native_diagnostics/runs/20261002T114903Z_11737/outputs/2FLU_A_B_normalized.pdb")]
medfiles=sorted((R/"steps/10_pose_reassessment/runs").glob("*/outputs/primary_medoids.json"))
assert len(medfiles)==1,medfiles
med=json.loads(medfiles[0].read_text())
for e in med["entries"]:
 if e["is_co_major"]:
  p=Path(e["normalized_pdb"]["path"])
  assert receipt(p)==e["normalized_pdb"]
  items.append((e["candidate"]+"_"+e["cluster_id"],p))
run=step/"runs"/(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+os.environ["SLURM_JOB_ID"])
run.mkdir(parents=True,exist_ok=False); (run/"outputs").mkdir()
entries=[]
for identity,p in items:
 structure=PDBParser(QUIET=True).get_structure(identity,p)
 chains=list(structure[0]); assert [c.id for c in chains]==["A","B"]
 seqs=["".join(seq1(r.resname) for r in c.get_residues()) for c in chains]
 for seed in [1042,1043,1044]:
  entries.append(dict(identity=identity,seed=seed,input=receipt(p),sequences=seqs))
plan=dict(status="FROZEN_INPUTS_FOR_CPU_ROSETTA_DIAGNOSTICS",entries=entries,
 primary_medoids=receipt(medfiles[0]), environment_freeze=receipt(R/"env/physics-freeze.txt"),
 worker=receipt(R/"source/rebuild/physics_reassessment_worker.py"),
 native_positive_scope="observed experimental fragments, not full length proteins",
 thresholds="No pass/fail energy threshold or superiority claim")
p=run/"plan.json"; p.write_text(json.dumps(plan,indent=2)+"\n")
script=step/"code"/"worker.sbatch"
job=subprocess.check_output(["sbatch","--parsable","--account=u21111210118","--qos=normal",
 "--array=0-"+str(len(entries)-1)+"%4",str(script),str(p),str(run)],text=True).strip()
manifest=dict(status="SUBMITTED",job_id=job,plan=receipt(p),run=str(run),entry_count=len(entries))
(step/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest))

