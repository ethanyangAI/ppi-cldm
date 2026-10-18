#!/usr/bin/env python3
import hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import torch
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/pilot_v6_mpnn_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
assert not torch.cuda.is_available() and torch.cuda.device_count()==0
runtime=R/"steps/22_matched_benchmark/settings/pilot_v6/source/benchmark_runtime.py";spec=importlib.util.spec_from_file_location("rt",runtime);rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
manifest=R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json";target=json.loads(manifest.read_text());assert target["rfd_binder_chain"]=="B" and target["rfd_output_target_chain"]=="A"
pdb=R/"steps/22_matched_benchmark/engineering_pilot/runs/13069_0/attempts/000000/generated/backbone_1436254356.pdb";identity=rt.validate_rfd_output(pdb,pdb.with_suffix(".trb"),target)
folder=O/"mpnn";fasta=folder/"seqs"/(pdb.stem+".fa");ledger=O/"sequences.jsonl";observed=[]
def emit(header,sequence):
 assert len(sequence)==65 and not set(sequence)-set("ADEFGHIKLMNPQRSTVWY")
 row={"sequence":sequence,"mpnn_header":header,"completed_at_epoch":time.time(),"engineering_cpu_only":True};observed.append(row);rt.append_stream(ledger,row)
args=[sys.executable,str(R/"vendor/ProteinMPNN/protein_mpnn_run.py"),"--pdb_path",str(pdb),"--pdb_path_chains","B","--out_folder",str(folder),"--num_seq_per_target","8","--batch_size","1","--sampling_temp","0.0001","--seed","1436254356","--omit_AAs","CX","--save_score","1"]
started=time.time();rt.resident_mpnn(args,fasta,emit)
readback=rt.parse_fasta_records(fasta) if hasattr(rt,"parse_fasta_records") else None
samples=[];header=None
for line in fasta.read_text().splitlines():
 if line.startswith(">"):header=line[1:]
 elif header and "sample=" in header and line:samples.append((header,line))
assert len(observed)==8 and [(r["mpnn_header"],r["sequence"]) for r in observed]==samples
assert len(ledger.read_text().splitlines())==8
result={"status":"ACTUAL_ORIGINAL_MPNN8_CHAIN_B_AND_INCREMENTAL_NATIVE_FASTA_PASS","runtime":rec(runtime),"input_manifest":rec(manifest),"actual_backbone":rec(pdb),"native_fasta":rec(fasta),"all_complete_sequences":rec(ledger),"designed_chain":"B","target_chain_fixed":"A","sequence_count":8,"arguments":args,"elapsed_seconds":time.time()-started,"cuda_device_count":0,"cpu_only":True,"scientific_comparison":False,"slurm_job_id":os.environ["SLURM_JOB_ID"],"scheduler_record":subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)}
out=O/"acceptance.json";out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"status":result["status"],"receipt":rec(out)},indent=2))

