import requests,base64,shutil,concurrent.futures
from pathlib import Path
from ppiblocker.common import Run,record_file,read_json,verify_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
up=root/"steps/31_calibration_sources/runs/20260922T095613Z_38be86bf866a/manifest.json"
run=Run(root,"39_method_sources",[record_file(up)])
shutil.copy2(__file__,run.path/"qc/driver.py")
m=read_json(up)
jobs=[]
for key,repo,paths in [
 ("bindcraft_tree","martinpacesa/BindCraft",["install_bindcraft.sh","functions/generic_utils.py","functions/colabdesign_utils.py","bindcraft.py","settings_advanced/default_4stage_multimer.json"]),
 ("rfd3_tree","RosettaCommons/foundry",["pyproject.toml","models/rfd3/README.md","models/rfd3/docs/tutorials/RFdiffusion3_installation_tutorial.md","models/rfd3/docs/examples/protein_binder_design.json","models/rfd3/configs/inference_engine/rfdiffusion3.yaml","src/foundry_cli/download_checkpoints.py"]),
 ("scoring_tree","DigBioLab/de_novo_binder_scoring",["README.md","analysis/README.md","analysis/data/bindcraft_predicted_and_experimental_data.csv","analysis/data/boltzgen_predicted_and_experimental_data.csv"])]:
 tree=read_json(verify_file(m["outputs"][key]))
 for path in paths:
  hit=next((x for x in tree["tree"] if x["path"]==path),None)
  if hit:jobs.append(dict(repo=repo,path=path,url=hit["url"],git_blob_sha=hit["sha"],commit=tree["sha"]))
def fetch(j):
 try:
  r=requests.get(j["url"],timeout=45);r.raise_for_status();obj=r.json();assert obj["encoding"]=="base64"
  b=base64.b64decode(obj["content"])
  p=run.path/"outputs"/j["repo"].replace("/","_")/j["path"];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  return dict(**j,status="FETCHED",artifact=record_file(p))
 except Exception as e:return dict(**j,status="FAILED",error=str(e))
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,jobs))
for i,r in enumerate(rows):
 if r["status"]=="FETCHED":run.output(str(i),r["artifact"]["path"])
atomic_json(run.path/"outputs/receipts.json",rows);run.output("receipts",run.path/"outputs/receipts.json")
print(run.finish("PINNED_METHOD_SOURCES_FETCHED","source_inspection",dict(failed=sum(r["status"]=="FAILED" for r in rows))),flush=True)

