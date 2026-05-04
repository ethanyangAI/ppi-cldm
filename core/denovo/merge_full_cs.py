"""
合并所有 partial 结果，按靶标输出 *_full_screened.csv
并打印全局 Top 候选
"""
import csv, json
from pathlib import Path

BASE    = Path("/home/huangym/zjy/ppi_gen_project/core/denovo")
PARTIAL = BASE / "full_cs_partial"
RESULTS = BASE / "results"

all_rows = []
for f in sorted(PARTIAL.glob("partial_*.csv")):
    with open(f) as _f:
        rows = list(csv.DictReader(_f))
    all_rows.extend(rows)
    print(f"Loaded {len(rows)} rows from {f.name}")

print(f"\nTotal: {len(all_rows)} molecules")

# Group by target
from collections import defaultdict
by_target = defaultdict(list)
for r in all_rows:
    by_target[r['target']].append(r)

fieldnames = ['uid','target','smiles','mw','logp','qed','vina_self','composite',
              'pains_flag','n_offtargets_docked','mean_off_vina','selectivity',
              'vina_CYP3A4','vina_hERG','vina_HSA','vina_CDK2','vina_Thrombin',
              'vina_EGFR','vina_AChE','vina_PARP1','vina_BRD4','vina_HDAC2']

def sort_key(r):
    try: return float(r.get('composite') or 99)
    except: return 99

for target, rows in sorted(by_target.items()):
    rows.sort(key=sort_key)
    out = RESULTS / f"{target}_full_screened.csv"
    with open(out,'w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    clean = sum(1 for r in rows if not r.get('pains_flag'))
    sel_1 = sum(1 for r in rows if r.get('selectivity') and r['selectivity'] not in ('',) and float(r['selectivity']) < -1.0)
    sel_2 = sum(1 for r in rows if r.get('selectivity') and r['selectivity'] not in ('',) and float(r['selectivity']) < -2.0)
    print(f"\n{target}: {len(rows)} total, {clean} PAINS-clean, {sel_1} sel<-1, {sel_2} sel<-2")

    top = [r for r in rows if not r.get('pains_flag') and r.get('vina_self')][:5]
    if top:
        print(f"  {'#':>2} {'comp':>6} {'vina':>6} {'sel':>6} {'qed':>6} {'mw':>5}  SMILES")
        for j,r in enumerate(top,1):
            print(f"  {j:2d} {r.get('composite','N/A'):>6} {r.get('vina_self',''):>6} "
                  f"{r.get('selectivity',''):>6} {r.get('qed',''):>6} "
                  f"{float(r['mw']) if r.get('mw') else 0:5.0f}  {r['smiles'][:40]}")
    print(f"  -> {out}")

print("\nMerge complete.")
