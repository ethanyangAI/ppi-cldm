"""
counter_screen_module.py
可复用的反筛选模块，供 ppi_pipeline_universal.py 导入。

主要 API:
    apply_pains(results)          -> 给 results 列表每行加 pains_flag 字段
    run_counter_screen(results,   -> 给 results 加 selectivity / vina_<key> 字段
        target_name,
        offtarget_db_path,
        top_n=None,
        n_workers=4)
"""
import os, re, csv, json, shutil, subprocess, tempfile
from pathlib import Path
from multiprocessing import Pool
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

# ── PAINS + Brenk catalog ──────────────────────────────────────────────────
_params = FilterCatalogParams()
_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
_CATALOG = FilterCatalog(_params)

def _pains_flag(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "invalid_smiles"
    if _CATALOG.HasMatch(mol):
        return _CATALOG.GetFirstMatch(mol).GetDescription()
    return ""

def apply_pains(results: list) -> list:
    """In-place: adds 'pains_flag' to every row. Returns results."""
    for r in results:
        r['pains_flag'] = _pains_flag(r.get('smiles', ''))
    return results

# ── PDBQT helpers ─────────────────────────────────────────────────────────
_ATYPE = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
          'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD'}

VINA_BIN = "/home/huangym/anaconda/conda/envs/ppi_env/bin/vina"

def _mol_to_pdbqt(smiles: str, path: str) -> bool:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
        if AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
            return False
    AllChem.MMFFOptimizeMolecule(mol)
    conf = mol.GetConformer()
    idx = 1
    lines = ['REMARK\nROOT\n']
    for i, a in enumerate(mol.GetAtoms()):
        if a.GetSymbol() == 'H':
            continue
        p = conf.GetAtomPosition(i)
        at = _ATYPE.get(a.GetSymbol().upper(), 'C')
        lines.append(f'ATOM  {idx:5d}  {a.GetSymbol():<4s}LIG A   1    '
                     f'{p.x:8.3f}{p.y:8.3f}{p.z:8.3f}  1.00  0.00    0.0000 {at}\n')
        idx += 1
    lines.append('ENDROOT\nTORSDOF 0\n')
    with open(path, 'w') as f:
        f.writelines(lines)
    return True

def _vina_score(rec: str, lig: str, center: list, box: list) -> float | None:
    cx, cy, cz = center
    sx, sy, sz = box
    out = lig.replace('.pdbqt', '_out.pdbqt')
    try:
        r = subprocess.run(
            [VINA_BIN,
             '--receptor', rec, '--ligand', lig, '--out', out,
             '--center_x', str(cx), '--center_y', str(cy), '--center_z', str(cz),
             '--size_x', str(sx), '--size_y', str(sy), '--size_z', str(sz),
             '--num_modes', '1', '--exhaustiveness', '4', '--cpu', '2'],
            capture_output=True, text=True, timeout=90)
        for line in r.stdout.split('\n'):
            if re.match(r'\s+1\s+', line):
                try:
                    return float(line.split()[1])
                except:
                    pass
    except Exception:
        pass
    return None

# ── Worker function (runs in subprocess pool) ─────────────────────────────
def _dock_one_offtarget(args):
    """Pool worker: dock one ligand PDBQT against one off-target."""
    lig_pdbqt, off_name, rec, center, box = args
    lig_copy = lig_pdbqt.replace('.pdbqt', f'_{off_name[:20]}.pdbqt')
    shutil.copy(lig_pdbqt, lig_copy)
    try:
        score = _vina_score(rec, lig_copy, center, box)
    finally:
        for f in [lig_copy, lig_copy.replace('.pdbqt', '_out.pdbqt')]:
            try:
                os.remove(f)
            except OSError:
                pass
    return off_name, score

# ── Key off-targets always reported as individual columns ─────────────────
KEY_OFFTARGETS = ['CYP3A4', 'hERG', 'HSA', 'CDK2', 'Thrombin',
                  'EGFR', 'AChE', 'PARP1', 'BRD4', 'HDAC2']

