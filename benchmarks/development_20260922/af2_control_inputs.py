import os,shutil,hashlib,copy
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,require
from ppiblocker.structure import read_structure,write_pdb
root=Path("/lustre/users/u21111210118/projects/test9")
p=root/"steps/41_control_constructs/runs/20260922T101321Z_2f8f58bad35d/outputs/controls.json"
ep=root/"steps/52_control_extension/runs/20260922T103806Z_35c0f36f8467/outputs/controls.json"
run=Run(root,"60_af2_control_inputs",[record_file(p),record_file(ep)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 entries=[]
 for row in read_json(p):
  cs,_=read_structure(verify_file(row["archive_matches"][0]));target=next(c for c in cs if c["sequence"]==row["B_seq"]);binder=next(c for c in cs if c["sequence"]==row["A_seq"])
  cid="ctrl_"+hashlib.sha256(row["binder_id"].encode()).hexdigest()[:12]
  native=run.path/"outputs"/(cid+".pdb");write_pdb(native,[target,binder])
  entries.append(dict(id=cid,source_id=row["binder_id"],target=row["target_id"],target_sequence=row["B_seq"],sequence=row["A_seq"],label=row["binder"],native=record_file(native),backbone=record_file(native),reference_role="author_design_model_not_native_partner"))
 for row in read_json(ep):
  require(row["status"]=="AUTHOR_MODEL_EXACT_BINDER_CORE","CONTROL_IDENTITY",row["id"])
  entries.append(dict(id="bc_"+row["id"],source_id=row["id"],target=row["target"],target_sequence=row["target_sequence"],sequence=row["sequence"],label=row["label"],native=row["backbone"],backbone=row["backbone"],reference_role="author_design_model_not_native_partner"))
 require(len(entries)==78,"CONTROL_COUNT",str(len(entries)))
 for i,e in enumerate(entries):e["group"]=f"batch_{i//12}"
 plan=run.path/"outputs/plan.json";atomic_json(plan,dict(entries=entries,analysis_role="retrospective_calibration",groups=7,protocol="AF2 multimer v3 model1 seeds1042-1044 max3recycles targetMSA128:256 singlebinder no templates no relaxation; BBF14 single target sequence",no_generated_binders_uploaded=True));run.output("plan",plan)
 worker=root/"source/benchmarks/development_20260922/af2_msa_worker.py";shutil.copy2(worker,run.path/"qc/msa_worker.py")
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",JAX_PLATFORMS="cpu",CUDA_VISIBLE_DEVICES="");env.pop("PYTHONPATH",None)
 checked_command([root/"env/colabfold/bin/python",worker,plan,run.path/"outputs/msa_queries"],run.path/"work",run.path/"logs/msa.log",env,timeout=2400)
 run.output("inputs",run.path/"outputs/msa_queries/inputs.json");run.output("target_receipts",run.path/"outputs/msa_queries/target_receipts.json")
 print(run.finish("MSA_INPUTS_VALIDATED","calibration_inputs_not_results"),flush=True)
except Exception as e:run.fail(e);raise
