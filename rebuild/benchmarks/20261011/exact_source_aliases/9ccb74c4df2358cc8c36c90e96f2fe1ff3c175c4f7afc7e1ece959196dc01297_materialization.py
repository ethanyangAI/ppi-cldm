import os,sys,json,hashlib,pickle,traceback,subprocess,re,time
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
O=R/"steps/24_benchmark_delivery/runs"/("rfd_cache_materialization_"+os.environ["SLURM_JOB_ID"]);O.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(R/"source/src"))
from ppiblocker.common import record_file,collect_runtime,atomic_json
def need(v,m):
 if not v:raise ValueError(m)
def vr(r):
 p=Path(r["path"]);need(p.is_absolute()and p.resolve()==p and p.is_file(),"badexactpath");need(record_file(p)==r,"receiptbyteschanged");return p
def save(n,o):
 p=O/n;atomic_json(p,o);p.chmod(0o444);return record_file(p)
v={"schema":"rfd-cache-materialization.v1","status":"RUNNING","default_lock_updated":False,"model_inference_performed":False,"GPU_allocated":0,"fixed_numeric_equivalence":{"rtol":1e-8,"atol":1e-8},"job_id":os.environ["SLURM_JOB_ID"]}
try:
 need(os.environ.get("CUDA_VISIBLE_DEVICES")=="" and not os.environ.get("SLURM_JOB_GPUS"),"GPUforbidden")
 raw=subprocess.check_output(["scontrol","show","job",os.environ["SLURM_JOB_ID"],"-o"],text=True)
 need("JobState=RUNNING"in raw and re.search(r"(?:TRES|AllocTRES)=cpu=1(?:,| )",raw),"actualCPU1required")
 need("gres/gpu"not in raw,"GPUallocationforbidden");v["actual_live_CPU_record"]=raw
 diag={"path":str(R/"steps/24_benchmark_delivery/runs/runtime_drift_diagnostic_13275/diagnostic.json"),"bytes":32980,"sha256":"fec7f6a05123d3702a9ad2f034bc25f33cab2810051a146ef7a997d507be2f88"}
 add={"path":str(R/"steps/24_benchmark_delivery/runs/rfd_igso3_cache_diagnostic_13278/diagnostic.json"),"bytes":3250,"sha256":"934e984e3c44bcf734ab212207a24d5ef9c1301f5cb6efe7a4755de4b05450db"}
 d=json.loads(vr(diag).read_text());a=json.loads(vr(add).read_text())
 need(d["runtime_mismatch_components"]==["rfd"]and a["all_preexisting_RFdiffusion_vendor_bytes_unchanged"]is True,"diagnosticcauseidentity")
 for k,c in d["components"].items():
  for key in ("expected","historical","actual_snapshot","expected_snapshot","historical_snapshot"):vr(c[key])
  if k!="rfd":need(c["live_matches_expected"]is True and not c["historical_vs_current_expected"],"unrelatedruntimedrift")
 old=vr(a["current_lock"]);old_r=record_file(old)
 cache=vr(a["exact_single_additional_file"]);generator=vr(a["cache_generation_source"])
 actual=collect_runtime(R,"rfd")
 need(actual==json.loads(vr(a["captured_runtime"]).read_text()),"capturedRFDchanged")
 import numpy as np,torch
 torch.set_num_threads(1)
 need(not torch.cuda.is_available()and not torch.cuda.is_initialized(),"CUDAnotusable")
 from rfdiffusion.diffusion import IGSO3
 from rfdiffusion import igso3
 source_records=[record_file(Path(__file__)),record_file(generator),record_file(Path(igso3.__file__)),record_file(R/"vendor/RFdiffusion/config/inference/base.yaml"),record_file(R/"source/src/ppiblocker/common.py")]
 spec={"T":50,"min_sigma":0.02,"max_sigma":1.5,"min_b":1.5,"max_b":2.5,"num_omega":1000,"schedule":"linear","L":2000,"cache_dir":str(O/"independent_regenerated_schedule")}
 started=time.monotonic()
 generated=IGSO3(**spec)
 with cache.open("rb")as f:historical=pickle.load(f)
 keys={"cdf","score_norm","exp_score_norms","discrete_omega","discrete_sigma"}
 need(set(historical)==set(generated.igso3_vals)==keys,"allfixedcachearraysrequired")
 rows=[]
 for k in sorted(keys):
  x=np.asarray(historical[k]);y=np.asarray(generated.igso3_vals[k])
  need(x.shape==y.shape and x.dtype==y.dtype and np.isfinite(x).all()and np.isfinite(y).all(),"cachearrayshape/dtype/nonfinite")
  delta=np.abs(x-y)
  ok=bool(np.allclose(x,y,rtol=1e-8,atol=1e-8,equal_nan=False))
  rows.append({"key":k,"shape":list(x.shape),"dtype":str(x.dtype),"exact_array_equal":bool(np.array_equal(x,y)),"max_absolute_difference":float(delta.max())if delta.size else 0.0,"fixed_numeric_equivalent":ok})
  need(ok,"officialregeneratedcachediffers:"+k)
 generated_file=O/"independent_regenerated_schedule"/cache.name
 need(generated_file.is_file(),"exactexpectedcachefilemissing")
 generated_r=record_file(generated_file);generated_file.chmod(0o444)
 need(not torch.cuda.is_initialized(),"CUDAcontextinitialized")
 need(record_file(old)==old_r and record_file(cache)==a["exact_single_additional_file"],"defaultlock/cachechanged")
 need(collect_runtime(R,"rfd")==actual,"RFDlivechangedduringregen")
 materialized=save("runtime-lock-rfd-materialized.json",actual)
 v.update(status="RFD_MATERIALIZED_IGSO3_RUNTIME_CPU_QUALIFIED_DEFAULT_LOCK_UNCHANGED",original_default_lock=old_r,materialized_runtime_lock=materialized,cause_diagnostic=diag,single_cache_diagnostic=add,original_cache=a["exact_single_additional_file"],regenerated_cache=generated_r,regenerated_pickle_byte_identical=generated_r["sha256"]==a["exact_single_additional_file"]["sha256"],official_constructor_arguments=spec,actual_num_sigma=generated.num_sigma,actual_max_sigma=float(generated.max_sigma),array_crosschecks=rows,source_records=source_records,regeneration_CPU_seconds_wall=time.monotonic()-started,baseline_vendor225_bytes_unchanged=True,all_other_RFD_runtime_fields_unchanged=True,core_and_boltz_captured_match_historical=True,old_pre_materialization_lock_preserved=True,application_to_staged_runtime_requires_independent_review=True,application_to_default_runtime_performed=False,scientific_generation_or_selection_settings_changed=False,experimental_binding_or_blockade=False)
except Exception as e:
 v.update(status="RFD_CACHE_MATERIALIZATION_TYPED_INCOMPLETE_DEFAULT_UNCHANGED",error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save("typed_incomplete.json",v);raise
rr=save("acceptance.json",v);print(json.dumps(rr),flush=True)
