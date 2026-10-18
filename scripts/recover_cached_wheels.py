from pathlib import Path
import zipfile,os
root=Path("/lustre/users/u21111210118/projects/test9")
out=root/"env/wheels";out.mkdir(exist_ok=True)
for p in (root/"env/pip_cache").rglob("*.body"):
 if p.stat().st_size<100000:continue
 try:
  with zipfile.ZipFile(p) as z:
   names=z.namelist()
   for name in names:
    if name.endswith(".dist-info/WHEEL") and (name.startswith("nvidia_cusparse_cu11-") or name.startswith("nvidia_cuda_runtime_cu11-")):
     tag=next(s[5:] for s in z.read(name).decode().splitlines() if s.startswith("Tag: "))
     filename=name.split(".dist-info")[0]+"-"+tag+".whl"
     q=out/filename
     if not q.exists():os.link(p,q)
     print(q,flush=True)
 except (zipfile.BadZipFile,OSError):pass

