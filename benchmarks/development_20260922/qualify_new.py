import sys,shutil,concurrent.futures
from pathlib import Path
from ppiblocker.common import Run,atomic_json,record_file,read_json
from ppiblocker.identity import Repository
root=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(root/"steps/12_extended_qualification/code"))
from qualify_extended import qualify_case
up=root/"source/benchmarks/development_20260922/protocol.json"
pairs=[
 ("N01","RNH1","RNASE1","LRR-enzyme","extended domain interface"),
 ("N02","UBE2I","SUMO1","SUMO enzyme","domain-domain noncovalent"),
 ("N03","TSG101","UBB","UEV-ubiquitin","domain-domain"),
 ("N04","YAP1","WBP1","WW","PPXY peptide"),
 ("N05","NEDD4","ARRB2","WW","PPXY peptide"),
 ("N06","DLG4","CRIPT","PDZ","terminal beta strand"),
 ("N07","DLG4","GRIN2B","PDZ","terminal beta strand"),
 ("N08","NCK1","WASL","SH3","polyproline peptide"),
 ("N09","GRB2","GAB1","SH3","polyproline peptide"),
 ("N10","SUMO1","PIAS2","SUMO","SIM beta strand"),
 ("N11","BIRC4","DIABLO","IAP","metal context challenge"),
 ("N12","GIPC1","SEMA4C","PDZ","terminal peptide")]
if len(sys.argv)>1:pairs=[p for p in pairs if p[0] in sys.argv[1].split(",")]
run=Run(root,"35_new_target_qualification",[record_file(up)])
shutil.copy2(__file__,run.path/"qc/driver.py")
# Separate retrieval caches per worker avoid concurrent writes to shared receipt paths.
def one(item):
 cid,a,b,family,geometry=item
 row=[cid,a,b,family,geometry,"soluble construct context pending","C0","none","candidate","unreviewed","exploratory","UNASSIGNED","",""]
 repo=Repository(root/"cache/new_qualification"/cid)
 result=qualify_case(row,repo)
 return result,repo.receipts
out=[];receipts=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 fs={ex.submit(one,p):p for p in pairs}
 for f in concurrent.futures.as_completed(fs):
  p=fs[f]
  try:r,rec=f.result();receipts+=rec
  except Exception as e:r=dict(case_id=p[0],target=p[1],partner=p[2],status="ERROR",error=str(e))
  out.append(r);atomic_json(run.path/"outputs/qualification.json",dict(cases=sorted(out,key=lambda r:r["case_id"]),complete=len(out)==len(pairs),planned=len(pairs)))
  print(r["case_id"],r["status"],len(r.get("structural_candidates",[])),flush=True)
atomic_json(run.path/"outputs/receipts.json",receipts)
run.output("qualification",run.path/"outputs/qualification.json");run.output("receipts",run.path/"outputs/receipts.json")
print(run.finish("ADDITIONAL_TARGET_INVENTORY_COMPLETE","structural_candidates_not_qualified"),flush=True)

