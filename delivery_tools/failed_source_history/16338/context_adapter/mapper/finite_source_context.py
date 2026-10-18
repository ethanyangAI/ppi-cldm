#!/usr/bin/env python3
"""Independent finite Source V10 provenance and six-parent exact source read views."""
import ast,copy,hashlib,io,json,subprocess,tokenize
from pathlib import Path
import exact_relative_bbf_context as b
R=b.R
def read(path):return json.loads(Path(path).read_text())
def scalar_identity(r):return dict(original_logical_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"])
def strict_snapshot(path,r):
 if path!=r["path"]:raise ValueError("Exact source snapshot path differs")
 return b.verify_bytes(r,True)
def receipt_edges(obj,trail=()):
 if isinstance(obj,dict):
  if {"path","bytes","sha256"}<=obj.keys()and isinstance(obj["path"],str):yield obj,trail
  for name,value in obj.items():yield from receipt_edges(value,trail+(str(name),))
 elif isinstance(obj,list):
  for i,value in enumerate(obj):yield from receipt_edges(value,trail+(str(i),))
"""Integrated finite source-alias policy; real pureCPU qualification repeats all actual proofs.
No restored or historical source code is executed. Unknown source permissions remain fatal.
"""
import ast,copy,json
from pathlib import Path

PREPARED_PLAN=json.loads("{\"schema\":\"prepared-finite-operative-source-alias-plan.v1\",\"status\":\"EXACT_LITERAL_SOURCE_SCOPE_FOR_NEW_CPU_REQUALIFICATION_NOT_ACCEPTED\",\"source_base\":\"source_refresh_relative_v9\",\"actual_failed_source_job\":\"13307\",\"actual_missing_diagnostic\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_missing_operative_inventory_13308/diagnostic.json\",\"bytes\":207548,\"sha256\":\"2a22a7f4aa4a787f934b72a1fe7ec4bf84c1891c08944120093519d4b469ba11\"},\"actual_saved_byte_diagnostic\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/diagnostic.json\",\"bytes\":75704,\"sha256\":\"48ce0453db4927cacea9804354fc9b0f598ca598922ff778f0f2024debc4b1ea\"},\"original_alias_registry\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_identity_n\":8,\"original_edge_n\":12,\"aliases\":[{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\",\"bytes\":50747},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/reconstructed_historical_source/3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740_benchmark_common_review.py\",\"bytes\":50747,\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\"},\"basis\":\"RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py\",\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\",\"bytes\":23056},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/reconstructed_historical_source/a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3_bbf_input_diagnostic.py\",\"bytes\":23056,\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\"},\"basis\":\"EXACT_RECORDED_BBF_SOURCE_RECONSTRUCTION_NOT_FOUND_ORIGINAL\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":36014,\"sha256\":\"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v3/source/benchmark_runtime.py\",\"bytes\":36014,\"sha256\":\"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7\"},\"basis\":\"EXISTING_READONLY_RUNTIME_SNAPSHOT\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":37816,\"sha256\":\"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v5/source/benchmark_runtime.py\",\"bytes\":37816,\"sha256\":\"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50\"},\"basis\":\"EXISTING_READONLY_RUNTIME_SNAPSHOT\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13180_source.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13168_reviewed_root_formal_helper.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/test_formal_benchmark_contract.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13168_contracts.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13168_source.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"}],\"edges\":[{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"source_field\":[\"common_score_source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\",\"bytes\":50747}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"source_field\":[\"source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py\",\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\",\"bytes\":23056}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13030/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"79347625bf297b8530a91fd5a200966d01128794babf7e75bb6d66bef7e72a0b\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13030/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"79347625bf297b8530a91fd5a200966d01128794babf7e75bb6d66bef7e72a0b\"},\"source_field\":[\"runtime\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":36014,\"sha256\":\"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13058/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"77d3e543e2b56fe22dacf4cbc167d9c7a86fd8af9d5486aa07811824e84e7fa7\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13058/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"77d3e543e2b56fe22dacf4cbc167d9c7a86fd8af9d5486aa07811824e84e7fa7\"},\"source_field\":[\"runtime\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":37816,\"sha256\":\"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13180/acceptance.json\",\"bytes\":3201,\"sha256\":\"b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13180/acceptance.json\",\"bytes\":3201,\"sha256\":\"b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb\"},\"source_field\":[\"source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"3\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"2\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"source_field\":[\"reviewed_root_formal_helper\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"source_field\":[\"contracts\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/test_formal_benchmark_contract.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"source_field\":[\"source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"1\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/test_formal_benchmark_contract.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"0\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"}}],\"source_acceptance\":false,\"current_execution_authorized\":false,\"raw_model_acceptance\":false,\"scientific_settings_changed\":false,\"licensed_runtime_or_model_assets_included\":false,\"BBF_actual_diagnostic\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/diagnostic.json\",\"bytes\":34363,\"sha256\":\"f77e8e0ec5331da3003349792dcb735f4d8836d014d7fa484e07321c1b3b5f3f\"}}")
ALLOWED_FOUND_BASES=frozenset({"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY","EXISTING_READONLY_RUNTIME_SNAPSHOT"})
RECONSTRUCTED_BASIS="RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL"

def source_alias_identity(r):
 if not isinstance(r,dict)or set(("path","bytes","sha256"))-set(r):raise ValueError("Complete source descriptor required")
 if type(r["path"])is not str or type(r["bytes"])is not int or r["bytes"]<0 or type(r["sha256"])is not str or len(r["sha256"])!=64:raise ValueError("Exact source identity types required")
 return r["path"],r["bytes"],r["sha256"]
def source_alias_field_value(obj,trail):
 for token in trail:
  if type(token)is not str:raise ValueError("String source field trail required")
  if isinstance(obj,list):
   if not token.isdigit()or str(int(token))!=token:raise ValueError("Exact decimal field index required")
   obj=obj[int(token)]
  elif isinstance(obj,dict):obj=obj[token]
  else:raise ValueError("Missing parent source field")
 return obj
def recorded_literal_replacements(freezer_bytes,expected):
 """One exact common-source s=common.read_text; twelve assignments; common.write_text(s) block."""
 tree=ast.parse(freezer_bytes.decode("utf-8"));body=tree.body
 anchors=[i for i,n in enumerate(body)if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="s"and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and n.value.func.attr=="read_text"and isinstance(n.value.func.value,ast.Name)and n.value.func.value.id=="common"and not n.value.args and not n.value.keywords]
 if len(anchors)!=1:raise ValueError("One authoritative common source read block required")
 i=anchors[0];rows=[]
 for n in body[i+1:i+13]:
  if not(isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="s"and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and isinstance(n.value.func.value,ast.Name)and n.value.func.value.id=="s"and n.value.func.attr=="replace"and len(n.value.args)==2 and not n.value.keywords and all(isinstance(a,ast.Constant)and type(a.value)is str for a in n.value.args)):raise ValueError("Only twelve recorded s.replace assignments allowed")
  rows.append([a.value for a in n.value.args])
 end=body[i+13]if len(body)>i+13 else None
 if not(isinstance(end,ast.Expr)and isinstance(end.value,ast.Call)and isinstance(end.value.func,ast.Attribute)and isinstance(end.value.func.value,ast.Name)and end.value.func.value.id=="common"and end.value.func.attr=="write_text"and len(end.value.args)==1 and isinstance(end.value.args[0],ast.Name)and end.value.args[0].id=="s"and not end.value.keywords):raise ValueError("Authoritative common block closing write required")
 if rows!=expected:raise ValueError("Exact twelve recorded common transformations required")
 return rows

def independent_recorded_replay(frozen_bytes,original_bytes,freezer_bytes,expected):
 tuples=recorded_literal_replacements(freezer_bytes,expected)
 text=frozen_bytes.decode("utf-8");reverse=[]
 for i,(old,new)in reversed(list(enumerate(tuples))):
  n=text.count(new)
  if n<1:raise ValueError("Recorded inverse anchor missing")
  text=text.replace(new,old);reverse.append({"recorded_index":i,"replacements":n})
 if text.encode("utf-8")!=original_bytes:raise ValueError("Independent inverse does not equal exact historical bytes")
 forward=[]
 for i,(old,new)in enumerate(tuples):
  n=text.count(old)
  if n<1:raise ValueError("Recorded forward anchor missing")
  text=text.replace(old,new);forward.append({"recorded_index":i,"replacements":n})
 if text.encode("utf-8")!=frozen_bytes:raise ValueError("Independent forward replay is not byte-identical")
 return dict(classification=RECONSTRUCTED_BASIS,inverse_equals_original_bytes=True,forward_equals_frozen_bytes=True,
  exact_replacement_tuples=tuples,reverse_log=reverse,forward_log=forward,freezer_executed=False,reconstructed_source_executed=False,current_execution_authorized=False)

