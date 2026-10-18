import argparse,shutil,sys,os,subprocess,importlib.metadata as metadata
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,tree_fingerprint,require
from ppiblocker.structure import read_structure,write_pdb
from ppiblocker.benchmark_adapters import import_pool
from ppiblocker.pipeline import evaluate
from ppiblocker.benchmark import select
p=argparse.ArgumentParser();p.add_argument("root");p.add_argument("case");args=p.parse_args();root=Path(args.root)
checks=root/"steps/09_benchmark_registry/runs/20260920T125042Z_c5523f54f659/outputs/preparation_checks.json"
case=next(r for r in read_json(checks) if r["case_id"]==args.case)
# Explicit keys inspected from the frozen registry; method manifest is resolved below.
inputs=case["method_inputs_manifest"] if "method_inputs_manifest" in case else case["method_inputs"]
mp=verify_file(case["method_inputs_manifest"]);m=read_json(mp)
pose=verify_file(case["prepare_manifest"])
run=Run(root,"11_comparators",[record_file(checks),record_file(mp),record_file(pose)])
shutil.copy2(__file__,run.path/"qc/driver.py")
wrapper=root/"steps/11_comparators/code/boltzgen_seeded.py"
shutil.copy2(wrapper,run.path/"qc/boltzgen_seeded.py")
try:
 config=verify_file(m["outputs"]["boltzgen"]);contract=read_json(verify_file(m["outputs"]["contract"]))
 work=run.path/"work/boltzgen"
 runtime=run.path/"qc/external_runtime.json"
 atomic_json(runtime,dict(method="BoltzGen",version="0.3.2",packages=record_file(root/"env/boltzgen-freeze.txt"),
  package_files=tree_fingerprint(root/"env/boltzgen/lib/python3.11/site-packages/boltzgen"),
  asset_receipt=record_file(root/"env/boltzgen-assets.json"),compatibility=dict(use_kernels=False,precision=32,cuda12_optional_packages_omitted=True),
  seed=42,seed_wrapper=record_file(wrapper),numerical_bitwise_determinism_guaranteed=False))
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",OMP_NUM_THREADS="8",HF_HUB_DISABLE_XET="1",HF_ENDPOINT="https://hf-mirror.com");env.pop("PYTHONPATH",None)
 argv=[root/"env/boltzgen/bin/python",wrapper,"42","run",config,"--output",work,
  "--protocol","protein-anything","--num_designs","2","--inverse_fold_num_sequences","2",
  "--inverse_fold_avoid","C","--budget","4","--devices","1","--num_workers","0",
  "--cache",root/"assets/boltzgen","--use_kernels","false","--steps","design","inverse_folding",
  "--config","design","trainer.precision=32","--config","inverse_folding","trainer.precision=32","--no_subprocess"]
 assets=read_json(root/"env/boltzgen-assets.json")["assets"]
 for item in assets.values():verify_file(item)
 argv += ["--design_checkpoints",assets["boltzgen1_diverse.ckpt"]["path"],assets["boltzgen1_adherence.ckpt"]["path"],"--inverse_fold_checkpoint",assets["boltzgen1_ifold.ckpt"]["path"],"--folding_checkpoint",assets["boltz2_conf_final.ckpt"]["path"],"--moldir",assets["mols.zip"]["path"]]
 env["HF_HUB_OFFLINE"]="1"
 checked_command(argv,run.path/"work",run.path/"logs/boltzgen.log",env,timeout=10800)
 candidates=[]
 files=sorted((work/"intermediate_designs_inverse_folded").glob("*.cif"))
 files=[f for f in files if not f.stem.endswith("_native")]
 require(len(files)==4,"INCOMPLETE_EXTERNAL_POOL",f"Expected 4, found {len(files)}")
 for i,f in enumerate(files):
  chains,context=read_structure(f)
  targets=[c for c in chains if c["sequence"]==contract["target_sequence"]]
  require(len(chains)==2 and len(targets)==1 and not context,"BOLTZGEN_CHAIN_MAPPING",str(f))
  target=targets[0];binder=next(c for c in chains if c is not target)
  require(len(binder["sequence"])==65,"BOLTZGEN_LENGTH",str(f))
  dest=run.path/"outputs"/f"bg_{i}.pdb";write_pdb(dest,[target,binder])
  candidates.append(dict(id=f"bg_{i}",sequence=binder["sequence"],backbone=record_file(dest),raw_source=record_file(f)))
 pool=dict(schema_version=1,pose_manifest=record_file(pose),method="BoltzGen0.3.2",
  code_revision=read_json(runtime)["package_files"]["tree_sha256"],runtime_record=record_file(runtime),
  candidate_budget=dict(backbones=2,sequences_per_backbone=2,sequence_slots=4,seed=42),candidates=candidates)
 poolpath=run.path/"outputs/pool_contract.json";atomic_json(poolpath,pool);run.output("pool_contract",poolpath)
 design=import_pool(root,pose,poolpath);run.manifest["design_manifest"]=record_file(design);run.save()
 evaluation=evaluate(root,design);run.manifest["evaluation_manifest"]=record_file(evaluation);run.save()
 selection=select(root,evaluation,8);run.manifest["selection_manifest"]=record_file(selection)
 print(run.finish("EXTERNAL_COMPARISON_COMPLETE","computational_only",dict(case_id=args.case)),flush=True)
except Exception as e:run.fail(e);raise

