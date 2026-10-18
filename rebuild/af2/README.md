# AF2 reconstruction execution archive

Reviewed drivers derive from steps/03_af2_restore and steps/08_candidate_refolds, bound to /lustre/users/u21111210118/projects/test9. Manifest distinguishes exact copies from PS1 guards added after execution.

Runtime: ColabFold1.5.5/AlphaFold-ColabFold2.3.6/JAX0.4.23CUDA11.8. CPUinstallation11692; A100kernel11714; runtime/assets/input acceptance11726. Five multimer weights match historic per-file SHA256 and complete official archive SHA256/MD5. Five PTMweights validated against immutable-ETagHTTPS ranges/tarheaders/readableNPZ; their SHA256 are newly recorded. Parameters CC BY4.0, AlphaFold Apache2.0, ColabFold MIT.

KEAP1 targetMSA was regenerated2026-10-02; September MSA snapshot unavailable. Query-only paired row preserves both sequences; no evolutionary interchain paired homologs. Complexes use mmseqs2_uniref_env CLI with frozen A3M and effective128:256; monomers use single_sequence1:1. Both five models,seeds1042–1044,up to12recycles,tolerance0.5,no templates,no relaxation.

Corrected array11743 generated90models(45complex+45monomer). CPU11746 verified unique model/seed, exact chain sequences, PAE dimensions, finite scores and hashes. Cancelled11732 used accidental1:1complex MSA and is excluded. Failures and originalexecuted drivers remain in live steps, unchanged.

Live accepted manifests: steps/03_af2_restore/manifest.json and steps/08_candidate_refolds/outputs/acceptance.json. New predictions are not old coordinate restoration; old generated backbone RMSD is unavailable. Technical validation does not establish binding, blockade, specificity or workflow superiority.

Only code copied here; no sequence input table/MSA/PDB/weights/environment/credential. Immutable original scripts retained; archived shell variants addPS1guard for noninteractive conda. Preserve system NVIDIA driver library paths. All install/download/CPUvalidation usesSlurm;GPU only runtimekernel/inference. Embedded live-step paths must be deliberately rebound during another restoration.
