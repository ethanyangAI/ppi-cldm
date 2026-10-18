#!/bin/bash
#SBATCH -J t9-physics-compat
#SBATCH -p interactive
#SBATCH -c 1
#SBATCH --mem=8G
#SBATCH -t 00:30:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/11_physics_restore/logs/compat_%j.log
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
unset PYTHONPATH
export PIP_CACHE_DIR=/lustre/users/u21111210118/projects/test9/env/cache/pip TMPDIR=/lustre/users/u21111210118/projects/test9/steps/11_physics_restore/work
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/physics
python -m pip install setuptools==80.9.0
python -m pip check
python -c 'import pyrosetta,openmm,pdbfixer; pyrosetta.init("-mute all"); print("PHYSICS_IMPORTS_OK",pyrosetta.version(),openmm.__version__); print([openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])'
python -m pip freeze > env/physics-freeze.txt
conda list --explicit > env/physics-explicit.txt

