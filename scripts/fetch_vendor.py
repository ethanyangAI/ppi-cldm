import io,json,tarfile,hashlib,os
from pathlib import Path
import requests
ROOT=Path(os.environ.get("PPIBLOCKER_ROOT",str(Path("/lustre/users/u21111210118/projects/test9")))).resolve()
lock=json.loads((Path(__file__).resolve().parents[1]/"environment/vendor-lock.json").read_text())
dest=ROOT/"vendor";dest.mkdir(parents=True,exist_ok=True)
for repo,expected in lock.items():
 out=dest/repo;commit=expected["commit"]
 if (out/"UPSTREAM.json").exists():
  current=json.loads((out/"UPSTREAM.json").read_text())
  assert current["commit"]==commit and current["sha256"]==expected["sha256"],f"Vendor differs from lock: {repo}"
  continue
 org=expected["repository"].split("/")[-2]
 url=f"https://codeload.github.com/{org}/{repo}/tar.gz/{commit}"
 r=requests.get(url,timeout=180);r.raise_for_status();data=r.content
 assert hashlib.sha256(data).hexdigest()==expected["sha256"],f"Archive checksum failed: {repo}"
 with tarfile.open(fileobj=io.BytesIO(data),mode="r:gz") as tar:
  for m in tar.getmembers():
   parts=Path(m.name).parts[1:]
   if not parts:continue
   p=out.joinpath(*parts)
   if not p.resolve().is_relative_to(out.resolve()) or m.issym() or m.islnk():raise RuntimeError("unsafe archive")
   if m.isdir():p.mkdir(parents=True,exist_ok=True)
   elif m.isfile():
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())
 (out/"UPSTREAM.json").write_text(json.dumps({**expected,"archive":url},indent=2))
 print(repo,commit,len(data),flush=True)
