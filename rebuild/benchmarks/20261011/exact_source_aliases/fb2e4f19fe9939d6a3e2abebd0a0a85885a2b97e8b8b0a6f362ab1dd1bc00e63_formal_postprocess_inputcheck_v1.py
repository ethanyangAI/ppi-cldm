#!/usr/bin/env python3
"""Only real existing input/receipt API connectivity; no generation/inference."""
import importlib.util,json,os
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
ENTRY=R/"steps/24_benchmark_delivery/frozen/formal_postprocess_v1_13250/code/formal_postprocess_v1.py"
spec=importlib.util.spec_from_file_location("post",ENTRY);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
guard=p.cpu();snapshot=p.immutable()
out=R/"steps/24_benchmark_delivery/runs"/("formal_postprocess_inputcheck_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
c=p.module("common");c.require_immutable_source_context();c.target_registry(p.PREPARED,out/"registry.json")
new=p.read(out/"registry.json");old=p.read(p.verify(p.pin("previous_registry")));old_by={t["target_id"]:t for t in old["targets"]}
assert {t["target_id"] for t in new["targets"]}==p.TARGETS
for t in new["targets"]:
 assert {k:v for k,v in t.items() if k!="input_manifest"}=={k:v for k,v in old_by[t["target_id"]].items() if k!="input_manifest"}
msa=p.read(p.verify(p.pin("msa")));by={t["target_id"]:t for t in new["targets"]};checks=[]
for row in msa["records"]:
 text=p.verify(row["file"]).read_text();diagnostics=c.a3m_rows(text,by[row["target_id"]]["sequence"])
 checks.append(dict(target_id=row["target_id"],a3m=row["file"],diagnostics=diagnostics))
assert len(checks)==7 and {x["target_id"] for x in checks}==p.TARGETS
final=p.dump(out/"acceptance.json",dict(status="COMMON_INPUT_BINDING_CHAINFIX7_AND_FROZEN_MSA_READBACK_PASS",
 allocation=guard,source_snapshot=snapshot,script=p.rec(__file__),common_source=p.pin("common"),prepared_inputs=p.rec(p.PREPARED),
 previous_registry=p.pin("previous_registry"),metadata_only_registry=p.rec(out/"registry.json"),msa=p.pin("msa"),
 checks=checks,no_new_predictions=True,formal_plan_frozen_or_executed=False))
print(json.dumps(final))

