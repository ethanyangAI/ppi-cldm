"""
从ChEMBL收集10个PPI靶点的已知阻断剂
每个靶点取 pChEMBL >= 6 (IC50 <= 1uM) 的活性分子
"""
import json, time, urllib.request, urllib.parse, os
from rdkit import Chem
from rdkit.Chem import Descriptors, QED

BASE_DIR = '/home/huangym/zjy/ppi_gen_project'
OUT_PATH = f'{BASE_DIR}/core/denovo/benchmark/known_inhibitors.json'
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# 每个靶点对应的ChEMBL ID（经过验证）
PPI_CHEMBL = {
    'MDM2_TP53'    : ['CHEMBL3959'],           # MDM2
    'BCL2_BAX'     : ['CHEMBL821','CHEMBL4885'],# BCL2 + BCL-XL
    'BRD4_HISTONE' : ['CHEMBL1163125'],         # BRD4 BD1
    'KRAS_SOS1'    : ['CHEMBL4523582'],         # SOS1
    'PD1_PDL1'     : ['CHEMBL4523134'],         # PD-L1
    'MENIN_MLL'    : ['CHEMBL2093872'],         # Menin
    'MYC_MAX'      : ['CHEMBL1293296'],         # MYC
    'VHL_HIF1A'    : ['CHEMBL3707'],            # VHL
    'XIAP_SMAC'    : ['CHEMBL2093868'],         # XIAP BIR3
    'IL2_IL2RA'    : ['CHEMBL1293272'],         # IL-2
}

def fetch_chembl_actives(target_id, limit=300):
    url = (f'https://www.ebi.ac.uk/chembl/api/data/activity'
           f'?format=json&target_chembl_id={target_id}'
           f'&pchembl_value__gte=6&limit={limit}'
           f'&standard_type__in=IC50,Ki,Kd,EC50')
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read())
        acts = data.get('activities', [])
        smiles = []
        for a in acts:
            s = a.get('canonical_smiles','')
            if s and Chem.MolFromSmiles(s):
                smiles.append({
                    'smiles'   : Chem.MolToSmiles(Chem.MolFromSmiles(s)),
                    'pchembl'  : a.get('pchembl_value'),
                    'type'     : a.get('standard_type'),
                    'chembl_id': a.get('molecule_chembl_id'),
                })
        return smiles
    except Exception as e:
        print(f'  Error {target_id}: {e}')
        return []

result = {}
for target_name, chembl_ids in PPI_CHEMBL.items():
    print(f'\n[{target_name}]')
    all_mols = {}
    for cid in chembl_ids:
        mols = fetch_chembl_actives(cid)
        for m in mols:
            all_mols[m['smiles']] = m  # dedup by SMILES
        print(f'  {cid}: {len(mols)} actives')
        time.sleep(0.5)

    # 计算属性
    enriched = []
    for smi, info in all_mols.items():
        mol = Chem.MolFromSmiles(smi)
        if mol is None: continue
        enriched.append({
            **info,
            'mw'  : round(Descriptors.MolWt(mol), 1),
            'logp': round(Descriptors.MolLogP(mol), 2),
            'qed' : round(QED.qed(mol), 3),
        })

    result[target_name] = enriched
    print(f'  合计: {len(enriched)} unique活性分子')

with open(OUT_PATH, 'w') as f:
    json.dump(result, f, indent=2)

total = sum(len(v) for v in result.values())
print(f'\n{"="*50}')
print(f'总计: {total} 个已知PPI阻断剂')
for k,v in result.items():
    print(f'  {k:<20}: {len(v):>3} 个')
print(f'保存 → {OUT_PATH}')
