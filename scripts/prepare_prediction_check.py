import json,sys
from pathlib import Path
import yaml
from ppiblocker.common import load_run,read_json
from ppiblocker.pipeline import prepare
ROOT=Path("/lustre/users/u21111210118/projects/test9")
m=load_run(sys.argv[1],{"POSE_ACCEPTED"})
pose=read_json(m["outputs"]["pose"]["path"])
config=read_json(m["outputs"]["config"]["path"])
config["proteins"]=[{"sequence":pose["observed_target_sequence"]},{"sequence":pose["observed_partner_sequence"]}]
config["structure"]={}
config["prediction"].update(samples=3,seed=2042)
path=ROOT/"steps/00_bootstrap/runs/rebuild_20260920/prediction_branch.yaml"
path.write_text(yaml.safe_dump(config,sort_keys=False))
result=prepare(ROOT,path)
assert read_json(result)["status"]=="NEEDS_PREDICTION"
print(json.dumps({"prediction_input_manifest":str(result)}))

