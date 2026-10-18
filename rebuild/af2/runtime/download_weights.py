import os,json,time,hashlib,base64,concurrent.futures,tarfile,urllib.request,urllib.error,numpy as np
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
STEP=ROOT/"steps/03_af2_restore";DEST=ROOT/"assets/colabfold"
CACHE=STEP/"download";CACHE.mkdir(exist_ok=True)
URL="https://storage.googleapis.com/alphafold/alphafold_params_colab_2022-12-06.tar"
EXPECTED_SHA="3bbc7551818c41d322f917af317453becba672b3c68f4230d028f213c7b8554b"
WEIGHTS=[
"611da8fc7478928f68de12e8b226260ef1f4ce62bcc29b008572e52f4f212959",
"51362b0844382ae0f5720c59b81dd13a43eea40fbf9995dd2573bdab88865378",
"46d9bcad288edc7ad5a6362ee8e5f84307a69712e00e6c36b1ef9daf96ebc9ce",
"59bdabd2d69c07fe26b37882d544acbd1b9f89f196828f4220da49e0610b572c",
"917742be5a105d6b80f13f1f13f20459f27ec3fdcd34ea088b359f4502d6177f"]
with urllib.request.urlopen(urllib.request.Request(URL,method="HEAD"),timeout=30) as r:
 total=int(r.headers["Content-Length"]);etag=r.headers["ETag"];headerhash=",".join(r.headers.get_all("x-goog-hash",[]))
assert total==4099624960,(total,"Unexpected official archive size")
print("HEAD",total,etag,headerhash,flush=True)
CHUNK=32*1024*1024
def fetch(i):
 a=i*CHUNK;b=min(total,(i+1)*CHUNK)-1;p=CACHE/f"part_{i:04d}"
 if p.exists() and p.stat().st_size==b-a+1:return p
 for attempt in range(3):
  try:
   req=urllib.request.Request(URL,headers={"Range":f"bytes={a}-{b}","If-Match":etag})
   with urllib.request.urlopen(req,timeout=90) as r:
    assert r.status==206 and r.headers.get("Content-Range")==f"bytes {a}-{b}/{total}",str(r.headers)
    tmp=p.with_suffix(".partial")
    with tmp.open("wb") as out:
     while True:
      data=r.read(1024*1024)
      if not data:break
      out.write(data)
   assert tmp.stat().st_size==b-a+1
   tmp.replace(p);return p
  except Exception as e:
   print("RETRY",i,attempt,str(e),flush=True)
   if attempt==2:raise
   time.sleep(3*(attempt+1))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for i,p in enumerate(pool.map(fetch,range((total+CHUNK-1)//CHUNK))):
  if i%8==0:print("DOWNLOADED_PART",i,flush=True)
archive=CACHE/"weights.tar";sha=hashlib.sha256();md5=hashlib.md5()
with archive.open("wb") as out:
 for i in range((total+CHUNK-1)//CHUNK):
  with (CACHE/f"part_{i:04d}").open("rb") as inp:
   while True:
    data=inp.read(1024*1024)
    if not data:break
    out.write(data);sha.update(data);md5.update(data)
assert sha.hexdigest()==EXPECTED_SHA,sha.hexdigest()
expectedmd5=dict(x.strip().split("=",1) for x in headerhash.split(",")).get("md5")
assert base64.b64encode(md5.digest()).decode()==expectedmd5
print("ARCHIVE_VERIFIED",sha.hexdigest(),flush=True)
params=DEST/"params";params.mkdir(exist_ok=True)
records=[]
with tarfile.open(archive) as tf:
 for k,expected in enumerate(WEIGHTS,1):
  name=f"params_model_{k}_multimer_v3.npz"
  matches=[m for m in tf.getmembers() if Path(m.name).name==name]
  assert len(matches)==1
  m=matches[0];assert m.isfile() and m.size==373043148
  p=params/name;tmp=p.with_suffix(".partial");digest=hashlib.sha256()
  with tf.extractfile(m) as inp,tmp.open("wb") as out:
   while True:
    data=inp.read(1024*1024)
    if not data:break
    out.write(data);digest.update(data)
  assert digest.hexdigest()==expected,(name,digest.hexdigest())
  with np.load(tmp) as z:
   assert len(z.files)>100
   for key in z.files:
    arr=z[key];assert np.isfinite(arr).all(),key
  tmp.replace(p)
  records.append({"path":str(p),"bytes":p.stat().st_size,"sha256":expected})
(params/"download_complexes_multimer_v3_finished.txt").write_text("Official archive checked against prior complete-archive SHA256 and current upstream MD5; every model weight verified and readable.\n")
receipt={"status":"AF2_MULTIMER_V3_WEIGHTS_VERIFIED","slurm_job_id":os.environ.get("SLURM_JOB_ID"),"timestamp":time.time(),"url":URL,"etag":etag,"archive_bytes":total,"archive_sha256":sha.hexdigest(),"upstream_md5_base64":expectedmd5,"weights":records,"checksum_provenance":"SHA256 from former test9 archived execution history; independently matches current HTTPS upstream MD5.","license":"AlphaFold parameters CC BY 4.0; AlphaFold source Apache 2.0; ColabFold MIT","license_source":"https://github.com/google-deepmind/alphafold"}
(STEP/"weights_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
# Verified extracted weights are authoritative. Reproducible download cache is expendable.
for p in CACHE.glob("part_*"):
 if p.is_file():p.unlink()
archive.unlink()
print(json.dumps(receipt,indent=2),flush=True)
