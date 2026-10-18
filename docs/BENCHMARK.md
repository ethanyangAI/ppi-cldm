# Benchmark execution status and interfaces

This is the benchmark infrastructure layer, not a completed comparative benchmark.

## Implemented and exercised
- `structure.mode: predict_only` bypasses RCSB search and coordinate retrieval, rejects reference-PDB/path/assembly hints and template/contact inputs. Protein identity resolution may still use UniProt. Training leakage is explicitly unknown.
- `python -m ppiblocker.benchmark --root ROOT select EVALUATION_MANIFEST --k 8` applies S0 and S1 to exactly the same immutable pool. Both use the same binding-confidence ranking; S1 adds native-interface/competition gates. Unfilled slots remain in the denominator. Deduplication is exact sequence only.
- Backend commands preserve wall time, child CPU time and failure/timeout status. Reported max RSS is a process-wide child high-water mark, not an isolated per-command peak. GPU utilization is not measured by this receipt.
- Registry validation rejects unresolved splits, family leakage and unreviewed test-set homology.
- `benchmark_adapters.export_inputs` exports equal-hotspot target inputs for BindCraft and BoltzGen. These are configurations, NOT successful method runs.
- `benchmark_adapters.import_pool` validates hashed external runtime/backbones and ordered target identity before using the existing common refold/evaluation route.

## Qualification
`scripts/qualify_benchmark.py ROOT MATRIX_JSON` examines every candidate in the proposal, with exact human identities, bounded RCSB searches, assembly/entity checks and target-backbone checks. Context-extension cases are triaged rather than stripped into two-chain inputs. Histone cases are explicitly narrowed to H4 canonical and H3.1; PAK1 uses Q13153 and IL7R-alpha uses P16871. These choices are recorded, not silently inferred.

Qualification of a deposited construct does not establish full-length physiological sufficiency. Three-pass cases (including the already-used MDM2 case) are insufficient to freeze a six-target positive design pilot. Do not count refusal controls as additional successful design targets.

## Not implemented or not verified
- Installed/tested BindCraft, BoltzGen and RFD3 runtime adapters; RFD3 input adapter.
- External independent verifier integration and official DockQ scoring.
- Structural/near-sequence clustering, calibrated thresholds and paired family-level outcome statistics.
- Prospective six-target generation benchmark, off-target experiments or wet-lab blockade labels.

Do not interpret these gaps as scientific failures of the external methods.

The proposal's four-generator GPU budgets are conditional on qualification and runtime verification; no large GPU campaign is automatically submitted by this layer.