class FiniteOperativeSourceAliases:
 """Verify each permission before caller dedup; there is no basename or unknown-path fallback."""
 def __init__(self,rows,edges,verify_readonly,reader,provenance_verifier,declared=PREPARED_PLAN):
  self.declared=copy.deepcopy(declared);self.verify=verify_readonly;self.reader=reader;self.provenance=provenance_verifier
  expected={source_alias_identity(x["original"]):x for x in self.declared["aliases"]}
  if len(expected)!=8 or len(rows)!=8:raise ValueError("Exactly eight predeclared source identities required")
  self.rows={};self.observed={}
  for row in rows:
   k=source_alias_identity(row["original"])
   if k not in expected or k in self.rows:raise ValueError("Unknown or duplicate finite source alias")
   pin=expected[k];canonical=row.get("canonical")
   if canonical is None:raise ValueError("Exact BBF evidence unresolved; no partial eight-source qualification")
   if source_alias_identity(canonical)[1:]!=k[1:]:raise ValueError("Alias changes source bytes")
   if pin["canonical"]is not None and canonical!=pin["canonical"]:raise ValueError("Selected literal readonly source snapshot differs")
   if row["basis"]!=pin["basis"]and pin["basis"]!="PENDING_EXACT_BBF_BYTE_PROOF":raise ValueError("Source provenance classification differs")
   if row["basis"]not in ALLOWED_FOUND_BASES|{RECONSTRUCTED_BASIS,"EXACT_RECORDED_BBF_SOURCE_RECONSTRUCTION_NOT_FOUND_ORIGINAL","EXISTING_EXACT_BBF_READONLY_BYTECOPY"}:raise ValueError("Unknown source provenance basis")
   self.verify(canonical["path"],canonical)
   proof=self.provenance(row)
   if not isinstance(proof,dict)or proof.get("classification")!=row["basis"]or proof.get("canonical_receipt")!=canonical or proof.get("current_execution_authorized")is not False:raise ValueError("Independently verified finite source provenance required")
   self.verify(canonical["path"],canonical)
   self.rows[k]={**copy.deepcopy(row),"independent_provenance":proof}
  expected_edges=self.declared["edges"]
  if edges!=expected_edges or len(edges)!=12:raise ValueError("Exact predeclared twelve source edge contexts required")
  self.edges={(source_alias_identity(e["source_parent"]),tuple(e["source_field"]),source_alias_identity(e["original"])):e for e in edges}
  if len(self.edges)!=12:raise ValueError("Duplicate predeclared source edge")
 def authorize(self,r,parent_context,trail):
  k=source_alias_identity(r)
  if k not in self.rows:return None
  if parent_context is None:raise ValueError("Known historical source requires its exact parent field")
  logical=parent_context["logical"];physical=parent_context["physical"];t=tuple(trail)
  edge=self.edges.get((source_alias_identity(logical),t,k))
  if edge is None:raise ValueError("Unknown parent/field permission for finite source identity")
  if physical!=edge["parent_canonical_receipt"]:raise ValueError("Source parent canonical identity differs")
  self.verify(physical["path"],physical)
  obj=self.reader(physical["path"])
  if source_alias_field_value(obj,t)!=r:raise ValueError("Actual source parent field differs")
  self.verify(physical["path"],physical)
  row=self.rows[k];self.verify(row["canonical"]["path"],row["canonical"])
  observed=dict(source_parent=logical,parent_canonical_receipt=physical,source_field=list(t),
   original_logical_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"],
   canonical_receipt=row["canonical"],basis=row["basis"],current_execution_authorized=False)
  self.observed[(source_alias_identity(logical),t,k)]=observed
  return observed
 def require_complete(self):
  if set(self.observed)!=set(self.edges):raise ValueError("All twelve original source edges must be actually observed")
  if {source_alias_identity(e["canonical_receipt"])for e in self.observed.values()}!={source_alias_identity(r["canonical"])for r in self.rows.values()}:raise ValueError("All eight source identities must be observed")
  for row in self.rows.values():self.verify(row["canonical"]["path"],row["canonical"])
  for edge in self.edges.values():
   parent=edge["parent_canonical_receipt"];self.verify(parent["path"],parent)
   if source_alias_field_value(self.reader(parent["path"]),tuple(edge["source_field"]))!=edge["original"]:raise ValueError("Final exact parent field changed")
   self.verify(parent["path"],parent)
  return dict(schema="finite-operative-source-alias-verification.v1",
   status="EXACT_EIGHT_SOURCE_IDENTITIES_AND_TWELVE_ORIGINAL_EDGES_CPU_VERIFIED_NOT_CURRENT_EXECUTION",
   source_identity_n=8,original_edge_n=12,aliases=list(self.rows.values()),observed_edges=list(self.observed.values()),
   original_JSON_bytes_unchanged=True,unknown_source_aliases_allowed=False,current_execution_authorized=False,
   historical_reconstruction_not_found_original=True,raw_models_reaudited=False,scientific_acceptance=False)


