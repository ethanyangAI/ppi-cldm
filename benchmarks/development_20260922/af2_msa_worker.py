import sys,json,hashlib
from pathlib import Path
from colabfold.colabfold import run_mmseqs2
from colabfold.batch import msa_to_str,unserialize_msa
plan=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True)
entries=json.loads(plan.read_text())["entries"];targets={}
for e in entries:
 key=hashlib.sha256(e["target_sequence"].encode()).hexdigest()
 if key not in targets:targets[key]=dict(sequence=e["target_sequence"],name=e["target"],de_novo=e["target"]=="BBF-14")
query=[k for k,v in targets.items() if not v["de_novo"]]
seqs=[targets[k]["sequence"] for k in query]
msas=run_mmseqs2(seqs,str(out/"public_targets"),use_env=True,use_templates=False,use_pairing=False,user_agent="ppi-blocker-calibration/1.0 public-published-target-only")
assert len(msas)==len(query)
for key,msa in zip(query,msas):targets[key]["msa"]=msa
for key,v in targets.items():
 if v["de_novo"]:v["msa"]=">published_de_novo_target\n"+v["sequence"]+"\n"
 assert [x for x in v["msa"].splitlines() if x and not x.startswith(">")][0]==v["sequence"]
 p=out/(key+".target.a3m");p.write_text(v["msa"])
 v["record"]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
 v["sequence_rows"]=sum(x.startswith(">") for x in v["msa"].splitlines())
 print("TARGET",v["name"],len(v["sequence"]),v["sequence_rows"],flush=True)
records={}
for e in entries:
 t,b=e["target_sequence"],e["sequence"];v=targets[hashlib.sha256(t.encode()).hexdigest()]
 combined=msa_to_str([v["msa"],">binder\n"+b+"\n"],[">101\n"+t+"\n",">102\n"+b+"\n"],[t,b],[1,1])
 decoded=unserialize_msa([combined],[t,b]);assert decoded[2]==[t,b] and decoded[3]==[1,1]
 assert all(sum(x.startswith(">") for x in msa.splitlines())==1 for msa in decoded[1])
 p=out/(e["id"]+".a3m");p.write_text(combined);records[e["id"]]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
(out/"inputs.json").write_text(json.dumps(records,indent=2))
(out/"target_receipts.json").write_text(json.dumps({k:{a:b for a,b in v.items() if a!="msa"} for k,v in targets.items()},indent=2))
print("VALIDATED",len(records),flush=True)
