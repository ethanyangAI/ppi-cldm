# Control refolding: supported validation entry points

The immutable scientific inference plan is `steps/17_control_calibration/plan.json` (job 11939); six exact target constructs, 78 identities, five AF2-Multimer v3 models and seeds 1042–1044. The GPU array is 11941, capped at two concurrent GPUs.

Inference was executed by `source/rebuild/control_review.py worker` through `control_run.sh`. Preserve those files as execution history. The original `control_review.py validate` contains an invalid byte-equality assertion for ColabFold's A3M serialization and must **not** be used as the validation entry point.

Supported CPU validation and scoring:

```sh
env PYTHONNOUSERSITE=1 JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1 env/colabfold/bin/python source/rebuild/control_review_v2.py validate 11941
env PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 env/core/bin/python source/rebuild/control_score_v2.py score 11941
```

Use project-root working directory and Slurm CPU jobs; do not run these on a login node. These commands create immutable acceptance/score outputs and are intentionally not overwrite-idempotent.

`control_msa_check.py` verifies full query and chain order/cardinality, each paired/unpaired MSA row in order, every deletion-matrix entry, and a raw retained-row mapping. It permits only explicitly mapped duplicate raw rows to disappear. Actual A3M files retain their own hashes. `plan_v2.json` and `inputs/msa_acceptance_v2.json` add this technical validation revision without changing inference or the fixed confidence formula.

Read `outputs/validation_release.json`: it corrects the initial v2 metadata phrase “before any GPU inference.” The first two array tasks (30 models) had completed before the validator amendment; the original scientific plan was frozen before inference, no confidence values informed the technical rule, and none of the 30 models are rerun. The first rewrite retry 11971 failed safely rather than overwrite immutable outputs.

The acceptance/score job is 11974, after GPU11941 and validation-release CPU11978. Final outputs:
- `outputs/acceptance_11941.json`: all 1170 technical model checks.
- `outputs/score_summary_11941.json`: all 78 identities, 15 model records each, and explicit missingness.
- `outputs/msa_semantics_11941/*.json`: exact per-condition MSA semantic receipts.
- `outputs/validation_release.json`: source hashes and provenance correction.
No-contact models have a null confidence score. A primary per-identity median requires all 15 model scores; technical completeness is separate from score estimability. Independent endpoint qualification and held-out-family calibration belong to step18.

All source files remain under `source/rebuild`; a source Git bundle restores both the original inference snapshot and the supported v2 validator. The corresponding step17 scheduler scripts and receipts should be included in the data recovery package.


MSA depth boundary: the raw and parser-effective full MSA row counts are measured and recorded, and the effective configuration caps are 128 cluster sequences plus 256 extra sequences. Default ColabFold does not export per-recycle stochastic MSA row-selection indices. Exact full-MSA order, deletion matrices, software version, model/seed identities and caps are frozen; do not report the full raw row count as the number actually consumed by each model.
