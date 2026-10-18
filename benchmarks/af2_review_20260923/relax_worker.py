import os,sys,json
os.environ.update(CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",OPENMM_CPU_THREADS="2",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="2")
from pathlib import Path
from alphafold.common import protein
from alphafold.relax import relax
from absl import logging
logging.set_verbosity(logging.INFO)
import openmm
print("OPENMM_PLATFORMS", [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())], openmm.Platform.getPluginLoadFailures(), flush=True)
from alphafold.relax import amber_minimize
from openmm import unit
original_minimize=amber_minimize._openmm_minimize
def compatible_minimize(*args,**kwargs):
    tolerance=kwargs["tolerance"]
    if tolerance.unit.is_compatible(unit.kilojoule_per_mole):
        # OpenMM 8 requires force units; preserve the legacy numeric kJ/mol tolerance.
        kwargs["tolerance"]=tolerance/unit.nanometer
    return original_minimize(*args,**kwargs)
amber_minimize._openmm_minimize=compatible_minimize
assert abs((2.39*unit.kilocalorie_per_mole/unit.nanometer).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)-9.99976)<1e-6
print("OPENMM8_TOLERANCE_COMPATIBILITY: 9.99976 kJ/mol/nm",flush=True)

p,out,receipt=map(Path,sys.argv[1:4])
obj=protein.from_pdb_string(p.read_text())
worker=relax.AmberRelaxation(max_iterations=2000,tolerance=2.39,stiffness=10.0,exclude_residues=[],max_outer_iterations=3,use_gpu=False)
result,debug,violations=worker.process(prot=obj)
out.write_text(result)
receipt.write_text(json.dumps(dict(openmm_version=openmm.__version__,tolerance_kJ_mol_nm=9.99976,compatibility="legacy AF2 numeric tolerance converted to OpenMM8 force units",debug={k:float(v) for k,v in debug.items()},residue_violations=list(map(float,violations))),indent=2))
print("RELAXATION_COMPLETE",flush=True)

