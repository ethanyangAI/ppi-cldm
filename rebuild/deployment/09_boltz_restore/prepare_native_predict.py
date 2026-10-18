from pathlib import Path
from copy import deepcopy
import yaml
from ppiblocker.common import read_json,atomic_json,record_file,load_run,require
from ppiblocker.pipeline import prepare
R=Path("/lustre/users/u21111210118/projects/test9");O=R/"steps/09_boltz_restore/outputs"
reference=R/"steps/01_pose/runs/20261002T114404Z_3857d8ffc36e/manifest.json"
m=load_run(reference,{"POSE_ACCEPTED"})
config=deepcopy(read_json(m["outputs"]["config"]["path"]))
config["structure"]={"mode":"predict_only"}
config["context_review"]["interaction_evidence"]="Independent experimental evidence supports this fragment interaction; coordinates withheld from the prediction and retained only for post hoc accuracy audit"
cp=O/"MDM2_p53_blind_predict_smoke.yaml"
require(not cp.exists(),"OUTPUT_EXISTS",str(cp))
cp.write_text(yaml.safe_dump(config,sort_keys=False))
prepared=prepare(R,cp)
p=read_json(prepared)
require(p["status"]=="NEEDS_PREDICTION","UNEXPECTED_PREPARE_STATUS",p["status"])
retrieval=read_json(p["outputs"]["retrieval"]["path"])
require(retrieval["search_performed"] is False and retrieval["experimental_coordinates_accessed"] is False,"REFERENCE_LEAKAGE",str(retrieval))
atomic_json(O/"native_predict_prepare_receipt.json",{"status":"BLIND_NATIVE_PREDICT_READY","config":record_file(cp),"prepare_manifest":record_file(prepared),"withheld_reference_manifest":record_file(reference),"withheld_reference_structure":m["outputs"]["native"],"prediction_source":"sequences_only","template_or_contact_inputs":False,"thresholds_changed":False,"training_overlap":"unknown_not_novel_generalization_benchmark"})
(O/"native_predict_manifest_path.txt").write_text(str(prepared)+"\n")
print(prepared,flush=True)
