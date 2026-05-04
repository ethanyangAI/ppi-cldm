"""
全量反筛 - Slurm Array 版本
SLURM_ARRAY_TASK_ID 决定处理哪批分子
每个 job: ~15 分子 × 83 off-targets = ~1245 次 Vina 对接
"""
import os, re, csv, json, subprocess, shutil
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

BASE      = Path("/home/huangym/zjy/ppi_gen_project/core/denovo")
RESULTS   = BASE / "results"
TMP       = BASE / "full_cs_tmp"
VINA      = "/home/huangym/anaconda/conda/envs/ppi_env/bin/vina"
PPI_DB    = BASE / "ppi_target_db.json"
OFF_DB    = BASE / "offtarget_db.json"
PARTIAL   = BASE / "full_cs_partial"

os.makedirs(TMP, exist_ok=True)
os.makedirs(PARTIAL, exist_ok=True)

# PAINS filter
_params = FilterCatalogParams()
_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
CATALOG = FilterCatalog(_params)

ATYPE = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
         'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD'}

def pains_flag(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None: return "invalid"
    if CATALOG.HasMatch(mol):
        return CATALOG.GetFirstMatch(mol).GetDescription()
    return ""

def mol_to_pdbqt(smi, path):
    mol = Chem.MolFromSmiles(smi)
    if mol is None: return None
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
        if AllChem.EmbedMolecule(mol, randomSeed=42) != 0: return None
    AllChem.MMFFOptimizeMolecule(mol)
    conf = mol.GetConformer()
    idx = 1; lines = ['REMARK\nROOT\n']
    for i, a in enumerate(mol.GetAtoms()):
        if a.GetSymbol() == 'H': continue
        p = conf.GetAtomPosition(i)
        at = ATYPE.get(a.GetSymbol().upper(), 'C')
        lines.append(f'ATOM  {idx:5d}  {a.GetSymbol():<4s}LIG A   1    '
                     f'{p.x:8.3f}{p.y:8.3f}{p.z:8.3f}  1.00  0.00    0.0000 {at}\n')
        idx += 1
    lines.append('ENDROOT\nTORSDOF 0\n')
    with open(path, 'w') as f:
        f.writelines(lines)
    return path

def run_vina(rec, lig, center, box=[25,25,25]):
    cx,cy,cz = center; sx,sy,sz = box
    try:
        r = subprocess.run([VINA,
            '--receptor',str(rec),'--ligand',str(lig),
            '--out',str(lig).replace('.pdbqt','_out.pdbqt'),
            '--center_x',str(cx),'--center_y',str(cy),'--center_z',str(cz),
            '--size_x',str(sx),'--size_y',str(sy),'--size_z',str(sz),
            '--num_modes','1','--exhaustiveness','4','--cpu','2'],
            capture_output=True, text=True, timeout=90)
        for line in r.stdout.split('\n'):
            if re.match(r'\s+1\s+', line):
                try: return float(line.split()[1])
                except: pass
    except: pass
    return None

# ---- Load all molecules (flattened across all targets) ----
TARGET_CSV = {
    'MDM2_TP53':    RESULTS/'MDM2_TP53_candidates.csv',
    'BCL2_BAX':     RESULTS/'BCL2_BAX_candidates.csv',
    'KRAS_SOS1':    RESULTS/'KRAS_SOS1_candidates.csv',
    'PD1_PDL1':     RESULTS/'PD1_PDL1_candidates.csv',
    'MENIN_MLL':    RESULTS/'MENIN_MLL_candidates.csv',
    'MYC_MAX':      RESULTS/'MYC_MAX_candidates.csv',
    'VHL_HIF1A':    RESULTS/'VHL_HIF1A_candidates.csv',
    'XIAP_SMAC':    RESULTS/'XIAP_SMAC_candidates.csv',
    'IL2_IL2RA':    RESULTS/'IL2_IL2RA_candidates.csv',
    'BRD4_HISTONE': RESULTS/'BRD4_HISTONE_candidates.csv',
}

all_mols = []  # list of (uid, target, smiles, own_vina, row_dict)
for target, csv_path in TARGET_CSV.items():
    if not csv_path.exists(): continue
    with open(csv_path) as _f:
        rows = list(csv.DictReader(_f))
    for i, row in enumerate(rows):
        smi = row.get('smiles','')
        if not smi: continue
        own_vina = row.get('vina_score','')
        try: own_vina = float(own_vina)
        except: own_vina = None
        uid = f"{target}_{i:04d}"
        all_mols.append((uid, target, smi, own_vina, row))

print(f"Total molecules: {len(all_mols)}")

# ---- Load off-target databases ----
ppi_db = json.load(open(PPI_DB))
off_db = json.load(open(OFF_DB))

# Merge all off-targets (PPI targets renamed to avoid confusion)
all_offtargets = {}
for k,v in ppi_db.items():
    all_offtargets[f"PPI_{k}"] = v
for k,v in off_db.items():
    all_offtargets[k] = v

print(f"Off-target panel: {len(all_offtargets)} receptors")

# ---- Determine this job's chunk ----
N_JOBS  = 40
task_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0))
chunk_size = (len(all_mols) + N_JOBS - 1) // N_JOBS
start = task_id * chunk_size
end   = min(start + chunk_size, len(all_mols))
my_mols = all_mols[start:end]

