import os,shutil,requests,zipfile
from pathlib import Path
from ppiblocker.common import *
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"67_rfd3_weights_repair",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 url="https://files.ipd.uw.edu/pub/rfd3/rfd3_foundry_2025_12_01_remapped.ckpt"
 p=root/"assets/rfd3/rfd3_latest.ckpt"
 h=requests.head(url,timeout=60,allow_redirects=True);h.raise_for_status()
 total=int(h.headers["Content-Length"]);size=p.stat().st_size if p.exists() else 0
 require(size<=total,"OVERSIZED_CHECKPOINT",str((size,total)))
 if size<total:
  # Resume only after checking that the local prefix matches this source.
  check=requests.get(url,headers={"Range":"bytes=0-1048575"},timeout=90);require(check.status_code==206,"RANGE_UNSUPPORTED",str(check.status_code))
  with p.open("rb") as f:require(f.read(1048576)==check.content,"PREFIX_MISMATCH","Do not append to mismatched checkpoint")
  with requests.get(url,headers={"Range":f"bytes={size}-{total-1}"},stream=True,timeout=(60,180)) as response:
   require(response.status_code==206 and response.headers["Content-Range"].startswith(f"bytes {size}-"),"RANGE_MISMATCH",str(response.headers))
   with p.open("ab") as f:
    for chunk in response.iter_content(1024*1024):f.write(chunk)
 require(p.stat().st_size==total,"INCOMPLETE_CHECKPOINT",str(p.stat().st_size))
 with zipfile.ZipFile(p) as z:require(z.testzip() is None,"CHECKPOINT_CRC","Corrupt archive")
 atomic_json(run.path/"outputs/receipt.json",dict(url=url,etag=h.headers.get("ETag"),bytes=total,checkpoint=record_file(p),publisher_checksum_available=False))
 run.output("receipt",run.path/"outputs/receipt.json")
 print(run.finish("CHECKPOINT_TRANSPORT_VERIFIED","runtime_load_pending"))
except Exception as e:run.fail(e);raise

