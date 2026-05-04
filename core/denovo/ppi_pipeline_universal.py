"""
通用PPI抑制剂生成Pipeline v2
用法:
  python ppi_pipeline_universal.py --target MDM2_TP53 --n 100
  python ppi_pipeline_universal.py --target BCL2_BAX --n 100
  python ppi_pipeline_universal.py --list
  python ppi_pipeline_universal.py --target MDM2_TP53 --vae vae_ppi.pt --n 100
"""
import sys, os, json, argparse, re, csv, subprocess
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import torch
import numpy as np
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors, QED, Lipinski, rdMolDescriptors
from rdkit.Chem.Descriptors import MolWt as _MolWt, MolLogP as _MolLogP, TPSA as _TPSA
from rdkit.Chem.Crippen import MolLogP as _MolLogP2
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')
try:
    from counter_screen_module import apply_pains, run_counter_screen, extra_csv_fields
    _CS_AVAILABLE = True
except ImportError:
    _CS_AVAILABLE = False

_OFF_DB_PATH = os.path.join(os.path.dirname(__file__), 'offtarget_db.json')
_PPI_DB_PATH = os.path.join(os.path.dirname(__file__), 'ppi_target_db.json')
try:
    from rdkit.Chem.FilterMatchers import PAINSFilter
    _PAINS = PAINSFilter()
except Exception:
    _PAINS = None

BASE_DIR = '/home/huangym/zjy/ppi_gen_project'
sys.path.insert(0, f'{BASE_DIR}/core/denovo')

from gru_vae import GRUVAE, I2CHAR, SOS, EOS, PAD, VOCAB_SIZE
from latent_diffusion import DenoiseMLP, DDPM
from interface_extractor import PocketEncoder, extract_interface
from target_db_validator import load_and_validate_target_db, validate_target_entry
from results_manifest import build_run_id, build_output_paths, summarize_results, write_manifest
from complex_builder import build_modeled_complex, detect_complex_backend

# ── 通用PDB获取函数 ────────────────────────────────────────────────────────
def fetch_pdb(pdb_id, out_path):
    """从RCSB下载PDB文件"""
    import urllib.request
    url = f'https://files.rcsb.org/download/{pdb_id.upper()}.pdb'
    try:
        urllib.request.urlretrieve(url, out_path)
        print(f'Downloaded {pdb_id} -> {out_path}')
        return out_path
    except Exception as e:
        raise RuntimeError(f'Failed to download {pdb_id}: {e}')

def search_pdb_for_complex(protein1, protein2):
    """用RCSB REST API查两个蛋白的复合物PDB ID"""
    try:
        import urllib.request as _request
        import urllib.parse as _parse
    except ImportError:
        import urllib2 as _request
        import urllib as _parse
    import json as _json
    query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {"type": "terminal", "service": "full_text", "parameters": {"value": protein1}},
                {"type": "terminal", "service": "full_text", "parameters": {"value": protein2}},
            ]
        },
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": 5},
                             "sort": [{"sort_by": "score", "direction": "desc"}]}
    }
    url = 'https://search.rcsb.org/rcsbsearch/v2/query?json=' + _parse.quote(_json.dumps(query))
    try:
        with _request.urlopen(url, timeout=15) as r:
            data = _json.loads(r.read())
            hits = data.get('result_set', [])
            if hits:
                return hits[0]['identifier']
    except Exception as e:
        print(f'PDB search failed: {e}')
    return None

def auto_detect_chains(pdb_path):
    """自动检测PDB中的蛋白链，返回前两条"""
    chains = []
    seen = set()
    with open(pdb_path) as f:
        for line in f:
            if line.startswith('ATOM'):
                ch = line[21]
                if ch not in seen and ch.strip():
                    seen.add(ch)
                    chains.append(ch)
    return chains[:2] if len(chains) >= 2 else (chains + ['A','B'])[:2]

def calc_pocket_center(pdb_path, chain):
    """从配体链Calpha质心计算口袋中心"""
    xs, ys, zs = [], [], []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith('ATOM') and line[21] == chain and line[12:16].strip() == 'CA':
                try:
                    xs.append(float(line[30:38]))
                    ys.append(float(line[38:46]))
                    zs.append(float(line[46:54]))
                except:
                    pass
    if not xs:
        return None
    return [round(sum(xs)/len(xs),2), round(sum(ys)/len(ys),2), round(sum(zs)/len(zs),2)]


def calc_interface_pocket_center(pdb_path, chain_r, chain_l, manual_center=None, cutoff=8.0):
    if manual_center is not None:
        return [round(float(x), 2) for x in manual_center], 'manual'

    atoms_r = []
    atoms_l = []
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith('ATOM'):
                continue
            chain = line[21].strip()
            if chain not in (chain_r, chain_l):
                continue
            try:
                coord = (
                    float(line[30:38]),
                    float(line[38:46]),
                    float(line[46:54]),
                )
            except Exception:
                continue
            if chain == chain_r:
                atoms_r.append(coord)
            else:
                atoms_l.append(coord)

    if atoms_r and atoms_l:
        contact = []
        cutoff2 = cutoff * cutoff
        for ar in atoms_r:
            for al in atoms_l:
                dx = ar[0] - al[0]
                dy = ar[1] - al[1]
                dz = ar[2] - al[2]
                if dx * dx + dy * dy + dz * dz <= cutoff2:
                    contact.append(ar)
                    contact.append(al)
        if contact:
            n = float(len(contact))
            return [
                round(sum(p[0] for p in contact) / n, 2),
                round(sum(p[1] for p in contact) / n, 2),
                round(sum(p[2] for p in contact) / n, 2),
            ], 'interface_centroid'

    center = calc_pocket_center(pdb_path, chain_l)
    if center is not None:
        return center, 'ligand_chain_centroid'
    return None, 'none'


