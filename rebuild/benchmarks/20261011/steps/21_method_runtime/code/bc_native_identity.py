import os,json,hashlib,subprocess
from pathlib import Path
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";job=os.environ["SLURM_JOB_ID"];out=S/"runs"/("bc_native_identity_"+job)/"outputs";out.mkdir(parents=True,exist_ok=True)
base=R/"steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_1/attempts/000000"
target=json.loads((R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json").read_text())
events=[json.loads(x) for x in (base/"bindcraft_native_events.jsonl").read_text().splitlines()]
t=next(x for x in events if x["event"]=="trajectory_complete");p=base/"generated/Trajectory/Clashing"/(t["design"]+".pdb")
st=PDBParser(QUIET=True).get_structure("actual",p)[0]
seq={c.id:"".join(seq1(r.resname) for r in c if r.id[0]==" ") for c in st}
expected={"A":target["target_sequence"],"B":t["sequence"]}
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
diff={c:{"expected":expected[c],"actual":seq.get(c),"expected_count":len(expected[c]),"actual_count":len(seq[c]),"mismatches":[[i+1,a,b] for i,(a,b) in enumerate(zip(expected[c],seq[c])) if a!=b]} for c in expected}
doc={"status":"ACTUAL_NATIVE_PDB_VS_TRAJECTORY_EVENT_DIAGNOSTIC_NO_SEQUENCE_REPLACEMENT","pose":rec(p),"trajectory":t,"chains":diff,"rf_acceptance":rec(S/"runs/actual_native_v8_13213/outputs/rf/acceptance.json"),"cpu_job":job,"scheduler":subprocess.check_output(["scontrol","show","job","-o",job],text=True)}
(out/"identity.json").write_text(json.dumps(doc,indent=2)+"\n");print(json.dumps(doc,indent=2))
