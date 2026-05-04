"""
修正版：用正确的ChEMBL ID补充缺失靶点数据
"""
import json, time, urllib.request, os
from rdkit import Chem
from rdkit.Chem import Descriptors, QED

BASE_DIR = '/home/huangym/zjy/ppi_gen_project'
OUT_PATH = f'{BASE_DIR}/core/denovo/benchmark/known_inhibitors.json'
db = json.load(open(OUT_PATH))

# 补充/修正的靶点ChEMBL ID
FIXES = {
    'BCL2_BAX'  : ['CHEMBL821','CHEMBL4885','CHEMBL3108643'],  # BCL2+BCLXL+MCL1
    'PD1_PDL1'  : ['CHEMBL4523134','CHEMBL3592','CHEMBL4895'],  # PD-L1+PD-1
    'MYC_MAX'   : ['CHEMBL1293296','CHEMBL2176771'],
    'VHL_HIF1A' : ['CHEMBL3707','CHEMBL4439'],
    'IL2_IL2RA' : ['CHEMBL1293272','CHEMBL260'],               # IL-2Ra
}

def fetch(target_id, limit=400):
    url = (f'https://www.ebi.ac.uk/chembl/api/data/activity'
           f'?format=json&target_chembl_id={target_id}'
           f'&pchembl_value__gte=5.5&limit={limit}'
           f'&standard_type__in=IC50,Ki,Kd,EC50,Inhibition')
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read())
        mols = []
        for a in data.get('activities', []):
            s = a.get('canonical_smiles','')
            mol = Chem.MolFromSmiles(s) if s else None
            if mol:
                mols.append({
                    'smiles'   : Chem.MolToSmiles(mol),
                    'pchembl'  : a.get('pchembl_value'),
                    'type'     : a.get('standard_type'),
                    'chembl_id': a.get('molecule_chembl_id'),
                })
        return mols
    except Exception as e:
        print(f'  Error {target_id}: {e}')
        return []

for target_name, chembl_ids in FIXES.items():
    print(f'\n[{target_name}] 当前: {len(db.get(target_name,[]))} 个')
    all_mols = {m['smiles']: m for m in db.get(target_name, [])}
    for cid in chembl_ids:
        mols = fetch(cid)
        for m in mols:
            all_mols[m['smiles']] = m
        print(f'  {cid}: {len(mols)} actives')
        time.sleep(0.5)

    enriched = []
    for smi, info in all_mols.items():
        mol = Chem.MolFromSmiles(smi)
        if mol:
            enriched.append({**info,
                'mw': round(Descriptors.MolWt(mol),1),
                'logp': round(Descriptors.MolLogP(mol),2),
                'qed': round(QED.qed(mol),3)})
    db[target_name] = enriched
    print(f'  → {len(enriched)} unique')

json.dump(db, open(OUT_PATH,'w'), indent=2)
total = sum(len(v) for v in db.values())
print(f'\n总计: {total} 个')
for k,v in db.items():
    print(f'  {k:<20}: {len(v):>4} 个')
