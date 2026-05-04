"""
Benchmark分析：已知PPI阻断剂 vs 生成分子
指标:
  1. Vina分数分布对比（每个靶点）
  2. Tanimoto相似度（生成分子与已知阻断剂）
  3. QED/MW/LogP分布对比
  4. MOSES指标: validity/uniqueness/novelty
  5. Internal diversity (IntDiv)
"""
import json, os, csv, re, subprocess
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, QED, DataStructs
from rdkit.Chem import rdMolDescriptors

BASE_DIR   = '/home/huangym/zjy/ppi_gen_project'
KNOWN_PATH = f'{BASE_DIR}/core/denovo/benchmark/known_inhibitors.json'
DB_PATH    = f'{BASE_DIR}/core/denovo/ppi_target_db.json'
RESULTS    = f'{BASE_DIR}/core/denovo/results'
BM_OUT     = f'{BASE_DIR}/core/denovo/benchmark/benchmark_results.json'
VINA       = '/home/huangym/anaconda/conda/envs/ppi_env/bin/vina'
WORK_DIR   = '/tmp/bm_dock'; os.makedirs(WORK_DIR, exist_ok=True)
ATYPE      = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
              'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD'}

known_db = json.load(open(KNOWN_PATH))
target_db = json.load(open(DB_PATH))

def mol_to_pdbqt(smi, path):
    mol = Chem.MolFromSmiles(smi)
    if mol is None: return None
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, AllChem.ETKDGv3()) != 0:
        if AllChem.EmbedMolecule(mol, randomSeed=42) != 0: return None
    AllChem.MMFFOptimizeMolecule(mol)
    conf = mol.GetConformer()
    idx=1; lines=['REMARK\nROOT\n']
    for i,a in enumerate(mol.GetAtoms()):
        if a.GetSymbol()=='H': continue
        p = conf.GetAtomPosition(i)
        at = ATYPE.get(a.GetSymbol().upper(),'C')
        lines.append(f'ATOM  {idx:5d}  {a.GetSymbol():<4s}LIG A   1    {p.x:8.3f}{p.y:8.3f}{p.z:8.3f}  1.00  0.00    0.0000 {at}\n')
        idx+=1
    lines.append('ENDROOT\nTORSDOF 0\n')
    open(path,'w').writelines(lines); return path

def run_vina(receptor, lig, out, center, box=(25,25,25)):
    import signal
    try:
        r = subprocess.run([VINA,'--receptor',receptor,'--ligand',lig,'--out',out,
            '--center_x',str(center[0]),'--center_y',str(center[1]),'--center_z',str(center[2]),
            '--size_x',str(box[0]),'--size_y',str(box[1]),'--size_z',str(box[2]),
            '--num_modes','1','--exhaustiveness','4','--cpu','2'],
            capture_output=True,text=True,timeout=25)
        for line in r.stdout.split('\n'):
            if re.match(r'\s+1\s+',line):
                try: return float(line.split()[1])
                except: pass
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None
    return None

def morgan_fp(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None: return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, 2048)

def tanimoto_matrix(fps_a, fps_b):
    """fps_a vs fps_b 的平均最大Tanimoto"""
    scores = []
    for fa in fps_a:
        sims = DataStructs.BulkTanimotoSimilarity(fa, fps_b)
        scores.append(max(sims) if sims else 0)
    return np.mean(scores)

def internal_diversity(smiles_list):
    fps = [morgan_fp(s) for s in smiles_list if morgan_fp(s)]
    if len(fps) < 2: return 0.0
    sims = []
    for i in range(min(200, len(fps))):
        for j in range(i+1, min(200, len(fps))):
            sims.append(DataStructs.TanimotoSimilarity(fps[i], fps[j]))
    return round(1 - np.mean(sims), 4)

def novelty(gen_smiles, ref_smiles_set):
    novel = [s for s in gen_smiles if s not in ref_smiles_set]
    return len(novel) / len(gen_smiles) if gen_smiles else 0

all_results = {}

