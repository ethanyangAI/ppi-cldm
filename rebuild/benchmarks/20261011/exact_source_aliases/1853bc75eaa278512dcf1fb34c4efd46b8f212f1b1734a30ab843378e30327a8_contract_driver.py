#!/usr/bin/env python3
import ast,difflib,hashlib,json,os,shutil,subprocess,sys,faulthandler
faulthandler.enable(all_threads=True)
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
D=S/f"runs/observation_v8_contracts_{os.environ['SLURM_JOB_ID']}";O=D/"outputs";F=D/"source";O.mkdir(parents=True);F.mkdir()
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,obj):p.write_text(json.dumps(obj,indent=2)+"\n")
raw=subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)
assert "gres/gpu=" not in raw,raw
for src,name in [(S/"code/benchmark_runtime_v8.py","benchmark_runtime.py"),(S/"code/test_runtime_v8_contracts.py","test_runtime_contracts.py"),(Path(__file__),"contract_driver.py")]:
 shutil.copyfile(src,F/name);(F/name).chmod(0o444)
previous=R/"steps/22_matched_benchmark/settings/pilot_v7/source/benchmark_runtime.py"
old=ast.parse(previous.read_text());new=ast.parse((F/"benchmark_runtime.py").read_text())
oldfunc={n.name:ast.dump(n,include_attributes=False) for n in old.body if isinstance(n,ast.FunctionDef)}
newfunc={n.name:ast.dump(n,include_attributes=False) for n in new.body if isinstance(n,ast.FunctionDef)}
changed=[k for k in oldfunc if oldfunc[k]!=newfunc[k]]
added=[k for k in newfunc if k not in oldfunc]
assert set(changed)=={"native_af2_batch","bindcraft_one_attempt","method_attempt","resident_native_af2","method_session"},changed
assert set(added)=={"durable_json","save_native_confidence","observed_native_predict_call"},added
diff=O/"observation_only_source.diff";diff.write_text("".join(difflib.unified_diff(previous.read_text().splitlines(True),(F/"benchmark_runtime.py").read_text().splitlines(True),fromfile=str(previous),tofile=str(F/"benchmark_runtime.py"))))
unitsources=[R/"vendor/ColabDesign/colabdesign/af/model.py",R/"vendor/ColabDesign/colabdesign/af/loss.py",R/"vendor/ColabDesign/colabdesign/af/utils.py",R/"vendor/BindCraft/functions/colabdesign_utils.py"]
os.environ["RUNTIME_SOURCE"]=str(F/"benchmark_runtime.py")
import importlib.util,unittest
# Load C extension dependencies before sys.modules mock fixtures can discard imports.
sys.path.insert(0,str(R/"vendor/BindCraft"))
import jax,colabdesign,functions
from colabdesign.shared.utils import Key
Key(seed=20901).get()
spec=importlib.util.spec_from_file_location("contracts",F/"test_runtime_contracts.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
accept={"schema":"observation_runtime_cpu_acceptance.v1","status":"OBSERVATION_ONLY_NATIVE_AF2_V8_CPU_CONTRACTS_PASS" if result.wasSuccessful() else "ENGINEERING_CONTRACT_FAILURE",
 "cpu_only":True,"model_inference_performed":False,"slurm_job_id":os.environ["SLURM_JOB_ID"],"scheduler_record":raw,
 "runtime_source":rec(F/"benchmark_runtime.py"),"previous_immutable_source":rec(previous),"contracts_source":rec(F/"test_runtime_contracts.py"),
 "driver_source":rec(F/"contract_driver.py"),"official_output_unit_and_serializer_sources":[rec(p) for p in unitsources],
 "source_change_review":{"changed_existing_functions":changed,"added_observation_helpers":added,"diff":rec(diff),
 "unchanged_existing_functions":sorted(set(oldfunc)-set(changed)),"capture_scope":"RF native validation and BC native complex PTM predict only; no design optimization observer"},
 "preloaded_official_modules_before_sysmodules_mocks":{"jax":jax.__file__,"colabdesign":colabdesign.__file__,"functions":functions.__file__},
 "test_fixture_failure_history":[13148,13150,13152],"test_fixture_repair":"Preload JAX/ml_dtypes and official package before patch.dict(sys.modules); avoid C extension re-import after mock teardown",
 "tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),
 "contract_scope":"synthetic arrays exercise actual official getters/save_pdb/native BindCraft early rejection; no synthetic evidence enters benchmark scientific outputs"}
write(O/"acceptance.json",accept)
for parent in [F,O]:
 for p in parent.iterdir():
  if p.is_file():p.chmod(0o444)
 parent.chmod(0o555)
print(json.dumps(accept,indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)

