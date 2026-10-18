#!/usr/bin/env python3
"""Exact byte-preserving resource closure for an already-scored native74 CPU run."""
import argparse,collections,hashlib,importlib.util,json,os,shutil,subprocess,sys
from pathlib import Path
from provenance_aliases_v2 import checksum,archive_alias,ReceiptResolver
R=Path("/lustre/users/u21111210118/projects/test9")
GUARD=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
GUARD_SHA="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9"
UNRECOVERABLE="b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd"
def read(p):return json.loads(Path(p).read_text())
def dump(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
def key(r):return str(r["path"]),r["sha256"]
def receipts(value,trail=()):
    if isinstance(value,dict):
        if {"path","sha256","bytes"}<=value.keys():yield value,trail
        for k,v in value.items():yield from receipts(v,trail+(str(k),))
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from receipts(v,trail+(str(i),))
def recompute_dependency(path):
    return any(part in str(path) for part in ("/env/","/assets/colabfold/params/","/assets/boltz/","/assets/mmseqs/","/assets/rfdiffusion/","/assets/bindcraft/"))
def historical_unavailable(r,parent,trail):
    return (r["sha256"]==UNRECOVERABLE and r["path"]==str(R/"source/rebuild/benchmark_runtime.py")
            and parent==str(R/"steps/21_method_runtime/runs/readiness_12980/outputs/acceptance.json")
            and trail==("adapter_source",))
def historical_gap(r,parent,trail,policy,resolver=None):
    if historical_unavailable(r,parent,trail):return dict(subtype="HISTORICAL_UNRESOLVED_PROVENANCE",role="OLD_READINESS_ENGINEERING_HISTORY_NOT_ACTUAL_NATIVE_INFERENCE_SOURCE")
    for entry in (policy or {}).get("entries",[]):
        if (entry["logical_path"],entry["expected_sha256"],entry["expected_bytes"])!=(r["path"],r["sha256"],r["bytes"]):continue
        if entry["parent_path"]!=parent or tuple(entry["field"])!=tuple(trail):continue
        if entry["status"]!="HISTORICAL_UNRESOLVED_MSA_DERIVATION" or entry.get("current_execution_allowed") is not False:raise ValueError("Historical derivation policy permits unavailable current execution")
        actual=checksum(resolver.resolve(parent,expected_sha=entry["parent_sha256"]) if resolver else parent)
        if actual["sha256"]!=entry["parent_sha256"]:raise ValueError("Historical policy parent bytes changed")
        operative=entry["actual_operative_scientific_source"]
        if operative["sha256"]!="876d29f9b8a20cf3f8bbf526262de96b1071a30b47590b632e5d31f97c362391":raise ValueError("Historical allowance lacks accepted actual native source")
        if checksum(resolver.verify(operative) if resolver else operative["path"])["sha256"]!=operative["sha256"]:raise ValueError("Actual native operative source unavailable")
        return dict(subtype=entry["status"],role=entry["role"],root_decision=entry["root_decision"],
                    parent_sha256=entry["parent_sha256"],actual_operative_scientific_source=operative,shortest_receipt_chain=entry.get("shortest_receipt_chain"))
    return None

def validate_native_matrix(assembly,score,a,raw):
    if assembly["n_jobs_expected"]!=20 or assembly["n_models_expected"]!=74 or a["n_jobs"]!=20 or a["n_models_expected"]!=74 or score["models_expected"]!=74:raise ValueError("Native20/74 denominator changed")
    ar={row["job_key"]:row for row in assembly["rows"]};sr={row["job_key"]:row for row in score["results"]};rr={row["job_key"]:row for row in raw["rows"]}
    if len(ar)!=20 or len(sr)!=20 or len(rr)!=20 or set(ar)!=set(sr) or set(ar)!=set(rr):raise ValueError("Native full20 job matrix incomplete")
    copied=0;raw_accepted=0;counts=collections.Counter()
    for job,row in ar.items():
        models=sr[job]["models"]
        if len(models)!=row["models_expected"]:raise ValueError("Native expected slot coverage lost")
        counts.update(m["status"] for m in models)
        if row["status"]=="ALL_REGULAR_RAW_FILES_BYTECOPIED":
            copied+=1
            if rr[job]["status"]!="NATIVE_ACTUAL_GPU_OWNERSHIP_AND_RAW_CONTENT_AUDITED" or len(rr[job]["models"])!=row["models_expected"]:raise ValueError("Copied native worker raw audit incomplete")
            raw_accepted+=sum(m["status"]=="RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED" for m in rr[job]["models"])
        elif row["status"]=="WORKER_MISSING_OR_FAILED_SCHEDULER_LEDGER_REQUIRED":
            if rr[job]["status"]!="WORKER_MISSING_TYPED_UNRESOLVED":raise ValueError("Missing native worker lacks typed raw audit")
            if any(m["status"]!="MODEL_UNRESOLVED" or m["R0"] is not None or m["R1"] is not None for m in models):raise ValueError("Missing worker converted to scored biology")
        else:raise ValueError("Unexpected assembly readiness state")
    if copied!=assembly["n_jobs_copied"] or sum(counts.values())!=74 or counts["VALID"]!=a["n_models_valid"] or 74-counts["VALID"]!=a["n_unresolved_or_no_interface"]:raise ValueError("Native count consistency failed")
    if raw["n_jobs_expected"]!=20 or raw["n_models_expected"]!=74 or raw["n_raw_confidence_accepted"]!=raw_accepted or raw["n_raw_unresolved"]!=74-raw_accepted:raise ValueError("Independent raw audit counts changed")
    return dict(counts)
def native_evidence(old):
    manifest=read(old/"manifest.json");score=read(old/"score.json");a=read(old/"score_acceptance.json")
    raw=read(old/"raw_audit.json");assembly=read(old/"assembly.json");repair=read(old/"score_metadata_repair.json");engine=read(old/"score_engine_original.json")
    for r in (manifest["score"],a["result"],repair["canonical_score"],repair["engine_original"]):
        actual=checksum(r["path"])
        if actual["sha256"]!=r["sha256"] or actual["bytes"]!=r["bytes"]:raise ValueError("Previously accepted native evidence changed")
    if a["status"]!="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY":raise ValueError("Native content acceptance missing")
    counts=validate_native_matrix(assembly,score,a,raw)
    if repair["scientific_source_or_scores_changed"] is not False or repair["all_other_fields_equal"] is not True or repair["changed_fields"]!=["plan"]:raise ValueError("Metadata-only repair guarantee missing")
    if {k:v for k,v in score.items() if k!="plan"}!={k:v for k,v in engine.items() if k!="plan"}:raise ValueError("Native science changed during receipt correction")
    if score["plan"]!=manifest["inference_plan"] or repair["correct_plan_field"]!=manifest["inference_plan"]:raise ValueError("Canonical native plan receipt not exact")
    tests=a["tests"]
    if tests.get("status")!="PASSED" or tests.get("n_tests",0)<14:raise ValueError("Native scientific contract tests not accepted")
    return manifest,assembly,a,raw,dict(counts)
class ClosureBuilder:
    def __init__(self,root,out,old,history_policy=None):
        self.history_policy=history_policy or {}
        self.root=Path(root);self.out=Path(out);self.old=Path(old);self.entries={};self.unresolved=[];self.dependencies={};self.verified={};self.candidates={}
        self.assembled={}
        for row in read(self.old/"assembly.json")["rows"]:
            for pair in row.get("files",[]):
                if key(pair["original"]) in self.assembled and self.assembled[key(pair["original"])]!=pair["copy"]:raise ValueError("Conflicting old raw receipt mapping")
                self.assembled[key(pair["original"])]=pair["copy"]
    def check(self,p,r):
        p=Path(p)
        if p.is_symlink() or not p.resolve().is_relative_to(self.root.resolve()):raise ValueError("Scientific byte source escapes project")
        if not p.is_file() or p.stat().st_size!=r["bytes"]:return False
        identity=(str(p),r["sha256"],r["bytes"])
        if identity not in self.verified:
            a=checksum(p);self.verified[identity]=(a["sha256"]==r["sha256"] and a["bytes"]==r["bytes"])
        return self.verified[identity]
    def resolve(self,r):
        p=Path(r["path"])
        if not p.is_absolute() or not p.is_relative_to(self.root):raise ValueError("Resource receipt outside authority")
        if key(r) in self.assembled:
            candidate=Path(self.assembled[key(r)]["path"])
            if not self.check(candidate,r):raise ValueError("Verified assembled raw bytes changed")
            # Original evidence is independently rechecked when present, never preferred to a mismatching copy.
            if p.exists() and not self.check(p,r):raise ValueError("Original raw differs from assembled raw")
            return candidate,"ORIGINAL_RAW_TO_ACCEPTED_HASH_IDENTICAL_BYTECOPY"
        if self.check(p,r):return p,"EXACT_ORIGINAL_RESOURCE"
        copied=self.old/"evidence_resources"/p.relative_to(self.root)
        if copied.exists() and self.check(copied,r):return copied,"PREVIOUS_PARTIAL_CLOSURE_BYTECOPY"
        # Only retained source/document/config snapshots can substitute a mutable receipt.
        # Raw predictions and missing scientific data are never found by name.
        if p.suffix not in {".py",".md",".json",".sh",".sbatch",".txt",".yaml",".yml",".toml"}:
            raise FileNotFoundError("Exact scientific bytes unavailable: "+str(p)+" "+r["sha256"])
        if p.name not in self.candidates:
            choices=[]
            for base in (self.root/"steps",self.root/"source"):
                for candidate in base.rglob(p.name):
                    if candidate.is_file() and not candidate.is_symlink():choices.append(candidate)
            self.candidates[p.name]=sorted(set(choices))
        matches=[candidate for candidate in self.candidates[p.name] if self.check(candidate,r)]
        if not matches:raise FileNotFoundError("Exact frozen resource revision unavailable: "+str(p)+" "+r["sha256"])
        return matches[0],"EXACT_RETAINED_FROZEN_REVISION_ALIAS"
    def build(self,seeds):
        queue=[(r,None,()) for r in seeds];visited=set();resources=[]
        while queue:
            r,parent,trail=queue.pop()
            k=key(r)
            if k in visited:
                if any(key(e["original"])==k for e in self.unresolved) and historical_gap(r,parent,trail,self.history_policy) is None:raise ValueError("Historical gap reused by a current operative receipt")
                continue
            visited.add(k)
            if recompute_dependency(r["path"]):
                self.dependencies[k]=r;resources.append(dict(original=r,scope="RECOMPUTE_DEPENDENCY",copied=False,required_for_frozen_raw_review=False));continue
            try:source,basis=self.resolve(r)
            except FileNotFoundError:
                gap=historical_gap(r,parent,trail,self.history_policy)
                if gap is None:raise
                entry=dict(original=r,status="HISTORICAL_UNRESOLVED_PROVENANCE",current_PASS_allowed=False,parent=parent,trail=list(trail),**gap)
                self.unresolved.append(entry);resources.append(dict(original=r,scope="ENGINEERING_HISTORY",copied=False,historical_unresolved=entry));continue
            alias=archive_alias(r,source,self.out/"evidence_resources","NATIVE_SCIENTIFIC_BYTE_IDENTICAL_RESOURCE")
            alias["resolution_basis"]=basis;self.entries[k]=alias
            resources.append(dict(original=r,copy=alias["archived"],scope="SCIENTIFIC_SOURCE_INPUT_REFERENCE_OR_RAW_EVIDENCE",copied=True,resolution_basis=basis))
            if source.suffix==".json":
                queue.extend((nested,r["path"],nested_trail) for nested,nested_trail in receipts(read(source)))
        index=dict(schema="exact-resource-aliases.v2",status="EXACT_NATIVE_RESOURCE_ALIASES_WITH_TYPED_ENGINEERING_HISTORY",
                   aliases=list(self.entries.values()),historical_unresolved=self.unresolved)
        return dict(schema="native-resource-closure.v2",status="NATIVE_CURRENT_OPERATIVE_RESOURCE_CLOSURE_WITH_TYPED_HISTORICAL_DERIVATION_AND_CONDITIONAL_ENGINE_DEPENDENCIES",
                    resources=resources,evidence_copy_n=len(self.entries),engine_recompute_dependency_n=len(self.dependencies),
                    historical_unresolved_n=len(self.unresolved),offline_GPU_recompute_guaranteed=False,
                    resolver_contract="Resolve only exact (original path,SHA) readonly hash-identical archive bytes; frozen JSON/source bytes remain unchanged."),index
def verify_closure(root,out,closure,index,seeds,history_policy=None):
    resolver=ReceiptResolver(root,index=index);covered={}
    for resource in closure["resources"]:
        r=resource["original"];k=key(r)
        if k in covered:raise ValueError("Duplicate exact resource receipt")
        covered[k]=resource
        if resource["scope"]=="RECOMPUTE_DEPENDENCY":
            if resource.get("copied") or not recompute_dependency(r["path"]):raise ValueError("Invalid engine dependency exception")
            continue
        if resource["scope"]=="ENGINEERING_HISTORY":
            h=resource["historical_unresolved"]
            if historical_gap(r,h["parent"],tuple(h["trail"]),history_policy,resolver) is None:raise ValueError("Unrecognized historical gap exception")
            if resolver.verify(r,scope="HISTORICAL") is not None:raise ValueError("Historical unknown accepted as bytes")
            continue
        physical=resolver.verify(r)
        if checksum(physical)!=resource["copy"]:raise ValueError("Closure copy receipt differs from resolved readonly bytes")
    seen=set();queue=[(r,None,()) for r in seeds]
    while queue:
        r,parent,trail=queue.pop();k=key(r)
        if k in seen:
            if covered[k]["scope"]=="ENGINEERING_HISTORY" and historical_gap(r,parent,trail,history_policy,resolver) is None:raise ValueError("Historical gap appears in a current evidence role")
            continue
        seen.add(k)
        if k not in covered:raise ValueError("Recursive JSON receipt omitted from closure")
        resource=covered[k]
        if resource["scope"]=="ENGINEERING_HISTORY":
            if historical_gap(r,parent,trail,history_policy,resolver) is None:raise ValueError("Historical gap appears in a current evidence role")
            continue
        if resource["scope"]=="RECOMPUTE_DEPENDENCY":continue
        physical=resolver.verify(r)
        if Path(r["path"]).suffix==".json":queue.extend((nested,r["path"],tr) for nested,tr in receipts(read(physical)))
    if seen!=set(covered):raise ValueError("Unreachable closure resource not declared from seeds")
    return dict(status="INDEPENDENT_EXACT_CLOSURE_READBACK_ACCEPTED",n_exact_resources=len(covered),n_readonly_bytecopies=closure["evidence_copy_n"],
                n_engine_recompute_dependencies=closure["engine_recompute_dependency_n"],n_typed_historical_unresolved=closure["historical_unresolved_n"],
                original_resource_fallback_used=False,frozen_JSON_bytes_rewritten=False)
def cpu_allocation():
    job=os.environ.get("SLURM_JOB_ID")
    if not job or os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU Slurm job with CUDA masked required")
    if checksum(GUARD)["sha256"]!=GUARD_SHA:raise ValueError("Frozen budgetv4 guard changed")
    spec=importlib.util.spec_from_file_location("closure_cpu_guard",GUARD);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    text=subprocess.run(["scontrol","show","job",job,"-o"],check=True,capture_output=True,text=True).stdout
    selected=module.select_scheduler_record(text,raw_job_id=job);module.scheduler_allocation_identity(selected,env=os.environ);module.validate_scheduler_gpu_allocation(selected,0)
    return dict(job_id=job,allocated_gpu_count=0,scheduler_record_full=text,selected_scheduler_record=selected)
def main():
    p=argparse.ArgumentParser();p.add_argument("--old-run",required=True);p.add_argument("--out-dir",required=True);p.add_argument("--history-policy");p.add_argument("--extra-source",action="append",default=[]);p.add_argument("--prior-run-role",choices=["HISTORY_FAILED_RESOURCE_CLOSURE","CURRENT_THREE_SOURCE_NATIVE_COLLECTION"],default="HISTORY_FAILED_RESOURCE_CLOSURE");a=p.parse_args()
    cpu=cpu_allocation();old=Path(a.old_run);out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=False)
    manifest,assembly,accepted,raw,counts=native_evidence(old)
    names=("manifest.json","assembly.json","score.json","raw_audit.json","score_acceptance.json","score_engine_original.json","score_metadata_repair.json","REPORT.md")
    prior={name:checksum(old/name) for name in names}
    seeds=list(prior.values())+[manifest[k] for k in ("source","inference_plan","analysis_plan","membership")]
    seeds+=[checksum(R/"steps/23_common_review/frozen/native_common_13051/source_bundle.json"),
            checksum(R/"steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py"),
            checksum(__file__),checksum(Path(__file__).with_name("provenance_aliases_v2.py")),
            checksum(Path(__file__).with_name("test_native_resource_closure_v2.py"))]
    policy=read(a.history_policy) if a.history_policy else {}
    if a.history_policy:seeds.append(checksum(a.history_policy))
    seeds.extend(checksum(p) for p in a.extra_source)
    builder=ClosureBuilder(R,out,old,policy);closure,index=builder.build(seeds)
    dump(out/"resource_aliases.json",index);dump(out/"resource_closure.json",closure)
    independent=verify_closure(R,out,closure,index,seeds,policy);dump(out/"closure_acceptance.json",independent)
    # Resolve every old scientific record from the new readonly closure, not its mutable old location.
    resolver=ReceiptResolver(R,index=index)
    restored=lambda name:read(resolver.verify(prior[name]))
    if restored("score.json")!=read(old/"score.json"):raise ValueError("Native score altered by packaging")
    if {name:checksum(old/name) for name in names}!=prior:raise ValueError("Closure mutated the failed run")
    restored_score=restored("score.json");restored_a=restored("score_acceptance.json")
    reconstructed=collections.Counter(m["status"] for result in restored_score["results"] for m in result["models"])
    if dict(reconstructed)!=counts or sum(reconstructed.values())!=74:raise ValueError("Restored native denominator/count differs")
    final=dict(schema="native74-closure-supplement.v2",status="NATIVE74_CONTENT_ACCEPTED_WITH_TYPED_MODEL_OUTCOMES_AND_EXACT_RESOURCE_CLOSURE_COMPUTATIONAL_ONLY",
        CPU_allocation=cpu,source=checksum(__file__),prior_scored_run=str(old),prior_run_role=a.prior_run_role,previous_failed_run=str(old) if a.prior_run_role=="HISTORY_FAILED_RESOURCE_CLOSURE" else None,previous_pipeline_terminal_state="FAILED_RESOURCE_PROVENANCE_CLOSURE_NOT_SCIENTIFIC_SCORE" if a.prior_run_role=="HISTORY_FAILED_RESOURCE_CLOSURE" else "CURRENT_THREE_SOURCE_CPU_SCORE_AND_RAW_AUDIT_ACCEPTED_BEFORE_CLOSURE",
        immutable_prior_evidence=prior,source_engine=manifest["source"],plan=manifest["inference_plan"],analysis=manifest["analysis_plan"],membership=manifest["membership"],
        resource_closure=checksum(out/"resource_closure.json"),resource_aliases=checksum(out/"resource_aliases.json"),independent_closure_acceptance=checksum(out/"closure_acceptance.json"),
        jobs_expected=20,models_expected=74,jobs_original_workers_copied=assembly["n_jobs_copied"],models_contact_valid=accepted["n_models_valid"],
        model_outcome_counts=dict(reconstructed),models_raw_confidence_accepted=raw["n_raw_confidence_accepted"],models_raw_typed_unresolved=raw["n_raw_unresolved"],
        scientific_contract_tests=accepted["tests"],closure_contract_tests=read(out.parent/"tests.json") if (out.parent/"tests.json").exists() else None,
        exact_resource_n=closure["evidence_copy_n"],conditional_engine_dependencies_n=closure["engine_recompute_dependency_n"],historical_unresolved_n=closure["historical_unresolved_n"],
        original_worker_or_score_bytes_modified=False,frozen_source_or_plan_bytes_modified=False,GPU_inference_rerun=False,scientific_score_recomputed=False,
        score_values_from_prior_content_acceptance=True,raw_symlinks=False,engines_summarized_separately=True,formal_RF_vs_BindCraft_benchmark_complete=False,
        ACTIVE_changed=False,offline_GPU_recompute_guaranteed=False,experimental_probability=None,independent_experimental_validation=False)
    dump(out/"acceptance.json",final);print(json.dumps({k:v for k,v in final.items() if k not in {"CPU_allocation","immutable_prior_evidence"}},indent=2),flush=True)
if __name__=="__main__":main()

