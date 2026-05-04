"""
GRU-VAE for SMILES generation
- Bidirectional GRU encoder → μ, σ
- Autoregressive GRU decoder
- Character-level tokenization (handles Cl, Br, [nH], etc.)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import re

# ── Tokenizer ──────────────────────────────────────────────────────────────
SPECIAL = ['<PAD>', '<SOS>', '<EOS>']
ATOMS   = ['C','N','O','S','P','F','Cl','Br','I','B','Si','Se','Na','K','H']
BONDS   = ['(',')',  '[',']','=','#','+','-','/','\\','@','%','.']
DIGITS  = list('0123456789')
VOCAB   = SPECIAL + ATOMS + BONDS + DIGITS
CHAR2I  = {c: i for i, c in enumerate(VOCAB)}
I2CHAR  = {i: c for i, c in enumerate(VOCAB)}
PAD, SOS, EOS = 0, 1, 2
VOCAB_SIZE = len(VOCAB)

_ATOM_RE = re.compile(r'(Cl|Br|Si|Se|Na|[A-Z])')

def tokenize(smi):
    tokens = []
    i = 0
    while i < len(smi):
        if smi[i:i+2] in ('Cl','Br','Si','Se','Na'):
            tokens.append(smi[i:i+2]); i += 2
        else:
            tokens.append(smi[i]); i += 1
    return tokens

def encode(smi, max_len=80):
    toks = tokenize(smi)[:max_len-2]
    ids = [SOS] + [CHAR2I.get(t, CHAR2I.get(t[0], 3)) for t in toks] + [EOS]
    ids += [PAD] * (max_len - len(ids))
    return ids[:max_len]

def decode_ids(ids):
    chars = []
    for i in ids:
        if i == EOS: break
        if i not in (PAD, SOS):
            chars.append(I2CHAR.get(i, '?'))
    return ''.join(chars)

# ── Model ──────────────────────────────────────────────────────────────────
class GRUVAE(nn.Module):
    def __init__(self, vocab_size=VOCAB_SIZE, emb_dim=128, hidden=512, latent=256,
                 enc_layers=2, dec_layers=2, dropout=0.1):
        super().__init__()
        self.latent = latent
        self.hidden = hidden
        self.dec_layers = dec_layers

        # Encoder
        self.emb_enc = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.encoder = nn.GRU(emb_dim, hidden, enc_layers, batch_first=True,
                               bidirectional=True, dropout=dropout)
        self.fc_mu  = nn.Linear(hidden * 2, latent)
        self.fc_var = nn.Linear(hidden * 2, latent)

        # Decoder
        self.emb_dec = nn.Embedding(vocab_size, emb_dim, padding_idx=PAD)
        self.z2h     = nn.Linear(latent, hidden * dec_layers)
        self.decoder = nn.GRU(emb_dim + latent, hidden, dec_layers,
                               batch_first=True, dropout=dropout)
        self.out_fc  = nn.Linear(hidden, vocab_size)

    def encode(self, x):
        # x: [B, L]
        emb = self.emb_enc(x)                       # [B, L, E]
        _, h = self.encoder(emb)                     # h: [2*layers, B, H]
        h = torch.cat([h[-2], h[-1]], dim=-1)        # [B, 2H]
        mu     = self.fc_mu(h)
        logvar = self.fc_var(h)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        return mu + std * torch.randn_like(std)

    def decode(self, z, tgt, teacher_force=True):
        """
        z:   [B, Z]
        tgt: [B, L] token ids (SOS + sequence + EOS)
        Returns logits [B, L-1, V]
        """
        B = z.size(0)
        h0 = torch.tanh(self.z2h(z))                     # [B, H*layers]
        h0 = h0.view(B, self.dec_layers, self.hidden)     # [B, layers, H]
        h0 = h0.permute(1, 0, 2).contiguous()             # [layers, B, H]

        tgt_in = tgt[:, :-1]                              # [B, L-1], drop EOS
        emb = self.emb_dec(tgt_in)                        # [B, L-1, E]
        z_expand = z.unsqueeze(1).expand(-1, emb.size(1), -1)
        inp = torch.cat([emb, z_expand], dim=-1)          # [B, L-1, E+Z]

        out, _ = self.decoder(inp, h0)                    # [B, L-1, H]
        logits = self.out_fc(out)                         # [B, L-1, V]
        return logits

    @torch.no_grad()
    def sample(self, n=1, device='cpu', max_len=80, temperature=1.0, top_k=10):
        """Pure de novo sampling from N(0,I)"""
        from rdkit import Chem
        results = []
        for _ in range(n):
            z = torch.randn(1, self.latent, device=device)
            h0 = torch.tanh(self.z2h(z))
            h0 = h0.view(1, self.dec_layers, self.hidden).permute(1,0,2).contiguous()

            token = torch.tensor([[SOS]], device=device)
            h = h0
            ids = []
            for _ in range(max_len):
                emb = self.emb_dec(token)                          # [1,1,E]
                inp = torch.cat([emb, z.unsqueeze(1)], dim=-1)    # [1,1,E+Z]
                out, h = self.decoder(inp, h)
                logits = self.out_fc(out[:, -1, :]) / temperature  # [1, V]
                # top-k sampling
                vals, idxs = torch.topk(logits, min(top_k, logits.size(-1)))
                probs = torch.softmax(vals, dim=-1)
                choice = torch.multinomial(probs[0], 1).item()
                tok = idxs[0, choice].item()
                if tok == EOS: break
                if tok != PAD: ids.append(tok)
                token = torch.tensor([[tok]], device=device)
            smi = decode_ids(ids)
            mol = Chem.MolFromSmiles(smi)
            results.append((smi, mol is not None))
        return results

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        logits = self.decode(z, x)
        return logits, mu, logvar

