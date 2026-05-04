"""
PPI靶点数据库 + 自动PDB下载 + 口袋中心计算
支持: MDM2-TP53, BCL2-BAX, BRD4-Histone, KRAS-SOS1,
      PD1-PDL1, Menin-MLL, MYC-MAX, VHL-HIF1a, XIAP-SMAC, IL2-IL2Ra
"""
import os, json, urllib.request
import numpy as np
from Bio import PDB

BASE_DIR = '/home/huangym/zjy/ppi_gen_project'
PDB_DIR  = f'{BASE_DIR}/structures/ppi_targets'
DB_PATH  = f'{BASE_DIR}/core/denovo/ppi_target_db.json'
os.makedirs(PDB_DIR, exist_ok=True)

# ── 靶点数据库 ──────────────────────────────────────────────────────────────
TARGET_DB = {
    'MDM2_TP53': {
        'pdb': '1ycr', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '癌症（p53通路）',
        'description': 'MDM2与p53转录激活域结合，抑制p53功能',
        'known_drugs': ['Nutlin-3a', 'RG7112', 'AMG232'],
    },
    'BCL2_BAX': {
        'pdb': '2xa0', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '癌症/凋亡',
        'description': 'BCL2抑制BAX介导的细胞凋亡',
        'known_drugs': ['ABT-199 (Venetoclax)', 'ABT-737'],
    },
    'BRD4_HISTONE': {
        'pdb': '3oni', 'chain_receptor': 'A', 'chain_ligand': 'A',
        'disease': '癌症/炎症',
        'description': 'BRD4溴结构域识别乙酰化组蛋白',
        'known_drugs': ['JQ1', 'I-BET762', 'OTX015'],
        'box_size': [20, 20, 20],
    },
    'KRAS_SOS1': {
        'pdb': '6epn', 'chain_receptor': 'R', 'chain_ligand': 'S',
        'disease': '肺癌/胰腺癌',
        'description': 'SOS1是KRAS的鸟嘌呤核苷酸交换因子',
        'known_drugs': ['BI-3406', 'BAY-293'],
    },
    'PD1_PDL1': {
        'pdb': '4zqk', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '免疫治疗',
        'description': 'PD-1/PD-L1检查点抑制',
        'known_drugs': ['CA-170', 'BMS-202'],
    },
    'MENIN_MLL': {
        'pdb': '4gq6', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '白血病',
        'description': 'Menin-MLL融合蛋白驱动白血病',
        'known_drugs': ['MI-2', 'VTP-50469', 'Revumenib'],
    },
    'MYC_MAX': {
        'pdb': '1nkp', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '多种癌症',
        'description': 'MYC-MAX二聚化驱动基因转录',
        'known_drugs': ['10058-F4', 'Omomyc'],
    },
    'VHL_HIF1A': {
        'pdb': '1lm8', 'chain_receptor': 'B', 'chain_ligand': 'C',
        'disease': '肾癌/缺氧',
        'description': 'VHL识别HIF1α进行泛素化降解',
        'known_drugs': ['VH032', 'PT2977 (Belzutifan)'],
    },
    'XIAP_SMAC': {
        'pdb': '1g73', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '癌症/凋亡抵抗',
        'description': 'XIAP抑制caspase，Smac拮抗XIAP',
        'known_drugs': ['LCL161', 'Birinapant'],
    },
    'IL2_IL2RA': {
        'pdb': '1z92', 'chain_receptor': 'A', 'chain_ligand': 'B',
        'disease': '自身免疫/炎症',
        'description': 'IL-2与IL-2Rα结合激活T细胞',
        'known_drugs': ['SP4206'],
    },
}

