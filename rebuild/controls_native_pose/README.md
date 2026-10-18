# Controls, native references and pose reconstruction scripts

This directory is a Git-ready archive of the exact small step scripts and configuration used during the 2026-10-02 reconstruction on u21111210118. MANIFEST.json retains the source project-relative path, SHA-256 and size for every copied file. No raw payloads, PDBs, archives, model weights, data tables or run outputs are copied here.

## Active entry and archived snapshots

The active pose implementation is ../pose_reassessment.py. It is deliberately not duplicated here. Its production invocation is:
    source/rebuild/pose_reassessment.py --config steps/10_pose_reassessment/config.json

The steps/ tree inside this directory contains faithful archived snapshots of the runtime step scripts. They preserve the run identifiers, source URLs, historical selection algorithm and absolute project root used for reconstruction. They are provenance assets, not automatic job launchers and not a second active copy. To re-execute in another project root, adapt paths explicitly and record a new version and new run; do not alter accepted run snapshots.

Accepted controls: reconstruction11698, independent11705; author60 structures11731, independent11758. Accepted native references:4CH9/6TTK11716, independent11722;2FLU11737, independent11749. Accepted pose reassessment and normalized medoid export:11761, independent11786. Run11757 completed the same geometric calculation before the requested medoid export was added and is superseded as the consumption entry. Validation11766 had a syntax error and was superseded by corrected independent11786.

All computations were submitted through Slurm on the CPU partition. The pose wrapper relies on the separately accepted90-model new AF2 output and a frozen plan hash. Future runs must verify both upstream scientific identity and receipts, not only scheduler exit status.

## Evidence boundary

Control identities and78 author input structures are restored; original60 selected table is byte-identical to the historical hash. All78 remain ineligible for the main benchmark until full assay qualification. Author structures are design references, not experimentally resolved native complexes or our predictions.

The new90-model candidate ensemble is a reconstruction with regenerated MSA. Pose clustering, medoid export and monomer support are computational diagnostics. Historical design backbones, AF2 coordinates, MSA and MD trajectories were not recovered. No experimental binding, PPI blockade or benchmark superiority is established by these scripts.

ACCEPTANCE_POINTERS.json stores hash-bearing pointers to remote accepted evidence; it does not embed the underlying data.
