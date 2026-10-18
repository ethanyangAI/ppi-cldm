import shutil
from util import *
run=Run(R,"92_strengthening_mutant_monomers",[record_file(SETUP)]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 p,m=one("82_strengthening_extensions","EXTENSION_INPUTS_READY");plan=read_json(verify_file(m["outputs"]["plan"]));refs={e["id"]:e for e in baseplan()["candidates"]};entries=[]
 for e in plan["entries"]:
  if e["kind"]!="ablation":continue
  entries.append(dict(id=e["id"]+"_mono",parent=e["id"],original_parent=e["parent"],kind="monomer",sequence=e["sequence"],target_sequence="",reference=refs[e["parent"]]["backbone"],msa=None,slot=114+len(entries),interpretation="mutant fold support separates global destabilization from interface perturbation"))
 require(len(entries)==15,"MUTANT_COUNT",str(len(entries)))
 atomic_json(run.path/"outputs/plan.json",dict(entries=entries));run.output("plan",run.path/"outputs/plan.json");run.manifest["inputs"].append(record_file(p))
 print(run.finish("MUTANT_MONOMER_INPUTS_READY","protocol_frozen"),flush=True)
except Exception as x:run.fail(x);raise

