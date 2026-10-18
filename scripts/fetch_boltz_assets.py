from pathlib import Path
import hashlib,json,time,tarfile
import requests
ROOT=Path("/lustre/users/u21111210118/projects/test9")
dest=ROOT/"assets/boltz";dest.mkdir(parents=True,exist_ok=True)
assets={
 "mols.tar":["https://huggingface.co/boltz-community/boltz-2/resolve/main/mols.tar"],
 "boltz2_conf.ckpt":["https://model-gateway.boltz.bio/boltz2_conf.ckpt","https://huggingface.co/boltz-community/boltz-2/resolve/main/boltz2_conf.ckpt"],
 "boltz2_aff.ckpt":["https://model-gateway.boltz.bio/boltz2_aff.ckpt","https://huggingface.co/boltz-community/boltz-2/resolve/main/boltz2_aff.ckpt"]}
for name,urls in assets.items():
 p=dest/name;receipt=p.with_suffix(p.suffix+".receipt.json")
 if p.exists() and receipt.exists():continue
 error=None
 for url in urls:
  try:
   print("DOWNLOAD",name,url,flush=True)
   r=requests.get(url,stream=True,timeout=(30,180));r.raise_for_status()
   h=hashlib.sha256();total=0;last=time.monotonic()
   with p.with_suffix(p.suffix+".part").open("wb") as f:
    for block in r.iter_content(1024*1024):
     f.write(block);h.update(block);total+=len(block)
     if time.monotonic()-last>30:
      print(name,total,flush=True);last=time.monotonic()
   assert total>1024*1024
   p.with_suffix(p.suffix+".part").replace(p)
   receipt.write_text(json.dumps({"url":url,"sha256":h.hexdigest(),"bytes":total},indent=2))
   print("DONE",name,total,h.hexdigest(),flush=True);error=None;break
  except Exception as e:error=e;print("DOWNLOAD_FAILED",name,str(e),flush=True)
 if error:raise error
if not (dest/"mols").exists():
 with tarfile.open(dest/"mols.tar") as tar:
  for m in tar.getmembers():
   p=(dest/m.name).resolve()
   if not p.is_relative_to(dest.resolve()) or m.issym() or m.islnk():raise RuntimeError("unsafe archive member")
  tar.extractall(dest)
print("BOLTZ_ASSETS_READY",flush=True)

