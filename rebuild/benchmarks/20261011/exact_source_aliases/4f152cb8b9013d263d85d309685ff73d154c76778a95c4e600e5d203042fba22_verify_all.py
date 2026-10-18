import os,json,time,hashlib
from pathlib import Path
from colabfold.batch import get_queries,unserialize_msa
from alphafold.data import parsers
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/03_af2_restore"
def record(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
receipts={}
for name in ["runtime_receipt.json","weights_receipt.json","ptm_weights_receipt.json","gpu_smoke_receipt.json","target_msa/receipt.json"]:
 p=S/name;receipts[name]={"file":record(p),"content":json.loads(p.read_text())}
weights=receipts["weights_receipt.json"]["content"]["weights"]+receipts["ptm_weights_receipt.json"]["content"]["weights"]
assert len(weights)==10 and len({x["path"] for x in weights})==10
for x in weights:assert record(Path(x["path"]))==x
e=receipts["target_msa/receipt.json"]["content"]["entries"]
by={x["id"]:x for x in e};qs,complex_=get_queries(S/"target_msa/candidate_queries")
assert complex_ and len(qs)==3
observations=[]
for name,sequence,lines in qs:
 unpaired,paired,sequences,cardinality,template=unserialize_msa(lines,sequence)
 entry=by[name];assert sequences==[entry["target_sequence"],entry["sequence"]]
 assert cardinality==[1,1]
 bindermsa=parsers.parse_a3m(unpaired[1]);assert bindermsa.sequences==[entry["sequence"]]
 targetmsa=parsers.parse_a3m(unpaired[0]);assert targetmsa.sequences[0]==entry["target_sequence"]
 rawmsa=parsers.parse_a3m((S/"target_msa/KEAP1_285aa.a3m").read_text());assert set(targetmsa.sequences)==set(rawmsa.sequences);assert 1<len(targetmsa.sequences)<=len(rawmsa.sequences)
 assert record(Path(entry["msa"]["path"]))==entry["msa"]
 observations.append({"id":name,"target_msa_sequence_count":len(targetmsa.sequences),"binder_msa_sequence_count":len(bindermsa.sequences),"chain_lengths":list(map(len,sequences))})
files=[p for p in S.iterdir() if p.suffix in (".py",".sh",".txt") and p.is_file()]
manifest={"status":"AF2_RUNTIME_ASSETS_AND_INPUTS_READY","job_id":os.environ.get("SLURM_JOB_ID"),"timestamp":time.time(),"receipts":{k:v["file"] for k,v in receipts.items()},"weights_count":10,"verified_candidate_msas":observations,"implementation_records":[record(p) for p in sorted(files)],"pending":"Actual AF2 protein inference and scientific output acceptance remain outstanding.","historical_reproduction_limit":"Target MSA regenerated from current public API, so exact old AF2 structure reproduction is not claimed."}
(S/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n");print(json.dumps(manifest,indent=2),flush=True)
