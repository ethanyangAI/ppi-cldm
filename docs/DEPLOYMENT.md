# Deployment and recovery record — 2026-09-20

The tested installation is the project-local Fudan installation described in WORKFLOW.md. Do not rerun bootstrap or recovery scripts over these working environments. The supported execution entry is scripts/submit_stage.sh; model computations require a Slurm allocation.

## Pinned components

The public baseline is e2984a94674ffcb75b280680038df5e9f39d684d. environment/vendor-lock.json pins RFdiffusion, ProteinMPNN and dllogger archives. The installed core/rfd/boltz Python versions and package snapshots are under environment/. Conda explicit files contain Linux package URLs; pip lock files are version snapshots, not a complete wheel-hash lock. Local RFdiffusion, SE3Transformer and dllogger installations are supplied by pinned vendor trees and are intentionally excluded from portable pip lists.

For a fresh Linux installation, create separate prefixes from each conda-explicit file, then reconcile the pip snapshot without replacing Conda-owned binary packages. CUDA wheels need the matching official PyTorch index (cu117 for RFdiffusion; cu118 for Boltz), and DGL needs its official cu117 wheel source. Install pinned vendor components in the RF environment, and install this source package in the core environment. Run pip check in all environments and the scientific-contract tests before inference. A clean-machine restore has not been tested; these snapshots document the tested installation rather than claiming a portable one-command installer.

Boltz requires RDKit 2024.09.6 from conda-forge on this glibc 2.17 host to read the official molecule serialization. Do not restore the older PyPI RDKit/Pillow pins in historical install_boltz.sh. The recovery script upgrade_rdkit.sh and logs preserve how the compatibility issue was resolved. Final runtime is Torch 2.5.1+cu118, NumPy 1.26.4, RDKit 2024.09.6, Boltz 2.2.1. RFdiffusion uses Torch 1.13.1+cu117, DGL 1.1.3+cu117 and e3nn 0.3.3.

Weights are external assets, not Git objects. Keep all assets/*.receipt.json records with the assets. Boltz checkpoints and molecule library were fetched from the official repository at commit 6fdef46d763fee7fbb83ca5501ccceff43b85607 and checked against SHA-256. RFdiffusion Complex_base_ckpt.pt is similarly verified. ProteinMPNN weights are inside the pinned vendor archive. No user-site dependencies are permitted: PYTHONNOUSERSITE=1 and no PYTHONPATH. The RF backend supplies its project-local CUDA library directories.

stage_job.sh raises the job's inherited virtual-address soft limit to the memory explicitly allocated by Slurm. This resolved an inherited 6 GiB limit that otherwise prevented loading Boltz weights despite a 48 GiB allocation. V100 inference was tested with Boltz --no_kernels. Failed installation/prediction attempts remain in their original run directories; they are not accepted inputs.

## Acceptance

scripts/final_acceptance.py checks the explicit accepted run manifests and every inventoried artifact, requires all four candidates and all twelve refolds to be present, and reruns the scientific-contract tests. It is specific to the engineering benchmark and is not a generic performance claim. scripts/benchmark_accuracy.py compares the sequence-only prediction with the known 1YCR complex. See the project acceptance report for results and remaining scientific limitations.

No GitHub push is part of this recovery. The remote branch rebuild/structure-first is the implementation authority; the public upstream remains unchanged.

## Runtime lock contract added after independent audit

Historical freeze files are documentation, not the runtime gate. Every prepare/predict/design/evaluate/reevaluate invocation now captures the actual core environment; model stages additionally capture the backend Python environment. The actual Python executable, installed package names/versions, selected model-distribution files, RFdiffusion/ProteinMPNN/dllogger trees including non-Python configuration, model checkpoints and Boltz molecule tree are compared against reviewed runtime locks. Captured state and the matching baseline are copied into each new run. Drift fails closed before the backend is invoked.

The initial baseline was registered explicitly by scripts/register_runtime_locks.py --root PROJECT_ROOT --initialize-reviewed after checking the official mols.tar hash and comparing each extracted file with its archive member. This command refuses existing locks and is never called automatically by model stages. A partial write requires manual review and recovery; do not delete locks to silence drift. The locks intentionally refer to this host's installation. A fresh environment needs a separately reviewed baseline.

Coverage is not a byte-level proof of every installed dependency: non-model dependencies are primarily tracked by installed versions, OS/driver/shared libraries outside the selected trees are not exhaustively hashed, and registration does not establish official provenance for every installed dependency. Python source provenance of ppiblocker is recorded separately in each run. Historic inference cannot be retroactively upgraded by a new CPU reanalysis.

load_run now checks direct inputs and recorded runtime receipts as well as outputs/file_inventory. For v2 runtime records this validates immutable snapshot/lock files; the live environment is checked at the next actual invocation. Original caller MSA files may change after preparation without affecting the retained run snapshot.
