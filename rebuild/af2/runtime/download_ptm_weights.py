import os,json,time,hashlib,concurrent.futures,urllib.request,numpy as np
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9");STEP=ROOT/"steps/03_af2_restore"
URL="https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar"
CACHE=STEP/"ptm_download";CACHE.mkdir(exist_ok=True)
with urllib.request.urlopen(urllib.request.Request(URL,method="HEAD"),timeout=30) as r:
 total=int(r.headers["Content-Length"]);etag=r.headers["ETag"];uphash=r.headers.get_all("x-goog-hash",[])
assert 5_000_000_000<total<7_000_000_000,total
def readrange(a,b):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(URL,headers={"Range":f"bytes={a}-{b}","If-Match":etag}),timeout=90) as r:
    assert r.status==206 and r.headers.get("Content-Range")==f"bytes {a}-{b}/{total}",str(r.headers)
    data=r.read()
   assert len(data)==b-a+1
   return data
  except Exception as e:
   if attempt==2:raise
   print("RETRY",a,b,attempt,str(e),flush=True);time.sleep(attempt+2)
headers=[];offset=0
while offset<total:
 block=readrange(offset,offset+511)
 if not any(block):break
 assert len(block)==512
 name=block[:100].split(b"\0")[0].decode();size=int(block[124:136].strip(b"\0 "),8)
 checksum=int(block[148:156].strip(b"\0 "),8)
 assert sum(block[:148])+8*32+sum(block[156:])==checksum
 assert 0<=size<500_000_000,(name,size)
 headers.append(dict(name=name,offset=offset+512,bytes=size,type=block[156:157].decode()))
 offset+=512+((size+511)//512)*512
(STEP/"ptm_archive_index.json").write_text(json.dumps(dict(url=URL,etag=etag,bytes=total,upstream_hash=uphash,members=headers),indent=2)+"\n")
print("ARCHIVE_INDEX",headers,flush=True)
params=ROOT/"assets/colabfold/params";params.mkdir(exist_ok=True)
records=[]
for modelnum in range(1,6):
 name=f"params_model_{modelnum}_ptm.npz";matches=[x for x in headers if Path(x["name"]).name==name]
 assert len(matches)==1
 x=matches[0];assert x["type"] in ("0","\0") and x["bytes"]>10_000_000
 chunks=(x["bytes"]+32*1024*1024-1)//(32*1024*1024)
 def fetch(i):
  start=x["offset"]+i*32*1024*1024;end=min(x["offset"]+x["bytes"]-1,start+32*1024*1024-1)
  p=CACHE/f"{modelnum}_{i:03d}";tmp=p.with_suffix(".partial")
  if p.exists() and p.stat().st_size==end-start+1:return p
  tmp.write_bytes(readrange(start,end));tmp.replace(p);return p
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:pieces=list(pool.map(fetch,range(chunks)))
 tmp=params/(name+".partial");sha=hashlib.sha256()
 with tmp.open("wb") as out:
  for p in pieces:
   with p.open("rb") as inp:
    for b in iter(lambda:inp.read(1024*1024),b""):out.write(b);sha.update(b)
 assert tmp.stat().st_size==x["bytes"]
 with np.load(tmp) as z:
  assert len(z.files)>100
  for k in z.files:assert np.isfinite(z[k]).all()
 dest=params/name;tmp.replace(dest)
 records.append(dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha.hexdigest()))
 for p in pieces:p.unlink()
 print("PTM_WEIGHT_VERIFIED",modelnum,sha.hexdigest(),flush=True)
(params/"download_finished.txt").write_text("All five PTM model weights extracted by validated byte ranges of official immutable-ETag HTTPS archive; NPZs fully read. See ptm_weights_receipt.json.\n")
receipt=dict(status="AF2_ALL_FIVE_PTM_WEIGHTS_VERIFIED",timestamp=time.time(),slurm_job_id=os.environ.get("SLURM_JOB_ID"),url=URL,etag=etag,archive_bytes=total,weights=records,checksum_semantics="Validated HTTPS byte ranges, tar header checksums, immutable ETag and readable finite NPZ arrays; per-file SHA256 recorded. Complete-archive digest not claimed for this range extraction.",license="AlphaFold parameters CC BY 4.0",license_source="https://github.com/google-deepmind/alphafold")
(STEP/"ptm_weights_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2),flush=True)
