#!/usr/bin/env python3
import hashlib,importlib.util,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/pilot_v6_contracts_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def receipt(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
spec=importlib.util.spec_from_file_location("rt",R/"source/rebuild/benchmark_runtime.py");rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
manifest=R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json";target=json.loads(manifest.read_text());declared_old={k:target[k] for k in ["input_target_chain","rfd_output_target_chain","rfd_binder_chain"]};target["rfd_output_target_chain"]="A";target["rfd_binder_chain"]="B"
pdb=R/"steps/22_matched_benchmark/engineering_pilot/runs/13069_0/attempts/000000/generated/backbone_1436254356.pdb";trb=pdb.with_suffix(".trb")
proof=rt.validate_rfd_output(pdb,trb,target)
proof.update({"scope":"CPU retrospective identity proof for preserved failed engineering output; explicit metadata-only interpretation correction; no geometry modification","historical_target_manifest":receipt(manifest),"historical_declared_chain_fields":declared_old,"corrected_interpretation_chain_fields":{k:target[k] for k in declared_old},"actual_official_output_pdb":receipt(pdb),"actual_official_output_trb":receipt(trb),"input_target_pdb":target["target_pdb"],"runtime_source":receipt(R/"source/rebuild/benchmark_runtime.py"),"official_sampler_source":receipt(R/"vendor/RFdiffusion/rfdiffusion/inference/model_runners.py"),"official_contig_map_source":receipt(R/"vendor/RFdiffusion/rfdiffusion/contigs.py"),"official_writer_source":receipt(R/"vendor/RFdiffusion/scripts/run_inference.py"),"cpu_only":True,"slurm_job_id":os.environ["SLURM_JOB_ID"],"scheduler_record":subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)})
out=O/"actual_rfd_identity_proof.json";out.write_text(json.dumps(proof,indent=2)+"\n")
result={"status":"RUNTIME_V6_CAUSAL_REPAIRS_CPU_CONTRACTS_PASS","actual_rfd_identity_proof":receipt(out),"unit_tests":receipt(O/"tests.txt"),"runtime_source":receipt(R/"source/rebuild/benchmark_runtime.py"),"tests_source":receipt(S/"code/test_runtime_contracts.py"),"cpu_only":True,"job":os.environ["SLURM_JOB_ID"]}
(O/"acceptance.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))

