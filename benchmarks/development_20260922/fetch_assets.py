import requests,hashlib,shutil,concurrent.futures
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
up=root/"steps/31_calibration_sources/runs/20260922T095613Z_38be86bf866a/manifest.json"
run=Run(root,"34_calibration_assets",[record_file(up)])
shutil.copy2(__file__,run.path/"qc/driver.py")
m=read_json(up);sources=[]
for key,chosen in [("meta_dataset",["input_pdbs.tar.zst"]),("bindcraft_models",["DesignModels.zip"])]:
 for f in read_json(verify_file(m["outputs"][key]))["files"]:
  if f["key"] in chosen:sources.append(dict(id=f["key"],url=f["links"]["self"],checksum=f["checksum"]))
revision=read_json(verify_file(m["outputs"]["scoring_tree"]))["sha"]
for path in ["README.md","analysis/README.md","analysis/data/bindcraft_predicted_and_experimental_data.csv","analysis/data/boltzgen_predicted_and_experimental_data.csv"]:
 sources.append(dict(id="scoring_"+path.replace("/","_"),url=f"https://raw.githubusercontent.com/DigBioLab/de_novo_binder_scoring/{revision}/{path}"))
for name,url in [
 ("bindcraft.xml","https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12507698/fullTextXML"),
 ("rfd.xml","https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10468394/fullTextXML"),
 ("bindcraft_install.sh","https://raw.githubusercontent.com/martinpacesa/BindCraft/7713aa0d0d351e4117a8befeb8541f3a8ebd3368/install_bindcraft.sh"),
 ("foundry_pyproject.toml","https://raw.githubusercontent.com/RosettaCommons/foundry/b02eed6a6bdf8f44d14a80cc36e3da13c9f2291c/pyproject.toml"),
 ("rfd3_readme.md","https://raw.githubusercontent.com/RosettaCommons/foundry/b02eed6a6bdf8f44d14a80cc36e3da13c9f2291c/models/rfd3/README.md"),
 ("rfd3_tutorial.md","https://raw.githubusercontent.com/RosettaCommons/foundry/b02eed6a6bdf8f44d14a80cc36e3da13c9f2291c/models/rfd3/docs/tutorials/RFdiffusion3_installation_tutorial.md")]:
 sources.append(dict(id=name,url=url))
def fetch(s):
 p=run.path/"outputs"/s["id"];h=hashlib.md5()
 try:
  with requests.get(s["url"],stream=True,timeout=(20,120)) as r:
   r.raise_for_status()
   with p.open("wb") as out:
    for b in r.iter_content(1024*1024):out.write(b);h.update(b)
  if s.get("checksum"):assert "md5:"+h.hexdigest()==s["checksum"]
  return dict(**s,status="VERIFIED",artifact=record_file(p))
 except Exception as e:return dict(**s,status="FAILED",error=str(e))
records=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,sources))
for r in records:
 if r["status"]=="VERIFIED":run.output(r["id"],r["artifact"]["path"])
atomic_json(run.path/"outputs/receipts.json",records);run.output("receipts",run.path/"outputs/receipts.json")
print(run.finish("CALIBRATION_ASSETS_FETCHED","published_data",dict(failed=sum(r["status"]=="FAILED" for r in records))),flush=True)

