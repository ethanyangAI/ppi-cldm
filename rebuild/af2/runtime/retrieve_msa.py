import os,json,time,hashlib
from pathlib import Path
from colabfold.colabfold import run_mmseqs2
from colabfold.batch import msa_to_str, get_queries
from alphafold.data import parsers
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/03_af2_restore"
inputpath=R/"01_raw/recovered_inputs/recovered_three_candidates.json"
entries=json.loads(inputpath.read_text())["entries"]
targets={e["target_sequence"] for e in entries};assert len(targets)==1
target=next(iter(targets));assert len(target)==285,len(target)
out=S/"target_msa";out.mkdir(exist_ok=True)
strings=run_mmseqs2([target],str(out/"KEAP1"),use_env=True,use_filter=True,use_templates=False,use_pairing=False,host_url="https://api.colabfold.com",user_agent="ppi-cldm-reconstruction/20261002")
assert len(strings)==1
text=strings[0];parsed=parsers.parse_a3m(text)
assert parsed.sequences[0]==target
assert len(parsed.sequences)>1
assert all(len(seq)==len(target) for seq in parsed.sequences)
targetfile=out/"KEAP1_285aa.a3m";targetfile.write_text(text)
queries=out/"candidate_queries";queries.mkdir(exist_ok=True)
def record(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
records=[]
for e in entries:
 seq=e["sequence"];a3m=msa_to_str([text,">binder\n"+seq+"\n"],[">101\n"+target+"\n",">102\n"+seq+"\n"],[target,seq],[1,1])
 p=queries/(e["id"]+".a3m");p.write_text(a3m)
 records.append({"id":e["id"],"sequence":seq,"target_sequence":target,"msa":record(p)})
receipt={"status":"REGENERATED_TARGET_MSA_AND_3_INPUTS_READY","slurm_job_id":os.environ.get("SLURM_JOB_ID"),"timestamp":time.time(),"inputs":record(inputpath),"target_sequence_sha256":hashlib.sha256(target.encode()).hexdigest(),"target_msa":record(targetfile),"target_msa_sequence_count":len(parsed.sequences),"database_snapshot":"Current ColabFold public MSA API snapshot; historic September snapshot unavailable, exact old predictions are not claimed reproducible.","use_templates":False,"use_pairing":False,"binder_msa":"single_sequence","inference_max_msa":"128:256","entries":records}
(out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2),flush=True)
