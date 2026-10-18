import os,json,time,re,hashlib
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/08_candidate_refolds";plan=json.loads((S/"plan.json").read_text())
def rec(p):
 b=p.read_bytes();return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
accepted=[];errors=[]
for e in plan["entries"]:
 runs=[p for p in (S/"runs").glob("*/manifest.json") if (m:=json.loads(p.read_text())).get("slot")==e["slot"] and m["status"]=="AF2_PREDICTIONS_GENERATED_PENDING_CPU_ACCEPTANCE"]
 if len(runs)!=1:
  errors.append({"slot":e["slot"],"id":e["id"],"error":"Expected one generated run","found":len(runs)});continue
 p=runs[0];m=json.loads(p.read_text());out=Path(m["output_directory"]);models=[];identities=set()
 cfg=m["effective_config"];assert cfg["max_seq"]==(128 if e["mode"]=="complex" else 1);assert cfg["max_extra_seq"]==(256 if e["mode"]=="complex" else 1)
 try:
  for pdb in sorted(out.glob("*_unrelaxed_rank_*.pdb")):
   mat=re.search(r"_model_(\d+)_seed_(\d+)\.pdb$",pdb.name);assert mat,pdb.name
   ident=tuple(map(int,mat.groups()));assert ident not in identities;identities.add(ident)
   score=pdb.with_name(pdb.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json"));obj=json.loads(score.read_text())
   structure=PDBParser(QUIET=True).get_structure("x",pdb)
   chains=["".join(seq1(r.resname) for r in c if r.id[0]==" " and "CA" in r) for c in next(structure.get_models())]
   chains=[x for x in chains if x];expected=[e["target_sequence"],e["sequence"]] if e["mode"]=="complex" else [e["sequence"]]
   assert chains==expected,(pdb.name,chains,expected)
   n=sum(map(len,expected));pae=np.asarray(obj["pae"]);plddt=np.asarray(obj["plddt"])
   assert pae.shape==(n,n) and plddt.shape==(n,) and np.isfinite(pae).all() and np.isfinite(plddt).all()
   assert np.isfinite(obj["ptm"]) and (e["mode"]!="complex" or np.isfinite(obj["iptm"]))
   models.append({"model":ident[0],"seed":ident[1],"pdb":rec(pdb),"scores":rec(score),"chain_lengths":list(map(len,chains)),"pae_shape":list(pae.shape),"ptm":obj["ptm"],"iptm":obj.get("iptm"),"mean_plddt":float(plddt.mean())})
  assert identities=={(i,j) for i in range(1,6) for j in (1042,1043,1044)},identities
  accepted.append({"slot":e["slot"],"id":e["id"],"mode":e["mode"],"run_manifest":rec(p),"models":models})
 except Exception as x:errors.append({"slot":e["slot"],"id":e["id"],"error":repr(x)})
report={"status":"ALL_90_AF2_MODELS_VERIFIED" if len(accepted)==6 and not errors else "INCOMPLETE_AF2_RECONSTRUCTION","timestamp":time.time(),"job_id":os.environ.get("SLURM_JOB_ID"),"plan":rec(S/"plan.json"),"accepted_entries":accepted,"errors":errors,"model_count":sum(len(e["models"]) for e in accepted),"coordinate_provenance":"NEW_PREDICTIONS_NOT_RESTORED_OLD_COORDINATES","scope":"Technical output identity/completeness validation; scientific scoring and clustering remain separate."}
p=S/"outputs/acceptance.json";p.parent.mkdir(exist_ok=True)
assert not p.exists(),"Acceptance file exists; use explicitly versioned rerun"
p.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="accepted_entries"},indent=2),flush=True)
if errors:raise RuntimeError(errors)