def prepare_target_from_pdb(pdb_path, chain_r, chain_l, name, manual_center=None, metadata=None):
    """从任意PDB文件构建靶点配置，返回target dict"""
    center, center_method = calc_interface_pocket_center(pdb_path, chain_r, chain_l, manual_center)
    target = {
        'name'          : name,
        'pdb'           : os.path.basename(pdb_path).replace('.pdb',''),
        'pdb_path'      : pdb_path,
        'pdbqt_path'    : None,
        'chain_receptor': chain_r,
        'chain_ligand'  : chain_l,
        'pocket_center' : center,
        'box_size'      : [25, 25, 25],
        'disease'       : 'custom',
        'known_drugs'   : [],
        'description'   : 'custom target',
        'structure_source': 'experimental',
        'complex_method': 'provided_pdb',
        'complex_status': 'ready',
        'modeled_complex': False,
        'pocket_center_method': center_method,
        'generation_mode': 'interface_conditioned',
    }
    if metadata:
        target.update(metadata)
        if 'pocket_center' not in metadata:
            target['pocket_center'] = center
        if 'pocket_center_method' not in metadata:
            target['pocket_center_method'] = center_method
    return target


def build_unresolved_target(name, protein1=None, protein2=None, failure_reason=None, notes=None):
    return {
        'name': name,
        'pdb': name,
        'disease': 'custom',
        'known_drugs': [],
        'description': 'unresolved target',
        'structure_source': 'unknown',
        'complex_method': 'none',
        'complex_status': 'unavailable',
        'modeled_complex': False,
        'pocket_center_method': 'none',
        'generation_mode': 'degraded_no_interface',
        'parent_targets': [protein1, protein2],
        'failure_reason': failure_reason,
        'notes': notes,
    }


def resolve_target_from_args(args, pdb_cache):
    if args.pdb:
        pdb_path = args.pdb
        name = args.name or os.path.basename(pdb_path).replace('.pdb','')
        return {
            'ok': True,
            'name': name,
            'pdb_path': pdb_path,
            'resolved_kind': 'provided_pdb',
            'metadata': {
                'structure_source': 'manual',
                'complex_method': 'provided_pdb',
                'complex_status': 'ready',
                'modeled_complex': False,
            },
        }

    if args.pdb_id:
        pdb_path = os.path.join(pdb_cache, f'{args.pdb_id.lower()}.pdb')
        if not os.path.exists(pdb_path):
            fetch_pdb(args.pdb_id, pdb_path)
        name = args.name or args.pdb_id.upper()
        return {
            'ok': True,
            'name': name,
            'pdb_path': pdb_path,
            'resolved_kind': 'pdb_id',
            'metadata': {
                'structure_source': 'experimental',
                'complex_method': 'pdb_id',
                'complex_status': 'ready',
                'modeled_complex': False,
            },
        }

    if args.protein1 and args.protein2:
        name = args.name or f'{args.protein1}_{args.protein2}'
        print(f'搜索 {args.protein1}-{args.protein2} 复合物...')
        pdb_id = search_pdb_for_complex(args.protein1, args.protein2)
        if pdb_id:
            print(f'找到: {pdb_id}')
            pdb_path = os.path.join(pdb_cache, f'{pdb_id.lower()}.pdb')
            if not os.path.exists(pdb_path):
                fetch_pdb(pdb_id, pdb_path)
            return {
                'ok': True,
                'name': name,
                'pdb_path': pdb_path,
                'resolved_kind': 'experimental_search',
                'metadata': {
                    'structure_source': 'experimental',
                    'complex_method': 'pdb_search',
                    'complex_status': 'ready',
                    'modeled_complex': False,
                    'parent_targets': [args.protein1, args.protein2],
                },
            }

        print(f'未找到{args.protein1}-{args.protein2}现成复合物，尝试自动构建...')
        modeled = build_modeled_complex(
            name=name,
            protein1=args.protein1,
            protein2=args.protein2,
            cache_dir=pdb_cache,
            provider=args.complex_provider,
            modeled_complex_pdb=args.modeled_complex_pdb,
            receptor_pdb=args.receptor_pdb,
            ligand_pdb=args.ligand_pdb,
            fetch_pdb_func=fetch_pdb,
        )
        if modeled.get('ok'):
            print('自动复合物构建成功')
            return {
                'ok': True,
                'name': name,
                'pdb_path': modeled['complex_pdb'],
                'resolved_kind': 'modeled_complex',
                'metadata': {
                    'structure_source': modeled.get('structure_source', 'modeled'),
                    'complex_method': modeled.get('complex_method', 'protein_docking'),
                    'complex_status': modeled.get('complex_status', 'modeled'),
                    'modeled_complex': modeled.get('modeled_complex', True),
                    'parent_targets': [args.protein1, args.protein2],
                    'resolved_complex_pdb': modeled['complex_pdb'],
                    'notes': modeled.get('notes'),
                },
            }

        unresolved = build_unresolved_target(
            name=name,
            protein1=args.protein1,
            protein2=args.protein2,
            failure_reason=modeled.get('failure_reason', 'complex_resolution_failed'),
            notes=modeled.get('notes'),
        )
        return {
            'ok': False,
            'name': name,
            'target_info': unresolved,
        }

    return {'ok': False, 'usage_error': True}