def download_pdb(pdb_id, out_dir):
    """从RCSB下载PDB文件"""
    path = os.path.join(out_dir, f'{pdb_id}.pdb')
    if os.path.exists(path):
        print(f'  Already exists: {pdb_id}.pdb')
        return path
    url = f'https://files.rcsb.org/download/{pdb_id.upper()}.pdb'
    try:
        urllib.request.urlretrieve(url, path)
        print(f'  Downloaded: {pdb_id}.pdb')
        return path
    except Exception as e:
        print(f'  Failed {pdb_id}: {e}')
        return None

def calc_pocket_center(pdb_path, chain_ligand):
    """计算配体链的质心作为口袋中心"""
    parser = PDB.PDBParser(QUIET=True)
    struct = parser.get_structure('p', pdb_path)[0]
    coords = []
    try:
        chain = struct[chain_ligand]
        for res in chain.get_residues():
            if res.get_id()[0] != ' ': continue
            for atom in res.get_atoms():
                coords.append(atom.get_vector().get_array())
    except KeyError:
        # 尝试所有链取非A链
        for chain in struct.get_chains():
            if chain.get_id() != 'A':
                for res in chain.get_residues():
                    if res.get_id()[0] != ' ': continue
                    for atom in res.get_atoms():
                        coords.append(atom.get_vector().get_array())
                break
    if not coords:
        return None
    center = np.array(coords).mean(axis=0)
    return [round(float(x), 2) for x in center]

def prepare_receptor_pdbqt(pdb_path, chain_receptor, out_path):
    """提取受体链并转PDBQT"""
    ATYPE = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
             'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD'}
    def pdb2pdbqt(line):
        elem = line[76:78].strip().upper() if len(line)>76 else line[12:14].strip().lstrip('0123456789').upper()
        at = ATYPE.get(elem, 'C')
        return f'{line[:54].ljust(54)}{float(line[54:60].strip() or 1):6.2f}{float(line[60:66].strip() or 0):6.2f}    0.0000 {at}\n'

    lines = []
    with open(pdb_path) as f:
        for line in f:
            if (line.startswith('ATOM') and len(line)>21
                    and line[21]==chain_receptor
                    and line[17:20].strip() not in ('HOH','WAT')):
                lines.append(pdb2pdbqt(line))
    if lines:
        with open(out_path, 'w') as fh:
            fh.writelines(lines)
        return out_path
    return None


if __name__ == '__main__':

    # ── 主流程 ──────────────────────────────────────────────────────────────────
    print('='*60)
    print('建立PPI靶点数据库')
    print('='*60)

    db_result = {}
    for name, info in TARGET_DB.items():
        print(f'\n[{name}] {info["disease"]}')
        pdb_id   = info['pdb']
        chain_r  = info['chain_receptor']
        chain_l  = info['chain_ligand']

        # 下载PDB
        pdb_path = download_pdb(pdb_id, PDB_DIR)
        if pdb_path is None:
            print(f'  SKIP: 下载失败')
            continue

        # 计算口袋中心
        center = calc_pocket_center(pdb_path, chain_l)
        if center is None:
            print(f'  SKIP: 无法计算口袋中心')
            continue
        print(f'  口袋中心: {center}')

        # 准备受体PDBQT
        pdbqt_path = os.path.join(PDB_DIR, f'{name}_receptor.pdbqt')
        result = prepare_receptor_pdbqt(pdb_path, chain_r, pdbqt_path)
        print(f'  受体PDBQT: {"OK" if result else "FAILED"}')

        db_result[name] = {
            **info,
            'pdb_path'   : pdb_path,
            'pdbqt_path' : pdbqt_path if result else None,
            'pocket_center': center,
            'box_size'   : info.get('box_size', [25, 25, 25]),
        }

    # 保存数据库
    with open(DB_PATH, 'w') as f:
        json.dump(db_result, f, indent=2, ensure_ascii=False)

    print(f'\n{"="*60}')
    print(f'完成! {len(db_result)}/{len(TARGET_DB)} 个靶点')
    print(f'数据库: {DB_PATH}')
    print(f'靶点列表: {list(db_result.keys())}')
