import requests,concurrent.futures,shutil,re
from pathlib import Path
from ppiblocker.common import Run,record_file,atomic_json,require
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"50_bindcraft_full_weights",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
url="https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar"
try:
 h=requests.head(url,timeout=60);h.raise_for_status();etag=h.headers["ETag"];size=int(h.headers["Content-Length"])
 def getrange(a,b):
  r=requests.get(url,headers={"Range":f"bytes={a}-{b}","If-Match":etag},stream=True,timeout=(30,120))
  require(r.status_code==206,"RANGE_NOT_SUPPORTED",str(r.status_code))
  require(r.headers.get("Content-Range")==f"bytes {a}-{b}/{size}","RANGE_MISMATCH",str(r.headers))
  data=r.content;require(len(data)==b-a+1,"RANGE_SIZE",str(len(data)));return data
 headers=[];off=0
 while off<size:
  block=getrange(off,off+511)
  if not any(block):break
  name=block[:100].split(b"\0")[0].decode();n=int(block[124:136].strip(b"\0 "),8)
  checksum=int(block[148:156].strip(b"\0 "),8)
  require(sum(block[:148])+8*32+sum(block[156:])==checksum,"TAR_HEADER_CHECKSUM",name)
  headers.append(dict(name=name,offset=off+512,bytes=n,type=block[156:157].decode()))
  off+=512+((n+511)//512)*512
 atomic_json(run.path/"outputs/archive_index.json",dict(url=url,etag=etag,bytes=size,headers=headers));run.output("archive_index",run.path/"outputs/archive_index.json")
 dest=root/"assets/bindcraft/params";wanted={f"params_model_{i}_ptm.npz" for i in [1,3,4,5]};records=[]
 for item in headers:
  name=Path(item["name"]).name
  if name not in wanted:continue
  p=dest/name;parts=run.path/"work"/name;parts.mkdir()
  n=item["bytes"];begin=item["offset"];chunk=16*1024*1024
  def fetch(k):
   a=begin+k*chunk;b=min(begin+n-1,a+chunk-1);out=parts/f"{k:04d}"
   out.write_bytes(getrange(a,b));return out
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:chunks=list(ex.map(fetch,range((n+chunk-1)//chunk)))
  with p.open("wb") as out:
   for f in chunks:
    with f.open("rb") as inp:shutil.copyfileobj(inp,out)
  require(p.stat().st_size==n,"WEIGHT_SIZE",name);records.append(record_file(p));print("FETCHED",name,flush=True)
 required=[dest/f"params_model_{i}_{suffix}.npz" for suffix in ["ptm","multimer_v3"] for i in range(1,6)]
 require(all(p.is_file() for p in required),"MISSING_WEIGHTS","All ten required")
 atomic_json(run.path/"outputs/weights.json",dict(url=url,etag=etag,range_provenance="Official HTTPS immutable ETag; per-file SHA256 pinned; whole archive checksum not claimed",weights=[record_file(p) for p in required]))
 run.output("weights",run.path/"outputs/weights.json")
 print(run.finish("BINDCRAFT_ALL_WEIGHTS_PREPARED","model_assets_not_runtime_acceptance"),flush=True)
except Exception as e:run.fail(e);raise
