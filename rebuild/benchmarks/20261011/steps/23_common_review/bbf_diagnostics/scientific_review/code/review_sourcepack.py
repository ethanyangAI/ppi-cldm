import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/23_common_review/bbf_diagnostics/scientific_review"
def rec(p):
 p=Path(p).absolute();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def verify(r):
 if rec(r["path"])!=r:raise ValueError("Changed receipt "+r["path"])
 return Path(r["path"])
raw=subprocess.check_output(["scontrol","show","job",os.environ["SLURM_JOB_ID"],"-o"],text=True)
own=[l for l in raw.splitlines() if re.search(r"\bJobId="+os.environ["SLURM_JOB_ID"]+r"\b",l)]
assert len(own)==1 and "JobState=RUNNING" in own[0] and not re.search(r"gres/gpu=[1-9]",own[0]) and os.environ["CUDA_VISIBLE_DEVICES"]==""
out=S/("runs/review_sourcepack_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
a=json.loads((S/"runs/metric_verify_13232/acceptance.json").read_text());p=json.loads((S/"runs/partner_pose_13236/acceptance.json").read_text())
wanted=[a["source"],a["review_source"],a["review_manifest"],a["review_metrics"],a["report"],a["independent_metrics"],p["source"],p["result"],p["report"],
p["inputs"]["endpoint_protocol"],p["inputs"]["original_frozen_protocol_semantics"],rec(S/"runs/metric_verify_13232/acceptance.json"),rec(S/"runs/partner_pose_13236/acceptance.json")]
copies=[]
for r in wanted:
 f=verify(r);relative=f.relative_to(R);dest=out/"resources"/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
 assert dest.read_bytes()==f.read_bytes()
 copies.append(dict(original=r,copy=rec(dest),byte_identical=True,role="mutable draft captured explanation, not pre-native preregistration" if r==p["inputs"]["endpoint_protocol"] else "scientific review source/result or original proxy protocol"))
obj=dict(status="BBF_SCIENCE_REVIEW_DOCUMENTS_AND_SOURCE_BYTECOPIES_ACCEPTED",job_id=os.environ["SLURM_JOB_ID"],allocated_gpu_count=0,source=rec(__file__),copies=copies,
BBF_science_acceptance=rec(S/"runs/metric_verify_13232/acceptance.json"),pose_supplement_acceptance=rec(S/"runs/partner_pose_13236/acceptance.json"),
source_preserving=True,all_raw_models_packaged_here=False,raw_dependency_role="root delivery owns original native74/BBF110 raw bundle; this packet adds review sources/results and exact protocol explanatory bytes",
current_reports=[a["report"],p["report"]],formal_primary_changed=False)
(out/"manifest.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n");print(json.dumps(rec(out/"manifest.json"),indent=2))

