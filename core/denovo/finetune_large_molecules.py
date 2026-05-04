import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from gru_vae import GRUVAE, VOCAB_SIZE, encode, decode_ids, PAD, SOS, EOS
from rdkit import Chem
from rdkit.Chem import Descriptors
import numpy as np

MAX_LEN = 80

class LargeMoleculeDataset(Dataset):
    def __init__(self, smi_file, max_len=MAX_LEN, min_mw=350, oversample_factor=50):
        self.max_len = max_len
        self.data = []
        
        # 读取大分子
        all_smiles = []
        with open(smi_file) as f:
            for line in f:
                smi = line.strip().split()[0]
                mol = Chem.MolFromSmiles(smi)
                if mol:
                    mw = Descriptors.MolWt(mol)
                    if mw >= min_mw and mw <= 600 and len(smi) < max_len - 2:
                        all_smiles.append(smi)
        
        print(f'筛选出 {len(all_smiles)} 个MW>={min_mw}的分子')
        
        # 过采样
        for smi in all_smiles * oversample_factor:
            encoded = torch.tensor(encode(smi, max_len), dtype=torch.long)
            self.data.append(encoded)
        
        print(f'过采样后总样本数: {len(self.data)}')
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]

def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')
    
    # 加载已有VAE
    checkpoint = torch.load('checkpoints/vae_ppi.pt', map_location=device)
    cfg = checkpoint.get('config', {})
    model = GRUVAE(
        vocab_size=cfg.get('vocab_size', VOCAB_SIZE),
        emb_dim=cfg.get('emb_dim', 128),
        latent=cfg.get('latent', 256),
        hidden=cfg.get('hidden', 512),
        enc_layers=cfg.get('enc_layers', 2),
        dec_layers=cfg.get('dec_layers', 2),
        dropout=cfg.get('dropout', 0.1),
    )
    model.load_state_dict(checkpoint['model'])
    model = model.to(device)
    
    # 准备数据（只用大分子）
    dataset = LargeMoleculeDataset('../../data/raw/ppi_inhibitors.smi', min_mw=350, oversample_factor=50)
    loader = DataLoader(dataset, batch_size=64, shuffle=True, num_workers=4)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    
    print('开始fine-tune（专注大分子）...')
    model.train()
    for epoch in range(20):
        total_loss = 0
        for batch in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            logits, mu, logvar = model(batch)
            
            # Loss
            tgt_out = batch[:, 1:].reshape(-1)
            logits_flat = logits.reshape(-1, logits.size(-1))
            recon_loss = nn.functional.cross_entropy(logits_flat, tgt_out, ignore_index=PAD)
            kl_loss = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).mean()
            loss = recon_loss + 0.005 * kl_loss
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(loader)
        print(f'Epoch {epoch+1}/20, Loss: {avg_loss:.4f}')
        
        # 每5轮测试生成
        if (epoch + 1) % 5 == 0:
            model.eval()
            results = model.sample(n=10, device=device, temperature=0.8)
            valid = sum(1 for _, ok in results if ok)
            mws = []
            for smi, ok in results:
                if ok:
                    mol = Chem.MolFromSmiles(smi)
                    if mol:
                        mws.append(Descriptors.MolWt(mol))
            if mws:
                print(f'  Valid: {valid}/10, 平均MW: {np.mean(mws):.1f}')
            model.train()
    
    # 保存
    torch.save({
        'model': model.state_dict(),
        'config': checkpoint.get('config', {})
    }, 'checkpoints/vae_large_molecules.pt')
    print('保存到 checkpoints/vae_large_molecules.pt')

if __name__ == '__main__':
    train()
