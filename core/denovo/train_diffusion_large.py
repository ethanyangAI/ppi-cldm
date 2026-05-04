"""
训练条件潜在扩散模型（MW>350大分子版）
- 只使用MW>350的P-L对，解决生成分子量偏小问题
- 所有架构参数保存到checkpoint config
"""
import sys, os, json, torch, torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader

BASE_DIR = '/home/huangym/zjy/ppi_gen_project'
sys.path.insert(0, f'{BASE_DIR}/core/denovo')

from gru_vae import GRUVAE, encode
from latent_diffusion import DenoiseMLP, DDPM
from interface_extractor import PocketEncoder

CFG = {
    'data_path' : f'{BASE_DIR}/core/diffusion_project/data/graph2smiles/pocket_ligand_pairs.cleaned.json',
    'vae_path'  : f'{BASE_DIR}/core/denovo/checkpoints/vae_ppi.pt',
    'save_path' : f'{BASE_DIR}/core/denovo/checkpoints/diffusion_cleaned_mw350.pt',
    'mw_min'    : 350,
    'batch'  : 128,
    'epochs' : 100,
    'lr'     : 1e-4,
    'T'              : 1000,
    'latent_dim'     : 256,
    'cond_dim'       : 256,
    'hidden'         : 512,
    'n_layers'       : 4,
    'n_heads'        : 8,
    'pocket_feat_dim': 4,
    'pocket_hidden'  : 128,
    'pocket_out_dim' : 256,
}
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
os.makedirs(os.path.dirname(CFG['save_path']), exist_ok=True)

print('Loading VAE...')
vae_ckpt = torch.load(CFG['vae_path'], map_location=DEVICE)
vae_cfg  = vae_ckpt['config']
vae = GRUVAE(latent=vae_cfg['latent'], hidden=vae_cfg['hidden'],
             enc_layers=vae_cfg['enc_layers'], dec_layers=vae_cfg['dec_layers']).to(DEVICE)
vae.load_state_dict(vae_ckpt['model'])
vae.eval()
for p in vae.parameters(): p.requires_grad_(False)
print('VAE loaded (frozen)')

class PLDataset(Dataset):
    def __init__(self, path, mw_min=350):
        from rdkit import Chem
        from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors
        from rdkit.Chem.Crippen import MolLogP
        print(f'Loading {path} (MW>{mw_min} + drug-like)...')
        raw = json.load(open(path))
        self.samples = []
        skipped_mw, skipped_dl = 0, 0
        for item in raw:
            smi    = item.get('smiles', '')
            pocket = item.get('pocket_features')
            if not smi or not pocket: continue
            mol = Chem.MolFromSmiles(smi)
            if mol is None: continue
            mw = Descriptors.MolWt(mol)
            if mw < mw_min or mw > 800:
                skipped_mw += 1
                continue
            # Drug-like filter
            logp = MolLogP(mol)
            hbd = Lipinski.NumHDonors(mol)
            hba = Lipinski.NumHAcceptors(mol)
            tpsa = rdMolDescriptors.CalcTPSA(mol)
            if not (-2 <= logp <= 7 and hbd <= 6 and hba <= 10 and tpsa <= 150):
                skipped_dl += 1
                continue
            self.samples.append({'smiles': smi, 'pocket': np.array(pocket, dtype=np.float32)})
        print(f'Loaded {len(self.samples)} P-L pairs (skipped {skipped_mw} MW, {skipped_dl} drug-like)')

    def __len__(self): return len(self.samples)
    def __getitem__(self, i):
        s = self.samples[i]
        return (torch.tensor(encode(s['smiles']), dtype=torch.long),
                torch.tensor(s['pocket'], dtype=torch.float32))

def collate_fn(batch):
    ids  = torch.stack([b[0] for b in batch])
    maxN = max(b[1].size(0) for b in batch)
    pkts = torch.zeros(len(batch), maxN, CFG['pocket_feat_dim'])
    for j, (_, pkt) in enumerate(batch):
        pkts[j, :pkt.size(0)] = pkt
    return ids, pkts

dataset = PLDataset(CFG['data_path'], mw_min=CFG['mw_min'])
train_n = int(0.9 * len(dataset))
train_ds, val_ds = torch.utils.data.random_split(dataset, [train_n, len(dataset)-train_n])
train_loader = DataLoader(train_ds, batch_size=CFG['batch'], shuffle=True,  collate_fn=collate_fn, num_workers=4)
val_loader   = DataLoader(val_ds,   batch_size=CFG['batch'], shuffle=False, collate_fn=collate_fn, num_workers=2)

pocket_enc = PocketEncoder(feat_dim=CFG['pocket_feat_dim'], hidden=CFG['pocket_hidden'], out_dim=CFG['pocket_out_dim']).to(DEVICE)
denoiser   = DenoiseMLP(latent_dim=CFG['latent_dim'], cond_dim=CFG['cond_dim'], hidden=CFG['hidden'], n_layers=CFG['n_layers'], n_heads=CFG['n_heads']).to(DEVICE)
ddpm       = DDPM(T=CFG['T'], device=DEVICE)

print(f'pocket_enc params: {sum(p.numel() for p in pocket_enc.parameters()):,}')
print(f'denoiser params:   {sum(p.numel() for p in denoiser.parameters()):,}')

params    = list(pocket_enc.parameters()) + list(denoiser.parameters())
optimizer = torch.optim.Adam(params, lr=CFG['lr'])
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=CFG['epochs'])

best_val = float('inf')
for epoch in range(1, CFG['epochs']+1):
    pocket_enc.train(); denoiser.train()
    t_loss = 0.0
    for ids, pkts in train_loader:
        ids, pkts = ids.to(DEVICE), pkts.to(DEVICE)
        with torch.no_grad():
            mu, _ = vae.encode(ids)
        c            = pocket_enc(pkts)
        t            = torch.randint(0, CFG['T'], (mu.size(0),), device=DEVICE)
        z_t, noise   = ddpm.q_sample(mu, t)
        eps_pred     = denoiser(z_t, t, c)
        loss         = nn.functional.mse_loss(eps_pred, noise)
        optimizer.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(params, 1.0)
        optimizer.step()
        t_loss += loss.item()

    pocket_enc.eval(); denoiser.eval()
    v_loss = 0.0
    with torch.no_grad():
        for ids, pkts in val_loader:
            ids, pkts = ids.to(DEVICE), pkts.to(DEVICE)
            mu, _  = vae.encode(ids)
            c      = pocket_enc(pkts)
            t      = torch.randint(0, CFG['T'], (mu.size(0),), device=DEVICE)
            z_t, noise = ddpm.q_sample(mu, t)
            v_loss += nn.functional.mse_loss(denoiser(z_t, t, c), noise).item()

    t_loss /= len(train_loader)
    v_loss /= len(val_loader)
    scheduler.step()
    print(f'Epoch {epoch:3d} | train={t_loss:.5f} val={v_loss:.5f}')

    if v_loss < best_val:
        best_val = v_loss
        torch.save({
            'pocket_enc': pocket_enc.state_dict(),
            'denoiser'  : denoiser.state_dict(),
            'config'    : CFG,
        }, CFG['save_path'])
        print(f'  Saved (val={v_loss:.5f})')

print('Diffusion (MW>350) training complete!')
