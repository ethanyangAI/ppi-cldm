import json,os,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
import benchmark_common_review as c
from screening_transfer import rec,read,dump,verify
c.cpu()
prior=R/"steps/23_common_review/runs/msa_12975"
source=read(prior/"msa.json")
registry_path=verify(source["registry"]);registry=read(registry_path)
out=R/"steps/23_common_review/runs"/("msa_content_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False)
records=[]
for t in registry["targets"]:
    p=prior/"a3m"/(t["target_id"]+".a3m")
    d=c.a3m_rows(p.read_text(),t["sequence"])
    # Use both actual runtime parsers as CPU format checks, not homemade symbol replacement.
    helper=r"""import json,sys
from pathlib import Path
from boltz.data.parse.a3m import parse_a3m
v=parse_a3m(Path(sys.argv[1]),taxonomy=None,max_seqs=100000)
print(json.dumps({"status":"OFFICIAL_BOLTZ_A3M_PARSE_ACCEPTED","residue_n":len(v.residues),"sequence_n":len(v.sequences)}))
"""
    pr=c.subprocess.run([str(R/"env/boltz/bin/python"),"-c",helper,str(p)],env=dict(os.environ,CUDA_VISIBLE_DEVICES=""),capture_output=True,text=True)
    assert pr.returncode==0,pr.stderr
    boltz=json.loads(pr.stdout)
    helper2=r"""import json,sys
from alphafold.data.parsers import parse_a3m
v=parse_a3m(open(sys.argv[1]).read())
assert all(len(s)==int(sys.argv[2]) for s in v.sequences)
print(json.dumps({"status":"OFFICIAL_AF2_A3M_PARSE_ACCEPTED","sequence_n":len(v.sequences),"deletion_total":sum(sum(r) for r in v.deletion_matrix)}))
"""
    pr=c.subprocess.run([str(R/"env/colabfold/bin/python"),"-c",helper2,str(p),str(len(t["sequence"]))],env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu"),capture_output=True,text=True)
    assert pr.returncode==0,pr.stderr
    af2=json.loads(pr.stdout)
    log=prior/"a3m"/(t["target_id"]+".log")
    records.append(dict(target_id=t["target_id"],status="EXACT_QUERY_MSA_ACCEPTED",kind="SYNTHETIC_SINGLE_PREDECLARED" if t["synthetic"] else "MMSEQS2_TARGET_ONLY_UNPAIRED",file=rec(p),diagnostics=d,official_boltz_parser=boltz,official_af2_parser=af2,original_request_log=rec(log) if log.exists() else None,api_database_snapshot="NOT_PROVIDED_BY_API"))
    print("OFFICIAL_MSA_ACCEPTED",t["target_id"],d,flush=True)
dump(out/"msa.json",dict(status="ALL_TARGET_EXACT_QUERY_MSAS_FROZEN",registry=rec(registry_path),source=rec(c.__file__),records=records,created_utc=c.now(),original_download_results=rec(prior/"msa.json"),validation_correction="Official common unknown/ambiguous residue alphabets accepted without modifying raw rows/query"))
print("FROZEN",str(out/"msa.json"),flush=True)

