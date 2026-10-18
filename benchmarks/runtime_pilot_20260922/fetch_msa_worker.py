import sys,json
from pathlib import Path
from colabfold.colabfold import run_mmseqs2
plan=Path(sys.argv[1]);dest=Path(sys.argv[2]);dest.mkdir(exist_ok=True)
entries=json.loads(plan.read_text())["entries"]
ids=["P06","P09"];seqs=[next(x["target_sequence"] for x in entries if x["group"]==cid) for cid in ids]
a3ms=run_mmseqs2(seqs,str(dest/"public_targets"),use_env=True,use_templates=False,use_pairing=False,user_agent="ppi-blocker-benchmark/1.0 public-target-only")
assert len(a3ms)==2
for cid,seq,a3m in zip(ids,seqs,a3ms):
 lines=[x for x in a3m.splitlines() if x and not x.startswith(">")]
 assert lines[0]==seq and len(lines)>1,(cid,len(lines))
 (dest/(cid+".a3m")).write_text(a3m)
print("PUBLIC_TARGET_MSA_COMPLETE",flush=True)