# ── Main API ───────────────────────────────────────────────────────────────
def run_counter_screen(
    results: list,
    target_name: str,
    offtarget_db_path: str,
    ppi_db_path: str | None = None,
    top_n: int | None = None,
    n_workers: int = 4,
    tmp_dir: str | None = None,
) -> list:
    """
    Dock top-N molecules against the full off-target panel.
    Adds to each row:
      selectivity       = vina_self - mean(vina_off_targets)   (lower = more selective)
      n_offtargets      = number of off-targets successfully docked
      mean_off_vina     = mean off-target Vina score
      vina_<KEY>        = individual score for each key off-target
    Returns results (modified in-place).
    """
    if not os.path.exists(offtarget_db_path):
        print(f'[CS] offtarget_db not found: {offtarget_db_path}, skipping counter-screen')
        return results

    off_db = json.load(open(offtarget_db_path))

    # Optionally merge PPI DB as additional off-targets
    if ppi_db_path and os.path.exists(ppi_db_path):
        ppi_db = json.load(open(ppi_db_path))
        for k, v in ppi_db.items():
            if k != target_name:
                off_db[f'PPI_{k}'] = v

    # Filter to targets with valid receptor files
    valid_off = {k: v for k, v in off_db.items()
                 if v.get('pdbqt_path') and os.path.exists(v['pdbqt_path'])
                 and v.get('pocket_center')}
    print(f'[CS] Off-target panel: {len(valid_off)} receptors')

    # Select molecules to screen
    candidates = results if top_n is None else results[:top_n]
    skip_set = set(range(len(candidates), len(results)))  # mark rest as not screened

    # Temp dir for ligand PDBQTs
    owns_tmp = tmp_dir is None
    if owns_tmp:
        tmp_dir = tempfile.mkdtemp(prefix='cs_')

    try:
        with Pool(processes=n_workers) as pool:
          for mol_idx, row in enumerate(candidates):
            smi = row.get('smiles', '')
            if not smi:
                continue

            lig = os.path.join(tmp_dir, f'cs_mol_{mol_idx:04d}.pdbqt')
            if not _mol_to_pdbqt(smi, lig):
                print(f'  [CS] mol {mol_idx} embed failed')
                continue

            # Build task list
            tasks = [
                (lig,
                 off_name,
                 v['pdbqt_path'],
                 v['pocket_center'],
                 v.get('box_size', [25, 25, 25]))
                for off_name, v in valid_off.items()
            ]

            scores = dict(pool.map(_dock_one_offtarget, tasks))

            valid_scores = {k: v for k, v in scores.items() if v is not None and v < 0}
            n_ok = len(valid_scores)
            mean_off = sum(valid_scores.values()) / n_ok if n_ok else None

            vina_self = row.get('vina_score')
            if isinstance(vina_self, str):
                try:
                    vina_self = float(vina_self)
                except:
                    vina_self = None

            sel = (vina_self - mean_off) if (vina_self is not None and mean_off is not None) else None

            row['selectivity']   = round(sel, 3) if sel is not None else None
            row['n_offtargets']  = n_ok
            row['mean_off_vina'] = round(mean_off, 3) if mean_off is not None else None

            for key in KEY_OFFTARGETS:
                row[f'vina_{key}'] = round(scores.get(key), 3) if scores.get(key) is not None else None

            tag = f'sel={sel:.2f}' if sel is not None else 'sel=N/A'
            print(f'  [CS {mol_idx+1}/{len(candidates)}] {tag}  n_off={n_ok}  {smi[:40]}')

    finally:
        if owns_tmp:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return results


def extra_csv_fields() -> list:
    """Returns the list of extra column names added by this module."""
    return (['pains_flag', 'selectivity', 'n_offtargets', 'mean_off_vina']
            + [f'vina_{k}' for k in KEY_OFFTARGETS])
