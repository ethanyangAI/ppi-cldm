# Structure-first PPI blocker workflow

This branch rebuilds public ppi-cldm into a protein binder workflow. Legacy GRU/small-molecule scripts remain historical and are not called by the new CLI.

## Scientific contract

Input is two ordered protein constructs: target A and native partner B. Use UniProt accessions, exact gene plus taxon, or one canonical sequence each. A gene name alone is insufficient. A pair of arbitrary proteins does not imply that they interact.

1. Retrieve an experimental biological assembly with both exact reference accessions. Validate observed sequences, species, entity accessions and physical contacts. Preserve the assembly, mapping and rejection ledger.
2. Without an accepted complex, return NEEDS_PREDICTION. Boltz-2 predicts multiple unrestrained poses. Pair-specific ipTM, interface PAE, local pLDDT and pose convergence gate further use. These scores are not interaction probabilities.
3. Require documented native-interaction support and reviewed construct context. This route supports soluble two-protein assemblies without required unmodelled cofactors, glycans, membranes or additional subunits. Unsupported context is rejected.
4. Derive geometric RFdiffusion anchors from native-interface contacts. Generate binder backbones; ProteinMPNN designs only the binder chain, keeping the target sequence fixed.
5. Blindly refold target plus each designed sequence without a complex template or contact restraint. Evaluate target-aligned binder RMSD, native-interface coverage, native-partner steric incompatibility, target distortion and confidence. Retain rejected and failed candidates.

COMPUTATIONAL_COMPETITION_CANDIDATE is a computational steric-competition hypothesis. It is not measured binding, functional blockade, selectivity, expression, stability, therapeutic activity or safety. Allosteric blockers are outside this route.

Example thresholds are engineering triage settings, not universally calibrated decisions. Single-sequence inference is explicit in the benchmark and may reduce reliability. Use approved local MSAs for natural proteins; public MSA submission is disabled unless allow_external_msa is explicitly set.

## Execution on public_cluster_2

The sole authoritative root is /lustre/users/u21111210118/projects/test9, account u21111210118, Slurm submission endpoint192.168.81.6:22560. The20003 endpoint shares storage but is not the validated submission endpoint. Read the root CLUSTER_BINDING.md and reconstruction registry before execution.

From the source directory, use only the active wrapper:

    bash scripts/submit_public.sh prepare configs/KEAP1_observed_rebuild.yaml
    bash scripts/submit_public.sh predict EXPLICIT_PREPARE_MANIFEST
    bash scripts/submit_public.sh design EXPLICIT_ACCEPTED_POSE_MANIFEST
    bash scripts/submit_public.sh evaluate EXPLICIT_DESIGN_MANIFEST
    bash scripts/submit_public.sh reevaluate EXPLICIT_EVALUATION_MANIFEST

Use predict only for NEEDS_PREDICTION; an accepted experimental pose goes directly to design. Keep each actual output manifest path. The active wrapper requires inputs within the project root and submits through Slurm with accountu21111210118/qosnormal. CPU prepare/reevaluate use interactive (2CPU,8GB,1hour). GPU predict/design/evaluate use organ, --gres=gpu:1 and --oversubscribe (4CPU,64GB,24hours). Larger CPUjobs may be explicitly reviewed forcell; the wrapper does not automatically change partitions. No GPU MD is authorized.

All installation, asset downloads, analysis and tests also run as CPU Slurm jobs. Login nodes only edit/read files and manage submissions. Use project-local core/rfd/boltz/colabfold conda environments, preserve injected NVIDIA driver paths, and initialize PS1 before noninteractive conda activation under set-u. Runtime locks are explicit reviewed baselines; never refresh them automatically during inference. Register only a missing component with --component when other reviewed locks already exist.

The historical scripts/submit_stage.sh is disabled and exits2 before submission. Its original Fudan body is retained solely for audit; do not execute historicalstage_job/benchmark wrappers. New public-cluster authority does not make historical runIDs or lost output files valid.

