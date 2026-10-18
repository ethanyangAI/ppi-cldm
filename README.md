# Structure-first PPI blocker workflow

Project authority: `/lustre/users/u21111210118/projects/test9`, account `u21111210118`.
Submit jobs through public_cluster_2 at `192.168.81.6:22560`.
Read `../CLUSTER_BINDING.md` and `../00_admin/reconstruction_20261002.json` before execution.

This checkout reconstructs the September protein-binder workflow from GitHub commit
`e2984a94674ffcb75b280680038df5e9f39d684d`, recorded source bodies, and reviewed
text edits. It is a new checkout. Source recovery records are in
`../01_raw/history/` and `../steps/01_recovery/work/history_handoff_receipt.json`.
The legacy `core/denovo` small-molecule code is retained as historical material.

## Active workflow

Run `scripts/submit_public.sh STAGE CONFIG_OR_MANIFEST` from this checkout.
Every stage executes through Slurm and consumes an explicit input.

| Stage | Resource | Result |
| --- | --- | --- |
| prepare | CPU | Validate two proteins, species, constructs, and assembly; retrieve an accepted experimental pair if available |
| predict | One GPU | Infer native-pair poses when an accepted experimental pose is unavailable |
| design | One GPU | Generate interface-directed RFdiffusion backbones and ProteinMPNN sequences |
| evaluate | One GPU | Independently repredict the binder complex and compute separate evidence axes |
| reevaluate | CPU | Recompute metrics from verified existing model artifacts |

Each downstream stage checks its upstream manifest and file hashes. Missing assets,
malformed structures, wrong chains, and environment changes stop execution.
Runtime locks are explicitly registered; inference never refreshes them automatically.
Use `scripts/register_runtime_locks.py --help` to register a missing component.
An existing lock must not be overwritten merely to suppress an error.

Example:

```sh
cd /lustre/users/u21111210118/projects/test9/source
bash scripts/submit_public.sh prepare configs/KEAP1_observed_rebuild.yaml
# Pass the exact accepted manifest printed by this job to design.
# Pass the resulting design manifest to evaluate.
```

The original MDM2 request used p53 residues 15–29, but 1YCR observes 17–29.
`configs/MDM2_observed_rebuild.yaml` explicitly declares the observed fragment.
KEAP1 uses 2FLU and Q14145 residues 325–609 / Q16236 residues 69–84.
Neither example silently substitutes a requested construct.

## Rebuild validation

Recovered tests include `tests/` and
`benchmarks/computational_strengthening_20260923/test_strengthening.py`.
Run `python -m pytest` in the core environment and retain the receipt.
New rebuild modules add their own validation and receipts.

Three historical candidate sequences were recovered from two recorded outputs.
Their original generated backbones and predicted coordinates remain unavailable.
New refolds have new run identities and cannot establish RMSD to a missing original
design backbone. The new AF2 protocol uses five models and three seeds for each
complex and monomer, checks effective MSA depth, and verifies all 90 outputs.
Pose reassessment uses all models, complete-link clustering, explicit medoids,
all co-major ties, and a separate monomer-fold comparison.

The 78-control identities, sequences, recorded labels, and author structure inputs
were reconstructed. The 60-row historical JSON is byte-identical. Reconstruction
does not qualify each label against its primary assay. Eligibility is stored explicitly.

Historical MD trajectories, calibration outputs, and candidate rankings were not
recovered. Archived reports describe previous results only.
Historical benchmark scripts embed missing run identities and old Slurm wrappers:
preserve them for provenance; execute the newly bound `rebuild/` and `../steps/`
workflows for this deployment.

Confidence, monomer folding, interface physics, competition, and specificity remain
separate evidence axes. A failed joint filter must not be presented as an improvement.
Neither a successful execution nor a computational candidate establishes binding,
blockade, experimental specificity, or benchmark superiority.

## Environments and reproducibility

Private project environments: core, rfd, colabfold, boltz, and physics.
Downloads, installation, validation, physics diagnostics, and reports use CPU.
Model inference uses the organ partition, one GPU per job with `--oversubscribe`.
Preserve the injected NVIDIA driver library paths.
All caches, temporary files, and logs remain under this project. GPU MD is not enabled.

The top-level reconstruction registry records current states and exact evidence paths.
Version-pinned model assets have download receipts and SHA-256 checks.
Source commits and Git bundles are independently restored and checked.
A bundle stored on this same filesystem is not an off-site backup.
GitHub publication is separate from this reconstruction.
