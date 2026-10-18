import os,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
from screening_transfer import dump,read,rec
import benchmark_common_review as c
c.cpu()
out=R/"steps/23_common_review/runs"/("native_controls_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False)
cohorts=out/"native_controls_only.json"
dump(cohorts,dict(status="PREDECLARED_NATIVE_RECOVERY_CONTROLS_ONLY_NO_GENERATED_COHORT",selected=[],coverage=[],scientific_scope="COMPUTATIONAL_REVIEWER_RECOVERY_NOT_GENERATOR_BENCHMARK_RESULTS"))
gate=out/"predeclared_gate.json"
dump(gate,dict(common_review_gate=dict(score="R0",threshold=1.0,operator=">=",aggregation="all_required_models_median",scope="COMPUTATIONAL_ONLY"),primary_endpoint="R1_continuous",operational_pass=None,gate_source="root protocol predeclared before generation on 2026-10-11",scope="NATIVE_RECOVERY_CONTROLS_ONLY"))
registry=R/"steps/23_common_review/inputs/registry7_bridge13010.json"
msa=R/"steps/23_common_review/runs/msa_content_12983/msa.json"
result=c.prepare(registry,msa,cohorts,out/"inference_plan.json",gate)
print("READY_FOR_ROOT_FREEZE_NATIVE_ONLY",result,flush=True)

