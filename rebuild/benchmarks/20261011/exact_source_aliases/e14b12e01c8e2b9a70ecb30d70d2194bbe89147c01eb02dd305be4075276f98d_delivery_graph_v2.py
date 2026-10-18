#!/usr/bin/env python3
"""Declared source/dependency graph; no mtime selection and no result promotion."""
import argparse,hashlib,json,os
from pathlib import Path
from delivery_core import cpu,rec,dump,SECRET_RE
from provenance_aliases_v2 import archive_alias
CORE=("screening_transfer.py","benchmark_target_prepare.py","benchmark_inputs.py","benchmark_inputs_v2.py",
      "benchmark_runtime.py","paired_budget_benchmark.py","benchmark_common_review.py","benchmark_common_review_v2.py","bbf_input_diagnostic.py")
SUFFIXES={".py",".sh",".sbatch",".md",".json"}
def graph_nodes(root,runtime_settings="pilot_v7"):
    root=Path(root)
    return [
      dict(role="CURRENT_EXPLICITLY_DECLARED_METHOD_CONFIG",path=str(root/"steps/22_matched_benchmark/settings"/runtime_settings),recursive=True),
      dict(role="CURRENT_IMMUTABLE_BUDGET_V4",path=str(root/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"),recursive=True),
      dict(role="CURRENT_CORRECTED_COMMON_CORE_V2",path=str(root/"steps/23_common_review/frozen/common_core_v2_13130"),recursive=True),
      dict(role="CURRENT_BBF_BACKEND_V2",path=str(root/"steps/21_method_runtime/frozen/bbf_backend_v2"),recursive=True),
      dict(role="HISTORICAL_NATIVE_SCIENTIFIC_SOURCE_13051",path=str(root/"steps/23_common_review/frozen/native_common_13051"),recursive=True),
      dict(role="CURRENT_NATIVE19_TECHNICAL_ENTRY_13106",path=str(root/"steps/23_common_review/runs/allocation_v2_13106/code"),recursive=True),
      dict(role="CURRENT_NATIVE18_ACTUAL_TECHNICAL_CORRECTION",path=str(root/"steps/23_common_review/engineering_history/native_index18_20261011/native18_gpu.sbatch"),recursive=False),
      dict(role="CURRENT_NATIVE19_LAUNCHER_13106",path=str(root/"steps/23_common_review/runs/allocation_v2_13106/native_index19/native19_gpu.sbatch"),recursive=False),
      dict(role="CURRENT_BBF_REMAINING_CHOSEN_ENTRY_13103",path=str(root/"steps/23_common_review/runs/allocation_v2_13103/code"),recursive=True),
      dict(role="CURRENT_BBF_REMAINING_CHOSEN_LAUNCHER_13103",path=str(root/"steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/bbf_gpu_remaining.sbatch"),recursive=False),
      dict(role="CURRENT_DOWNSTREAM_SOURCE_13119_NOT_FULL_ACCEPTANCE",path=str(root/"steps/23_common_review/runs/downstream_frozen_13119/code"),recursive=True),
      dict(role="CURRENT_NATIVE_CPU_LAUNCHER_13119",path=str(root/"steps/23_common_review/runs/downstream_frozen_13119/native74_review_cpu.sbatch"),recursive=False),
      dict(role="CURRENT_BBF_CPU_LAUNCHER_13119",path=str(root/"steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_cpu.sbatch"),recursive=False),
      dict(role="CURRENT_ACTUAL_NATIVE74_COLLECTOR_SOURCE_13211",path=str(root/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code"),recursive=True),
      dict(role="CURRENT_ACTUAL_NATIVE74_EDGE_VERIFIER_SOURCE_13214",path=str(root/"steps/24_benchmark_delivery/frozen/native74_edge_seal_13214/code"),recursive=True),
      dict(role="CURRENT_FULL_QUERY_CHAIN_FIXED_INPUT_SOURCE",path=str(root/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/source"),recursive=True,optional=True)
    ]
def source_entries(root,runtime_settings="pilot_v7"):
    root=Path(root);entries={}
    def add(path,role,dest=None):
        path=Path(path)
        if path.is_symlink():raise ValueError("Source symlink not allowed")
        relative=path.relative_to(root)
        if dest is None:dest=Path("rebuild/benchmarks/20261011")/relative
        key=str(path)
        entry=(path,dest,role)
        if key in entries and entries[key][1]!=dest:raise ValueError("Duplicate source destination mismatch")
        entries[key]=entry
    for name in CORE:add(root/"source/rebuild"/name,"CORE_IMPLEMENTATION",Path("rebuild")/name)
    for dirname in ("steps/20_screening_improvement/code","steps/21_method_runtime/code","steps/22_matched_benchmark/code",
                    "steps/23_common_review/code","steps/24_benchmark_delivery/code"):
        for path in sorted((root/dirname).iterdir()):
            if path.is_file() and path.suffix in SUFFIXES and path.suffix!=".json":
                add(path,"CLUSTER_HELPER_TEST_OR_DOCUMENT")
    for path in (root/"steps/20_screening_improvement/PROTOCOL.md",root/"steps/23_common_review/PROTOCOL.md",
                 root/"steps/23_common_review/PROGRESS_AND_NEXT.md",root/"steps/24_benchmark_delivery/code/native_msa_history_policy.json"):
        add(path,"PROTOCOL_AND_EVIDENCE_ROLE_DOCUMENT")
    for node in graph_nodes(root,runtime_settings):
        path=Path(node["path"])
        if not path.exists():
            if node.get("optional"):continue
            raise FileNotFoundError("Declared graph node unavailable: "+str(path))
        candidates=path.rglob("*") if path.is_dir() and node["recursive"] else [path]
        for p in sorted(candidates):
            if "__pycache__" in p.parts or not p.is_file():continue
            if p.suffix in SUFFIXES or p.parent.name=="runtime_entries":
                add(p,node["role"])
    return list(entries.values())
def audit(root,out,runtime_settings="pilot_v7",stage=False):
    cpu();rows=[];issues=[]
    for path,destination,role in source_entries(root,runtime_settings):
        data=path.read_bytes()
        try:text=data.decode("utf-8")
        except UnicodeDecodeError:raise ValueError("Source graph contains binary "+str(path))
        if SECRET_RE.search(text) or "-----BEGIN "+"OPENSSH PRIVATE KEY-----" in text:
            issues.append({"path":str(path),"reason":"POTENTIAL_CREDENTIAL_REQUIRES_REVIEW"})
        rows.append({"source":rec(path),"repository_relative":str(destination),"role":role,
                     "cluster_specific":"/lustre/users/" in text or "#SBATCH" in text})
    if stage:
        if issues:raise ValueError("Credential review required before staging")
        import shutil
        for row in rows:
            original=Path(row["source"]["path"]);dest=Path(root)/"source"/row["repository_relative"]
            if dest==original:continue
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists() and dest.read_bytes()!=original.read_bytes():raise FileExistsError("Source stage collision "+str(dest))
            if not dest.exists():shutil.copyfile(original,dest)
    result={"schema":"benchmark-source-inclusion.v2","status":"SOURCE_INCLUSION_AUDIT_PASS" if not issues else "SOURCE_INCLUSION_REVIEW_REQUIRED",
      "authority_root":str(root),"declared_runtime_settings":runtime_settings,"graph_nodes":graph_nodes(root,runtime_settings),
      "files":rows,"issues":issues,"applied":stage,"production_benchmark_completed":False,
      "evidence_scope":"Source inclusion and current graph identity only; CPU readiness is not full GPU/scientific acceptance."}
    dump(out,result);return result
def historical_aliases(root,out):
    cpu();root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    aliases=[]
    logical=root/"source/rebuild/benchmark_runtime.py"
    for version,prefix in (("pilot_v3","f3726"),("pilot_v5","773dc1")):
        source=root/"steps/22_matched_benchmark/settings"/version/"source/benchmark_runtime.py"
        original=rec(source);original["path"]=str(logical)
        if not original["sha256"].startswith(prefix):raise ValueError("Declared historical snapshot prefix mismatch")
        aliases.append(archive_alias(original,source,out/"readonly_aliases","HISTORICAL_EXACT_SOURCE_BYTES"))
    old= json.loads((root/"steps/21_method_runtime/runs/readiness_12980/outputs/acceptance.json").read_text())["adapter_source"]
    if old["sha256"]!="b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd":raise ValueError("Historical missing receipt changed")
    result={"schema":"benchmark-resource-aliases.v2","status":"EXACT_HISTORICAL_ALIASES_WITH_TYPED_UNRESOLVED_PROVENANCE",
      "aliases":aliases,"historical_unresolved":[{"original":old,"status":"HISTORICAL_UNRESOLVED_PROVENANCE",
       "reason":"Exact 12980 mutable adapter bytes were not archived; no reconstruction from another revision is permitted.",
       "allowed_role":"ENGINEERING_HISTORY_ONLY","current_PASS_allowed":False}],
      "current_12980_dependency_allowed":False}
    dump(out/"aliases.json",result);return result
def main():
    p=argparse.ArgumentParser();p.add_argument("command",choices=["source-audit","historical-aliases"])
    p.add_argument("--root",required=True);p.add_argument("--out",required=True);p.add_argument("--runtime-settings",default="pilot_v7");p.add_argument("--stage",action="store_true")
    a=p.parse_args();r=audit(a.root,a.out,a.runtime_settings,a.stage) if a.command=="source-audit" else historical_aliases(a.root,a.out)
    print(r["status"])
if __name__=="__main__":main()

