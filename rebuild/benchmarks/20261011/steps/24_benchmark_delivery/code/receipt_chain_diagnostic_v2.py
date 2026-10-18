#!/usr/bin/env python3
import collections,json,os
from pathlib import Path
import native_resource_closure_v2 as n
R=n.R;old=R/"steps/23_common_review/runs/downstream_frozen_13119/native74_review_13124"
out=Path(os.environ["NATIVE_CLOSURE_TEST_OUTPUT"]);manifest,assembly,a,raw,counts=n.native_evidence(old)
names=("manifest.json","assembly.json","score.json","raw_audit.json","score_acceptance.json","score_engine_original.json","score_metadata_repair.json")
seeds=[n.checksum(old/name) for name in names]+[manifest[k] for k in ("source","inference_plan","analysis_plan","membership")]
seeds+=[n.checksum(R/"steps/23_common_review/frozen/native_common_13051/source_bundle.json")]
builder=n.ClosureBuilder(R,out,old);queue=collections.deque((r,[]) for r in seeds);seen=set();gaps=[];revision_aliases=[]
while queue:
    r,chain=queue.popleft();k=n.key(r)
    if k in seen:continue
    seen.add(k)
    if n.recompute_dependency(r["path"]):continue
    try:p,basis=builder.resolve(r)
    except FileNotFoundError as error:
        gaps.append(dict(receipt=r,shortest_receipt_chain=chain,error=str(error)));continue
    if basis!="EXACT_ORIGINAL_RESOURCE":revision_aliases.append(dict(receipt=r,physical=n.checksum(p),basis=basis))
    if p.suffix==".json":
        for nested,trail in n.receipts(n.read(p)):
            queue.append((nested,chain+[dict(parent=r,field=list(trail))]))
result=dict(status="RECEIPT_GRAPH_DIAGNOSTIC_ONLY_NOT_ACCEPTANCE",n_exact_receipts_seen=len(seen),gaps=gaps,revision_aliases=revision_aliases)
n.dump(out/"receipt_graph_diagnostic.json",result)
print(json.dumps(result,indent=2),flush=True)

