"""
PPI界面提取器
输入: 两个蛋白的PDB文件（或序列→ColabFold预测）
输出: 界面热点特征矩阵 [N_hotspot, 4]
特征: [AA_type_onehot_20 + hydrophobic + hbond + charged]
"""
import numpy as np
import os
from Bio import PDB

# 氨基酸属性
AA_LIST = ['ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
           'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL']
AA2IDX  = {aa: i for i, aa in enumerate(AA_LIST)}

HYDROPHOBIC = {'ALA','VAL','LEU','ILE','MET','PHE','TRP','PRO'}
HBOND_DONOR = {'SER','THR','TYR','TRP','ASN','GLN','LYS','ARG','HIS'}
CHARGED_POS = {'ARG','LYS','HIS'}
CHARGED_NEG = {'ASP','GLU'}

def aa_features(resname):
    """返回4维氨基酸特征向量"""
    # 将3字母缩写标准化
    resname = resname.strip().upper()[:3]
    return np.array([
        AA2IDX.get(resname, 20) / 20.0,        # AA type (normalized)
        float(resname in HYDROPHOBIC),           # hydrophobic
        float(resname in HBOND_DONOR),           # H-bond donor
        float(resname in CHARGED_POS or resname in CHARGED_NEG),  # charged
    ], dtype=np.float32)

def get_ca_coords(chain):
    """获取链上所有残基的Cα坐标和残基名"""
    residues = []
    for res in chain.get_residues():
        if res.get_id()[0] != ' ': continue  # skip HETATMs
        if 'CA' not in res: continue
        ca = res['CA'].get_vector().get_array()
        residues.append((ca, res.get_resname()))
    return residues

def extract_interface(pdb_path, chain1='A', chain2='B', cutoff=8.0):
    """
    从PDB文件提取PPI界面残基特征
    Returns: numpy array [N_interface, 4]
    """
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('ppi', pdb_path)
    model = structure[0]

    # 获取两条链
    try:
        c1 = model[chain1]
        c2 = model[chain2]
    except KeyError as e:
        chains = list(model.get_chains())
        if len(chains) >= 2:
            c1, c2 = chains[0], chains[1]
        else:
            raise ValueError(f"Cannot find chains {chain1}/{chain2}: {e}")

    res1 = get_ca_coords(c1)
    res2 = get_ca_coords(c2)

    if not res1 or not res2:
        raise ValueError("Empty chain(s)")

    # 找界面残基（任意Cα距离 < cutoff）
    coords1 = np.array([r[0] for r in res1])
    coords2 = np.array([r[0] for r in res2])

    # 距离矩阵
    diff = coords1[:, None, :] - coords2[None, :, :]   # [N1, N2, 3]
    dists = np.sqrt((diff**2).sum(-1))                  # [N1, N2]

    interface_idx1 = np.where(dists.min(axis=1) < cutoff)[0]
    interface_idx2 = np.where(dists.min(axis=0) < cutoff)[0]

    # 合并两侧界面残基特征
    feats = []
    for idx in interface_idx1:
        _, resname = res1[idx]
        feats.append(aa_features(resname))
    for idx in interface_idx2:
        _, resname = res2[idx]
        feats.append(aa_features(resname))

    if not feats:
        # 如果没有找到界面，取两条链各最近5个残基
        for top_idx, res in [
            (np.argsort(dists.min(axis=1))[:5], res1),
            (np.argsort(dists.min(axis=0))[:5], res2),
        ]:
            for idx in top_idx:
                _, resname = res[idx]
                feats.append(aa_features(resname))

    return np.array(feats, dtype=np.float32)  # [N, 4]

def run_colabfold(seq1, seq2, output_dir, colabfold_bin=None):
    """
    运行ColabFold预测PPI复合物结构
    输入: 两个蛋白序列
    输出: PDB文件路径
    """
    import subprocess
    if colabfold_bin is None:
        colabfold_bin = '/home/huangym/zjy/localcolabfold/colabfold-conda/bin/colabfold_batch'

    os.makedirs(output_dir, exist_ok=True)
    fasta_path = os.path.join(output_dir, 'input.fasta')

    # 写FASTA（用:分隔两条链）
    with open(fasta_path, 'w') as f:
        f.write(f'>complex\n{seq1}:{seq2}\n')

    cmd = [colabfold_bin, fasta_path, output_dir,
           '--num-recycle', '3', '--num-models', '1']
    print(f"Running ColabFold: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

    if result.returncode != 0:
        raise RuntimeError(f"ColabFold failed: {result.stderr[-500:]}")

    # 找输出PDB
    pdbs = [f for f in os.listdir(output_dir) if f.endswith('_relaxed_rank_001_model_1.pdb')
            or f.endswith('rank_1.pdb') or f.endswith('.pdb')]
    if not pdbs:
        raise FileNotFoundError(f"No PDB found in {output_dir}")

    return os.path.join(output_dir, sorted(pdbs)[0])


class PocketEncoder(nn.Module if False else object):
    """轻量口袋编码器: [N, 4] → [256]"""
    pass

# 如有PyTorch，提供可训练版
try:
    import torch
    import torch.nn as nn

    class PocketEncoder(nn.Module):
        def __init__(self, feat_dim=4, hidden=128, out_dim=256):
            super().__init__()
            self.fc1 = nn.Linear(feat_dim, hidden)
            self.fc2 = nn.Linear(hidden, hidden)
            self.out = nn.Linear(hidden, out_dim)
            self.norm = nn.LayerNorm(out_dim)

        def forward(self, x):
            """x: [N, 4] or [B, N, 4]"""
            if x.dim() == 2:
                x = x.unsqueeze(0)          # [1, N, 4]
            h = torch.relu(self.fc1(x))     # [B, N, H]
            h = torch.relu(self.fc2(h))     # [B, N, H]
            h = h.mean(dim=1)               # [B, H] (mean pooling over residues)
            return self.norm(self.out(h))   # [B, out_dim]

except ImportError:
    pass

if __name__ == '__main__':
    # 测试：使用已有的P-L数据
    import glob
    pdbs = glob.glob('/home/huangym/zjy/ppi_gen_project/core/diffusion_project/data/P-L/*/*_pocket.pdb')[:3]
    for pdb in pdbs:
        try:
            feats = extract_interface(pdb, chain1='A', chain2='B')
            print(f"{os.path.basename(pdb)}: {feats.shape} interface residues")
        except Exception as e:
            print(f"Failed {pdb}: {e}")