# Exact code restoration is source provenance; it never runs the old programs.
SOURCE_ALIAS_DIAGNOSTICS=(PREPARED_PLAN["actual_missing_diagnostic"],PREPARED_PLAN["actual_saved_byte_diagnostic"],PREPARED_PLAN["BBF_actual_diagnostic"])
BBF_REPLAY_PINS=json.loads("{\"target\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py\",\"bytes\":23056,\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\"},\"bundle\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/source_bundle.json\",\"bytes\":8124,\"sha256\":\"9b89ed8b673597002e6ce52cc6561e009ad2041a253b6484cfacaa7896c8c1e9\"},\"freezer\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/freeze_bbf.py\",\"bytes\":3857,\"sha256\":\"31fce180c514667831a736e34c340769a72836d641ea81d5a753d25910e30d02\"},\"launcher\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/freeze_launcher.py\",\"bytes\":4050,\"sha256\":\"5d4efd31a7ae3fed701a9f409499a2aa5f86f8ff143ab7b55d9c5ddab9b573c9\"},\"frozen\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/code/bbf_input_diagnostic.py\",\"bytes\":24842,\"sha256\":\"d2eefb850802a0b93a6724051218c5e686d556c9358d08ab17c7a28dabc247ca\"},\"records\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/source_bbf_recorded_recovery_diagnostic_v1/historical_patch_records.json\",\"bytes\":6584,\"sha256\":\"e28d3267075826d7e728fac58dcea4df700c328ee74c5c6ef381db4a1c553b33\"},\"transforms\":[[\"ROOT/\\\"source/rebuild/benchmark_common_review.py\\\"\",\"Path(__file__).resolve().parent/\\\"benchmark_common_review.py\\\"\"],[\"ROOT/\\\"vendor\\\"/(\\\"IPSAE_\\\"+REVISION[:12])/\\\"ipsae.py\\\"\",\"Path(__file__).resolve().parent/\\\"vendor/ipsae.py\\\"\"]],\"reconstructed\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/reconstructed_historical_source/a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3_bbf_input_diagnostic.py\",\"bytes\":23056,\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\"},\"record_proofs\":[{\"record_line\":1381,\"timestamp\":\"2026-10-11T05:06:04.414Z\",\"tool_item_id\":\"ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f\",\"call_id\":\"call_1507b4e1755942269e8cf5d83799737f\",\"raw_record_sha256\":\"764f91b32b9838d7ea24d5df9c90ca1911096244323db3d8d8bf58c5f69f39b2\",\"input_sha256\":\"05f3c35c1f3e7f6912736e8113256f1ff139d34fb7e29be491c352bb85719ab2\",\"literal_patch_count\":10,\"extracted_patches\":[{\"record_line\":1381,\"input_line\":2,\"old\":\"msa=np.asarray(data[f[\\\"msa_feature_key\\\"]])\",\"new\":\"msa=np.asarray(data[f.get(\\\"msa_feature_key\\\",f.get(\\\"msa_feat_key\\\"))])\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":3,\"old\":\"    mapping={int(k)-1:int(v)-1 for k,v in job[\\\"target_query_to_template_indices\\\"].items()}\",\"new\":\"    prev=np.asarray(data[f.get(\\\"initial_prev_pos_key\\\",\\\"prev_pos\\\")],float)\\n    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError(\\\"Initial previous-position guess leaked\\\")\\n    cbmask=np.asarray(data[\\\"template_pseudo_beta_mask\\\"],float);cbpos=np.asarray(data[\\\"template_pseudo_beta\\\"],float)\\n    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError(\\\"Pseudo-beta template features malformed\\\")\\n    rawmask=np.asarray(data[\\\"batch_all_atom_mask\\\"],float);rawpos=np.asarray(data[\\\"batch_all_atom_positions\\\"],float)\\n    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError(\\\"Raw target-only source batch shape\\\")\\n    mapping={int(k)-1:int(v)-1 for k,v in job[\\\"target_query_to_template_indices\\\"].items()}\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":4,\"old\":\"    if mask[:,T:].any() or pos[:,T:].any():\",\"new\":\"    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError(\\\"Binder raw/template pseudo-beta leakage\\\")\\n    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError(\\\"Missing target raw/pseudo-beta leakage\\\")\\n    if mask[:,T:].any() or pos[:,T:].any():\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":5,\"old\":\"    if not job[\\\"target_template_enabled\\\"] and n!=0:\",\"new\":\"    if not job[\\\"target_template_enabled\\\"] and (cbmask.any() or cbpos.any()):raise ValueError(\\\"No-template pseudo-beta channel leaked\\\")\\n    if not job[\\\"target_template_enabled\\\"] and n!=0:\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":6,\"old\":\"actual_query_length=L)\",\"new\":\"actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\"all_models_feature_arrays_identical\\\"))\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":7,\"old\":\"        if worker.get(\\\"allocation\\\",{}).get(\\\"allocated_gpu_count\\\")!=1:raise ValueError(\\\"GPU worker actual scheduler allocation missing/not1\\\")\",\"new\":\"        allocation_receipt=worker.get(\\\"allocation\\\",{})\\n        if allocation_receipt.get(\\\"allocated_gpu_count\\\")!=1:raise ValueError(\\\"GPU worker actual scheduler allocation missing/not1\\\")\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":8,\"old\":\"components(conf[\\\"iptm\\\"],float(pp[na:].mean()),ip,cp)\",\"new\":\"components(conf.get(\\\"iptm\\\",conf.get(\\\"globaliptm\\\")),float(pp[na:].mean()),ip,cp)\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":9,\"old\":\"global_iptm=float(conf[\\\"iptm\\\"])\",\"new\":\"global_iptm=float(conf.get(\\\"iptm\\\",conf.get(\\\"globaliptm\\\")))\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":10,\"old\":\"        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)))\",\"new\":\"        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))\\n        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":11,\"old\":\"actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\"all_models_feature_arrays_identical\\\"))\",\"new\":\"actual_query_length=L,initial_prev_pos_nonzero=0)\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"}],\"historical_exec_input_executed\":false},{\"record_line\":1408,\"timestamp\":\"2026-10-11T05:07:12.719Z\",\"tool_item_id\":\"ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f\",\"call_id\":\"call_695893637f52466ba2c6f5638ac69a8b\",\"raw_record_sha256\":\"1d348fde3009169f67d9639b364db152ef288ff831f07a23e565f5d0ed6073a0\",\"input_sha256\":\"6488e36acaa4fb96916e70175981a62a4280e225a224a4ffb44ba9f98a242c41\",\"literal_patch_count\":2,\"extracted_patches\":[{\"record_line\":1408,\"input_line\":2,\"old\":\"    checked=[]\\n    for key,job\",\"new\":\"    verify(features[\\\"source\\\"])\\n    checked=[]\\n    for key,job\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1408,\"input_line\":3,\"old\":\"        f=actual[key];actual_stats=feature_arrays(job,f)\",\"new\":\"        f=actual[key];actual_stats=feature_arrays(job,f)\\n        if f[\\\"actual_validated_model_slots\\\"]!=job[\\\"slots\\\"] or not f[\\\"all_models_feature_arrays_identical\\\"]:raise ValueError(\\\"Every fixed model actual forward feature proof required\\\")\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"}],\"historical_exec_input_executed\":false}]}")
COMMON_REPLAY_PINS=json.loads("{\"status\":\"RECONSTRUCTED_EXACT_HISTORICAL_SOURCE_FROM_RECORDED_FREEZER_REVERSE_AND_FORWARD_REPLAY_NOT_CURRENT_EXECUTION\",\"classification\":\"RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL\",\"original_logical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"bytes\":50747,\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\"},\"historical_bundle\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13022/source_bundle.json\",\"bytes\":10053,\"sha256\":\"729e3acd0cd371cf2a4dd571850d241c4a9a0fb2470090b178f36d8bc058f500\"},\"source_field\":[\"files\",\"0\"],\"recorded_freezer\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/code/freeze_native_review.py\",\"bytes\":6790,\"sha256\":\"1306a59077d99702da69c88f8b142e6e09a0ce5affcf5c45028009df069ea9fd\"},\"frozen_source\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13022/code/benchmark_common_review.py\",\"bytes\":50999,\"sha256\":\"78fbf3a5dc7c2b7ca1729ad7d2a94fffd6ca0110c4ab203becddd2a737ceeae4\"},\"reconstructed_source\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/reconstructed_historical_source/3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740_benchmark_common_review.py\",\"bytes\":50747,\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\"},\"exact_twelve_replacements\":[[\"STEP=ROOT/\\\"steps/23_common_review\\\"\",\"STEP=ROOT/\\\"steps/23_common_review\\\"\\nFROZEN_DIR=Path(__file__).resolve().parent\"],[\"sys.path.insert(0,str(ROOT/\\\"source/src\\\"))\",\"sys.path.insert(0,str(FROZEN_DIR/\\\"src\\\"))\"],[\"ROOT/\\\"source/rebuild/screening_transfer.py\\\"\",\"FROZEN_DIR/\\\"screening_transfer.py\\\"\"],[\"ROOT/\\\"source/rebuild/control_msa_check.py\\\"\",\"FROZEN_DIR/\\\"control_msa_check.py\\\"\"],[\"ROOT/\\\"source/src/ppiblocker/structure.py\\\"\",\"FROZEN_DIR/\\\"src/ppiblocker/structure.py\\\"\"],[\"ROOT/\\\"steps/03_af2_restore/inference_env.sh\\\"\",\"FROZEN_DIR/\\\"runtime_entries/af2_inference_env.sh\\\"\"],[\"ROOT/\\\"env/colabfold/bin/colabfold_batch\\\"\",\"FROZEN_DIR/\\\"runtime_entries/colabfold_batch\\\"\"],[\"ROOT/\\\"env/boltz/bin/boltz\\\"\",\"FROZEN_DIR/\\\"runtime_entries/boltz\\\"\"],[\"ROOT/\\\"vendor\\\"/(\\\"IPSAE_\\\"+REVISION[:12])/\\\"ipsae.py\\\"\",\"FROZEN_DIR/\\\"vendor/ipsae.py\\\"\"],[\"str(ROOT/\\\"source/rebuild\\\"),job[\\\"input\\\"][\\\"path\\\"]\",\"str(FROZEN_DIR),job[\\\"input\\\"][\\\"path\\\"]\"],[\"method_origin_present=False)\",\"method_origin_present=False,frozen_source_bundle=rec(FROZEN_DIR.parent/\\\"source_bundle.json\\\"))\"],[\"allocation=allocated,runs=runs)\",\"allocation=allocated,runs=runs,source=plan[\\\"source\\\"],frozen_source_bundle=plan[\\\"frozen_source_bundle\\\"],runtime_locks=plan[\\\"runtime_locks\\\"],receipt_policy=\\\"CPU_PRECOMPUTED_SOURCE_AND_DEPENDENCY_HASH_REFERENCES_NO_GPU_HASH_TASK\\\")\"]],\"reverse_log\":[{\"recorded_index\":11,\"source_line\":38,\"replacements\":1},{\"recorded_index\":10,\"source_line\":37,\"replacements\":1},{\"recorded_index\":9,\"source_line\":36,\"replacements\":1},{\"recorded_index\":8,\"source_line\":35,\"replacements\":2},{\"recorded_index\":7,\"source_line\":34,\"replacements\":1},{\"recorded_index\":6,\"source_line\":33,\"replacements\":2},{\"recorded_index\":5,\"source_line\":32,\"replacements\":1},{\"recorded_index\":4,\"source_line\":31,\"replacements\":1},{\"recorded_index\":3,\"source_line\":30,\"replacements\":1},{\"recorded_index\":2,\"source_line\":29,\"replacements\":1},{\"recorded_index\":1,\"source_line\":28,\"replacements\":1},{\"recorded_index\":0,\"source_line\":27,\"replacements\":1}],\"forward_log\":[{\"recorded_index\":0,\"source_line\":27,\"replacements\":1},{\"recorded_index\":1,\"source_line\":28,\"replacements\":1},{\"recorded_index\":2,\"source_line\":29,\"replacements\":1},{\"recorded_index\":3,\"source_line\":30,\"replacements\":1},{\"recorded_index\":4,\"source_line\":31,\"replacements\":1},{\"recorded_index\":5,\"source_line\":32,\"replacements\":1},{\"recorded_index\":6,\"source_line\":33,\"replacements\":2},{\"recorded_index\":7,\"source_line\":34,\"replacements\":1},{\"recorded_index\":8,\"source_line\":35,\"replacements\":2},{\"recorded_index\":9,\"source_line\":36,\"replacements\":1},{\"recorded_index\":10,\"source_line\":37,\"replacements\":1},{\"recorded_index\":11,\"source_line\":38,\"replacements\":1}],\"old_source_size_and_SHA_verified\":true,\"forward_replay_byte_identical\":true,\"historical_freezer_executed\":false,\"reconstructed_source_executed\":false,\"current_execution_authorized\":false,\"new_alias_accepted\":false,\"source_acceptance\":false}")
def source_alias_need(value,message):
 if not value:raise ValueError(message)
