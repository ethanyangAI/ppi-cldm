"""
批量反筛选脚本 - 对所有已有候选分子进行：
1. PAINS / 结构警报过滤
2. 自身靶标对接（若尚无 vina_score）
3. 3 个对照靶标反筛（MDM2_TP53, BCL2_BAX, MENIN_MLL）
4. 计算选择性得分 = vina_self - mean(vina_off_targets)
输出: results/{TARGET}_screened.csv
"""
import os, re, csv, json, subprocess, multiprocessing, shutil
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

BASE    = Path("/home/huangym/zjy/ppi_gen_project/core/denovo")
RESULTS = BASE / "results"
TMP     = BASE / "cs_tmp"
VINA    = "/home/huangym/anaconda/conda/envs/ppi_env/bin/vina"
DB_PATH = BASE / "ppi_target_db.json"

os.makedirs(TMP, exist_ok=True)

# ---- PAINS + structural alerts filter ----
_params = FilterCatalogParams()
_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
PAINS_CATALOG = FilterCatalog(_params)

def pains_flag(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "invalid"
    if PAINS_CATALOG.HasMatch(mol):
        entry = PAINS_CATALOG.GetFirstMatch(mol)
        return entry.GetDescription()
    return ""

# ---- ATYPE for ligand PDBQT ----
ATYPE = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
         'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD'}

def mol_to_pdbqt(smi, path):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
        if AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
            return None
    AllChem.MMFFOptimizeMolecule(mol)
    conf = mol.GetConformer()
    idx = 1
    lines = ['REMARK\nROOT\n']
    for i, a in enumerate(mol.GetAtoms()):
        if a.GetSymbol() == 'H':
            continue
        p = conf.GetAtomPosition(i)
        at = ATYPE.get(a.GetSymbol().upper(), 'C')
        lines.append(
            f'ATOM  {idx:5d}  {a.GetSymbol():<4s}LIG A   1    '
            f'{p.x:8.3f}{p.y:8.3f}{p.z:8.3f}  1.00  0.00    0.0000 {at}\n'
        )
        idx += 1
    lines.append('ENDROOT\nTORSDOF 0\n')
    with open(path, 'w') as f:
        f.writelines(lines)
    return path

def run_vina(rec_pdbqt, lig_pdbqt, center, box=(25,25,25)):
    cx, cy, cz = center
    sx, sy, sz = box
    try:
        r = subprocess.run([
            VINA,
            '--receptor', str(rec_pdbqt),
            '--ligand', str(lig_pdbqt),
            '--out', str(lig_pdbqt).replace('.pdbqt', '_out.pdbqt'),
            '--center_x', str(cx), '--center_y', str(cy), '--center_z', str(cz),
            '--size_x', str(sx), '--size_y', str(sy), '--size_z', str(sz),
            '--num_modes', '1', '--exhaustiveness', '4', '--cpu', '2',
        ], capture_output=True, text=True, timeout=90)
        for line in r.stdout.split('\n'):
            if re.match(r'\s+1\s+', line):
                try:
                    return float(line.split()[1])
                except:
                    pass
    except Exception as e:
        pass
    return None

# ---- Load target DB ----
with open(DB_PATH) as _f:
    db = json.load(_f)

# Off-target panel (diverse binding site types)
OFF_TARGETS = ['MDM2_TP53', 'BCL2_BAX', 'MENIN_MLL']

# Latest candidates CSV per target (prefer *_docked.csv if exists)
TARGET_CSV = {
    'MDM2_TP53':    RESULTS / 'MDM2_TP53_candidates.csv',
    'BCL2_BAX':     RESULTS / 'BCL2_BAX_candidates.csv',
    'KRAS_SOS1':    RESULTS / 'KRAS_SOS1_candidates.csv',
    'PD1_PDL1':     RESULTS / 'PD1_PDL1_candidates.csv',
    'MENIN_MLL':    RESULTS / 'MENIN_MLL_candidates.csv',
    'MYC_MAX':      RESULTS / 'MYC_MAX_candidates.csv',
    'VHL_HIF1A':    RESULTS / 'VHL_HIF1A_candidates.csv',
    'XIAP_SMAC':    RESULTS / 'XIAP_SMAC_candidates.csv',
    'IL2_IL2RA':    RESULTS / 'IL2_IL2RA_candidates.csv',
    'BRD4_HISTONE': RESULTS / 'BRD4_HISTONE_candidates.csv',
}

