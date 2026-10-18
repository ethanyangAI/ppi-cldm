import concurrent.futures, hashlib, json, os, tarfile, time
from pathlib import Path
import requests
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/"assets/boltz";D.mkdir(parents=True,exist_ok=True)
OUT=R/"steps/09_boltz_restore/outputs";OUT.mkdir(parents=True,exist_ok=True)
REV="6fdef46d763fee7fbb83ca5501ccceff43b85607"
ASSETS={
"mols.tar":(1855662080,"39e076d96dbec6b4e86982bbda16f3a53a2a60c9bdc17828d88f6f9a0c7d1fd7"),
"boltz2_conf.ckpt":(2286561469,"090e82ac8c92f5e943fa1b39e7410a44027bea7243c0bbb3caa67a77fc1428e1"),
"boltz2_aff.ckpt":(2062139170,"dcc5cd3722b1c9eaa34267e4ae32f55cbbf1963f4c19319381ccfa30fdd2ca9e")}
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def fetch(item):
 name,(size,expected)=item;p=D/name;attempts=[]
 if p.exists() and p.stat().st_size==size and sha(p)==expected:
  return dict(name=name,status="HASH_VERIFIED_REUSED",bytes=size,sha256=expected)
 partial=D/(name+".part")
 for host in ("https://huggingface.co","https://hf-mirror.com"):
  url=f"{host}/boltz-community/boltz-2/resolve/{REV}/{name}"
  for attempt in range(1,3):
   started=time.monotonic();last=started
   try:
    print("FETCH",name,host,attempt,flush=True)
    with requests.get(url,stream=True,timeout=(20,90),headers={"User-Agent":"PPI-source-reconstruction/1.0"}) as r:
     r.raise_for_status();h=hashlib.sha256();total=0
     with partial.open("wb") as f:
      for block in r.iter_content(4*1024*1024):
       f.write(block);h.update(block);total+=len(block)
       if total>size:raise ValueError("response exceeds pinned size")
       if time.monotonic()-started>5400:raise TimeoutError("bounded 90min transfer")
       if time.monotonic()-last>30:
        print("PROGRESS",name,total,size,flush=True);last=time.monotonic()
    assert total==size,(name,"size",total,size)
    assert h.hexdigest()==expected,(name,"sha256 mismatch")
    partial.replace(p)
    receipt=dict(name=name,status="HASH_VERIFIED",url=url,hf_commit=REV,bytes=size,sha256=expected,attempts=attempts)
    p.with_suffix(p.suffix+".receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("VERIFIED",name,total,expected,flush=True);return receipt
   except Exception as ex:
    err={"host":host,"attempt":attempt,"error_type":type(ex).__name__}
    if isinstance(ex,requests.HTTPError):err["status_code"]=ex.response.status_code
    attempts.append(err);print("FETCH_FAILED",name,err,flush=True)
 raise RuntimeError(json.dumps(dict(name=name,attempts=attempts)))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(fetch,ASSETS.items()))
if not (D/"mols").exists():
 stage=D/("mols_extract_"+os.environ.get("SLURM_JOB_ID","manual"));stage.mkdir(exist_ok=True)
 with tarfile.open(D/"mols.tar") as tar:
  members=tar.getmembers()
  for m in members:
   q=(stage/m.name).resolve()
   assert q.is_relative_to(stage.resolve()),m.name
   assert m.isfile() or m.isdir(),m.name
   assert not m.islnk() and not m.issym(),m.name
  print("EXTRACT",len(members),flush=True);tar.extractall(stage,members=members)
 assert (stage/"mols").is_dir()
 (stage/"mols").rename(D/"mols")
print("MOLS_FILES",sum(p.is_file() for p in (D/"mols").rglob("*")),flush=True)
receipt=dict(status="BOLTZ_ASSETS_HASH_VERIFIED_NO_INFERENCE",hf_commit=REV,assets=results,mols_files=sum(p.is_file() for p in (D/"mols").rglob("*")))
(OUT/"assets_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print("BOLTZ_ASSETS_READY",flush=True)

