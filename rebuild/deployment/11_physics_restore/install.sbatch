#!/bin/bash
#SBATCH -J t9-physics-restore
#SBATCH -p interactive
#SBATCH -c 2
#SBATCH --mem=12G
#SBATCH -t 02:00:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/11_physics_restore/logs/install_%j.log
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
unset PYTHONPATH
export CONDA_PKGS_DIRS=/lustre/users/u21111210118/projects/test9/env/pkgs PIP_CACHE_DIR=/lustre/users/u21111210118/projects/test9/env/cache/pip TMPDIR=/lustre/users/u21111210118/projects/test9/steps/11_physics_restore/work
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/core
python steps/11_physics_restore/code/fetch_pyrosetta.py
conda create -y --override-channels -c conda-forge -p /lustre/users/u21111210118/projects/test9/env/physics python=3.10 numpy=1.24.3 scipy=1.12 openmm=8.1.1 pdbfixer=1.9 pip
conda activate /lustre/users/u21111210118/projects/test9/env/physics
python -m pip install assets/pyrosetta/pyrosetta-2026.29+releasequarterly.80a0635615-cp310-cp310-linux_x86_64.whl
python -m pip check
python -c 'import pyrosetta,openmm,pdbfixer; pyrosetta.init("-mute all"); print("PHYSICS_IMPORTS_OK",pyrosetta.version(),openmm.__version__)'
python -m pip freeze > env/physics-freeze.txt
conda list --explicit > env/physics-explicit.txt