def process_target(target_name):
    csv_path = TARGET_CSV.get(target_name)
    if not csv_path or not csv_path.exists():
        print(f"[{target_name}] CSV not found, skip")
        return

    tinfo = db.get(target_name, {})
    rec_self  = tinfo.get('pdbqt_path')
    center_self = tinfo.get('pocket_center')
    box_self  = tinfo.get('box_size', [25,25,25])

    with open(csv_path) as _f:
        rows = list(csv.DictReader(_f))
    print(f"[{target_name}] {len(rows)} molecules")

    out_rows = []
    for i, row in enumerate(rows):
        smi = row['smiles']
        uid = f"{target_name}_{i:04d}"
        lig = TMP / f"{uid}.pdbqt"

        # PAINS filter
        pf = pains_flag(smi)
        row['pains_flag'] = pf

        # Embed once
        embedded = mol_to_pdbqt(smi, lig) is not None

        # Self docking (skip if already has valid vina_score)
        vina_self_val = row.get('vina_score', '')
        if vina_self_val and vina_self_val not in ('', 'N/A'):
            try:
                vina_self_val = float(vina_self_val)
            except:
                vina_self_val = None
        else:
            vina_self_val = None

        if vina_self_val is None and embedded and rec_self and center_self:
            vina_self_val = run_vina(rec_self, lig, center_self, box_self)

        row['vina_score'] = f'{vina_self_val:.3f}' if vina_self_val is not None else ''

        # Off-target docking
        off_scores = {}
        for off in OFF_TARGETS:
            if off == target_name:
                continue
            off_info = db.get(off, {})
            rec_off  = off_info.get('pdbqt_path')
            ctr_off  = off_info.get('pocket_center')
            box_off  = off_info.get('box_size', [25,25,25])
            if not rec_off or not ctr_off or not embedded:
                off_scores[off] = None
                continue
            lig_off = TMP / f"{uid}_{off}.pdbqt"
            shutil.copy(lig, lig_off)
            score = run_vina(rec_off, lig_off, ctr_off, box_off)
            off_scores[off] = score
            for _f in [lig_off,
                        TMP / f'{uid}_{off}_out.pdbqt']:
                try: _f.unlink()
                except OSError: pass

        for off in OFF_TARGETS:
            row[f'vina_{off}'] = f"{off_scores.get(off):.3f}" if off_scores.get(off) is not None else ''

        # Selectivity score
        valid_off = [v for v in off_scores.values() if v is not None and v < 0]
        if vina_self_val is not None and valid_off:
            sel = vina_self_val - sum(valid_off) / len(valid_off)
            row['selectivity'] = f'{sel:.3f}'
        else:
            row['selectivity'] = ''

        # Recompute composite with new vina if available
        try:
            mw  = float(row.get('mw', 0))
            qed = float(row.get('qed', 0))
            vs  = float(row['vina_score']) if row['vina_score'] else None
            if vs is not None:
                row['composite'] = f'{vs*0.6 - qed*3.0 + max(0,(mw-500)/100):.3f}'
        except:
            pass

        out_rows.append(row)
        if (i+1) % 10 == 0:
            print(f"  [{target_name}] {i+1}/{len(rows)} done")

    # Sort by composite
    def sort_key(r):
        try:
            return float(r.get('composite') or 99)
        except:
            return 99
    out_rows.sort(key=sort_key)

    # Write output
    out_path = RESULTS / f"{target_name}_screened.csv"
    all_fields = ['smiles','mw','logp','qed','vina_score','composite',
                  'pains_flag','selectivity'] + [f'vina_{o}' for o in OFF_TARGETS]
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(out_rows)

    # Summary
    docked   = sum(1 for r in out_rows if r.get('vina_score'))
    clean    = sum(1 for r in out_rows if not r.get('pains_flag'))
    sel_ok   = sum(1 for r in out_rows if r.get('selectivity') and float(r['selectivity']) < -1.0)
    print(f"  [{target_name}] done: {docked} docked, {clean}/{len(out_rows)} PAINS-clean, {sel_ok} selective")
    print(f"  -> {out_path}")

    # Print top 5
    top = [r for r in out_rows if r.get('vina_score') and not r.get('pains_flag')][:5]
    print(f"  Top 5 (PAINS-clean):")
    print(f"  {'#':>2} {'comp':>6} {'vina':>6} {'sel':>6} {'qed':>6} {'mw':>5}  SMILES")
    for j, r in enumerate(top, 1):
        comp = r.get('composite','')
        vina = r.get('vina_score','')
        sel  = r.get('selectivity','')
        print(f"  {j:2d} {comp:>6} {vina:>6} {sel:>6} {r['qed']:>6} {float(r['mw']):5.0f}  {r['smiles'][:40]}")

if __name__ == '__main__':
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(TARGET_CSV.keys())
    print(f"Processing {len(targets)} targets: {targets}")
    for t in targets:
        process_target(t)
    print("\nAll done.")
