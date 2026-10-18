import os,shutil,requests,zipfile,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from ppiblocker.common import *
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"70_rfd3_segmented_repair",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 url="https://files.ipd.uw.edu/pub/rfd3/rfd3_foundry_2025_12_01_remapped.ckpt"
 p=root/"assets/rfd3/rfd3_latest.ckpt"
 h=requests.head(url,timeout=60,allow_redirects=True);h.raise_for_status()
 total=int(h.headers["Content-Length"]);etag=h.headers.get("ETag");size=p.stat().st_size
 require(size<=total,"OVERSIZED_CHECKPOINT",str((size,total)))
 print("RESUME",size,"TOTAL",total,"ETAG",etag,flush=True)
 check=requests.get(url,headers={"Range":"bytes=0-1048575","If-Range":etag},timeout=90)
 require(check.status_code==206,"RANGE_UNSUPPORTED",str(check.status_code))
 with p.open("rb") as f:require(f.read(1048576)==check.content,"PREFIX_MISMATCH","Do not append")
 ranges=[(a,min(a+16*1024*1024,total)-1) for a in range(size,total,16*1024*1024)]
 def download(pair):
  a,b=pair;dest=run.path/"work"/f"{a}-{b}.part"
  for attempt in range(4):
   try:
    with requests.get(url,headers={"Range":f"bytes={a}-{b}","If-Range":etag},stream=True,timeout=(30,45)) as response:
     require(response.status_code==206 and response.headers["Content-Range"]==f"bytes {a}-{b}/{total}","RANGE_MISMATCH",str(response.headers))
     with dest.open("wb") as f:
      for chunk in response.iter_content(1024*1024):f.write(chunk)
    require(dest.stat().st_size==b-a+1,"CHUNK_LENGTH",str(dest))
    print("CHUNK_VERIFIED",a,b,flush=True);return dest
   except Exception:
    if attempt==3:raise
    time.sleep(2*(attempt+1))
 with ThreadPoolExecutor(max_workers=4) as ex:parts=list(ex.map(download,ranges))
 with p.open("ab") as out:
  for part in parts:
   with part.open("rb") as f:shutil.copyfileobj(f,out)
 require(p.stat().st_size==total,"INCOMPLETE_CHECKPOINT",str(p.stat().st_size))
 with zipfile.ZipFile(p) as z:require(z.testzip() is None,"CHECKPOINT_CRC","Corrupt archive")
 atomic_json(run.path/"outputs/receipt.json",dict(url=url,etag=etag,bytes=total,resumed_from=size,parts=[record_file(x) for x in parts],checkpoint=record_file(p),publisher_checksum_available=False))
 run.output("receipt",run.path/"outputs/receipt.json")
 print(run.finish("CHECKPOINT_TRANSPORT_VERIFIED","runtime_load_pending"),flush=True)
except Exception as e:run.fail(e);raise

