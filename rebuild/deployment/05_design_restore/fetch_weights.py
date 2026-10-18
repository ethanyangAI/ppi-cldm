from pathlib import Path
import requests,hashlib,json,os
R=Path("/lustre/users/u21111210118/projects/test9");D=R/"assets/rfdiffusion";D.mkdir(parents=True,exist_ok=True)
url="https://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt"
dest=D/"Complex_base_ckpt.pt";tmp=dest.with_suffix(".part");expected="76e4e260aefee3b582bd76b77ab95d2592e64f00c51bf344968ab9239f3250bc"
h=hashlib.sha256()
with requests.get(url,stream=True,timeout=(30,180)) as resp:
 resp.raise_for_status()
 with tmp.open("wb") as f:
  for b in resp.iter_content(1024*1024):
   f.write(b);h.update(b)
assert tmp.stat().st_size==483619179
assert h.hexdigest()==expected
os.replace(tmp,dest)
rec={"status":"WEIGHT_HASH_MATCHES_HISTORICAL","path":str(dest),"url":url,"bytes":dest.stat().st_size,"sha256":h.hexdigest(),"historical_source":"task session RF_WEIGHTS output"}
(D/"Complex_base_ckpt.receipt.json").write_text(json.dumps(rec,indent=2));print(json.dumps(rec))