for target_name, target_info in target_db.items():
    print(f'\n{"="*55}')
    print(f'[{target_name}]')

    known = known_db.get(target_name, [])
    if len(known) < 5:
        print(f'  已知阻断剂不足({len(known)}个)，跳过')
        continue

    # 读取生成分子
    gen_csv = os.path.join(RESULTS, f'{target_name}_candidates.csv')
    if not os.path.exists(gen_csv):
        print(f'  无生成结果，跳过 ({gen_csv})')
        continue

    gen_mols = []
    with open(gen_csv) as f:
        for row in csv.DictReader(f):
            if row.get('smiles'): gen_mols.append(row['smiles'])

    print(f'  已知阻断剂: {len(known)} 个')
    print(f'  生成分子:   {len(gen_mols)} 个')

    receptor   = target_info.get('pdbqt_path','')
    center     = target_info.get('pocket_center')
    has_vina   = bool(receptor and os.path.exists(receptor) and center)

    # ── MOSES指标 ──────────────────────────────────────────────────────
    known_smi_set = {m['smiles'] for m in known}
    gen_valid     = [s for s in gen_mols if Chem.MolFromSmiles(s)]
    gen_unique    = list(set(gen_valid))
    validity  = len(gen_valid)  / len(gen_mols)  if gen_mols  else 0
    uniqueness= len(gen_unique) / len(gen_valid) if gen_valid else 0
    nov       = novelty(gen_unique, known_smi_set)

    print(f'  Validity:   {validity:.3f}')
    print(f'  Uniqueness: {uniqueness:.3f}')
    print(f'  Novelty:    {nov:.3f}')

    # ── 多样性 ──────────────────────────────────────────────────────────
    intdiv_gen   = internal_diversity(gen_unique[:200])
    intdiv_known = internal_diversity([m['smiles'] for m in known[:200]])
    print(f'  IntDiv(gen):   {intdiv_gen:.4f}')
    print(f'  IntDiv(known): {intdiv_known:.4f}')

    # ── Tanimoto vs 已知阻断剂 ──────────────────────────────────────────
    fps_gen   = [fp for s in gen_unique[:100]  if (fp:=morgan_fp(s))]
    fps_known = [fp for m in known[:200]        if (fp:=morgan_fp(m['smiles']))]
    tan_score = tanimoto_matrix(fps_gen, fps_known) if fps_gen and fps_known else 0
    print(f'  Tanimoto(gen→known): {tan_score:.4f}  (理想: 0.2-0.5)')

    # ── 属性分布 ────────────────────────────────────────────────────────
    gen_props   = [(Descriptors.MolWt(m), Descriptors.MolLogP(m), QED.qed(m))
                   for s in gen_unique if (m:=Chem.MolFromSmiles(s))]
    known_props = [(Descriptors.MolWt(Chem.MolFromSmiles(m['smiles'])),
                    Descriptors.MolLogP(Chem.MolFromSmiles(m['smiles'])),
                    QED.qed(Chem.MolFromSmiles(m['smiles'])))
                   for m in known if Chem.MolFromSmiles(m['smiles'])]

    g_mw  = np.mean([p[0] for p in gen_props])
    k_mw  = np.mean([p[0] for p in known_props])
    g_qed = np.mean([p[2] for p in gen_props])
    k_qed = np.mean([p[2] for p in known_props])
    print(f'  MW:  gen={g_mw:.0f}  known={k_mw:.0f}')
    print(f'  QED: gen={g_qed:.3f} known={k_qed:.3f}')

    # ── Vina分数对比（取前50个已知阻断剂对接） ──────────────────────────
    vina_known, vina_gen = [], []
    if has_vina:
        print(f'  Vina对接已知阻断剂(前50个)...')
        for i, m in enumerate(known[:50]):
            lig = os.path.join(WORK_DIR, f'{target_name}_known_{i}.pdbqt')
            out = os.path.join(WORK_DIR, f'{target_name}_known_{i}_out.pdbqt')
            if mol_to_pdbqt(m['smiles'], lig):
                s = run_vina(receptor, lig, out, center)
                if s: vina_known.append(s)

        # 生成分子的Vina分数（从已有结果读取）
        with open(gen_csv) as f:
            for row in csv.DictReader(f):
                if row.get('vina_score'):
                    try: vina_gen.append(float(row['vina_score']))
                    except: pass

        if vina_known and vina_gen:
            print(f'  Vina known: mean={np.mean(vina_known):.2f} min={np.min(vina_known):.2f}')
            print(f'  Vina gen:   mean={np.mean(vina_gen):.2f}  min={np.min(vina_gen):.2f}')

    all_results[target_name] = {
        'n_known'    : len(known),
        'n_gen'      : len(gen_mols),
        'validity'   : round(validity,4),
        'uniqueness' : round(uniqueness,4),
        'novelty'    : round(nov,4),
        'intdiv_gen' : intdiv_gen,
        'intdiv_known': intdiv_known,
        'tanimoto'   : round(tan_score,4),
        'mw_gen'     : round(g_mw,1),
        'mw_known'   : round(k_mw,1),
        'qed_gen'    : round(g_qed,3),
        'qed_known'  : round(k_qed,3),
        'vina_known_mean': round(np.mean(vina_known),2) if vina_known else None,
        'vina_gen_mean'  : round(np.mean(vina_gen),2)   if vina_gen   else None,
        'vina_known_min' : round(np.min(vina_known),2)  if vina_known else None,
        'vina_gen_min'   : round(np.min(vina_gen),2)    if vina_gen   else None,
    }

json.dump(all_results, open(BM_OUT,'w'), indent=2)

# 汇总打印
print(f'\n{"="*70}')
print(f'{"靶点":<20} {"Valid":>6} {"Novel":>6} {"Tan":>6} {"QEDg":>6} {"QEDk":>6} {"Vg":>6} {"Vk":>6}')
print('─'*70)
for t,r in all_results.items():
    vg = f'{r["vina_gen_mean"]:6.1f}'   if r['vina_gen_mean']   else '   N/A'
    vk = f'{r["vina_known_mean"]:6.1f}' if r['vina_known_mean'] else '   N/A'
    print(f'{t:<20} {r["validity"]:6.3f} {r["novelty"]:6.3f} {r["tanimoto"]:6.4f} '
          f'{r["qed_gen"]:6.3f} {r["qed_known"]:6.3f} {vg} {vk}')
print(f'\n保存 → {BM_OUT}')
