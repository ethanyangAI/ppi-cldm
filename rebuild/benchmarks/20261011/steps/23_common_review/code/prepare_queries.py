import os,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
from screening_transfer import rec,read,verify,dump
from benchmark_common_review import cpu,seqcheck,seqhash,msa
cpu()
inventory=R/"steps/22_matched_benchmark/input_preparation/runs/12971/inventory.json"
i=read(inventory);targets=[]
assert i["target_count"]==7 and not i["failures"]
for t in i["targets"]:
    receipt=t["identity_receipt"];ident=read(verify(receipt));s=ident["spec"]
    seq=seqcheck(ident["target_context"]["coordinate_required_sequence"])
    targets.append(dict(target_id=s["target_id"],family=s["family"],analysis_role=s["analysis_role"],sequence=seq,sequence_sha256=seqhash(seq),synthetic=s["family"].upper()=="BBF",query_identity_receipt=receipt,coordinate_status=ident["status"]))
out=R/"steps/23_common_review/runs"/("msa_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False)
registry=out/"query_registry.json"
dump(registry,dict(status="QUERY_IDENTITIES_ONLY_PENDING_COORDINATE_REPAIR",source=rec(inventory),targets=targets,scientific_scope="MSA_QUERY_PREPARATION_ONLY_NOT_GENERATION_FREEZE"))
print("EXACT_QUERIES_PREPARED",str(registry),flush=True)
msa(registry,out/"msa.json")
print("COMPLETE_MSA_INPUT",str(out/"msa.json"),flush=True)

