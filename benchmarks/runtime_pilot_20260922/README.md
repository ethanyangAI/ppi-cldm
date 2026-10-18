# Frozen runtime pilot, 2026-09-22

These are provenance-preserving benchmark drivers, not a claim of workflow superiority.
Authority is the test9 root. Submit through Slurm; execute with env/core.
Model environments and assets are separate. Exact manifest inputs are embedded in drivers.
Archived per-run qc/driver.py remains the source of truth for historical execution.
The primary developmental cases are P06 WDR5 and P09 KEAP1: two backbones, two sequences each, seed 42, 65 residues.
Generators: RFdiffusion + ProteinMPNN, whole-native-peptide motif scaffolding, BoltzGen 0.3.2.
The P06 predicted-pose branch is a separate input ablation.
P32 is excluded from the wild-type comparison: 2K5B has S63T relative to current P07900 and is an NMR-restrained docking reference.
P32 historical generation used the observed sequence; blind prediction used the requested canonical sequence. They are not a valid matched pose pair.
AF2 is a separate single-sequence multimer-v3 sensitivity verifier; its global ipTM is not Boltz directional pair-ipTM.
Published KEAP1 controls are not new experimental measurements, and the assay construct is not reproduced exactly.
TM-align clustering is descriptive single-link clustering, not experimental validation.
The planned six-target / four-generator / two-seed / 64-candidate pilot remains a separate, unmet benchmark gate.
No public repository push or experimental synthesis is performed by these drivers.
