import hashlib,json,sys,collections,statistics,math
from pathlib import Path
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9"); run=R/"steps/12_physics_reassessment/runs/20261002T120847Z_11767"
def receipt(p):
 p=Path(p); b=p.read_bytes()
 return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def verify(r):
 assert receipt(r["path"])==r, r["path"]
plan=json.loads((run/"plan.json").read_text()); verify(plan["worker"]); verify(plan["environment_freeze"]); verify(plan["primary_medoids"])
records=[]; errors=[]
for i,e in enumerate(plan["entries"]):
 p=run/f"outputs/task_{i}/result.json"
 try:
  x=json.loads(p.read_text()); verify(e["input"]); verify(x["input"]); verify(x["relaxed_pdb"])
  assert x["input"]==e["input"] and x["identity"]==e["identity"] and x["seed"]==e["seed"]
  assert x["environment_freeze"]==plan["environment_freeze"]
  assert x["plan"]==receipt(run/"plan.json") and x["sequences"]==e["sequences"]
  s=PDBParser(QUIET=True).get_structure("relax",x["relaxed_pdb"]["path"])
  assert len(list(s))==1
  ch=list(s[0]); assert [c.id for c in ch]==["A","B"]
  seqs=["".join(seq1(r.resname) for r in c.get_residues()) for c in ch]
  assert seqs==e["sequences"]
  assert all(math.isfinite(float(v)) for a in s.get_atoms() for v in a.coord)
  for key in ["dG_separated","dSASA","shape_complementarity","packstat","hbond_count","buried_unsatisfied","dG_per_area_x100"]:
   assert math.isfinite(x[key])
  records.append(dict(result=receipt(p),**x))
 except Exception as ex:errors.append(dict(task=i,error=repr(ex)))
groups=collections.defaultdict(list)
for x in records:groups[x["identity"]].append(x)
summary=[]
for name,xs in sorted(groups.items()):
 assert len(xs)==3 and sorted(x["seed"] for x in xs)==[1042,1043,1044]
 row=dict(identity=name,n_seeds=3)
 for key in ["dG_separated","dSASA","shape_complementarity","packstat","buried_unsatisfied"]:
  a=[x[key] for x in xs];row[key]=dict(median=statistics.median(a),min=min(a),max=max(a))
 summary.append(row)
out=dict(status="ALL_18_CPU_PHYSICS_RUNS_VERIFIED" if len(records)==18 and not errors else "INCOMPLETE",
 plan=receipt(run/"plan.json"),verified_count=len(records),errors=errors,summary=summary,results=[r["result"] for r in records],
 evidence_boundary="Computational diagnostics; seeds are technical replicates, not independent experiments. Native controls are observed fragments. No energy threshold, affinity, blockade, specificity or workflow superiority is established.")
(run/"acceptance.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
print(json.dumps({k:out[k] for k in ["status","verified_count","errors","summary"]},indent=2))
assert not errors and len(records)==18

