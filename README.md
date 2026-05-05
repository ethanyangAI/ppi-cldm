# PPI-CLDM: Conditional Latent Diffusion for PPI Inhibitor Discovery

A **Conditional Latent Diffusion Model (CLDM)** that generates de novo small-molecule inhibitors targeting protein-protein interactions (PPIs). The pipeline combines interface-aware pocket conditioning, GRU-VAE constrained decoding, AutoDock Vina docking, and 83-target counter-screening to produce selective, drug-like candidates.

---

## Architecture

```
PDB complex
    │
    ▼
interface_extractor.py ──→ PocketEncoder ──→ cond vector c [256]
                                                    │
                                     DDPM reverse diffusion (T=1000)
                                     z_T ~ N(0,I) ──→ z_0
                                                    │
                                     GRU-VAE constrained decode
                                     (token-level SMILES validity filter)
                                                    │
                                     Lipinski + PAINS + chemically_reasonable
                                                    │
                                     Tanimoto diversity filter (threshold=0.4)
                                                    │
                                     AutoDock Vina  ←── receptor.pdbqt
                                                    │
                                     Counter-screen (83 off-targets)
                                     Selectivity = vina_self − mean(vina_off)
                                                    │
                                              candidates.csv
                                          full_screened.csv
```

### Key Components

| File | Role |
|------|------|
| `gru_vae.py` | GRU-VAE encoder/decoder; character-level SMILES tokenizer |
| `latent_diffusion.py` | DDPM + DenoiseMLP (Transformer blocks) + PocketEncoder |
| `interface_extractor.py` | PPI interface residue extraction → pocket feature tensor |
| `ppi_pipeline_universal.py` | **Main entry point** — generation → docking → screening |
| `ppi_targets.py` | Builds `ppi_target_db.json` (downloads PDB, computes pocket centers) |
| `build_offtarget_db.py` | Builds `offtarget_db.json` (~83 diverse human drug targets) |
| `counter_screen_module.py` | Off-target Vina docking + PAINS/Brenk filtering |
| `full_counter_screen.py` | SLURM-array batch version of counter-screening |
| `run_retrosynthesis.py` | AiZynthFinder retrosynthesis analysis |
| `complex_builder.py` | ColabFold/ESMFold complex modeling for novel targets |
| `train_vae.py` | GRU-VAE training on ZINC 100k |
| `train_diffusion.py` | DDPM training on pocket-ligand pairs |
| `train_diffusion_large.py` | Fine-tuning on MW>350 subset for larger molecules |

---

## Supported Targets

10 canonical PPI targets pre-registered in `ppi_target_db.json`:

| Target | Disease | Known Inhibitors |
|--------|---------|-----------------|
| MDM2_TP53 | Cancer (p53 pathway) | Nutlin-3a, AMG232 |
| BCL2_BAX | Apoptosis / Cancer | Venetoclax |
| KRAS_SOS1 | Lung/Pancreatic Cancer | BI-3406 |
| PD1_PDL1 | Immunotherapy | CA-170, BMS-202 |
| MENIN_MLL | Leukemia | Revumenib |
| MYC_MAX | Pan-cancer | 10058-F4 |
| VHL_HIF1A | Renal cancer | Belzutifan |
| XIAP_SMAC | Apoptosis resistance | Birinapant |
| IL2_IL2RA | Autoimmune | SP4206 |
| BRD4_HISTONE | Cancer / Inflammation | JQ1 |

Custom targets can be added via `complex_builder.py`.

---

## Installation

```bash
# 1. Clone
git clone https://github.com/ethanyangAI/ppi-cldm.git
cd ppi-cldm

# 2. Conda environment
conda create -n ppi_env python=3.10
conda activate ppi_env
pip install -r requirements.txt

# 3. Install AutoDock Vina
conda install -c conda-forge vina

# 4. Download model weights  ← see Releases tab
# Place in: core/denovo/checkpoints/
#   vae_ppi.pt                (~40 MB)
#   diffusion_cleaned_mw350.pt (~51 MB)

# 5. Build target databases (downloads PDB files)
cd core/denovo
python ppi_targets.py            # ppi_target_db.json
python build_offtarget_db.py     # offtarget_db.json
```

---

## Quick Start

```bash
cd core/denovo
conda activate ppi_env

# List available targets
python ppi_pipeline_universal.py --list

# Generate 100 candidates for MDM2-TP53
python ppi_pipeline_universal.py --target MDM2_TP53 --n 100

# Full pipeline: generation + docking + counter-screening
python ppi_pipeline_universal.py \
    --target MENIN_MLL --n 100 \
    --vae vae_ppi.pt \
    --counter_screen --cs_top_n 30 --cs_workers 4
```

### SLURM Jobs (HPC)

```bash
# Standard generation (GPU)
sbatch slurm_generate.sh

# Full pipeline with counter-screening (GPU + CPU)
TARGET=KRAS_SOS1 N_MOLS=200 sbatch slurm_full_pipeline.sh

# Counter-screening array (40 tasks × CPU)
sbatch slurm_counter_screen.sh
```

### Training from Scratch

```bash
# 1. Train GRU-VAE on ZINC 100k
sbatch submit_vae_train.sh          # → checkpoints/vae_best.pt

# 2. Train DDPM conditioned on pockets
sbatch submit_diffusion_train.sh    # → checkpoints/diffusion_best.pt

# 3. Fine-tune on MW>350 molecules
python train_diffusion_large.py     # → diffusion_cleaned_mw350.pt
```

### Retrosynthesis

