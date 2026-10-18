import os,sys,shutil,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
from screening_transfer import rec,read,dump,verify
import benchmark_common_review as original
original.cpu()
jid=os.environ["SLURM_JOB_ID"]
snap=R/"steps/23_common_review/bbf_diagnostics/frozen"/("bbf_common_"+jid);snap.mkdir(parents=True,exist_ok=False)
common_src=R/"steps/23_common_review/frozen/native_common_13051/code"
code=snap/"code";shutil.copytree(common_src,code,ignore=shutil.ignore_patterns("__pycache__"))
own=code/"bbf_input_diagnostic.py";shutil.copyfile(R/"source/rebuild/bbf_input_diagnostic.py",own)
source=own.read_text().replace('ROOT/"source/rebuild/benchmark_common_review.py"','Path(__file__).resolve().parent/"benchmark_common_review.py"').replace('ROOT/"vendor"/("IPSAE_"+REVISION[:12])/"ipsae.py"','Path(__file__).resolve().parent/"vendor/ipsae.py"')
own.write_text(source)
backend=R/"steps/21_method_runtime/frozen/bbf_backend_v2/bbf_feature_backend.py";verify(dict(path=str(backend),bytes=15084,sha256="ea568fb4fa1905d54c304a60d7f6b78af4a01a80941d5cf0c0152c1254d361b3"))
# Retain accepted immutable backend at its original immutable path to keep feature-source provenance exact.
env=R/"steps/21_method_runtime/frozen/bbf_backend_v2/bindcraft_env.sh";verify(dict(path=str(env),sha256="1ae3baafe2cac87dc60b7ad7f32075ec11deab07b5d2d4eadfe3241535332245",bytes=env.stat().st_size))
for name in list(sys.modules):
    if name in ["benchmark_common_review","screening_transfer","control_msa_check","bbf_input_diagnostic"] or name=="ppiblocker" or name.startswith("ppiblocker."):del sys.modules[name]
sys.path.insert(0,str(code))
import bbf_input_diagnostic as frozen
frozen.cpu();tests=frozen.run_tests()
prior=R/"steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json"
old=read(prior);plan=snap/"plan.json"
frozen.prepare(R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/prepared_inputs.json",plan)
new=read(plan)
if new["jobs"]!=old["jobs"] or new["controls"]!=old["controls"] or new["settings"]!=old["settings"]:raise ValueError("BBF source freeze changed scientific inputs")
fm=R/"steps/21_method_runtime/runs/bbf_features_13057/outputs/feature_manifest.json";features=read(fm)
if features["plan"]!=rec(prior):raise ValueError("Original feature input plan receipt mismatch")
features["original_feature_manifest"]=rec(fm);features["original_capture_plan"]=features["plan"];features["plan"]=rec(plan);features["cpu_rebase_job"]=jid;features["scientific_jobs_exactly_unchanged"]=True
rebased=snap/"feature_manifest.json";dump(rebased,features)
frozen.validate_features(plan,rebased,snap/"feature_acceptance.json")
files=[rec(v) for v in sorted(code.rglob("*")) if v.is_file() and "__pycache__" not in v.parts]
for f in files:
    p=Path(f["path"]);p.chmod(0o555 if p.name in ["boltz","colabfold_batch"] else 0o444)
for p in [plan,rebased,snap/"feature_acceptance.json"]:p.chmod(0o444)
bundle=dict(status="BBF110_SCIENTIFIC_INPUTS_AND_SOURCE_CONTENT_ACCEPTED_AWAIT_NEW_BUDGET_GUARD_LAUNCHER",cpu_job=jid,plan=rec(plan),source=rec(own),source_files=files,common_source=rec(code/"benchmark_common_review.py"),backend=rec(backend),backend_env=rec(env),original_feature_capture=rec(fm),feature_manifest=rec(rebased),feature_acceptance=rec(snap/"feature_acceptance.json"),original_plan=rec(prior),scientific_jobs_exactly_unchanged=True,tests=tests,expected_models=110,expected_jobs=22,scope="DEVELOPMENT_ONLY_NO_GPU_SUBMITTED",budget_guard=None,hardware_inventory=original.HARDWARE_INVENTORY)
dump(snap/"source_bundle.json",bundle);(snap/"source_bundle.json").chmod(0o444)
print(json.dumps(dict(status=bundle["status"],bundle=rec(snap/"source_bundle.json"),source=bundle["source"],plan=bundle["plan"],feature_acceptance=bundle["feature_acceptance"]),indent=2),flush=True)

