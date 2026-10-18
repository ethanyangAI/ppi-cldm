import os,sys,shutil,hashlib,requests,base64
from pathlib import Path
from ppiblocker.common import *
from ppiblocker.structure import read_structure
root=Path("/lustre/users/u21111210118/projects/test9");src=root/"source/benchmarks/af2_review_20260923";run=Run(root,"73_af2_review_setup",[record_file(src/"protocol.json")])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 cm=root/"steps/60_af2_control_inputs/runs/20260922T111813Z_0f6bf85d0301/manifest.json";c=read_json(cm)
 controls=read_json(verify_file(c["outputs"]["plan"]))["entries"];cinputs=read_json(verify_file(c["outputs"]["inputs"]))
 targets=sorted({x["target"] for x in controls});selected=[]
 for t in targets:
  for positive in (False,True):
   subset=[x for x in controls if x["target"]==t and (str(x["label"]).lower() in ("true","1"))==positive]
   require(subset,"EMPTY_CONTROL_STRATUM",str((t,positive)))
   x=dict(min(subset,key=lambda x:hashlib.sha256(("af2-v2-control:"+x["id"]).encode()).hexdigest()))
   x.update(role="control",positive=positive);selected.append(x)
 require(len(selected)==10,"CONTROL_COUNT",str(len(selected)))
 candidates=[]
 for p in (root/"steps/43_development_refold/runs").glob("*/manifest.json"):
  m=read_json(p);em=read_json(verify_file(m["outputs"]["evaluation_manifest"]));dm=read_json(verify_file(em["inputs"][0])) if False else None
  accepted=[x for x in read_json(verify_file(em["outputs"]["evaluation"]))["candidates"] if x["status"]=="COMPUTATIONAL_COMPETITION_CANDIDATE"]
  if not accepted:continue
  gm=read_json(verify_file(m["inputs"][0]));design=verify_file(gm["design_manifest"]);dm=read_json(design)
  pool=read_json(verify_file(dm["outputs"]["candidates"]));native=dm["outputs"]["native"];target=read_structure(verify_file(native))[0][0]["sequence"]
  for x in accepted:
   d=next(v for v in pool if v["id"]==x["id"])
   candidates.append(dict(id=f'dev_{m["cell_index"]:02d}_{x["id"]}',source_id=x["id"],group="P09",target="KEAP1",role="candidate",sequence=x["sequence"],target_sequence=target,native=native,backbone=d["backbone"],reference_role="native_partner",design_manifest=record_file(design)))
 require(len(candidates)==3,"CANDIDATE_COUNT",str(len(candidates)))
 cp=run.path/"outputs/candidates_plan.json";atomic_json(cp,dict(entries=candidates))
 msa_up=root/"steps/24_target_msa/runs/20260922T053230Z_5f5d81e4f519/manifest.json"
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",JAX_PLATFORMS="cpu",CUDA_VISIBLE_DEVICES="",OPENBLAS_NUM_THREADS="1");env.pop("PYTHONPATH",None)
 checked_command([root/"env/colabfold/bin/python",root/"source/benchmarks/runtime_pilot_20260922/serialize_msa_parallel.py",cp,verify_file(read_json(msa_up)["outputs"]["receipt"]),run.path/"outputs/msa_queries"],run.path/"work",run.path/"logs/msa.log",env,timeout=1200)
 inputs=read_json(run.path/"outputs/msa_queries/inputs.json")
 old={}
 for step in ("61_af2_calibration","68_development_af2"):
  for p in (root/"steps"/step/"runs").glob("*/manifest.json"):
   m=read_json(p)
   if m["status"]!="AF2_VERIFICATION_COMPLETE":continue
   for row in read_json(verify_file(m["outputs"]["results"])):
    require(row["id"] not in old,"DUPLICATE_BASELINE",row["id"]);old[row["id"]]=row
 entries=sorted(candidates,key=lambda x:x["id"])+selected
 for i,e in enumerate(entries):
  e["slot"]=i;e["baseline_models"]=old.get(e["id"],{}).get("models",[])
  if e["role"]=="control":
   path=verify_file(cinputs[e["id"]]);dest=run.path/"outputs/msa_queries"/(e["id"]+".a3m");shutil.copy2(path,dest);inputs[e["id"]]=record_file(dest)
  e["msa"]=inputs[e["id"]]
 atomic_json(run.path/"outputs/plan.json",dict(entries=entries,protocol=record_file(src/"protocol.json"),source_manifests=[record_file(cm),record_file(msa_up)]))
 run.output("plan",run.path/"outputs/plan.json")
 # Pin official ipSAE implementation and license through the GitHub API.
 api="https://api.github.com/repos/DunbrackLab/IPSAE"
 response=requests.get(api+"/commits/main",timeout=60);response.raise_for_status();revision=response.json()["sha"]
 dest=root/"vendor"/("IPSAE_"+revision[:12]);dest.mkdir(exist_ok=True)
 files={}
 for name in ("ipsae.py","README.md","LICENSE"):
  response=requests.get(api+"/contents/"+name,params={"ref":revision},timeout=60);response.raise_for_status()
  p=dest/name;p.write_bytes(base64.b64decode(response.json()["content"]));files[name]=record_file(p)
 atomic_json(run.path/"outputs/ipsae_source.json",dict(repository=api,revision=revision,files=files));run.output("ipsae_source",run.path/"outputs/ipsae_source.json")
 print(run.finish("AF2_REVIEW_INPUTS_READY","protocol_frozen",dict(entries=13,candidates=3,controls=10)),flush=True)
except Exception as e:run.fail(e);raise

