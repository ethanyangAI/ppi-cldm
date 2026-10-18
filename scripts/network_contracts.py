import json
from pathlib import Path
import yaml
from ppiblocker.pipeline import prepare
from ppiblocker.common import EvidenceError,atomic_json,read_json
ROOT=Path("/lustre/users/u21111210118/projects/test9")
base=yaml.safe_load((ROOT/"source/configs/mdm2_tp53_benchmark.yaml").read_text())
work=ROOT/"steps/00_bootstrap/runs/rebuild_20260920/network_contracts"
work.mkdir(parents=True,exist_ok=True)
results=[]
cases=[("automatic_fetch",{},None),("same_chain",{"pdb":"1YCR","assembly":"1","chains":["A","A"]},"REQUESTED_STRUCTURE_REJECTED")]
for name,structure,error in cases:
 c=json.loads(json.dumps(base));c["structure"]=structure
 path=work/(name+".yaml");path.write_text(yaml.safe_dump(c))
 try:
  m=prepare(ROOT,path)
  status=read_json(m)["status"]
  assert error is None and status=="POSE_ACCEPTED",(name,status)
  results.append({"case":name,"passed":True,"manifest":str(m),"status":status})
 except EvidenceError as e:
  assert e.code==error,(name,e.code,str(e))
  results.append({"case":name,"passed":True,"rejection":e.code})
atomic_json(work/"results.json",results)
print(json.dumps(results,indent=2))

