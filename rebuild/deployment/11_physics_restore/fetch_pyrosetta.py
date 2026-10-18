import re,requests,urllib.parse,hashlib,zipfile,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");D=R/"assets/pyrosetta";D.mkdir(parents=True,exist_ok=True)
index="https://west.rosettacommons.org/pyrosetta/quarterly/release.cxx11thread.serialization/"
name="pyrosetta-2026.29+releasequarterly.80a0635615-cp310-cp310-linux_x86_64.whl"
res=requests.get(index,timeout=90);res.raise_for_status()
hrefs=re.findall(r'href=["\']([^"\']+)["\']',res.text)
xs=[x for x in hrefs if urllib.parse.unquote(x.split("#")[0]).endswith(name)]
assert len(xs)==1,xs
url=urllib.parse.urljoin(index,xs[0]).split("#")[0];p=D/name;q=p.with_suffix(".part")
with requests.get(url,stream=True,timeout=(30,180)) as res:
 res.raise_for_status();expected=int(res.headers.get("Content-Length",0));h=hashlib.sha256()
 with q.open("wb") as f:
  for b in res.iter_content(1024*1024):f.write(b);h.update(b)
assert expected and q.stat().st_size==expected
with zipfile.ZipFile(q) as z:assert z.testzip() is None
q.replace(p)
rec=dict(url=url,path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest(),status="VERSION_PINNED_DOWNLOAD_CRC_VERIFIED",historical_sha_match_claimed=False)
(D/"receipt.json").write_text(json.dumps(rec,indent=2));print(json.dumps(rec))