Every invocation gets a UTC/UUID run ID. No command selects a latest file. Input and output hashes prevent changed artifacts entering downstream runs. Failed invocations retain errors and logs.

## Boundaries

- Construct ranges are one-based inclusive UniProt positions. Observed residues map to canonical positions.
- Provided sequences have caller-supplied identity; model outputs must match them exactly.
- An isolated monomer is never accepted as a complex.
- Search is bounded to 20 entries; no hit does not prove that no matching complex exists.
- The first identity-valid contacting assembly is used; this is not a guarantee of the best experimental structure.
- Experimental coordinates establish an observed interface, not universal physiological relevance.
- RFdiffusion currently requires a continuous observed target backbone and a 30–200-residue binder.
- Membranes, glycans, oligomers and construct changes need a reviewed extension.
- A familiar benchmark tests integration, not leakage-controlled generalization.
- ProteinMPNN scores and Boltz confidence are not averaged into a binding probability.
- No automatic small-molecule route or automatic public sequence upload exists.

## Evidence

Runs contain manifest.json, outputs/, work/, logs/ and qc/. Original assembly, normalized pose, residue mapping, metadata receipts, model confidences/PAEs and design/refold structures are preserved. The manifest contains source identity, hashes, status and evidence tier.

Public baseline: e2984a94674ffcb75b280680038df5e9f39d684d. Remote Git-over-HTTPS failed, so the verified matching local Git archive supplied the initial tree. External model packages use official commit archives with commit/SHA-256 receipts.

Official references:
- https://github.com/RosettaCommons/RFdiffusion
- https://github.com/dauparas/ProteinMPNN
- https://github.com/jwohlwend/boltz
- https://search.rcsb.org/
- https://www.uniprot.org/help/api


## Independent-audit corrections (2026-09-20)

Configuration approval flags require YAML booleans; quoted "false", numbers and null are rejected. Native-pair MSAs belong in proteins[0/1].msa; binder refolding accepts refold.target_msa. prediction.target_msa is rejected. Local MSA formats are .a3m or .csv; snapshots preserve the original format. Relative MSA paths resolve against the original configuration directory. Prepare copies each MSA into its immutable run and records original-source and snapshot hashes. Downstream stages consume verified snapshots, not a mutable external path. Legacy manifests containing unpinned MSAs must be prepared again.

The contact_cutoff gate now governs structure contact selection, confidence interfaces, RF geometric anchors and competition coverage. Entity metadata is checked for each candidate physical chain pair before selecting the maximum-contact valid pair.

Evaluation distinguishes predicted_complex_interface (same predicted A/B model) from reference_projection_interface (native target plus aligned predicted binder). Only the actual predicted complex is used for the severe target–binder clash gate. Native-interface coverage intersects native contact residue indices with actual predicted target contact residue indices; reference-projection coverage is a separate diagnostic. Original-partner overlap is intentionally computed after alignment to the reference, because it addresses simultaneous occupancy of that reference pose.

Valid, sequence-correct models without contact are scientifically rejected. Corrupt JSON/PAE/structures, wrong sequences/chains and unsupported extra context are evaluation failures. Any failed sample prevents a candidate or a pose from receiving an accepted/complete classification. Incomplete states exit with status 2.

Existing complete evaluations can be reanalysed on CPU without regenerating any structures:

    bash scripts/submit_public.sh reevaluate EXPLICIT_OLD_EVALUATION_MANIFEST

This creates a new run, verifies the original design/sequence/model relationship, records the old inference provenance separately, and preserves the old results. Reanalysis does not retroactively validate the old inference environment or count as independent model validation.

Each stage checks the core environment. Model stages additionally check their actual backend runtime against reviewed environment/runtime-lock-*.json. Runtime drift is fatal. See DEPLOYMENT.md for scope and initialization limits.