print(f"Task {task_id}: processing molecules {start}-{end-1} ({len(my_mols)} total)")

# ---- Process each molecule ----
results = []

for mol_idx, (uid, target, smi, own_vina, orig_row) in enumerate(my_mols):
    print(f"  [{task_id}:{mol_idx+1}/{len(my_mols)}] {uid}")

    pf = pains_flag(smi)

    # Embed molecule
    lig = TMP / f"{uid}.pdbqt"
    embedded = mol_to_pdbqt(smi, lig) is not None

    off_scores = {}
    if embedded:
        for off_name, off_info in all_offtargets.items():
            # Skip if this is the molecule's own PPI target
            if off_name == f"PPI_{target}":
                continue
            rec   = off_info.get('pdbqt_path') or off_info.get('pdbqt_path')
            ctr   = off_info.get('pocket_center')
            box   = off_info.get('box_size', [25,25,25])
            if not rec or not ctr or not Path(rec).exists():
                continue
            lig_off = TMP / f"{uid}_{off_name[:20]}.pdbqt"
            shutil.copy(lig, lig_off)
            score = run_vina(rec, lig_off, ctr, box)
            off_scores[off_name] = score
            for _tmp in [lig_off, Path(str(lig_off).replace('.pdbqt', '_out.pdbqt'))]:
                try: _tmp.unlink()
                except OSError: pass

    # Selectivity (exclude positive/failed dockings)
    valid_off = [v for v in off_scores.values() if v is not None and v < 0]
    if own_vina is not None and len(valid_off) >= 5:
        sel = own_vina - (sum(valid_off) / len(valid_off))
    else:
        sel = None

    result = {
        'uid': uid,
        'target': target,
        'smiles': smi,
        'mw': orig_row.get('mw',''),
        'logp': orig_row.get('logp',''),
        'qed': orig_row.get('qed',''),
        'vina_self': f'{own_vina:.3f}' if own_vina is not None else '',
        'composite': orig_row.get('composite',''),
        'pains_flag': pf,
        'n_offtargets_docked': len(valid_off),
        'mean_off_vina': f'{sum(valid_off)/len(valid_off):.3f}' if valid_off else '',
        'selectivity': f'{sel:.3f}' if sel is not None else '',
    }
    # Add individual off-target scores for key targets
    for key in ['CYP3A4','hERG','HSA','CDK2','Thrombin','EGFR','AChE','PARP1','BRD4','HDAC2']:
        result[f'vina_{key}'] = f'{off_scores.get(key):.3f}' if off_scores.get(key) is not None else ''
    results.append(result)

# Save partial result
out_path = PARTIAL / f"partial_{task_id:03d}.csv"
fieldnames = ['uid','target','smiles','mw','logp','qed','vina_self','composite',
              'pains_flag','n_offtargets_docked','mean_off_vina','selectivity',
              'vina_CYP3A4','vina_hERG','vina_HSA','vina_CDK2','vina_Thrombin',
              'vina_EGFR','vina_AChE','vina_PARP1','vina_BRD4','vina_HDAC2']
with open(out_path,'w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    w.writeheader()
    w.writerows(results)

print(f"Task {task_id} done -> {out_path}")
