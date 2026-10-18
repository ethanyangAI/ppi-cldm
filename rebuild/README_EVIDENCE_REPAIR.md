# Evidence repair and qualified calibration (public-cluster reconstruction)

Execution root: /lustre/users/u21111210118/projects/test9.
Submit via u21111210118@192.168.81.6 port22560. All analysis, downloads, hashes,
packaging and restore checks are CPU Slurm jobs; only model inference requests GPUs.

The previous lvying artifacts were not recovered. The retained original GitHub
baseline, current source tree and new output receipts distinguish reconstruction
from historical results. Never call new predictions the lost original coordinates.

## Recorded modules

- qualification_rfd60.py and qualification_bindcraft18.py: source-level assay,
  identity and construct adjudication. Author-conditioned binding screens are not
  standardized monomer affinity or general PPI blockade truth.
- specificity_prepare.py / specificity_review.py / specificity_analyze.py and
  related independent scripts: declared experimental constructs plus separate
  observed-residue sensitivities. Do not replace the declared result by the better
  sensitivity. Full scores and geometry remain separate.
- evidence_axes.py: all45 KEAP1 observed-core complex models, all5 cluster medoids,
  monomer support and24 Rosetta diagnostics. evidence_axes_independent.py is the
  immutable independent review snapshot. ipSAE uses both directions and their
  minimum; original backbone RMSD stays unavailable.
- control_prepare.py / control_review.py / control_score.py: all78 controls,
  5 multimer-v3 weights by3 seeds, without template or coordinate input.
  The successful CPU validator is the explicitly registered v2 semantic-A3M
  entrypoint, documented by step17 receipts. Preserve the original worker and
  failed byte-comparison validator as historical execution snapshots.
- calibration_qualified.py: frozen qualification, confidence-only held-family math
  and tests. calibration_qualified_run.py and calibration_qualified_validate.py
  archive the execution/independent driver bytes; runtime receipts identify
  executed paths. Main32 and wider67 are distinct, with11 QC-confounded nonhits
  retained in the full78 catalog.
- evidence_delivery.py: freeze terminal gates, close the artifact graph, create
  a source Git bundle/data parts, then verify an independent restore and pytest.
- publish_evidence_repair.py: promote accepted phase only after independent
  restore; keep reconstruction_20261002.json immutable and publish a new phase
  registry plus ACTIVE.json after live graph verification.

## Scientific and statistical contracts

Every sequence is a statistical unit; models and seeds are technical replicates.
Incomplete confidence ensembles and absent contact scores remain null. Training
folds missing a class abstain. Test-fold class-specific metrics and AUROC retain
their defined denominators. No label is selected or revised using model scores.

The old strict joint fold/physics rule is not the sole rejection gate. Confidence,
ipSAE, free-fold support, interface physics, competition geometry, specificity and
structural context are separate axes. Rosetta energy units are not experimental
free energies; static overlap is not blockade. No new MD is authorized in this phase.

The scientific report is reports/EVIDENCE_REPAIR_20261004.md after acceptance.
00_admin/ACTIVE.json becomes the active phase pointer only after publication.
Before publication, consult each step's actual status; queued jobs and planned
paths do not establish completion.

## Reproducibility boundary

Run scripts through their recorded Slurm recipes and immutable plan/input hashes.
Some scripts intentionally refer to the registered run paths and are not generic
relocatable CLIs. Restoring the same project root preserves these references.
Do not overwrite accepted manifests to reuse a historical run identity.

The data package contains scientific input/output evidence and source snapshots.
Runtime environments, downloadable model weights and explicitly unavailable old
artifacts are separately inventoried with recipes/locks. A same-filesystem
independent restore is not an offsite backup or a fully offline runtime image.

