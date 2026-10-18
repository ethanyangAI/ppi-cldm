import requests,shutil,zipfile,subprocess
from pathlib import Path
from ppiblocker.common import Run,atomic_json,record_file,require
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"44_supplement_retry",[])
shutil.copy2(__file__,run.path/"qc/driver.py");records=[]
for pmc in ["PMC10468394","PMC12507698"]:
 url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles"
 p=run.path/"work"/(pmc+".zip")
 try:
  with requests.get(url,stream=True,timeout=(30,120)) as r:
   r.raise_for_status()
   with p.open("wb") as f:
    for b in r.iter_content(1024*1024):f.write(b)
  assert zipfile.is_zipfile(p)
  records.append(dict(url=url,artifact=record_file(p),status="FETCHED"))
  with zipfile.ZipFile(p) as z:
   for n in z.namelist():
    name=Path(n).name
    if not name.endswith((".pdf",".csv",".xlsx")):continue
    out=run.path/"outputs"/name;require(not out.exists(),"DUPLICATE_NAME",name)
    out.write_bytes(z.read(n));run.output(name,out)
    if out.suffix==".pdf":
     code="from pypdf import PdfReader;import sys;from pathlib import Path;p=Path(sys.argv[1]);p.with_suffix('.txt').write_text('\\n'.join(f'PAGE {i+1}\\n'+(x.extract_text() or '') for i,x in enumerate(PdfReader(p).pages)))"
     proc=subprocess.run([root/"env/metrics/bin/python","-c",code,str(out)],capture_output=True,text=True)
     print("PDF",name,proc.returncode,proc.stderr[-500:],flush=True)
    print("FILE",name,out.stat().st_size,flush=True)
 except Exception as e:
  records.append(dict(url=url,status="FAILED",error=str(e)));print("ERROR",pmc,str(e),flush=True)
atomic_json(run.path/"outputs/receipts.json",records);run.output("receipts",run.path/"outputs/receipts.json")
print(run.finish("SUPPLEMENT_RETRIEVAL_COMPLETE","primary_source",dict(failed=sum(r["status"]=="FAILED" for r in records))),flush=True)