# ── 路径配置（集中管理，无硬编码靶点） ─────────────────────────────────────
CHECKPOINTS = f'{BASE_DIR}/core/denovo/checkpoints'
DB_PATH     = f'{BASE_DIR}/core/denovo/ppi_target_db.json'
RESULTS_DIR = f'{BASE_DIR}/core/denovo/results'
VINA_BIN    = '/home/huangym/anaconda/conda/envs/ppi_env/bin/vina'
WORK_DIR    = '/tmp/ppi_universal'
DEVICE      = 'cuda' if torch.cuda.is_available() else 'cpu'
ATYPE       = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
               'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD'}

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)


def validate_target_db_for_runtime(db):
    valid = {}
    invalid = {}
    for name, info in db.items():
        result = validate_target_entry(name, info)
        if result['errors']:
            invalid[name] = result
        else:
            valid[name] = result['normalized']
    return valid, invalid

# ── 模型加载（从checkpoint config自动推断参数） ──────────────────────────
def load_vae(vae_name='vae_best.pt'):
    path = os.path.join(CHECKPOINTS, vae_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f'VAE checkpoint not found: {path}')
    ck  = torch.load(path, map_location=DEVICE)
    cfg = ck['config']
    vae = GRUVAE(latent=cfg['latent'], hidden=cfg['hidden'],
                 enc_layers=cfg['enc_layers'], dec_layers=cfg['dec_layers'],
                 vocab_size=cfg.get('vocab_size', VOCAB_SIZE),
                 emb_dim=cfg.get('emb_dim', 128),
                 dropout=cfg.get('dropout', 0.1)).to(DEVICE)
    vae.load_state_dict(ck['model'])
    vae.eval()
    print(f'VAE loaded: {vae_name} (val_loss={ck.get("val_loss","?")})')
    return vae

def load_diffusion(diff_name='diffusion_best.pt'):
    path = os.path.join(CHECKPOINTS, diff_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f'Diffusion checkpoint not found: {path}')
    ck  = torch.load(path, map_location=DEVICE)
    cfg = ck.get('config', {})
    # 从config读取参数，fallback到默认值保证向后兼容
    penc = PocketEncoder(
        feat_dim = cfg.get('pocket_feat_dim', 4),
        hidden   = cfg.get('pocket_hidden', 128),
        out_dim  = cfg.get('pocket_out_dim', 256),
    ).to(DEVICE)
    dnet = DenoiseMLP(
        latent_dim = cfg.get('latent_dim', 256),
        cond_dim   = cfg.get('cond_dim', 256),
        hidden     = cfg.get('hidden', 512),
        n_layers   = cfg.get('n_layers', 4),
        n_heads    = cfg.get('n_heads', 8),
    ).to(DEVICE)
    penc.load_state_dict(ck['pocket_enc'])
    dnet.load_state_dict(ck['denoiser'])
    penc.eval(); dnet.eval()
    T = cfg.get('T', 1000)
    print(f'Diffusion loaded: {diff_name} (T={T})')
    return penc, dnet, T

# ── 约束解码 ─────────────────────────────────────────────────────────────
def is_partial_valid(s):
    if not s: return True
    if s.count('(') < s.count(')'): return False
    if s.count('[') < s.count(']'): return False
    if s.endswith('%'): return False
    return True

def can_close(s):
    if not s or s.count('(') != s.count(')'): return False
    return Chem.MolFromSmiles(s) is not None

@torch.no_grad()
def constrained_sample(vae, z, temperature=0.8, top_k=15, max_len=80):
    zi = z.unsqueeze(0) if z.dim()==1 else z
    h  = torch.tanh(vae.z2h(zi)).view(1, vae.dec_layers, vae.hidden).permute(1,0,2).contiguous()
    token, partial = torch.tensor([[SOS]], device=zi.device), ''
    for _ in range(max_len):
        emb = vae.emb_dec(token)
        inp = torch.cat([emb, zi.unsqueeze(1)], dim=-1)
        out, h = vae.decoder(inp, h)
        logits = vae.out_fc(out[:,-1,:]) / temperature
        vals, idxs = torch.topk(logits[0], min(top_k, logits.size(-1)))
        probs = torch.softmax(vals, dim=-1).cpu().numpy()
        vc, vp = [], []
        for prob, idx in zip(probs, idxs.tolist()):
            if idx == EOS:
                if can_close(partial): vc.append(idx); vp.append(prob)
            elif idx != PAD:
                char = I2CHAR.get(idx, '')
                if char and is_partial_valid(partial + char):
                    vc.append(idx); vp.append(prob)
        if not vc: break
        vp = np.array(vp); vp /= vp.sum()
        tok = vc[np.random.choice(len(vc), p=vp)]
        if tok == EOS: break
        partial += I2CHAR.get(tok, '')
        token = torch.tensor([[tok]], device=zi.device)
    mol = Chem.MolFromSmiles(partial)
    if mol is None:
        for end in range(len(partial), 0, -1):
            mol = Chem.MolFromSmiles(partial[:end])
            if mol and Descriptors.MolWt(mol) >= 250 and Descriptors.MolLogP(mol) <= 7: partial = partial[:end]; break
    return partial, mol

# ── 成药性过滤 ────────────────────────────────────────────────────────────

