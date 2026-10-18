import re,requests,urllib.parse,concurrent.futures,shutil,zipfile
from pathlib import Path
from ppiblocker.common import Run,record_file,atomic_json,require
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"58_pyrosetta_download",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 index="https://west.rosettacommons.org/pyrosetta/quarterly/release.cxx11thread.serialization/"
 r=requests.get(index,timeout=60);r.raise_for_status()
 name="pyrosetta-2026.29+releasequarterly.80a0635615-cp310-cp310-linux_x86_64.whl"
 hrefs=re.findall(r'href=["\']([^"\']+)["\']',r.text)
 selected=[x for x in hrefs if urllib.parse.unquote(x.split("#")[0]).endswith(name)]
 require(len(selected)==1,"WHEEL_INDEX_MATCH",str(selected));url=urllib.parse.urljoin(index,selected[0]).split("#")[0]
 head=requests.head(url,timeout=60);head.raise_for_status();size=int(head.headers["Content-Length"]);etag=head.headers.get("ETag")
 parts=list((root/"cache/benchmark_tmp").glob("pip-unpack-*/"+name))
 require(len(parts)==1,"PARTIAL_NOT_UNIQUE",str(parts));partial=parts[0];n=partial.stat().st_size;require(0<n<size,"PARTIAL_SIZE",str(n))
 def get(a,b):
  headers={"Range":f"bytes={a}-{b}"}
  if etag:headers["If-Match"]=etag
  rr=requests.get(url,headers=headers,stream=True,timeout=(30,120));require(rr.status_code==206,"RANGE_UNAVAILABLE",str(rr.status_code))
  require(rr.headers.get("Content-Range")==f"bytes {a}-{b}/{size}","RANGE_IDENTITY",str(rr.headers));data=rr.content
  require(len(data)==b-a+1,"RANGE_LENGTH",str(len(data)));return data
 with partial.open("rb") as f:require(f.read(1024*1024)==get(0,1024*1024-1),"PARTIAL_SOURCE_MISMATCH",name)
 dest=root/"assets/pyrosetta";dest.mkdir(exist_ok=True);out=dest/name
 with partial.open("rb") as f,out.open("wb") as g:
  left=n
  while left:
   data=f.read(min(left,8*1024*1024));require(data,"PARTIAL_TRUNCATED","download changed");g.write(data);left-=len(data)
 chunk=16*1024*1024
 def fetch(k):
  a=n+k*chunk;b=min(size-1,a+chunk-1);p=run.path/"work"/f"chunk{k:04d}";p.write_bytes(get(a,b));return p
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:chunks=list(ex.map(fetch,range((size-n+chunk-1)//chunk)))
 with out.open("ab") as f:
  for p in chunks:
   with p.open("rb") as g:shutil.copyfileobj(g,f)
 require(out.stat().st_size==size,"WHEEL_SIZE",str(out.stat().st_size))
 with zipfile.ZipFile(out) as z:require(z.testzip() is None,"WHEEL_CRC","CRC failure")
 atomic_json(run.path/"outputs/receipt.json",dict(index=index,url=url,etag=etag,bytes=size,prefix_reused=n,source_prefix_verified_bytes=1024*1024,zip_crc_verified=True,wheel=record_file(out)))
 run.output("receipt",run.path/"outputs/receipt.json");print(run.finish("PYROSETTA_WHEEL_VERIFIED","installation_asset_only"),flush=True)
except Exception as e:run.fail(e);raise
