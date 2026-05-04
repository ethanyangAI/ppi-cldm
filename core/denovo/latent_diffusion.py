"""
条件潜在扩散模型（Conditional Latent Diffusion Model）
- 输入: 噪声向量 z_T + 口袋条件向量 c
- 去噪: z_T → z_{T-1} → ... → z_0
- 解码: VAE.decode(z_0) → SMILES
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SinusoidalTimeEmb(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, t):
        # t: [B] int timesteps
        half = self.dim // 2
        freqs = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / (half - 1))
        args  = t.float()[:, None] * freqs[None]
        return torch.cat([args.sin(), args.cos()], dim=-1)  # [B, dim]


class DenoiseMLP(nn.Module):
    """
    Predicts noise ε given (z_t, t, c)
    Architecture: MLP with residual connections + cross-attention to condition
    """
    def __init__(self, latent_dim=256, cond_dim=256, hidden=512, n_layers=6, n_heads=8):
        super().__init__()
        self.latent_dim = latent_dim
        self.time_emb   = SinusoidalTimeEmb(hidden)
        self.z_proj     = nn.Linear(latent_dim, hidden)
        self.c_proj     = nn.Linear(cond_dim, hidden)
        self.t_proj     = nn.Linear(hidden, hidden)

        # Transformer blocks: self-attn on z + cross-attn to condition
        self.blocks = nn.ModuleList([
            nn.ModuleDict({
                'norm1': nn.LayerNorm(hidden),
                'ff1'  : nn.Sequential(nn.Linear(hidden, hidden*2), nn.GELU(), nn.Linear(hidden*2, hidden)),
                'norm2': nn.LayerNorm(hidden),
                'cross': nn.MultiheadAttention(hidden, n_heads, batch_first=True),
                'norm3': nn.LayerNorm(hidden),
                'ff2'  : nn.Sequential(nn.Linear(hidden, hidden*2), nn.GELU(), nn.Linear(hidden*2, hidden)),
            }) for _ in range(n_layers)
        ])

        self.out = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, latent_dim))

    def forward(self, z_t, t, c):
        """
        z_t: [B, Z]   noisy latent
        t:   [B]      timestep
        c:   [B, C]   pocket condition vector
        Returns: predicted noise ε [B, Z]
        """
        h = self.z_proj(z_t) + self.t_proj(self.time_emb(t))  # [B, H]
        h = h.unsqueeze(1)   # [B, 1, H]   (single token sequence)
        cv = self.c_proj(c).unsqueeze(1)  # [B, 1, H]

        for blk in self.blocks:
            # FF with residual
            h = h + blk['ff1'](blk['norm1'](h))
            # Cross attention to condition
            ha, _ = blk['cross'](blk['norm2'](h), cv, cv)
            h = h + ha
            h = h + blk['ff2'](blk['norm3'](h))

        return self.out(h.squeeze(1))  # [B, Z]


class DDPM:
    """DDPM noise schedule and sampling"""
    def __init__(self, T=1000, beta_start=1e-4, beta_end=0.02, device='cpu'):
        self.T = T
        beta  = torch.linspace(beta_start, beta_end, T, device=device)
        alpha = 1.0 - beta
        alpha_bar = torch.cumprod(alpha, dim=0)
        self.register = {
            'beta'       : beta,
            'alpha'      : alpha,
            'alpha_bar'  : alpha_bar,
            'sqrt_ab'    : alpha_bar.sqrt(),
            'sqrt_1mab'  : (1 - alpha_bar).sqrt(),
        }

    def q_sample(self, z0, t, noise=None):
        """Forward diffusion: q(z_t | z_0)"""
        if noise is None: noise = torch.randn_like(z0)
        sqrt_ab  = self.register['sqrt_ab'][t].view(-1,1)
        sqrt_1mb = self.register['sqrt_1mab'][t].view(-1,1)
        return sqrt_ab * z0 + sqrt_1mb * noise, noise

    @torch.no_grad()
    def p_sample(self, model, z_t, t_scalar, c):
        """One reverse step: p(z_{t-1} | z_t, c)"""
        t = torch.full((z_t.size(0),), t_scalar, device=z_t.device, dtype=torch.long)
        beta      = self.register['beta'][t_scalar]
        alpha     = self.register['alpha'][t_scalar]
        alpha_bar = self.register['alpha_bar'][t_scalar]

        eps_pred = model(z_t, t, c)
        coef = beta / (1 - alpha_bar).sqrt()
        mean = (z_t - coef * eps_pred) / alpha.sqrt()

        if t_scalar > 0:
            noise = torch.randn_like(z_t)
            z_prev = mean + beta.sqrt() * noise
        else:
            z_prev = mean
        return z_prev

    @torch.no_grad()
    def sample(self, model, n, cond_dim, c, device='cpu'):
        """Full reverse diffusion: z_T → z_0"""
        z = torch.randn(n, model.latent_dim, device=device)
        for t in reversed(range(self.T)):
            z = self.p_sample(model, z, t, c)
        return z