# Lipinski 类药性宽松版（PPI 分子通常偏大，放宽 MW 上限到 800）
DRUG_LIKE = {
    'mw'     : (150, 800),     # 分子量
    'logp'   : (-2,   7),      # cLogP
    'hbd'    : (0,    6),      # 氢键供体
    'hba'    : (0,   10),      # 氢键受体
    'tpsa'   : (0,  150),      # TPSA（过高说明渗透性差）
    'n_rot'  : (0,   12),      # 可旋转键（过高说明脱靶风险大）
    'n_arom' : (1,   99),      # 至少1个芳香环（PPI界面偏好疏水+pi-pi）
    'n_ring' : (1,    6),      # 环数（太少无特异性，太多溶解度差）
    'n_heavy': (10,  999),     # 重原子数
}

def drug_like_ok(mol, thresholds=None):
    if mol is None:
        return False, ['None mol']
    if thresholds is None:
        thresholds = DRUG_LIKE
    reasons = []
    mw    = rdMolDescriptors.CalcExactMolWt(mol)
    logp  = _MolLogP2(mol)
    hbd   = Lipinski.NumHDonors(mol)
    hba   = Lipinski.NumHAcceptors(mol)
    tpsa  = rdMolDescriptors.CalcTPSA(mol)
    n_rot = Lipinski.NumRotatableBonds(mol)
    n_arom = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())
    n_ring = mol.GetRingInfo().NumRings()
    n_heavy = mol.GetNumHeavyAtoms()
    vals = dict(mw=mw, logp=logp, hbd=hbd, hba=hba, tpsa=tpsa,
                n_rot=n_rot, n_arom=n_arom, n_ring=n_ring, n_heavy=n_heavy)
    for key, (lo, hi) in thresholds.items():
        v = vals.get(key)
        if v is None:
            reasons.append('missing_{}'.format(key))
            continue
        if not (lo <= v <= hi):
            reasons.append('{}_{:.1f}not[{},{}]'.format(key, v, lo, hi))
    return (len(reasons) == 0, reasons)

def pass_pains(mol):
    if mol is None or _PAINS is None:
        return True
    try:
        matches = _PAINS.GetMatches(mol)
        return len(matches) == 0
    except Exception:
        return True

def chemically_reasonable(mol):
    if mol is None:
        return False

    if any(a.GetNumRadicalElectrons() > 0 for a in mol.GetAtoms()):
        return False

    total_charge = sum(a.GetFormalCharge() for a in mol.GetAtoms())
    charged_atoms = sum(1 for a in mol.GetAtoms() if a.GetFormalCharge() != 0)
    if abs(total_charge) > 1 or charged_atoms > 1:
        return False

    allowed = {'C','N','O','S','P','F','Cl','Br','I','H'}
    if any(a.GetSymbol() not in allowed for a in mol.GetAtoms()):
        return False

    n_s = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == 'S')
    n_o = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == 'O')
    if n_s >= 4 or n_o >= 12:
        return False

    smi = Chem.MolToSmiles(mol)
    bad_patterns = ['[O][O]', 'S=S', 'S#', '[SH]', '[CH]', '[C+]', '[C-]', '[S+]', '[S-]', 'N=O', 'SSSS', 'OOO']
    if any(pat in smi for pat in bad_patterns):
        return False

    heavy = mol.GetNumHeavyAtoms()
    hetero = sum(1 for a in mol.GetAtoms() if a.GetSymbol() not in ('C','H'))
    if heavy > 0 and hetero / float(heavy) > 0.45:
        return False

    if mol.GetRingInfo().NumRings() < 2:
        return False

    return True

def smiles_clean(smi):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol)


def diversity_filter(candidates, threshold=0.4):
    """
    Greedy Tanimoto diversity filter using Morgan fingerprints (r=2, 2048 bits).
    Keeps a molecule only when its max similarity to already-selected molecules
    is strictly below `threshold`.  Input order sets priority (first = best kept).
    Returns a filtered list of (smi, mol) tuples.
    """
    if not candidates:
        return candidates
    fps = [AllChem.GetMorganFingerprintAsBitVect(mol, 2, 2048) for _, mol in candidates]
    selected_idx = [0]
    for i in range(1, len(candidates)):
        sel_fps = [fps[j] for j in selected_idx]
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], sel_fps)
        if max(sims) < threshold:
            selected_idx.append(i)
    return [candidates[i] for i in selected_idx]

# ── 多目标打分 ──────────────────────────────────────────────────────────
# composite = vina*0.4 + qed*(-3.0) + sa*(1.5) + size_penalty + diversity_bonus
# 越低越好
def compute_composite(mol, vina_score=None, qed=None, sa=None):
    vina = vina_score if vina_score is not None else 0.0
    q = qed if qed is not None else QED.qed(mol)
    if sa is None:
        try:
            from rdkit.Chem import rdMolDescriptors
            sa = rdMolDescriptors.CalcNumHBA(mol) + rdMolDescriptors.CalcNumHBD(mol)
            sa_score = max(0, (sa - 5) * 0.2)
        except Exception:
            sa_score = 0.0
    else:
        sa_score = sa

    mw = rdMolDescriptors.CalcExactMolWt(mol)
    # 对 MW 做软惩罚：500 以内无惩罚，500-700 轻微惩罚，>700 加重
    if mw <= 500:
        size_pen = 0.0
    elif mw <= 700:
        size_pen = (mw - 500) * 0.01
    else:
        size_pen = 2.0 + (mw - 700) * 0.02

    # 芳香环软惩罚：<1 或 >5 都惩罚
    n_arom = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())
    arom_pen = 0.0
    if n_arom < 1:
        arom_pen = 0.5
    elif n_arom > 5:
        arom_pen = (n_arom - 5) * 0.1

    comp = (vina * 0.4
            + q * (-3.0)
            + sa_score * 1.5
            + size_pen
            + arom_pen)
    return comp, dict(vina=vina, qed=q, sa=sa_score, size_pen=size_pen,
                      arom_pen=arom_pen, mw=mw, logp=_MolLogP2(mol),
                      tpsa=rdMolDescriptors.CalcTPSA(mol),
                      hbd=Lipinski.NumHDonors(mol),
                      hba=Lipinski.NumHAcceptors(mol),
                      n_arom=n_arom, n_ring=mol.GetRingInfo().NumRings())


