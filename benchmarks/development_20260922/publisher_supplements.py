import requests,shutil,concurrent.futures,subprocess
from pathlib import Path
from ppiblocker.common import Run,atomic_json,record_file,read_json,require
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"47_publisher_supplements",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
sources=[]
for doi,base,exts in [("s41586-023-06415-8","41586_2023_6415",[(1,"pdf")]),("s41586-025-09429-6","41586_2025_9429",[(1,"pdf"),(4,"csv"),(5,"xlsx")])]:
 for i,ext in exts:
  name=f"{base}_MOESM{i}_ESM.{ext}"
  sources.append(dict(id=name,url=f"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2F{doi}/MediaObjects/{name}"))
def fetch(s):
 p=run.path/"outputs"/s["id"]
 try:
  with requests.get(s["url"],stream=True,timeout=(30,120)) as r:
   r.raise_for_status()
   with p.open("wb") as f:
    for b in r.iter_content(1024*1024):f.write(b)
  if p.suffix==".pdf":
   require(p.read_bytes()[:4]==b"%PDF","NOT_PDF",str(p))
   code="from pypdf import PdfReader;import sys;from pathlib import Path;p=Path(sys.argv[1]);p.with_suffix('.txt').write_text('\\n'.join(f'PAGE {i+1}\\n'+(x.extract_text() or '') for i,x in enumerate(PdfReader(p).pages)))"
   subprocess.run([root/"env/metrics/bin/python","-c",code,str(p)],check=True)
  return dict(**s,status="FETCHED",artifact=record_file(p))
 except Exception as e:return dict(**s,status="FAILED",error=str(e))
records=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,sources))
for r in records:
 print(r,flush=True)
 if r["status"]=="FETCHED":run.output(r["id"],r["artifact"]["path"])
atomic_json(run.path/"outputs/receipts.json",records);run.output("receipts",run.path/"outputs/receipts.json")
print(run.finish("PUBLISHER_SUPPLEMENTS_RETRIEVED","primary_source",dict(failed=sum(x["status"]=="FAILED" for x in records))),flush=True)
