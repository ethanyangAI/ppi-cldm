import json,sys,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from colabfold.batch import msa_to_str,unserialize_msa
def serialize(args):
 row,msa,out=args
 cid="P09" if row["group"]=="published_controls" else row["group"]
 path=Path(msa[cid]["path"]);text=path.read_text()
 assert hashlib.sha256(path.read_bytes()).hexdigest()==msa[cid]["sha256"]
 target,binder=row["target_sequence"],row["sequence"]
 assert [l for l in text.splitlines() if l and not l.startswith(">")][0]==target
 query=[">101\n"+target+"\n",">102\n"+binder+"\n"]
 combined=msa_to_str([text,">binder\n"+binder+"\n"],query,[target,binder],[1,1])
 decoded=unserialize_msa([combined],[target,binder])
 assert decoded[2]==[target,binder] and decoded[3]==[1,1]
 assert all(sum(l.startswith(">") for l in a.splitlines())==1 for a in decoded[1])
 p=out/(row["id"]+".a3m");p.write_text(combined)
 return row["id"],dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
if __name__=="__main__":
 plan,receipt,out=map(Path,sys.argv[1:4]);out.mkdir(exist_ok=True)
 entries=json.loads(plan.read_text())["entries"];msa=json.loads(receipt.read_text())["targets"]
 with ProcessPoolExecutor(max_workers=4) as pool:
  records={}
  for key,record in pool.map(serialize,[(r,msa,out) for r in entries if r["group"]!="P32"]):
   records[key]=record;print("VALIDATED",len(records),key,flush=True)
 (out/"inputs.json").write_text(json.dumps(records,indent=2))
 print("SERIALIZED_AND_ROUNDTRIP_VALIDATED",len(records),flush=True)