# ── Vina对接 ──────────────────────────────────────────────────────────────

def prepare_receptor_pdbqt(pdb_path, chain_r, out_pdbqt):
    """
    从PDB自动生成受体PDBQT（无需obabel/MGLTools）
    只保留受体链的ATOM记录，转换为Vina 1.1.2兼容格式
    """
    ATYPE_MAP = {
        'C':'C', 'N':'NA', 'O':'OA', 'S':'SA', 'P':'P',
        'F':'F', 'CL':'Cl', 'BR':'Br', 'I':'I', 'H':'HD',
        'FE':'Fe', 'ZN':'Zn', 'MG':'Mg', 'CA':'Ca', 'MN':'Mn',
    }
    lines_out = []
    with open(pdb_path) as f:
        for line in f:
            if not (line.startswith('ATOM') or line.startswith('HETATM')):
                continue
            ch = line[21]
            if ch != chain_r:
                continue
            if line.startswith('HETATM'):
                continue  # 去掉小分子/水
            # 提取原子元素
            elem = line[76:78].strip() if len(line) > 76 else ''
            if not elem:
                name = line[12:16].strip()
                elem = ''.join(c for c in name if c.isalpha())[:2].upper()
            atype = ATYPE_MAP.get(elem, elem[:1] if elem else 'C')
            # 构建PDBQT行 (80列 + 电荷 + 原子类型)
            pdbqt_line = line[:54]
            occ  = line[54:60].strip() or '1.00'
            bfac = line[60:66].strip() or '0.00'
            pdbqt_line += f'{float(occ):6.2f}{float(bfac):6.2f}    0.0000 {atype:<2}\n'
            lines_out.append(pdbqt_line)
    if not lines_out:
        raise ValueError(f'Chain {chain_r} not found in {pdb_path}')
    with open(out_pdbqt, 'w') as f:
        f.writelines(lines_out)
    print(f'受体PDBQT: {len(lines_out)} 原子 → {out_pdbqt}')
    return out_pdbqt

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
        at = ATYPE.get(a.GetSymbol().upper(), 'C')
        lines.append(f'ATOM  {idx:5d}  {a.GetSymbol():<4s}LIG A   1    {p.x:8.3f}{p.y:8.3f}{p.z:8.3f}  1.00  0.00    0.0000 {at}\n')
        idx+=1
    lines.append('ENDROOT\nTORSDOF 0\n')
    open(path,'w').writelines(lines)
    return path

def run_vina(receptor_pdbqt, lig, out, center, box=(25,25,25)):
    if not os.path.exists(receptor_pdbqt):
        return None
    r = subprocess.run([VINA_BIN,
        '--receptor', receptor_pdbqt, '--ligand', lig, '--out', out,
        '--center_x', str(center[0]), '--center_y', str(center[1]), '--center_z', str(center[2]),
        '--size_x', str(box[0]), '--size_y', str(box[1]), '--size_z', str(box[2]),
        '--num_modes','3','--exhaustiveness','8','--cpu','2'],
        capture_output=True, text=True, timeout=60)
    for line in r.stdout.split('\n'):
        if re.match(r'\s+1\s+', line):
            try: return float(line.split()[1])
            except: pass
    return None

# ── 主流程 ────────────────────────────────────────────────────────────────

def _dock_one_worker(args):
    """
    Top-level worker for ProcessPoolExecutor parallel docking.
    Must be at module level so it is picklable by multiprocessing spawn.
    Returns (index, smiles, vina_score, result_dict) or None on failure.
    """
    i, smi, receptor_pdbqt, center, box, work_dir, target_name = args
    lig = os.path.join(work_dir, f'{target_name}_dock_{i}.pdbqt')
    out = os.path.join(work_dir, f'{target_name}_dock_{i}_out.pdbqt')
    try:
        if mol_to_pdbqt(smi, lig) is None:
            return None
        score = run_vina(receptor_pdbqt, lig, out, center, box)
        if score is None or score >= 0:
            return None
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return None
        mw   = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        qed  = QED.qed(mol)
        comp, _ = compute_composite(mol, vina_score=score, qed=qed)
        return (i, smi, score, {
            'smiles': smi, 'mw': round(mw, 1), 'logp': round(logp, 2),
            'qed': round(qed, 3), 'vina_score': score, 'composite': round(comp, 3),
        })
    except Exception:
        return None
    finally:
        for _f in [lig, out]:
            try:
                os.remove(_f)
            except OSError:
                pass

