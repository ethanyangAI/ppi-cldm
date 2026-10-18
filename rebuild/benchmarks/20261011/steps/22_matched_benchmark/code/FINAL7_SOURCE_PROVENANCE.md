# Final seven-target input provenance audit

Status: SOURCE_AND_INPUT_PROVENANCE_PASS.
Evidence is input identity and software provenance. No generated binder, native AF2 result, common-evaluator result or method performance estimate is included.

Authority: /lustre/users/u21111210118/projects/test9

## Verified records

- Root input inventory: steps/22_matched_benchmark/input_preparation/prepared_7_13010/prepared_inputs.json.
- Immutable orchestration source snapshot: steps/22_matched_benchmark/settings/pilot_v1/source/snapshot_manifest.json.
- Independent audit report: steps/22_matched_benchmark/code/provenance_final7_13019.json, 79,571 bytes, SHA-256 4d6c339ffda336254cb445e12505ff7cfdabc159dc94c43961b6d522dbd2845e.
- Auditor: steps/22_matched_benchmark/code/audit_input_provenance.py. It independently recomputes file hashes and coordinate/sequence identities; it does not import the input-preparation or generation implementation.
- CPU Slurm job 13019: COMPLETED; AllocTRES billing=1,cpu=1,node=1; zero allocated GPUs.

The auditor recursively followed the two root JSON records and their referenced JSON receipts. All 75 distinct path/hash receipts matched their current bytes, including the immutable input-generation source, original deposited structure/entity/identity records, prepared target/reference files, repair record/package source and orchestration snapshots.

## Seven-target identity checks

| Target | Role | Family | Input identity / mapping |
|---|---|---|---|
| MDM2_1YCR | primary | MDM2 | PASS |
| KEAP1_2FLU | primary | Kelch | PASS |
| EGFR_DIII_1IVO | primary | EGFR | PASS |
| BCLXL_2M04 | primary | BCL2 | PASS |
| HRAS_4G0N | primary | RAS | PASS; missing 64/65 remain modeled |
| CRK_SH3_1CKA | primary | SH3 | PASS; mouse construct |
| BBF111_9HAG | diagnostic | BBF | PASS; synthetic target, excluded from primary target n |

For each target, the supplied complete sequence matched the target PDB CA residue sequence. The target input used the declared single chain and contiguous design numbering. Hotspots were inside that exact target, binder length was fixed at 65, and reference residue mappings were unique and complete for all observed coordinates.

For HRAS, the experimental reference contains 164 observed residues; the repaired target contains 166 residues. Positions 64 and 65 have no experimental coordinate mapping and are explicitly retained as modeled positions. This missing-reference status is allowed by the audit and does not invent reference coordinates.

## HRAS repair gate

The repair receipt pins the immutable input source and original observed structure. It records PDBFixer addMissingAtoms and OpenMM Reference/Amber14 with fixed seed 21101, no partner coordinates, and only missing residues 64/65 allowed to move. Reported peptide closures are within 1.1–1.6 Å and the receipt reports no severe nonneighbor clash.

The independent auditor transformed the old compact 164-residue numbering to full label_seq_id numbering using the verified original identity mapping, then compared every observed heavy atom to the repaired target. All 1,283 original heavy atoms were present and the maximum coordinate displacement was exactly 0.0 Å at PDB precision. This directly verifies the fixed-observed-coordinate gate.

The audit verifies the reported repair platform, variable residues, seed, force field and closure/clash receipt. It independently recomputes the observed-heavy-atom preservation; it does not rerun minimization or infer that the modeled missing loop has experimental validity.

## Preserved engineering history

The earlier prepared_6_12996 inventory referenced a mutable preparation source whose bytes later changed during engineering. That source-provenance problem remains recorded in provenance_preformal_13014.json and is not used as a formal input freeze.

Audit 13017 used a checker assumption that original compact indices and repaired full indices were identical and that modeled positions required an experimental mapping. The corrected audit 13019 explicitly uses the original identity mapping and the two typed modeled positions. Report 13017 is retained as checker-engineering history; its apparent displacement is not evidence that observed atoms moved.

## What still needs live pilot acceptance

The declared RF contig A1-N/0 65-65 follows the official ContigMap mapping to output binder A/receptor B. A real GPU pilot must still produce an output-PDB chain/sequence/length identity receipt. Common external inference uses target A/binder B from its own exact query construction.

Runtime/native AF2 model fidelity, immutable method/environment/config/weight sources, persistent session startup, actual allocated physical GPU, end-to-end timing, hard-budget ledger completeness and common-evaluator outcomes are separate live acceptance gates. They are not established by this input-provenance PASS.

