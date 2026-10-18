import json,shutil,requests,xml.etree.ElementTree as ET,concurrent.futures,subprocess
from pathlib import Path
from ppiblocker.common import Run,read_json,verify_file,record_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
run=Run(root,"42_primary_assay_review",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
lit=read_json(root/"steps/41_control_constructs/runs/20260922T101321Z_2f8f58bad35d/outputs/literature_extracts.json")
sources=[]
for key,base in [("rfd.xml","41586_2023_6415"),("bindcraft.xml","41586_2025_9429")]:
 for e in lit[key]["media"]:
  href=next((v for k,v in e["attrs"].items() if k.endswith("href")),None)
  if href and href.startswith(base):
   print("SUPPLEMENT",key,href,flush=True)
   sources.append(dict(id=href,url="https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs"+base.replace("_","-")+"/MediaObjects/"+href))
def fetch(s):
 p=run.path/"outputs"/s["id"]
 try:
  r=requests.get(s["url"],timeout=(30,90));r.raise_for_status();p.write_bytes(r.content)
  if p.suffix==".pdf":
   assert r.content[:4]==b"%PDF"
   code="from pypdf import PdfReader;import sys;from pathlib import Path;p=Path(sys.argv[1]);p.with_suffix('.txt').write_text('\\n'.join(f'PAGE {i+1}\\n'+(x.extract_text() or '') for i,x in enumerate(PdfReader(p).pages)))"
   subprocess.run([root/"env/metrics/bin/python","-c",code,str(p)],check=True)
  return dict(**s,status="FETCHED",artifact=record_file(p))
 except Exception as e:return dict(**s,status="FAILED",error=str(e))
records=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(fetch,sources))
for r in records:
 if r["status"]=="FETCHED":run.output(r["id"],r["artifact"]["path"])
atomic_json(run.path/"outputs/receipts.json",records);run.output("receipts",run.path/"outputs/receipts.json")
for key,rec in read_json(root/"steps/41_control_constructs/runs/20260922T101321Z_2f8f58bad35d/outputs/external_schema.json").items():
 print("CSV",key,"n",rec["n"],"columns",[x for x in rec["columns"] if not any(y in x.lower() for y in ["interface_res","interface_aa","sequence"])],flush=True)
for p in sorted((root/"steps/35_new_target_qualification/runs").glob("*/outputs/qualification.json")):
 d=read_json(p)
 for c in d["cases"]:
  if c["case_id"] in ["N01","N03","N06","N07"]:
   print("TARGET",c["case_id"],[(x["pdb"],x["chains"],x["reasons"],x["context"]) for x in c.get("structural_candidates",[])],flush=True)
print(run.finish("PRIMARY_SUPPLEMENTS_FETCHED","assay_adjudication_pending",dict(failures=sum(x["status"]=="FAILED" for x in records))),flush=True)