def alias_read_bytes(r):
 p=strict_snapshot(r["path"],r);value=p.read_bytes();strict_snapshot(r["path"],r);return value
def alias_json(r,read_bytes):
 data=read_bytes(r);obj=json.loads(data.decode("utf-8"))
 source_alias_need(read_bytes(r)==data,"Source proof changed during read");return obj
def alias_terminal(job,name,state="COMPLETED",exit_code="0:0"):
 raw=subprocess.check_output(["sacct","-X","-j",job,"--noheader","--parsable2","--format=JobIDRaw,User%64,Account%64,Partition%64,JobName%100,State%40,ExitCode,AllocCPUS,AllocTRES%300"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.strip()and x.split("|")[0]==job]
 source_alias_need(len(rows)==1,"One actual exact diagnostic job required")
 result=dict(job_id=job,expected_job_name=name,expected_state=state,expected_exit_code=exit_code,raw_sacct=raw)
 source_alias_terminal_record(result);return result
def source_alias_terminal_record(result):
 jid=result["job_id"];raw=result["raw_sacct"];rows=[x.split("|")for x in raw.splitlines()if x.strip()and x.split("|")[0]==jid]
 source_alias_need(len(rows)==1,"One saved diagnostic job required")
 row=rows[0];source_alias_need(len(row)==9 and row[1:8]==["u21111210118","u21111210118","organ",result["expected_job_name"],result.get("expected_state","COMPLETED"),result.get("expected_exit_code","0:0"),"1"],"Actual diagnostic CPU terminal ownership differs")
 tres={}
 for part in row[8].split(","):
  source_alias_need("="in part,"Malformed diagnostic allocated TRES");k,v=part.split("=",1);source_alias_need(k not in tres,"Duplicate diagnostic TRES");tres[k]=v
 source_alias_need(tres.get("cpu")=="1","Allocated diagnostic CPU1 required")
 for k,v in tres.items():
  if k.startswith("gres/gpu"):source_alias_need(v.isdecimal()and int(v)==0,"Diagnostic allocated GPU must be0")
 return result

def js_literal(token):
 source_alias_need(len(token)>=2 and token[0]in ("'",'"')and token[-1]==token[0]and not token.startswith(token[0]*3),"Only simple JS quoted literal supported")
 result=[];i=1
 escapes={"n":"\n","r":"\r","t":"\t","b":"\b","f":"\f","v":"\v","\\":"\\","'":"'",'"':'"'}
 while i<len(token)-1:
  c=token[i]
  if c=="\\":
   i+=1;source_alias_need(i<len(token)-1 and token[i]in escapes,"Unknown/nonshared JavaScript escape rejected");result.append(escapes[token[i]])
  else:
   source_alias_need(c not in ("\n","\r",token[0]),"Unescaped JS quoted literal delimiter");result.append(c)
  i+=1
 return "".join(result)
def recorded_js_patches(receipt,read_bytes):
 data=alias_json(receipt,read_bytes)
 source_alias_need(data.get("schema")=="exact-two-historical-BBF-patch-records-data-only.v1"and data.get("original_session_id")=="01a12917-8539-7e20-89ae-37dd9dcc35c1"and data.get("original_local_session_file")=="/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl"and data.get("recorded_tool_calls_executed")is False,"Only exact authorized two historical input records permitted")
 declarations=[
  (1381,"2026-10-11T05:06:04.414Z","ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f","call_1507b4e1755942269e8cf5d83799737f",'let c=load("bbf_diagnostic_code_v2");',10),
  (1408,"2026-10-11T05:07:12.719Z","ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f","call_695893637f52466ba2c6f5638ac69a8b",'let c=load("bbf_diagnostic_code_v3");',2)]
 source_alias_need(len(data["records"])==2,"Exactly two historical input records required")
 patches=[];proofs=[]
 for row,decl in zip(data["records"],declarations):
  line,timestamp,item_id,call_id,start,wanted=decl
  source_alias_need(row["record_line"]==line and type(row["raw_JSONL_record"])is str,"Authorized historical record identity differs")
  item=json.loads(row["raw_JSONL_record"]);payload=item["payload"];code=payload["input"];lines=code.splitlines()
  source_alias_need(item["type"]=="response_item"and item["timestamp"]==timestamp and payload["type"]=="custom_tool_call"and payload["id"]==item_id and payload["call_id"]==call_id and payload["name"]=="exec"and type(code)is str and lines[0]==start,"Exact historical tool input metadata differs")
  statements=[(i+1,text)for i,text in enumerate(lines)if text.lstrip().startswith("c=")]
  source_alias_need(len(statements)==wanted and all(text.startswith("c=c.replace(")for _,text in statements),"Only exact literal c.replace chain permitted")
  extracted=[]
  for innerline,text in statements:
   parsed=ast.parse(text);source_alias_need(len(parsed.body)==1 and isinstance(parsed.body[0],ast.Assign),"One literal assignment statement required")
   node=parsed.body[0];value=node.value
   source_alias_need(len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=="c"and isinstance(value,ast.Call)and isinstance(value.func,ast.Attribute)and isinstance(value.func.value,ast.Name)and value.func.value.id=="c"and value.func.attr=="replace"and len(value.args)==2 and not value.keywords and all(isinstance(x,ast.Constant)and type(x.value)is str for x in value.args),"Only c.replace(two literal strings) AST permitted")
   tokens=[t.string for t in tokenize.generate_tokens(io.StringIO(text).readline)if t.type==tokenize.STRING]
   source_alias_need(len(tokens)==2,"Implicit concatenation/multiple literals forbidden")
   pair=tuple(js_literal(t)for t in tokens);source_alias_need(pair==tuple(x.value for x in value.args)and pair[0]and pair[1]and pair[0]!=pair[1]and "$"not in pair[1],"Shared JS/AST literal decoding or replacement expansion differs")
   extracted.append(dict(record_line=line,input_line=innerline,old=pair[0],new=pair[1],replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));patches.append(pair)
  proofs.append(dict(record_line=line,timestamp=timestamp,tool_item_id=item_id,call_id=call_id,raw_record_sha256=hashlib.sha256(row["raw_JSONL_record"].encode()).hexdigest(),input_sha256=hashlib.sha256(code.encode()).hexdigest(),literal_patch_count=wanted,extracted_patches=extracted,historical_exec_input_executed=False))
 source_alias_need(len(patches)==12,"Exact total10+2 historical transformations required")
 return patches,proofs

def alias_literal_freeze_chain(node):
 if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="replace":
  source_alias_need(len(node.args)==2 and not node.keywords and all(isinstance(a,ast.Constant)and type(a.value)is str for a in node.args),"Literal recorded BBF freeze pair required")
  return alias_literal_freeze_chain(node.func.value)+[[a.value for a in node.args]]
 source_alias_need(isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="read_text"and isinstance(node.func.value,ast.Name)and node.func.value.id=="own"and not node.args and not node.keywords,"Authoritative BBF own.read_text origin required")
 return []
def scalar_source_proof_view(obj):
 """Only called for five exact independently verified provenance parents below."""
 if isinstance(obj,dict):
  if {"path","bytes","sha256"}<=obj.keys()and isinstance(obj["path"],str):
   metadata={"original_logical_path":obj["path"],"expected_bytes":obj["bytes"],"expected_sha256":obj["sha256"],"role":"EXACT_SOURCE_PROVENANCE_OBSERVATION_NOT_CURRENT_INPUT_OR_RAW_ACCEPTANCE","current_execution_authorized":False,"raw_byte_acceptance":False}
   return {"source_provenance_observation":metadata,"additional_metadata":{k:scalar_source_proof_view(v)for k,v in obj.items()if k not in {"path","bytes","sha256"}}}
  return {k:scalar_source_proof_view(v)for k,v in obj.items()}
 if isinstance(obj,list):return [scalar_source_proof_view(v)for v in obj]
 return obj
def alias_restore_proof_parents(qualified,read_bytes):
 # No schema-only marker: parent descriptors, full expected bytes, and complete
 # verified reconstruction inputs are bound to the actual Source CPU proof.
 actual=qualify_source_alias_inputs(read_bytes,qualified["terminal_accounting"])
 source_alias_need(actual["schema"]==qualified["schema"]and actual["aliases"]==qualified["aliases"]and actual["reconstruction_proofs"]==qualified["reconstruction_proofs"]and actual["proof_parent_views"]==qualified["proof_parent_views"]and actual["canonical_source_and_provenance_inputs"]==qualified["canonical_source_and_provenance_inputs"],"Saved source provenance proof fork/truncation")
 return actual
def qualify_source_alias_inputs(read_bytes=alias_read_bytes,terminal_accounting=None):
 jobs=(("13308","test9_missing_source_diagnostic_v1","COMPLETED","0:0"),("13310","test9_saved_source_diagnostic_v1","COMPLETED","0:0"),("13313","test9_bbf_source_diagnostic_v1","COMPLETED","0:0"),("13307","test9_source_relative_v9","FAILED","1:0"))
 terminal_accounting=[alias_terminal(*j)for j in jobs]if terminal_accounting is None else terminal_accounting
 source_alias_need(len(terminal_accounting)==4 and [(r["job_id"],r["expected_job_name"],r.get("expected_state","COMPLETED"),r.get("expected_exit_code","0:0"))for r in terminal_accounting]==list(jobs),"Exact three diagnostics and failed V9 numeric terminal records required")
 for row in terminal_accounting:source_alias_terminal_record(row)
 missing,saved,final=[alias_json(r,read_bytes)for r in SOURCE_ALIAS_DIAGNOSTICS]
 source_alias_need(missing.get("schema")=="source-missing-exact-operative-inventory-diagnostic-only.v1"and missing.get("status")=="FINITE_ACCESSIBLE_MISSING_OPERATIVE_TEXT_EDGES_DIAGNOSED_NO_SOURCE_ACCEPTANCE_NO_AUTHORIZATION"and missing.get("job_id")=="13308"and missing.get("missing_identity_count")==8 and missing.get("parent_count")==6 and missing.get("missing_edge_count")==12 and missing.get("source_acceptance")is False,"Actual13308 complete finite failed-source inventory required")
 actual_edges=[dict(source_parent=e["parent"],parent_canonical_receipt=e["physical_parent"],source_field=e["field"],original=e["operative_receipt_after_declared_context_normalization"])for e in missing["edges"]]
 source_alias_need(actual_edges==PREPARED_PLAN["edges"],"Actual eight-source twelve-edge identity fork")
 source_alias_need(saved.get("schema")=="saved-source-exact-byte-recovery-diagnostic-only.v1"and saved.get("status")=="FINITE_EIGHT_SOURCE_IDENTITIES_SEARCHED_NO_SOURCE_OR_ALIAS_ACCEPTANCE"and saved.get("job_id")=="13310"and saved.get("input_missing_inventory")==SOURCE_ALIAS_DIAGNOSTICS[0]and {source_alias_identity(r)for r in saved["targets"]}=={source_alias_identity(r["original"])for r in PREPARED_PLAN["aliases"]}and saved.get("matched_identity_count")==6 and saved.get("reconstructed_historical_identity_count")==1,"Actual13310 whole finite source identity required")
 source_alias_need(final.get("schema")=="bbf-recorded-source-recovery-diagnostic-only.v1"and final.get("status")=="EXACT_PRECEDING_SEVEN_IDENTITIES_AND_ONLY_RECORDED_BBF_TRANSFORM_CPU_DIAGNOSED_NO_SOURCE_ACCEPTANCE"and final.get("job_id")=="13313"and final.get("previous_actual_diagnostic")==SOURCE_ALIAS_DIAGNOSTICS[1]and final.get("whole_missing_identity_count")==8 and final.get("all_eight_byte_identities_closed")is True and final.get("unresolved_source_identities")==[],"Actual13313 eight identities closed required")
 for obj,jid in zip((missing,saved,final),("13308","13310","13313")):
  source_alias_need(obj.get("actual_allocation",{}).get("job_id")==jid and obj.get("source_acceptance")is False and obj.get("current_execution_authorized",False)is False and obj.get("default_changed")is False,"Diagnostic-only scope/current source preservation required")
 inputs={source_alias_identity(r):r for r in SOURCE_ALIAS_DIAGNOSTICS}
 def add(r):
  read_bytes(r);inputs[source_alias_identity(r)]=r
 for r in saved["executed_source_files"]+final["executed_source_files"]:add(r)
 for k in ("failed_source","failed_source_software92","failed_source_snapshot","failed_source_contracts","failed_source_typed_incomplete"):add(missing[k])
 registry=PREPARED_PLAN["original_alias_registry"];reg=alias_json(registry,read_bytes);add(registry)
 source_alias_need(saved["original_five_alias_registry"]==registry and len(reg["historical_exact_byte_aliases"])==5 and len(saved["existing_five_declared_aliases"])==5,"Original five-row registered source aliases required")
 for i,item in enumerate(saved["existing_five_declared_aliases"]):
  raw=reg["historical_exact_byte_aliases"][i]
  source_alias_need(raw["logical_receipt"]==item["logical_receipt"]and raw["resolved_readonly_exact_byte_receipt"]==item["physical_receipt"]and raw["historical_report"]==item["historical_report"]and raw["original_mutable_path_hash_claimed_equal"]is False,"Actual registered original/frozen source lineage differs")
  source_alias_need(source_alias_identity(item["logical_receipt"])[1:]==source_alias_identity(item["physical_receipt"])[1:],"Registered original byte identity differs")
  add(item["physical_receipt"]);add(item["historical_report"])
 common=saved["recorded_common_reconstruction"]
 source_alias_need(common==COMMON_REPLAY_PINS,"Actual common recorded reconstruction proof differs")
 for k in ("historical_bundle","recorded_freezer","frozen_source","reconstructed_source"):add(common[k])
 cb=alias_json(common["historical_bundle"],read_bytes)
 source_alias_need(cb.get("status")=="IMMUTABLE_COMMON_REVIEW_SOURCE_BUNDLE"and cb.get("freeze_job")=="13022"and cb.get("source")==common["frozen_source"]and cb["files"][0]["original"]==common["original_logical_receipt"]and cb["files"][0]["frozen"]==common["frozen_source"],"Original common source bundle lineage differs")
 # Every actual frozen origin source is qualified; original mutable fields in
 # the immutable source bundle remain provenance observations only.
 for pair in cb["files"]:add(pair["frozen"])
 common_replay=independent_recorded_replay(read_bytes(common["frozen_source"]),read_bytes(common["reconstructed_source"]),read_bytes(common["recorded_freezer"]),common["exact_twelve_replacements"])
 source_alias_need(common_replay["reverse_log"]==[{k:r[k]for k in ("recorded_index","replacements")}for r in common["reverse_log"]]and common_replay["forward_log"]==[{k:r[k]for k in ("recorded_index","replacements")}for r in common["forward_log"]],"Actual common inverse/forward numeric logs differ")
 actual_bbf=final["bbf_recorded_transform"]
 source_alias_need(actual_bbf["requested_logical_receipt"]==BBF_REPLAY_PINS["target"]and actual_bbf["historical_source_bundle"]==BBF_REPLAY_PINS["bundle"]and actual_bbf["recorded_freezer"]==BBF_REPLAY_PINS["freezer"]and actual_bbf["recorded_launcher_source"]==BBF_REPLAY_PINS["launcher"]and actual_bbf["frozen_source"]==BBF_REPLAY_PINS["frozen"]and actual_bbf["historical_patch_records"]==BBF_REPLAY_PINS["records"]and actual_bbf["reconstructed_source"]==BBF_REPLAY_PINS["reconstructed"],"Exact recorded BBF proof lineage differs")
 for k in ("bundle","freezer","launcher","frozen","records","reconstructed"):add(BBF_REPLAY_PINS[k])
 bb=alias_json(BBF_REPLAY_PINS["bundle"],read_bytes)
 source_alias_need(bb.get("status")=="BBF110_SCIENTIFIC_INPUTS_AND_SOURCE_CONTENT_ACCEPTED_AWAIT_NEW_BUDGET_GUARD_LAUNCHER"and bb.get("cpu_job")=="13061"and bb["source"]==BBF_REPLAY_PINS["frozen"]and bb["source_files"][0]==BBF_REPLAY_PINS["frozen"],"Exact BBF frozen provenance bundle differs")
 for r in bb["source_files"]:add(r)
 patches,patch_proofs=recorded_js_patches(BBF_REPLAY_PINS["records"],read_bytes)
 source_alias_need(patch_proofs==BBF_REPLAY_PINS["record_proofs"]and actual_bbf["historical_patch_record_proofs"]==patch_proofs,"BBF literal record data/proof fork")
 tree=ast.parse(read_bytes(BBF_REPLAY_PINS["freezer"]).decode());nodes=[n for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="source"]
 source_alias_need(len(nodes)==1 and nodes[0].lineno==13,"Exact BBF recorded source block required")
 transforms=alias_literal_freeze_chain(nodes[0].value);source_alias_need(transforms==BBF_REPLAY_PINS["transforms"],"Only recorded BBF Python freeze2 allowed")
 frozen=read_bytes(BBF_REPLAY_PINS["frozen"]);candidate=frozen.decode();freeze_reverse=[]
 for i,(old,new)in reversed(list(enumerate(transforms))):
  count=candidate.count(new);source_alias_need(count>0,"BBF freeze inverse missing");freeze_reverse.append(dict(index=i,replacements=count));candidate=candidate.replace(new,old)
 post=candidate.encode();patch_reverse=[]
 for i,(old,new)in reversed(list(enumerate(patches))):
  count=candidate.count(new);source_alias_need(count>0,"BBF JS inverse missing");patch_reverse.append(dict(index=i,available_occurrences=count,replacements=1,replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));candidate=candidate.replace(new,old,1)
 original=read_bytes(BBF_REPLAY_PINS["reconstructed"]);source_alias_need(candidate.encode()==original,"BBF inverse does not equal exact old source")
 patch_forward=[]
 for i,(old,new)in enumerate(patches):
  count=candidate.count(old);source_alias_need(count>0,"BBF JS forward missing");patch_forward.append(dict(index=i,available_occurrences=count,replacements=1,replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));candidate=candidate.replace(old,new,1)
 source_alias_need(candidate.encode()==post and len(post)==24830 and hashlib.sha256(post).hexdigest()=="c0d6528aeb736ac34cf80fe88e9dde203f89959306d50e7a6a8dffb7eee82583","BBF intermediate exact content differs")
 freeze_forward=[]
 for i,(old,new)in enumerate(transforms):
  count=candidate.count(old);source_alias_need(count>0,"BBF Python forward missing");freeze_forward.append(dict(index=i,replacements=count,replace_semantics="PYTHON_LITERAL_ALL_OCCURRENCES"));candidate=candidate.replace(old,new)
 source_alias_need(candidate.encode()==frozen and actual_bbf["reverse_log"]==freeze_reverse and actual_bbf["forward_log"]==freeze_forward and actual_bbf["historical_patch_reverse_log"]==patch_reverse and actual_bbf["historical_patch_forward_log"]==patch_forward,"BBF full independent replay/saved log differs")
 bbf_replay=dict(classification="EXACT_RECORDED_BBF_SOURCE_RECONSTRUCTION_NOT_FOUND_ORIGINAL",historical_patch_record_proofs=patch_proofs,python_freeze_pairs=transforms,freeze_reverse=freeze_reverse,freeze_forward=freeze_forward,JS_first_reverse=patch_reverse,JS_first_forward=patch_forward,original_byte_identity=BBF_REPLAY_PINS["target"],intermediate_bytes=24830,intermediate_sha256="c0d6528aeb736ac34cf80fe88e9dde203f89959306d50e7a6a8dffb7eee82583",inverse_equals_original=True,forward_equals_frozen=True,source_or_historical_exec_executed=False,current_execution_authorized=False)
 aliases=[]
 for row in PREPARED_PLAN["aliases"]:
  source_alias_need(row["canonical"]is not None and source_alias_identity(row["original"])[1:]==source_alias_identity(row["canonical"])[1:],"All eight exact source bytes required");add(row["canonical"])
  if row["basis"]=="EXISTING_READONLY_RUNTIME_SNAPSHOT":
   source_alias_need(any(c["physical_content_receipt"]==row["canonical"]and row["original"]in c["matches_missing_receipts"]and c["readonly"]is True for c in saved["source_candidates"]),"Runtime exact actual source origin missing")
  aliases.append(dict(original=row["original"],canonical=row["canonical"],basis=row["basis"]))
 proof_parents=list(SOURCE_ALIAS_DIAGNOSTICS)+[common["historical_bundle"],BBF_REPLAY_PINS["bundle"]]
 views=[dict(parent_manifest=r,view=scalar_source_proof_view(alias_json(r,read_bytes)),role="EXACT_INDEPENDENTLY_VERIFIED_SOURCE_PROVENANCE_VIEW_NOT_CURRENT_INPUT_OR_RAW_GATE")for r in proof_parents]
 for r in list(inputs.values()):read_bytes(r)
 return dict(schema="finite-source-recovery-inputs-qualification.v1",status="EXACT_SELECTED8_SOURCE_BYTES_RECORDS_REPLAYS_AND_PROOF_PARENTS_CPU_VERIFIED_NOT_CURRENT_EXECUTION",terminal_accounting=terminal_accounting,diagnostics=list(SOURCE_ALIAS_DIAGNOSTICS),aliases=aliases,reconstruction_proofs=dict(common=common_replay,BBF=bbf_replay),proof_parent_views=views,canonical_source_and_provenance_inputs=list(inputs.values()),source_identity_n=8,original_known_edge_n=12,original_JSON_bytes_unchanged=True,raw_byte_acceptance=False,current_execution_authorized=False,models_executed=False)
def source_alias_provenance_verifier(qualified,row):
 expected=next((r for r in qualified["aliases"]if r["original"]==row["original"]),None)
 source_alias_need(expected=={k:row[k]for k in ("original","canonical","basis")},"Qualified selected source provenance differs")
 return dict(classification=row["basis"],canonical_receipt=row["canonical"],full_input_qualification_schema=qualified["schema"],reconstruction=qualified["reconstruction_proofs"]["common"if row["original"]["path"].endswith("benchmark_common_review.py")else"BBF"]if "RECONSTRUCTION"in row["basis"]or row["basis"]==RECONSTRUCTED_BASIS else None,current_execution_authorized=False)

def export_source_alias_qualification(qualified):
 """New proof fields never embed a historical receipt-shaped original child."""
 value=copy.deepcopy(qualified)
 value["aliases"]=[dict(original_logical_path=r["original"]["path"],expected_bytes=r["original"]["bytes"],expected_sha256=r["original"]["sha256"],canonical_receipt=r["canonical"],basis=r["basis"])for r in qualified["aliases"]]
 bbf=value["reconstruction_proofs"]["BBF"]
 bbf["original_byte_identity"]=scalar_identity(bbf["original_byte_identity"])
 return value
def verify_exported_source_alias_qualification(saved,read_bytes=alias_read_bytes,restore=False):
 source_alias_need(not restore or read_bytes is not alias_read_bytes,"Restore requires an explicit restored-index byte reader; live default is forbidden")
 actual=qualify_source_alias_inputs(read_bytes,saved["terminal_accounting"]if restore else None)
 expected=export_source_alias_qualification(actual)
 source_alias_need(saved==expected,"Exact source alias qualification changed, truncated or forked")
 return actual
def source_alias_provenance_postreadback(qualified,read_bytes=alias_read_bytes):
 rows=qualified["canonical_source_and_provenance_inputs"]
 source_alias_need(len({source_alias_identity(r)for r in rows})==len(rows),"Duplicate qualified provenance input")
 for r in rows:read_bytes(r)
 return dict(status="ALL_EXACT_CANONICAL_SOURCE_AND_PROVENANCE_INPUTS_REVERIFIED_AFTER_GRAPH_WALK",input_n=len(rows),verified_inputs=copy.deepcopy(rows),unknown_source_permission_added=False)
def source_alias_proof_parent_view(r,qualified,read_bytes=alias_read_bytes):
 rows=[x for x in qualified["proof_parent_views"]if x["parent_manifest"]==r]
 if not rows:return None
 source_alias_need(len(rows)==1,"Duplicate exact source proof parent")
 obj=alias_json(r,read_bytes)
 source_alias_need(scalar_source_proof_view(obj)==rows[0]["view"],"Exact verified source proof parent view differs")
 return copy.deepcopy(rows[0]["view"])
def export_finite_source_alias_verification(value):
 out=copy.deepcopy(value)
 for row in out["aliases"]:
  original=row.pop("original");row.update(scalar_identity(original))
  replay=row["independent_provenance"].get("reconstruction")
  if replay and "original_byte_identity"in replay:replay["original_byte_identity"]=scalar_identity(replay["original_byte_identity"])
 return out


ALIASES_STATUS="EXACT_EIGHT_HISTORICAL_SOURCE_BYTES_AND_TWELVE_CONTEXTS_CPU_ACCEPTED_NO_CURRENT_EXECUTION"
def verify_source_alias_scope(base,closure,read_exact,restore=False):
 def data(r):
  path=read_exact(r)
  source_alias_need(not(path.stat().st_mode&0o222),"Readonly source-alias metadata/evidence required")
  return path.read_bytes()
 artifacts={}
 for name in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index"):
  source_alias_need(isinstance(base.get(name),dict)and base.get(name)==closure.get(name),"Actual Source V10 exact alias artifact chain differs")
  artifacts[name]=base[name]
 source_alias_need(base.get("exact_recovered_source_identity_n")==closure.get("exact_recovered_source_identity_n")==8 and base.get("exact_original_source_edge_n")==closure.get("exact_original_source_edge_n")==12,"Actual complete V10 eight identities/twelve edges required")
 saved=alias_json(artifacts["finite_source_recovery_inputs_qualification"],data)
 qualified=verify_exported_source_alias_qualification(saved,data,restore=restore)
 verifier=FiniteOperativeSourceAliases(qualified["aliases"],PREPARED_PLAN["edges"],lambda p,r:read_exact(r),lambda p:alias_json(next(e["parent_canonical_receipt"]for e in PREPARED_PLAN["edges"]if e["parent_canonical_receipt"]["path"]==p),data),lambda row:source_alias_provenance_verifier(qualified,row))
 for edge in PREPARED_PLAN["edges"]:verifier.authorize(edge["original"],dict(logical=edge["source_parent"],physical=edge["parent_canonical_receipt"]),edge["source_field"])
 expected=export_finite_source_alias_verification(verifier.require_complete())
 actual=alias_json(artifacts["finite_source_alias_verification"],data)
 def canonical(value):
  result=copy.deepcopy(value)
  result["observed_edges"]=sorted(result["observed_edges"],key=lambda x:(x["source_parent"]["path"],x["source_field"],x["expected_sha256"]))
  return result
 source_alias_need(canonical(actual)==canonical(expected),"Saved actual Source alias verification missing/truncated/forked")
 index=alias_json(artifacts["finite_exact_source_alias_index"],data)
 source_alias_need(index.get("schema")=="finite-exact-source-alias-index.v1"and index.get("status")==ALIASES_STATUS and index.get("qualification")==artifacts["finite_source_recovery_inputs_qualification"]and index.get("verification")==artifacts["finite_source_alias_verification"],"Exact Source alias index source/proof pointers differ")
 source_alias_need(index.get("aliases")==saved["aliases"],"Complete Source alias index aliases required")
 source_alias_need(sorted(index.get("edges",[]),key=lambda x:(x["source_parent"]["path"],x["source_field"],x["expected_sha256"]))==canonical(expected)["observed_edges"]and index.get("source_identity_n")==8 and index.get("original_edge_n")==12 and index.get("current_execution_authorized")is False and index.get("raw_byte_acceptance")is False and index.get("original_JSON_bytes_unchanged")is True,"Complete Source alias index twelve contexts/nonexecution required")
 source_alias_provenance_postreadback(qualified,data)
 generated=qualify_generated_source_outputs(base,closure,qualified,data)
 qualified["_generated_source_closure"]=generated
 return qualified,dict(generated_source_output_scope=export_generated_source_scope(generated),schema="independent-source-alias-and-provenance-verification.v1",status="EXACT_V10_SELECTED8_ORIGINAL12_AND_FIVE_PROOF_PARENTS_INDEPENDENTLY_CPU_VERIFIED",artifacts=artifacts,qualification=saved,verification=actual,index=index,restore_only=restore,raw_JSON_changed=False,current_execution_authorized=False,scientific_acceptance=False)
def replace_source_field(obj,trail,value):
 parent=source_alias_field_value(obj,trail[:-1]);token=trail[-1]
 if isinstance(parent,list):parent[int(token)]=value
 else:parent[token]=value
def exact_source_manifest_view(parent,obj,qualified,read_bytes=alias_read_bytes):
 generated=qualified.get("_generated_source_closure")
 if generated is not None and parent==generated["parent_manifest"]:
  source_alias_need(obj==alias_json(parent,read_bytes),"Exact generated Source closure caller bytes/payload forked")
  view=copy.deepcopy(obj)
  for row in generated["contexts"]:
   source_alias_need(source_alias_field_value(obj,row["source_field"])==row["original"],"Generated Source closure exact observation forked")
   read_bytes(row["canonical_receipt"]);replace_source_field(view,row["source_field"],row["canonical_receipt"])
  return view,dict(role="ACTUAL_V10_GENERATED_CLOSURE_SIX_PARENT_PROOF_BOUND_SOURCE_OBSERVATIONS",parent_manifest=parent,contexts=[dict(source_field=x["source_field"],**scalar_identity(x["original"]),canonical_receipt=x["canonical_receipt"],current_execution_authorized=False)for x in generated["contexts"]],raw_JSON_changed=False)
 proof=source_alias_proof_parent_view(parent,qualified,read_bytes)
 if proof is not None:
  source_alias_need(obj==alias_json(parent,read_bytes),"Exact proof parent caller payload differs from original bytes")
  return proof,dict(role="EXACT_SOURCE_PROVENANCE_OBSERVATIONS_SCALAR_VIEW",parent_manifest=parent,source_observations_scalar=True)
 edges=[e for e in PREPARED_PLAN["edges"]if e["source_parent"]==parent]
 if not edges:return None,None
 source_alias_need(obj==alias_json(parent,read_bytes),"Exact original source-parent JSON bytes/payload differ")
 view=copy.deepcopy(obj);contexts=[]
 for edge in edges:
  original=source_alias_field_value(obj,edge["source_field"])
  source_alias_need(original==edge["original"],"Exact original source field differs")
  row=next(r for r in qualified["aliases"]if r["original"]==original)
  read_bytes(row["canonical"])
  replace_source_field(view,edge["source_field"],dict(original,path=row["canonical"]["path"]))
  contexts.append(dict(source_field=edge["source_field"],**scalar_identity(original),canonical_receipt=row["canonical"],basis=row["basis"],current_execution_authorized=False))
 return view,dict(role="EXACT_ORIGINAL_SOURCE_PARENT_TWELVE_FIELDS_TO_SELECTED_BYTE_IDENTICAL_SOURCE",parent_manifest=parent,contexts=contexts,raw_JSON_changed=False)
class VerifiedFiniteSourceReader:
 def __init__(self,base,closure,reader,read_exact,parent_aliases=(),restore=False):
  self.qualified,self.verification=verify_source_alias_scope(base,closure,read_exact,restore)
  self.reader=reader;self.exact=read_exact;self.restore=restore;self.used=[]
  originals={source_alias_identity(e["source_parent"]):e["source_parent"]for e in PREPARED_PLAN["edges"]}
  originals.update({source_alias_identity(v["parent_manifest"]):v["parent_manifest"]for v in self.qualified["proof_parent_views"]})
  generated=self.qualified["_generated_source_closure"]["parent_manifest"];originals[source_alias_identity(generated)]=generated
  self.parents={r["path"]:dict(logical=r,physical=r)for r in originals.values()}
  for row in parent_aliases:
   source_alias_need(isinstance(row,dict)and set(row)=={"logical","physical"}and source_alias_identity(row["logical"])in originals,"Only explicit exact finite source/proof parent aliases allowed")
   source_alias_need(source_alias_identity(row["logical"])[1:]==source_alias_identity(row["physical"])[1:]and row["physical"]["path"]not in self.parents,"Finite source parent alias byte fork/duplicate")
   read_exact(row["physical"]);self.parents[row["physical"]["path"]]=row
 def data(self,r):
  path=self.exact(r);source_alias_need(not(path.stat().st_mode&0o222),"Readonly finite source/proof input required")
  value=path.read_bytes();self.exact(r);return value
 def __call__(self,path):
  row=self.parents.get(str(path))
  if row is None:return self.reader(path)
  logical,physical=row["logical"],row["physical"];self.exact(physical);obj=self.reader(path)
  view,proof=exact_source_manifest_view(logical,obj,self.qualified,self.data)
  source_alias_need(view is not None,"Exact finite source parent has no qualified view")
  self.exact(physical);self.used.append(dict(logical_parent=logical,physical_parent=physical,**proof))
  return view
 def require_all_used(self):
  expected={source_alias_identity(r)for r in required_parent_receipts(self.qualified)}
  source_alias_need({source_alias_identity(x["logical_parent"])for x in self.used}==expected,"All six source and five proof original parents must actually use their narrow views")
  source_alias_provenance_postreadback(self.qualified,self.data)
  return True
 def proof(self):
  return dict(schema="exact-finite-source-and-provenance-read-view.v1",verification=self.verification,read_views_used=self.used,source_identity_n=8,original_source_parent_n=6,original_source_edge_n=12,source_proof_parent_n=5,generated_source_output_parent_n=1,generated_source_observation_n=16,raw_JSON_changed=False,module_local_reader_only=True,restore_only=self.restore,current_execution_authorized=False,no_live_root_fallback=self.restore)

def normalize_source_edge(r,parent,trail,qualified,read_bytes=alias_read_bytes):
 identity=source_alias_identity(r)
 rows=[x for x in qualified["aliases"]if source_alias_identity(x["original"])==identity]
 if not rows:return r,None
 edges=[e for e in PREPARED_PLAN["edges"]if e["original"]==r and e["source_parent"]==parent and tuple(e["source_field"])==tuple(trail)]
 source_alias_need(len(edges)==1,"Known historical source bytes require exact original parent/field permission before dedup")
 source_alias_need(source_alias_field_value(alias_json(parent,read_bytes),trail)==r,"Actual source parent field forked")
 read_bytes(rows[0]["canonical"])
 return rows[0]["canonical"],dict(source_parent=parent,source_field=list(trail),**scalar_identity(r),canonical_receipt=rows[0]["canonical"],basis=rows[0]["basis"],current_execution_authorized=False)
def verify_saved_alias_proofs(accepted,base,closure,read_exact,restore=False):
 qualified,actual=verify_source_alias_scope(base,closure,read_exact,restore)
 for name in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index"):
  source_alias_need(accepted.get(name)==base[name],"Mapper accepted finite-source artifact pointer differs")
 saved=json.loads(read_exact(accepted["finite_source_independent_verification"]).read_text())
 # Restore recreates the same content with explicit restored-only flag.
 comparison=copy.deepcopy(actual);comparison["restore_only"]=False
 source_alias_need(saved==comparison,"Actual independent complete source/provenance proof missing/truncated/forked")
 view=json.loads(read_exact(accepted["finite_source_read_view_proof"]).read_text())
 source_alias_need(view.get("schema")=="exact-finite-source-and-provenance-read-view.v1"and view.get("verification")==comparison and view.get("raw_JSON_changed")is False and view.get("module_local_reader_only")is True and view.get("current_execution_authorized")is False,"Saved complete finite source view proof differs")
 parents={source_alias_identity(e["source_parent"]):e["source_parent"]for e in PREPARED_PLAN["edges"]}
 parents.update({source_alias_identity(v["parent_manifest"]):v["parent_manifest"]for v in qualified["proof_parent_views"]})
 generated=qualified["_generated_source_closure"]["parent_manifest"];parents[source_alias_identity(generated)]=generated
 saved_readview_shape(view)
 rows=view.get("read_views_used");source_alias_need(isinstance(rows,list)and len(rows)==len(parents)and {source_alias_identity(v["logical_parent"])for v in rows}==set(parents),"Saved exact six source/five proof parents required")
 def data(r):return read_exact(r).read_bytes()
 for row in rows:
  p=row["logical_parent"];physical=row["physical_parent"]
  source_alias_need(source_alias_identity(p)[1:]==source_alias_identity(physical)[1:],"Saved parent physical byte identity differs");read_exact(physical)
  _,proof=exact_source_manifest_view(p,alias_json(p,data),qualified,data)
  source_alias_need(row==dict(logical_parent=p,physical_parent=physical,**proof),"Saved finite parent view rows are incomplete/forked")
 return qualified,actual

def required_parent_receipts(qualified):
 parents={source_alias_identity(e["source_parent"]):e["source_parent"]for e in PREPARED_PLAN["edges"]}
 parents.update({source_alias_identity(x["parent_manifest"]):x["parent_manifest"]for x in qualified["proof_parent_views"]})
 generated=qualified["_generated_source_closure"]["parent_manifest"];parents[source_alias_identity(generated)]=generated
 source_alias_need(len(parents)==12,"Exactly six original source/five proof/one generated Source closure parents required")
 return [parents[k]for k in sorted(parents)]

def qualify_generated_source_outputs(base,closure,qualified,read_bytes):
 parent=base["source_closure"];source_alias_need(alias_json(parent,read_bytes)==closure,"Exact accepted Source closure bytes/payload required")
 source_alias_need(closure.get("schema")=="benchmark-source-receipt-closure.v1"and closure.get("status")=="EXACT_CURRENT_TEXT_AND_SOURCE_DEPENDENCY_CLOSURE_WITH_TYPED_HISTORY","Actual generated Source closure role differs")
 selected={source_alias_identity(r["original"]):r for r in qualified["aliases"]};contexts=[];edge_ids=set();source_ids=set()
 for i,edge in enumerate(closure["edges"]):
  old=edge.get("receipt");identity=source_alias_identity(old)if isinstance(old,dict)and {"path","bytes","sha256"}<=old.keys()else None
  if identity not in selected:continue
  row=selected[identity];matching=[e for e in PREPARED_PLAN["edges"]if e["original"]==old and e["source_parent"]["path"]==edge.get("parent")and e["source_field"]==edge.get("field")]
  source_alias_need(len(matching)==1 and edge.get("physical")==row["canonical"]and edge.get("role")=="EXACT_TEXT_RECEIPT_READBACK"and edge.get("resolution_basis")=="EXACT_ACCEPTED_BYTECOPY_ALIAS","Generated Source edge lacks exact original six-parent/field/canonical proof")
  expected=dict(source_parent=matching[0]["source_parent"],parent_canonical_receipt=matching[0]["parent_canonical_receipt"],source_field=matching[0]["source_field"],**scalar_identity(old),canonical_receipt=row["canonical"],basis=row["basis"],current_execution_authorized=False)
  source_alias_need(edge.get("finite_exact_source_alias_context")==expected and identity not in edge_ids,"Generated Source exact finite edge proof fork/duplicate")
  edge_ids.add(identity);contexts.append(dict(source_field=["edges",str(i),"receipt"],original=old,canonical_receipt=row["canonical"]))
 for i,item in enumerate(closure["source_receipts"]):
  old=item.get("logical");identity=source_alias_identity(old)if isinstance(old,dict)and {"path","bytes","sha256"}<=old.keys()else None
  if identity not in selected:continue
  row=selected[identity];source_alias_need(item.get("physical")==row["canonical"]and item.get("basis")=="EXACT_ACCEPTED_BYTECOPY_ALIAS"and identity not in source_ids,"Generated Source logical/physical identity fork/duplicate")
  source_ids.add(identity);contexts.append(dict(source_field=["source_receipts",str(i),"logical"],original=old,canonical_receipt=row["canonical"]))
 source_alias_need(edge_ids==source_ids==set(selected)and len(contexts)==16,"Exact generated Source closure eight edge/eight source observations required")
 allowed={tuple(c["source_field"])for c in contexts}
 for r,trail in receipt_edges(closure):
  if source_alias_identity(r)in selected:source_alias_need(tuple(trail)in allowed,"Unknown generated Source observation field cannot gain alias permission")
 inclusion=alias_json(base["source_inclusion"],read_bytes)
 source_alias_need(inclusion.get("status")=="SOURCE_INCLUSION_AUDIT_PASS"and inclusion.get("source_receipt_closure")==parent and inclusion.get("issues")==[]and inclusion.get("applied")is False,"Actual nonstaged Source inclusion proof required")
 source_alias_need(not any(source_alias_identity(r)in selected for r,_ in receipt_edges(inclusion)),"Unknown inclusion old-source observation requires separate exact context")
 return dict(parent_manifest=parent,inclusion_receipt=base["source_inclusion"],source_identity_n=8,generated_source_observation_n=16,contexts=contexts,original_JSON_bytes_unchanged=True,current_execution_authorized=False)
def saved_readview_shape(view):
 source_alias_need(all(view.get(k)==v for k,v in dict(source_identity_n=8,original_source_parent_n=6,original_source_edge_n=12,source_proof_parent_n=5,generated_source_output_parent_n=1,generated_source_observation_n=16,restore_only=False,no_live_root_fallback=False).items()),"Complete saved finite read-view denominator/authority flags required")

def export_generated_source_scope(generated):
 result=copy.deepcopy(generated)
 result["contexts"]=[dict(source_field=x["source_field"],**scalar_identity(x["original"]),canonical_receipt=x["canonical_receipt"])for x in generated["contexts"]]
 return result
