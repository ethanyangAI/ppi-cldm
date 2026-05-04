"""
训练GRU-VAE on ZINC 100k
用法: conda run -n ppi_env python train_vae.py
"""
import sys, os, time, torch, torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
sys.path.insert(0, '/home/huangym/zjy/ppi_gen_project/core/denovo')
from gru_vae import GRUVAE, encode, decode_ids, VOCAB_SIZE, PAD, SOS, EOS

DATA_PATH = '/home/huangym/zjy/ppi_gen_project/data/raw/zinc_100k.smi'
SAVE_PATH = '/home/huangym/zjy/ppi_gen_project/core/denovo/checkpoints/vae_best.pt'
DEVICE    = 'cuda' if torch.cuda.is_available() else 'cpu'
MAX_LEN   = 80
BATCH     = 256
EPOCHS    = 50
LR        = 3e-4
KL_WEIGHT = 0.005   # warm up KL gradually

os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

class SMILESDataset(Dataset):
    def __init__(self, path, max_len=MAX_LEN):
        from rdkit import Chem
        print(f"Loading {path}...")
        raw = open(path).readlines()
        self.data = []
        for line in raw:
            smi = line.strip().split()[0]
            mol = Chem.MolFromSmiles(smi)
            if mol and len(smi) < max_len - 2:
                self.data.append(smi)
        print(f"Loaded {len(self.data)} valid SMILES")

    def __len__(self): return len(self.data)

    def __getitem__(self, i):
        return torch.tensor(encode(self.data[i], MAX_LEN), dtype=torch.long)

print(f"Device: {DEVICE}")
dataset = SMILESDataset(DATA_PATH)
train_size = int(0.95 * len(dataset))
val_size   = len(dataset) - train_size
train_ds, val_ds = torch.utils.data.random_split(dataset, [train_size, val_size])
train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True,  num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH, shuffle=False, num_workers=2)

model = GRUVAE(latent=256, hidden=512, enc_layers=2, dec_layers=2).to(DEVICE)
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)

def loss_fn(logits, tgt, mu, logvar, kl_w):
    # logits: [B, L-1, V]; tgt: [B, L]
    tgt_out = tgt[:, 1:].reshape(-1)          # [B*(L-1)]
    logits  = logits.reshape(-1, logits.size(-1))  # [B*(L-1), V]
    recon   = nn.functional.cross_entropy(logits, tgt_out, ignore_index=PAD)
    kl      = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).mean()
    return recon + kl_w * kl, recon.item(), kl.item()

best_val = float('inf')
for epoch in range(1, EPOCHS + 1):
    kl_w = min(KL_WEIGHT * epoch / 10, KL_WEIGHT)  # warmup
    model.train()
    t_loss = 0.0
    for batch in train_loader:
        batch = batch.to(DEVICE)
        logits, mu, logvar = model(batch)
        loss, r, k = loss_fn(logits, batch, mu, logvar, kl_w)
        optimizer.zero_grad(); loss.backward(); 
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        t_loss += loss.item()

    # Validation
    model.eval()
    v_loss = 0.0
    with torch.no_grad():
        for batch in val_loader:
            batch = batch.to(DEVICE)
            logits, mu, logvar = model(batch)
            loss, *_ = loss_fn(logits, batch, mu, logvar, kl_w)
            v_loss += loss.item()

    t_loss /= len(train_loader)
    v_loss /= len(val_loader)
    scheduler.step(v_loss)

    # Quick validity check every 5 epochs
    if epoch % 5 == 0:
        results = model.sample(n=20, device=DEVICE, temperature=0.8)
        valid = sum(1 for _, ok in results if ok)
        print(f"Epoch {epoch:3d} | train={t_loss:.4f} val={v_loss:.4f} | valid={valid}/20 | kl_w={kl_w:.4f}")
        if valid >= 5:  # save if any decent validity
            ex = [s for s,ok in results if ok][:3]
            print(f"  Examples: {ex}")
    else:
        print(f"Epoch {epoch:3d} | train={t_loss:.4f} val={v_loss:.4f} | kl_w={kl_w:.4f}")

    if v_loss < best_val:
        best_val = v_loss
        torch.save({'model': model.state_dict(), 'config': {
            'latent': 256, 'hidden': 512, 'enc_layers': 2, 'dec_layers': 2,
            'vocab_size': VOCAB_SIZE, 'emb_dim': 128, 'dropout': 0.1,
        }}, SAVE_PATH)
        print(f"  ✓ Saved checkpoint (val={v_loss:.4f})")

print("\nTraining complete!")
