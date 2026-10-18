#!/usr/bin/env python3
"""CPU format/content integration: existing predictions, not new protocol evidence."""
import json,os,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
import benchmark_common_review as common
from screening_transfer import read,rec,dump,verify
common.cpu()
out=R/"steps/23_common_review/runs"/("integration_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False)
old=R/"steps/02_predict/runs/20261002T121305Z_be69fbefc530"
old_manifest=read(old/"manifest.json")
for key in ["model_0_structure","model_0_confidence","model_0_pae"]:verify(old_manifest["outputs"][key])
raw=old/"work/boltz/results/boltz_results_complex/predictions/complex"
dest=out/"worker/fixture_native/seed_42/boltz_results_complex/predictions/complex";dest.mkdir(parents=True)
for name in ["complex_model_0.pdb","confidence_complex_model_0.json","pae_complex_model_0.npz","plddt_complex_model_0.npz"]:os.link(raw/name,dest/name)
chains,_=common.read_structure(raw/"complex_model_0.pdb");a,b=chains
identpath=R/"steps/22_matched_benchmark/input_preparation/runs/12961/targets/MDM2_1YCR/identity.json"
if not identpath.exists():identpath=R/"steps/22_matched_benchmark/input_preparation/runs/12956/targets/MDM2_1YCR/identity.json"
ident=read(identpath)
t=dict(reference_complex=ident["reference_complex"],query_to_reference_indices=ident["design_to_reference_indices"])
e=dict(target_sequence=a["sequence"],binder_sequence=b["sequence"])
model=common.one_score(dict(job_key="fixture_native",engine="boltz"),e,t,dict(seed=42,model=0),out/"worker",out/"scoring",True)
assert model["status"]=="VALID" and model["R0"] is not None and model["R1"] is not None
assert model["geometry"]["known_partner_target_aligned_CA_RMSD_A"] is not None
# Published AF2 confidence files: verify raw fraction/Angstrom conversion and exact R0.
prep=read(R/"steps/20_screening_improvement/inputs/preparation_receipt.json")
pointer=read(R/"steps/20_screening_improvement/run_pointer.json")
accepted=read(Path(pointer["manifest"]["path"]).parent/"outputs/model_features1170.json")["rows"]
afrow=next(v for v in accepted if v["target"]=="Mdm2")
verify(afrow["pdb"]);verify(afrow["scores"]);araw=read(afrow["scores"]["path"]);acs,_=common.read_structure(afrow["pdb"]["path"])
na=len(acs[0]["sequence"]);n=na+len(acs[1]["sequence"])
pp,pa=common.units(araw["plddt"],araw["pae"],n,100);pairs=common.interface(acs[0],acs[1],5)["residue_pairs"]
ai=sorted({x-1 for x,y in pairs});bi=sorted({na+y-1 for x,y in pairs})
ip=float(pp[ai+bi].mean());cp=float(common.np.mean([pa[x-1,na+y-1] for x,y in pairs]+[pa[na+y-1,x-1] for x,y in pairs]))
r0=common.components(araw["iptm"],float(pp[na:].mean()),ip,cp)
assert abs(r0["score"]-afrow["R0"])<1e-12
# Both feature roundtrip regions retain ordered A3M insertions/deletions.
target=a["sequence"];binder=b["sequence"];a3m=out/"fixture.a3m"
helper=r"""import json,sys
sys.path.insert(0,sys.argv[1])
from colabfold.batch import msa_to_str
from control_msa_check import verify_roundtrip
t,b,out=sys.argv[2:];tm=">query\n"+t+"\n>gapped\n"+"-"+t[1:]+"\n>insert\n"+t[0]+"a"+t[1:]+"\n"
text=msa_to_str([tm,">binder\n"+b+"\n"],[">101\n"+t+"\n",">102\n"+b+"\n"],[t,b],[1,1])
with open(out,"x") as f:f.write(text)
print(json.dumps(verify_roundtrip(out,out,t,b)))
"""
pr=common.subprocess.run([str(R/"env/colabfold/bin/python"),"-c",helper,str(R/"source/rebuild"),target,binder,str(a3m)],env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu"),capture_output=True,text=True)
assert pr.returncode==0,pr.stderr
features=json.loads(pr.stdout)
dump(out/"acceptance.json",dict(status="REAL_BOLTZ_AF2_RAW_FORMAT_AND_MSA_FEATURE_INTEGRATION_ACCEPTED",scope="TEST_FIXTURES_ONLY_NOT_NEW_COMMON_PROTOCOL_PREDICTIONS",source=rec(common.__file__),fixture_source_manifest=rec(old/"manifest.json"),boltz=model,af2=dict(raw_files=[afrow["pdb"],afrow["scores"]],computed_R0=r0,accepted_R0=afrow["R0"]),msa_roundtrip=features,msa=rec(a3m),job_id=os.environ["SLURM_JOB_ID"]))
print(json.dumps(dict(status="ACCEPTED",path=str(out/"acceptance.json"),boltz_R0=model["R0"],boltz_R1=model["R1"]),indent=2))

