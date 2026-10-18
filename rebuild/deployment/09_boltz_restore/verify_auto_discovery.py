import json,os,subprocess
from pathlib import Path
from copy import deepcopy
import yaml
from ppiblocker.common import read_json,load_run,atomic_json,record_file,require
R=Path("/lustre/users/u21111210118/projects/test9");O=R/"steps/09_boltz_restore/outputs"
original=R/"steps/01_pose/runs/20261002T114404Z_3857d8ffc36e/manifest.json"
known=load_run(original,{"POSE_ACCEPTED"})
cfg=deepcopy(read_json(known["outputs"]["config"]["path"]))
cfg["structure"]={"mode":"retrieve"}
cfg["context_review"]["interaction_evidence"]="Independent experimental evidence supports the specified MDM2/p53 fragments; discover an experimental assembly by their two UniProt accessions without a supplied PDB or chain hint"
cp=O/"MDM2_p53_auto_discovery_smoke.yaml"
require(not cp.exists(),"OUTPUT_EXISTS",str(cp));cp.write_text(yaml.safe_dump(cfg,sort_keys=False))
argv=[str(R/"env/core/bin/python"),"-m","ppiblocker.cli","--root",str(R),"prepare",str(cp)]
result=subprocess.run(argv,text=True,capture_output=True,timeout=720)
(O/"auto_discovery_stdout.json").write_text(result.stdout)
(O/"auto_discovery_stderr.txt").write_text(result.stderr)
receipt={"status":"AUTO_DISCOVERY_NOT_YET_ACCEPTED","cpu_job_id":os.environ["SLURM_JOB_ID"],"config":record_file(cp),"command":argv,"exit_code":result.returncode,"stdout":record_file(O/"auto_discovery_stdout.json"),"stderr":record_file(O/"auto_discovery_stderr.txt"),"pdb_chain_assembly_hint_provided":False,"thresholds_changed":False}
if result.stdout.strip():
 cli=json.loads(result.stdout)
 if cli.get("manifest"):
  mp=Path(cli["manifest"]);m=read_json(mp);receipt["manifest"]=record_file(mp);receipt["prepare_status"]=m["status"]
  if m["status"]=="POSE_ACCEPTED":
   m=load_run(mp,{"POSE_ACCEPTED"})
   pose=read_json(m["outputs"]["pose"]["path"]);ret=read_json(m["outputs"]["retrieval"]["path"]);proteins=read_json(m["outputs"]["proteins"]["path"])
   require(pose["source"]["kind"]=="rcsb_experimental_assembly","UNEXPECTED_STRUCTURE_SOURCE",str(pose["source"]))
   searches=[r for r in ret["receipts"] if "search.rcsb.org/rcsbsearch/" in r["url"]]
   require(len(searches)==1,"AUTO_SEARCH_RECEIPT_MISSING","Actual two-accession search must be recorded")
   search=read_json(searches[0]["path"])
   require(pose["source"]["pdb"] in [x["identifier"] for x in search["result_set"]],"SEARCH_SOURCE_MISMATCH","Selected source not returned by actual search")
   require(pose["observed_target_sequence"]==proteins[0]["sequence"] and pose["observed_partner_sequence"]==proteins[1]["sequence"],"CONSTRUCT_MISMATCH","Observed construct must exactly match requested fragment")
   receipt.update(status="AUTO_EXPERIMENTAL_DISCOVERY_ACCEPTED",structure_source=pose["source"],search_total_count=search.get("total_count"),search_returned_ids=[x["identifier"] for x in search["result_set"]],rejected_assemblies=ret["rejected"],search_receipt=searches[0],exact_requested_constructs=True,manifest_files_verified=len(m.get("file_inventory",[])),evidence_tier=m["evidence_tier"])
  else:
   receipt["error"]=m.get("error");receipt["classification"]="unresolved_no_accepted_structure" if m["status"]=="NEEDS_PREDICTION" else "prepare_failed_requires_diagnosis"
else:receipt["classification"]="CLI_FAILED_REQUIRES_DIAGNOSIS"
atomic_json(O/"auto_discovery_acceptance.json",receipt)
print(json.dumps(receipt,indent=2),flush=True)
require(receipt["status"]=="AUTO_EXPERIMENTAL_DISCOVERY_ACCEPTED","AUTO_DISCOVERY_NOT_ACCEPTED","Inspect captured outputs/receipt; do not equate network failure with absence")
