"""Benchmark seed wrapper; upstream BoltzGen code is unmodified."""
import sys,random,numpy as np,torch
seed=int(sys.argv.pop(1))
random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
# Upstream explicitly creates fresh entropy-seeded Generators in its featurizer.
# Supply deterministic child seeds for this single-worker benchmark invocation.
original=np.random.default_rng
master=original(seed)
def seeded_default_rng(value=None):
 return original(int(master.integers(0,2**63-1)) if value is None else value)
np.random.default_rng=seeded_default_rng
from boltzgen.cli.boltzgen import main
main()

