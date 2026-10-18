import os,json,time,hashlib
from pathlib import Path
from colabfold.batch import msa_to_str
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/03_af2_restore"
out=S/"target_msa";rp=out/"receipt.json";receipt=json.loads(rp.read_text())
rp.rename(out/"receipt_before_serialization_fix_11719.json")
queries=out/"candidate_queries";queries.rename(out/"invalid_candidate_queries_11719")
queries.mkdir()
targettext=(out/"KEAP1_285aa.a3m").read_text()
def record(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
for e in receipt["entries"]:
 target=e["target_sequence"];seq=e["sequence"]
 a3m=msa_to_str([targettext,">binder\n"+seq+"\n"],[">101\n"+target+"\n",">102\n"+seq+"\n"],[target,seq],[1,1])
 p=queries/(e["id"]+".a3m");p.write_text(a3m);e["msa"]=record(p)
receipt["slurm_job_id_serialization_fix"]=os.environ.get("SLURM_JOB_ID")
receipt["query_serialization"]="Explicit target+binder query-only paired row; target homologs unpaired, binder has no homologs. No evolutionary interchain paired MSA."
rp.write_text(json.dumps(receipt,indent=2)+"\n")
p=S/"retrieve_msa.py";text=p.read_text()
old='msa_to_str([text,">binder\\n"+seq+"\\n"],None,[target,seq],[1,1])'
new='msa_to_str([text,">binder\\n"+seq+"\\n"],[">101\\n"+target+"\\n",">102\\n"+seq+"\\n"],[target,seq],[1,1])'
assert old in text;p.write_text(text.replace(old,new))
print("FIXED_SERIALIZATION_PRESERVED_RAW_MSA",flush=True)
