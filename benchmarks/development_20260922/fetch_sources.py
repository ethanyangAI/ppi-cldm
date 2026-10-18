import requests,shutil,hashlib,concurrent.futures
from pathlib import Path
from ppiblocker.common import Run,atomic_json,record_file
root=Path("/lustre/users/u21111210118/projects/test9")
run=Run(root,"31_calibration_sources",[record_file(root/"source/benchmarks/development_20260922/protocol.json")])
shutil.copy2(__file__,run.path/"qc/driver.py")
sources={
 "meta_dataset":"https://zenodo.org/api/records/15722219",
 "bindcraft_models":"https://zenodo.org/api/records/14249738",
 "bindcraft_tree":"https://api.github.com/repos/martinpacesa/BindCraft/git/trees/main?recursive=1",
 "scoring_tree":"https://api.github.com/repos/DigBioLab/de_novo_binder_scoring/git/trees/main?recursive=1",
 "bindcraft_paper":"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41586-025-09429-6&format=json",
 "keap_paper":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12158508/fullTextXML",
 "rfd_figshare":"https://api.figshare.com/v2/articles?resource_doi=10.1038/s41586-023-06415-8",
 "rfd3_tree":"https://api.github.com/repos/RosettaCommons/foundry/git/trees/production?recursive=1"
}
def fetch(item):
 name,url=item;p=run.path/"outputs"/(name+".txt")
 try:
  r=requests.get(url,timeout=90);r.raise_for_status();p.write_bytes(r.content)
  return dict(id=name,url=url,final_url=r.url,status="FETCHED",artifact=record_file(p))
 except Exception as e:return dict(id=name,url=url,status="FAILED",error=str(e))
records=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,sources.items()))
for r in records:
 if r["status"]=="FETCHED":run.output(r["id"],r["artifact"]["path"])
atomic_json(run.path/"outputs/sources.json",records);run.output("sources",run.path/"outputs/sources.json")
# Retrieve only the compact feature table; raw model archives await inventory.
meta=next(r for r in records if r["id"]=="meta_dataset")
if meta["status"]=="FETCHED":
 m=requests.models.complexjson.loads(Path(meta["artifact"]["path"]).read_text())
 for f in m.get("files",[]):
  if f["key"]!="final_dataset.csv":continue
  url=f["links"]["self"];p=run.path/"outputs/final_dataset.csv"
  h=hashlib.md5()
  with requests.get(url,stream=True,timeout=120) as r:
   r.raise_for_status()
   with p.open("wb") as out:
    for b in r.iter_content(1024*1024):out.write(b);h.update(b)
  assert "md5:"+h.hexdigest()==f["checksum"],"Publisher checksum mismatch"
  run.output("feature_table",p)
  atomic_json(run.path/"qc/feature_download.json",dict(url=url,publisher_checksum=f["checksum"],bytes=p.stat().st_size))
print(run.finish("SOURCE_ACQUISITION_COMPLETE","published_data_not_locally_validated",dict(failed_sources=sum(r["status"]=="FAILED" for r in records))),flush=True)