def run_pipeline(target_name, n=100, vae_name="vae_ppi.pt", diff_name="diffusion_cleaned_mw350.pt", temperature=0.8, db=None, counter_screen=False, cs_top_n=None, cs_workers=4):
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f'靶点数据库不存在: {DB_PATH}\n请先运行: python ppi_targets.py')
    if db is None:
        db, invalid_targets = load_and_validate_target_db(DB_PATH)
    else:
        db, invalid_targets = validate_target_db_for_runtime(db)

    if target_name not in db:
        print(f'未知或无效靶点: {target_name}')
        if target_name in invalid_targets:
            print('原因: ' + '; '.join(invalid_targets[target_name]['errors']))
        list_targets(db, invalid_targets)
        return

    target = db[target_name]
    pdb_path       = target.get('pdb_path')
    receptor_pdbqt = target.get('pdbqt_path')
    center         = target.get('pocket_center')
    chain_r        = target.get('chain_receptor', 'A')
    chain_l        = target.get('chain_ligand', 'B')
    complex_status = target.get('complex_status', 'ready')
    generation_mode = target.get('generation_mode', 'interface_conditioned')

    run_id = build_run_id(target_name)
    output_paths = build_output_paths(RESULTS_DIR, target_name, run_id)

    _no_structure = complex_status == 'unavailable' or not pdb_path or not os.path.exists(pdb_path)
    if _no_structure and generation_mode != 'degraded_no_interface':
        summary = summarize_results([])
        summary.update({
            'target_name': target_name,
            'run_id': run_id,
            'vae': vae_name,
            'diffusion': diff_name,
            'temperature': temperature,
            'requested_n': n,
            'total_sampled': 0,
            'candidate_count': 0,
            'pdb_path': pdb_path,
            'pdbqt_path': receptor_pdbqt,
            'chain_receptor': chain_r,
            'chain_ligand': chain_l,
            'structure_source': target.get('structure_source'),
            'complex_method': target.get('complex_method'),
            'complex_status': complex_status,
            'generation_mode': generation_mode,
            'modeled_complex': target.get('modeled_complex'),
            'resolved_complex_pdb': target.get('resolved_complex_pdb'),
            'pocket_center_method': target.get('pocket_center_method'),
            'used_docking': False,
            'failure_reason': target.get('failure_reason') or 'complex_unavailable',
            'notes': target.get('notes').decode('utf-8', errors='replace') if isinstance(target.get('notes'), bytes) else target.get('notes'),
            'output_csv': output_paths['run_csv'],
            'latest_csv': output_paths['latest_csv'],
        })
        write_manifest(output_paths['run_manifest'], summary)
        write_manifest(output_paths['latest_manifest'], summary)
        print('警告: 无可用复合物结构，跳过界面条件生成与对接')
        print('SUMMARY generated=0 docked=0 undocked=0 manifest=%s' % output_paths['run_manifest'])
        return []
    if _no_structure:
        print('无结构模式 (degraded_no_interface): 使用空口袋条件向量，跳过对接')

    if not _no_structure and (not receptor_pdbqt or not os.path.exists(receptor_pdbqt)):
        auto_pdbqt = os.path.join(WORK_DIR, f'{target_name}_receptor.pdbqt')
        try:
            prepare_receptor_pdbqt(pdb_path, chain_r, auto_pdbqt)
            receptor_pdbqt = auto_pdbqt
            target['pdbqt_path'] = auto_pdbqt
        except Exception as e:
            print(f'警告: 自动PDBQT生成失败: {e}')

    print(f'\n{"="*60}')
    print(f'靶点    : {target_name}')
    print(f'疾病    : {target["disease"]}')
    print(f'PDB     : {target.get("pdb", target.get("pdb_id","N/A"))} ({pdb_path})')
    print(f'口袋中心: {center}')
    print(f'VAE     : {vae_name}')
    print(f'Device  : {DEVICE}')
    print(f'{"="*60}\n')

    vae            = load_vae(vae_name)
    penc, dnet, T  = load_diffusion(diff_name)

    if _no_structure:
        pkt = torch.zeros(1, 4, device=DEVICE)  # null pocket: unconditioned generation
    else:
        print(f'提取PPI界面特征 (chain {chain_r} vs {chain_l})...')
        feats = extract_interface(pdb_path, chain1=chain_r, chain2=chain_l)
        print(f'界面残基: {feats.shape[0]} 个')
        pkt = torch.tensor(feats, dtype=torch.float32).to(DEVICE)

    ddpm = DDPM(T=T, device=DEVICE)
    candidates = []
    total_sampled = 0

    for it in range(5):
        if len(candidates) >= n:
            break
        bs = max((n - len(candidates)) * 3, 64)
        print(f'扩散采样 {bs} 个潜向量 (T={T}, iter={it+1})...')
        zi = torch.randn(bs, 256, device=DEVICE)
        ci = penc(pkt.unsqueeze(0)).expand(bs, -1)
        with torch.no_grad():
            for step in reversed(range(T)):
                zi = ddpm.p_sample(dnet, zi, step, ci)
        print(f'约束解码 (temperature={temperature})...')
        with torch.no_grad():
            for i in range(bs):
                smi, mol = constrained_sample(vae, zi[i], temperature=temperature)
                if mol:
                    mw = Descriptors.MolWt(mol)
                    if 250 <= mw <= 600 and Descriptors.MolLogP(mol) <= 7 and pass_pains(mol) and chemically_reasonable(mol):
                        candidates.append((Chem.MolToSmiles(mol), mol))
                        if len(candidates) >= n:
                            break
        total_sampled += bs
        print(f'  MW 250-600有效: {len(candidates)}/{n}')

    candidates = candidates[:n]
    seen_smi = set()
    candidates = [(s,m) for s,m in candidates if s not in seen_smi and not seen_smi.add(s)]
    candidates = diversity_filter(candidates, threshold=0.4)
    print(f'有效分子(去重+多样性过滤): {len(candidates)}/{total_sampled} ({len(candidates)/max(total_sampled,1)*100:.1f}%)')

    results = []
    if receptor_pdbqt and os.path.exists(receptor_pdbqt) and center:
        box = target.get('box_size', [25, 25, 25])
        n_dock_workers = max(1, min(cs_workers, len(candidates), os.cpu_count() or 4))
        print(f'Vina对接 ({n_dock_workers} workers, {len(candidates)} molecules)...')
        dock_args = [
            (i, smi, receptor_pdbqt, center, box, WORK_DIR, target_name)
            for i, (smi, _) in enumerate(candidates)
        ]
        mp_ctx = multiprocessing.get_context('spawn')
        with ProcessPoolExecutor(max_workers=n_dock_workers, mp_context=mp_ctx) as pool:
            for res in pool.map(_dock_one_worker, dock_args):
                if res is not None:
                    idx, smi, score, row = res
                    results.append(row)
                    print(f'[{idx+1:3d}] {score:6.1f} kcal/mol  QED={row["qed"]:.3f}  {smi[:45]}')
        results.sort(key=lambda x: x['composite'])
    else:
        print('警告: 受体PDBQT不可用，跳过Vina对接，仅输出生成结果')
        for smi, mol in candidates:
            mw, logp, qed = Descriptors.MolWt(mol), Descriptors.MolLogP(mol), QED.qed(mol)
            comp, _ = compute_composite(mol, vina_score=None, qed=qed)
            results.append({'smiles': smi, 'mw': round(mw,1), 'logp': round(logp,2),
                            'qed': round(qed,3), 'vina_score': None, 'composite': round(comp,3)})
        results.sort(key=lambda x: x['composite'])


    # ── PAINS filter + counter-screen (always label PAINS; CS if requested) ──
    if _CS_AVAILABLE and results:
        apply_pains(results)
        if counter_screen:
            print('\n反筛选 (93 off-targets)...')
            run_counter_screen(
                results, target_name,
                offtarget_db_path=_OFF_DB_PATH,
                ppi_db_path=_PPI_DB_PATH,
                top_n=cs_top_n,
                n_workers=cs_workers,
                tmp_dir=WORK_DIR,
            )
            results.sort(key=lambda x: (
                x.get('selectivity') if x.get('selectivity') is not None else 99,
                x.get('composite', 99)
            ))

    summary = summarize_results(results)
    summary.update({
        'target_name': target_name,
        'run_id': run_id,
        'vae': vae_name,
        'diffusion': diff_name,
        'temperature': temperature,
        'requested_n': n,
        'total_sampled': total_sampled,
        'candidate_count': len(candidates),
        'pdb_path': pdb_path,
        'pdbqt_path': receptor_pdbqt,
        'chain_receptor': chain_r,
        'chain_ligand': chain_l,
        'structure_source': target.get('structure_source'),
        'complex_method': target.get('complex_method'),
        'complex_status': complex_status,
        'generation_mode': generation_mode,
        'modeled_complex': target.get('modeled_complex'),
        'resolved_complex_pdb': target.get('resolved_complex_pdb', pdb_path),
        'pocket_center_method': target.get('pocket_center_method'),
        'used_docking': bool(receptor_pdbqt and os.path.exists(receptor_pdbqt) and center),
        'failure_reason': None if (receptor_pdbqt and os.path.exists(receptor_pdbqt) and center) else 'receptor_pdbqt_unavailable_or_missing_center',
        'notes': target.get('notes'),
        'output_csv': output_paths['run_csv'],
        'latest_csv': output_paths['latest_csv'],
    })

    if results:
        with open(output_paths['run_csv'], 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader(); w.writerows(results)
        with open(output_paths['latest_csv'], 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader(); w.writerows(results)

    write_manifest(output_paths['run_manifest'], summary)
    write_manifest(output_paths['latest_manifest'], summary)

    if results:
        print(f'\n{"="*60}')
        print(f'结果: {len(results)} 个候选分子 → {output_paths["run_csv"]}')
        print(f'Latest: {output_paths["latest_csv"]}')
        print(f'{"#":<3} {"Comp":>6} {"Vina":>6} {"Sel":>6} {"QED":>5} {"MW":>5}  SMILES')
        print('─'*75)
        for i,r in enumerate(results[:10],1):
            vina = r.get('vina_score')
            vina_str = f'{vina:6.1f}' if vina not in (None, '', 'None') else '   N/A'
            sel = r.get('selectivity')
            sel_str = f'{sel:6.2f}' if sel not in (None, '', 'None') else '   N/A'
            print(f'{i:<3} {r["composite"]:>6.2f} {vina_str} {sel_str} {r["qed"]:>5.3f} {r["mw"]:>5.0f}  {r["smiles"][:40]}')

    print('SUMMARY generated=%d docked=%d undocked=%d manifest=%s' % (summary['result_count'], summary['docked_count'], summary['undocked_count'], output_paths['run_manifest']))
    return results

def list_targets(db=None, invalid_targets=None):
    if db is None:
        db, invalid_targets = load_and_validate_target_db(DB_PATH)
    elif invalid_targets is None:
        invalid_targets = {}
    print(f'\n可用PPI靶点 ({len(db)}个):')
    print(f'{"靶点":<20} {"疾病":<18} {"PDB":<6} {"已知药物"}')
    print('─'*75)
    for name in sorted(db):
        info = db[name]
        known_drugs = info.get('known_drugs', ['?'])
        if not isinstance(known_drugs, list):
            known_drugs = [str(known_drugs)]
        drugs = ', '.join(known_drugs[:2])
        pdbqt_path = info.get('pdbqt_path')
        ready = bool(pdbqt_path and os.path.exists(pdbqt_path))
        if not ready:
            ready = bool(info.get('pdb_path') and os.path.exists(info.get('pdb_path', '')) and info.get('chain_receptor'))
        ok = '✓' if ready else '✗'
        pdb_id = info.get('pdb', info.get('pdb_id', 'N/A'))
        disease = info.get('disease', 'unknown')
        print(f'{name:<20} {disease:<18} {pdb_id:<6} {ok} {drugs}')
    if invalid_targets:
        print('\n无效靶点:')
        for name in sorted(invalid_targets):
            print('- %s: %s' % (name, '; '.join(invalid_targets[name]['errors'])))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='通用PPI抑制剂生成Pipeline - 支持任意蛋白对',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 预注册靶点
  python ppi_pipeline_universal.py --target MDM2_TP53

  # 直接提供PDB文件
  python ppi_pipeline_universal.py --pdb complex.pdb --chain_r A --chain_l B --name MY_PPI

  # 从RCSB下载PDB
  python ppi_pipeline_universal.py --pdb_id 1ycr --chain_r A --chain_l B --name MDM2_P53

  # 按蛋白名称自动查找PDB
  python ppi_pipeline_universal.py --protein1 MDM2 --protein2 TP53 --name MDM2_TP53_auto
        """
    )
    # 输入模式（三选一）
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('--target',   type=str, help='预注册靶点名称 (--list查看)')
    grp.add_argument('--pdb',      type=str, help='直接提供PDB复合物文件路径')
    grp.add_argument('--pdb_id',   type=str, help='RCSB PDB ID，自动下载')
    grp.add_argument('--protein1', type=str, help='蛋白1名称（配合--protein2使用）')

    # 通用参数
    parser.add_argument('--protein2',    type=str,   help='蛋白2名称')
    parser.add_argument('--chain_r',     type=str,   default=None, help='受体链ID（默认自动检测）')
    parser.add_argument('--chain_l',     type=str,   default=None, help='配体链ID（默认自动检测）')
    parser.add_argument('--name',        type=str,   default=None, help='靶点名称（用于输出文件命名）')
    parser.add_argument('--n',           type=int,   default=100,  help='生成分子数')
    parser.add_argument('--vae',         type=str,   default='vae_ppi.pt')
    parser.add_argument('--diffusion',   type=str,   default='diffusion_cleaned_mw350.pt')
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--list',        action='store_true', help='列出预注册靶点')
    parser.add_argument('--modeled-complex-pdb', type=str, default=None, help='手动提供建模复合物PDB路径')
    parser.add_argument('--receptor-pdb', type=str, default=None, help='自动复合物构建时受体单体PDB路径')
    parser.add_argument('--ligand-pdb',   type=str, default=None, help='自动复合物构建时配体单体PDB路径')
    parser.add_argument('--complex-provider', type=str, default='auto', choices=['auto', 'dock', 'colabfold', 'manual', 'none'], help='复合物构建provider')
    parser.add_argument('--interface-center', type=float, nargs=3, default=None, metavar=('X', 'Y', 'Z'), help='手动指定界面中心')
    parser.add_argument('--counter_screen', action='store_true',
                        help='运行反筛选：对接93个多样化人类靶标，计算选择性得分')
    parser.add_argument('--cs_top_n',  type=int, default=None,
                        help='仅对 Top-N 分子做反筛（默认全部）')
    parser.add_argument('--cs_workers',type=int, default=4,
                        help='反筛并行进程数（默认4）')
    args = parser.parse_args()

    if args.list:
        list_targets()

    elif args.target:
        # 模式1: 预注册靶点
        run_pipeline(args.target, args.n, args.vae, args.diffusion, args.temperature,
                     counter_screen=args.counter_screen, cs_top_n=args.cs_top_n, cs_workers=args.cs_workers)

    else:
        # 模式2/3/4: 自定义PDB / 自动复合物解析
        PDB_CACHE = os.path.join(BASE_DIR, 'structures', 'custom')
        os.makedirs(PDB_CACHE, exist_ok=True)

        resolved = resolve_target_from_args(args, PDB_CACHE)
        if resolved.get('usage_error'):
            parser.print_help()
            sys.exit(1)

        name = resolved['name']
        _db2 = json.load(open(DB_PATH))

        if resolved.get('ok'):
            pdb_path = resolved['pdb_path']
            chains = auto_detect_chains(pdb_path)
            chain_r = args.chain_r or chains[0]
            chain_l = args.chain_l or chains[1]
            print(f'链: 受体={chain_r}, 配体={chain_l}')
            target_info = prepare_target_from_pdb(
                pdb_path,
                chain_r,
                chain_l,
                name,
                manual_center=args.interface_center,
                metadata=resolved.get('metadata'),
            )
        else:
            target_info = resolved['target_info']
            backend = detect_complex_backend(args.complex_provider)
            target_info['complex_provider'] = backend.get('provider')
            print('警告: 未能解析可用复合物，流程将输出结构化失败结果')

        _db2[name] = target_info
        run_pipeline(name, args.n, args.vae, args.diffusion, args.temperature, db=_db2)
