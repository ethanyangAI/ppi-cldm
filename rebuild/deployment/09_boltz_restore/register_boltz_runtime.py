from pathlib import Path
from datetime import datetime, timezone
from ppiblocker.common import collect_runtime, atomic_json, read_json, record_file, require, load_run
R=Path("/lustre/users/u21111210118/projects/test9")
O=R/"steps/09_boltz_restore/outputs"
lock=R/"source/environment/runtime-lock-boltz.json"
require(not lock.exists(),"LOCK_ALREADY_EXISTS","Explicit initial registration refuses overwrite")
accept=read_json(O/"boltz_restore_acceptance.json")
require(accept["status"]=="BOLTZ_RESTORE_ACCEPTED_CPU_IMPORT_AND_ASSET_CHECKS_NO_INFERENCE","RESTORE_NOT_ACCEPTED",str(O))
state=collect_runtime(R,"boltz")
mt=state["molecule_tree"]
require(mt["file_count"]==accept["mols_files"] and mt["bytes"]==accept["mols_bytes"] and mt["tree_sha256"]==accept["mols_tree_sha256"],"MOLECULE_PAYLOAD_MISMATCH","Restoration acceptance differs from live state")
for filename in ("boltz2_conf.ckpt","boltz2_aff.ckpt"):
 receipt=read_json(R/"assets/boltz"/(filename+".receipt.json"))
 require(receipt["status"]=="HASH_VERIFIED" and receipt["hf_commit"]=="6fdef46d763fee7fbb83ca5501ccceff43b85607","ASSET_PROVENANCE_MISMATCH",filename)
 require(receipt["bytes"]==state["assets"][filename]["bytes"],"ASSET_SIZE_MISMATCH",filename)
upstream=R/"steps/03_design/runs/20261002T114616Z_cfa6d86555db/manifest.json"
m=load_run(upstream,{"DESIGNS_GENERATED"})
require(m["candidate_count"]==1,"SMOKE_SCOPE_MISMATCH","Expected exactly one fresh candidate")
atomic_json(lock,state)
receipt={"status":"BOLTZ_INITIAL_RUNTIME_LOCK_REGISTERED","registered_utc":datetime.now(timezone.utc).isoformat(),"slurm_job_id":__import__("os").environ["SLURM_JOB_ID"],"runtime_lock":record_file(lock),"restoration_acceptance":record_file(O/"boltz_restore_acceptance.json"),"upstream_design":record_file(upstream),"molecule_tree":mt,"collect_runtime_calls":1,"lock_overwritten":False}
atomic_json(O/"runtime_lock_registration.json",receipt)
print(receipt,flush=True)