```bash
# Analyze top candidates for synthetic accessibility
python run_retrosynthesis.py --csv results/MDM2_TP53_candidates.csv --top 5

# Single SMILES
python run_retrosynthesis.py --smiles "CCO" --name test_mol
```

---

## Output Files

| File | Description |
|------|-------------|
| `results/{TARGET}_candidates.csv` | Generated + docked candidates |
| `results/{TARGET}_full_screened.csv` | After 83-target counter-screening |
| `results/{TARGET}_manifest.latest.json` | Run metadata + statistics |

Key columns in `full_screened.csv`:

| Column | Meaning |
|--------|---------|
| `vina_self` | Docking score to target (kcal/mol; lower = stronger) |
| `selectivity` | `vina_self − mean(vina_offtargets)`; **negative = target-selective** |
| `composite` | Multi-objective score (lower = better) |
| `pains_flag` | PAINS/Brenk alert (empty = clean) |
| `qed` | Drug-likeness (0–1; higher = better) |
| `vina_CYP3A4` | CYP3A4 off-target score (metabolic liability) |
| `vina_hERG` | hERG off-target score (cardiac safety) |

---

## Composite Score

```
composite = vina × 0.6  −  qed × 3.0  +  size_penalty(MW)
```
Lower is better. When `--counter_screen` is used, results are re-ranked by selectivity.

---

## Checkpoints

Model weights are distributed via GitHub Releases (not tracked by git):

| File | Size | Description |
|------|------|-------------|
| `vae_ppi.pt` | ~40 MB | GRU-VAE fine-tuned on 1401 ChEMBL PPI inhibitors |
| `diffusion_cleaned_mw350.pt` | ~51 MB | DDPM trained on MW>350 pocket-ligand pairs |

---

## Comparison with Related Work

### Quantitative benchmark (PPI targets)

Metrics computed on our pipeline's output across 4 PPI targets (MDM2-TP53, BCL2-BAX, KRAS-SOS1, MENIN-MLL). DiffSBDD and TargetDiff were independently re-run on MDM2-TP53 (n=100, GPU A100) using official pretrained checkpoints (Zenodo 8183747 and 14041881 respectively).

| Method | Validity (%) | QED ↑ | SA score ↓ | Mean MW (Da) | Vina mean (kcal/mol) ↓ | PAINS-clean (%) | Counter-screening |
|---|---|---|---|---|---|---|---|
| **PPI-CLDM — MDM2-TP53** | **100** | 0.534 | 5.44 | 362 | -7.30 | 98.2 | ✅ 83 targets |
| **PPI-CLDM — MENIN-MLL** | **100** | 0.555 | 5.59 | 370 | -7.99 | **100** | ✅ 83 targets |
| **PPI-CLDM — KRAS-SOS1** | **100** | 0.491 | 5.61 | 406 | -3.41 | **100** | ✅ 83 targets |
| Pocket2Mol† ([Peng et al., 2022](https://arxiv.org/abs/2205.07249)) | 94.4 | 0.575 | 4.14 | ~300 | -7.15 | N/R | ❌ |
| DiffSBDD‡ ([Schneuing et al., 2022](https://arxiv.org/abs/2210.13695)) | **97** | 0.495 | **4.47** | 360 | N/M | 96.9 | ❌ |
| TargetDiff§ ([Guan et al., 2023](https://arxiv.org/abs/2302.07573)) | 97.9 | 0.579 | 5.14 | ~310 | -7.80 | N/R | ❌ |

> † Evaluated on CrossDocked2020 benchmark (kinase/GPCR-dominant); PPI targets not separately reported.  
> ‡ Independently measured on MDM2-TP53 pocket (n=100, Zenodo 8183747, ppi\_env + A100). Vina not run (N/M). Published CrossDocked2020: validity=87.7%, QED=0.475, SA=4.96, MW≈280, Vina=−6.88.  
> § TargetDiff re-run on MDM2-TP53 (n=100, Zenodo 14041881, A100); only 3/100 molecules survived RDKit reconstruction due to a mixed conda/pip numpy environment causing silent failures in openbabel→RDKit conversion. Surviving molecule properties (MW=459, QED=0.304, SA=4.95) are not statistically representative. Literature CrossDocked2020 numbers shown.  
> SA score: RDKit scale 1–10, lower = easier to synthesize. N/R = not reported.

### Capability comparison

| | PPI-CLDM | Pocket2Mol | DiffSBDD | TargetDiff | REINVENT |
|---|---|---|---|---|---|
| PPI-specific training | ✅ 1401 ChEMBL PPI inhibitors | ❌ | ❌ | ❌ | ❌ per-target RL only |
| 100% valid SMILES (constrained decode) | ✅ | ❌ 94.4% | ❌ 97%‡ | ❌ 97.9% | ✅ |
| MW>350 bias correction | ✅ re-trained subset | ❌ | ❌ | ❌ | reward-dependent |
| Built-in 83-target counter-screening | ✅ | ❌ | ❌ | ❌ | ❌ |
| Selectivity score (Δ vina) | ✅ | ❌ | ❌ | ❌ | ❌ |
| PAINS/Brenk auto-filter | ✅ | ❌ | ❌ | ❌ | configurable |
| HPC SLURM array support | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{ppi_cldm_2026,
  title  = {PPI-CLDM: Conditional Latent Diffusion for PPI Inhibitor Discovery},
  author = {Yang, Zijian},
  year   = {2026},
  url    = {https://github.com/ethanyangAI/ppi-cldm}
}
```
