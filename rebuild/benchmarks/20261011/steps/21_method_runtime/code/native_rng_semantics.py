import ast,os,random,json,hashlib,subprocess
from pathlib import Path
import numpy as np
from colabdesign.shared.utils import Key
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
main=R/"steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py"
supp=S/"frozen/supplemental_bindcraft_13224/bindcraft_supplemental_stage_coverage.py"
key=R/"vendor/ColabDesign/colabdesign/shared/utils.py"
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def keyed(seed):
 np.random.seed(791205);random.seed(seed);return Key(seed=None).seed
a=keyed(791205);b=keyed(791205);assert a==b
different=keyed(791206);assert a!=different
source=main.read_text();fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=="bindcraft_one_attempt")
calls=[ast.unparse(n) for n in ast.walk(fn) if isinstance(n,ast.Call)]
assert "random.seed(attempt_seed)" in calls
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=="random" and n.func.attr=="seed" for n in ast.walk(ast.parse(supp.read_text())))
out=S/"runs"/("native_rng_semantics_"+os.environ["SLURM_JOB_ID"])/"outputs";out.mkdir(parents=True,exist_ok=True)
doc={"status":"FORMAL_V8_PYTHON_AND_NUMPY_SEEDING_SOURCE_AND_REAL_KEY_CPU_CONTRACT_PASS_SUPPLEMENTAL_RNG_LIMITATION_IDENTIFIED",
"formal_runtime_source":rec(main),"supplemental_source":rec(supp),"official_key_source":rec(key),"formal_actual_seed_call":"random.seed(attempt_seed)",
"real_Key_none_repeated_root_seed_fixture":{"root_python_seed":791205,"actual_key_seed_first":a,"actual_key_seed_repeat":b,"different_python_seed_key":different},
"supplemental_limitation":"Official MPnn constructor Key(seed=None) uses Python random.randint. Supplemental13224 seeded NumPy/AF2/Rosetta but did not seed Python random; actual MPNN key cannot be reconstructed from root seed. Retain literal20pool as actual fixed fixture. Technical API content coverage only.",
"formal_impact":"None: frozenv8 formal native adapter already seeds Python random and NumPy. Supplemental sequences are not formal.",
"cpu_job":os.environ["SLURM_JOB_ID"],"scheduler":subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)}
(out/"acceptance.json").write_text(json.dumps(doc,indent=2)+"\n");print(json.dumps(doc,indent=2))
