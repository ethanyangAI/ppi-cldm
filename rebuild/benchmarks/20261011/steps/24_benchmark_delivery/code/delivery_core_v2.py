#!/usr/bin/env python3
"""Portable delivery gates, deterministic packaging and transactional publication.

CPU Slurm only. Packaging is a same-Lustre evidence archive, not a GPU runtime
image or an offsite backup. Publication is a separate explicit CLI operation.
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, tarfile, tempfile
from pathlib import Path

SCHEMA = "benchmark-delivery.v2"
GATES = ("screening_content", "bbf_input_sensitivity_content", "target_identity",
         "runtime_gpu_pilot", "generation_accounting", "common_review_content",
         "independent_score_recomputation", "scientific_report_content", "source_release")
PROHIBITED_PUBLIC = (".whl", ".pth", ".pt", ".ckpt", ".npz", ".pkl", ".zip", ".tar", ".gz")
SECRET_RE = re.compile(r"(?im)(?:password|access_token|secret_key|api_key|private_key)\s*[:=]\s*[\"']?(?!None\b|null\b|os\.|env\b|\$\{|<|YOUR_|getenv\b)[A-Za-z0-9+/=_-]{12,}")
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(path):
    return json.loads(Path(path).read_text())
def rec(path):
    p=Path(path); h=hashlib.sha256(); n=0
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1048576), b""):
            h.update(block); n += len(block)
    return {"path":str(p),"bytes":n,"sha256":h.hexdigest()}
def dump(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x") as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
    return rec(p)
def verify(receipt,root=None):
    p=Path(receipt["path"])
    if root is not None:
        relative=p.relative_to(Path(root))
        if p.is_symlink() or p.resolve()!=Path(root).resolve()/relative:
            raise ValueError("Symlink/outside authority: "+str(p))
    v=rec(p)
    if v["sha256"]!=receipt["sha256"] or ("bytes" in receipt and v["bytes"]!=receipt["bytes"]):
        raise ValueError("Receipt mismatch: "+str(p))
    return p
def cpu():
    jid=os.environ.get("SLURM_JOB_ID")
    if not jid: raise RuntimeError("Delivery work requires a Slurm CPU allocation")
    row=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
    fields=dict(re.findall(r"(\w+)=(\S+)",row));tres=fields.get("AllocTRES") or fields.get("TRES")
    if tres is None: raise RuntimeError("Authoritative TRES unavailable")
    vals=dict(x.split("=",1) for x in tres.split(",") if "=" in x)
    n=int(vals.get("gres/gpu",0)) if "gres/gpu" in vals else sum(int(v) for k,v in vals.items() if k.startswith("gres/gpu:"))
    if n!=0:raise RuntimeError("Delivery CPU step must allocate no GPU")
    if os.environ.get("CUDA_VISIBLE_DEVICES","") not in ("","NoDevFiles","-1"):
        raise RuntimeError("Delivery CPU step must hide CUDA devices")
    return {"job_id":jid,"scheduler_record":row.strip(),"allocated_gpus":0}
def content_expect(obj,expect):
    for dotted,value in expect.items():
        actual=obj
        for key in dotted.split("."):
            actual=actual[key]
        if actual!=value:raise ValueError("Content gate mismatch: "+dotted)
def legacy_source_entries(root):
    """Only code/documents; no run outputs, caches, weights or licensed wheels."""
    root=Path(root);entries=[]
    modules=("screening_transfer.py","benchmark_target_prepare.py","benchmark_inputs.py",
             "benchmark_runtime.py","paired_budget_benchmark.py","benchmark_common_review.py",
             "bbf_input_diagnostic.py")
    for name in modules:
        p=root/"source/rebuild"/name
        if not p.is_file(): raise FileNotFoundError(p)
        entries.append((p,Path("rebuild")/name,"core_module"))
    directories=[
      "steps/20_screening_improvement/code",
      "steps/21_method_runtime/code",
      "steps/22_matched_benchmark/code",
      "steps/23_common_review/code",
      "steps/23_common_review/bbf_diagnostics/code",
      "steps/24_benchmark_delivery/code"]
    allowed={".py",".sh",".sbatch",".md"}
    for directory in directories:
        d=root/directory
        if not d.exists():
            if "bbf_diagnostics" in directory:continue
            raise FileNotFoundError(d)
        for p in sorted(d.iterdir()):
            if p.is_file() and p.suffix in allowed:
                destination=Path("rebuild/benchmarks/20261011")/Path(directory).relative_to("steps")/p.name
                entries.append((p,destination,"cluster_support"))
    for directory in ("steps/20_screening_improvement","steps/23_common_review"):
        for name in ("PROTOCOL.md","PROTOCOL_DRAFT.md"):
            p=root/directory/name
            if p.is_file():
                entries.append((p,Path("rebuild/benchmarks/20261011")/Path(directory).relative_to("steps")/name,"protocol_document"))
    prep=root/"steps/22_matched_benchmark/input_preparation"
    for name in ("inputfinal.sbatch","repair_hras.sbatch","REPAIR_12956.md"):
        p=prep/name
        if p.is_file():entries.append((p,Path("rebuild/benchmarks/20261011/22_matched_benchmark/input_preparation")/name,"input_support"))
    return entries
def source_audit(root,out,apply=False,runtime_settings="pilot_v7"):
    from delivery_graph_v2 import audit
    return audit(root,out,runtime_settings,apply)
def validate(config_path,out):
    allocation=cpu();config=read(config_path)
    from provenance_aliases_v2 import ReceiptResolver
    alias_index=read(verify(config["resource_aliases"])) if config.get("resource_aliases") else {}
    resolver=ReceiptResolver(config["authority_root"],index=alias_index)
    from historical_scope_v2 import HistoricalScopeVerifier
    policy=read(resolver.verify(config["historical_provenance_policy"])) if config.get("historical_provenance_policy") else {}
    history_scope=HistoricalScopeVerifier(resolver,policy)
    if config["schema"]!=SCHEMA or config["scientific_scope"]!="COMPUTATIONAL_ONLY":
        raise ValueError("Wrong delivery scope/schema")
    root=Path(config["authority_root"]);verify(config["previous_active"],root)
    previous=read(config["previous_active"]["path"])
    for name in ("current_phase","reconstruction","human_report"):
        verify(previous[name],root)
    if set(config["gates"])!=set(GATES):raise ValueError("Required delivery gate omitted")
    gates={}
    for name in GATES:
        gate=config["gates"][name];path=verify(gate["receipt"],root);obj=read(path)
        if not gate.get("expect") or "status" not in gate["expect"]:
            raise ValueError("Explicit terminal status expectation required")
        content_expect(obj,gate["expect"]);gates[name]=gate
    ledger=read(config["gates"]["generation_accounting"]["receipt"]["path"])
    if ledger.get("complete_generation_matrix") is not True or ledger.get("expected_tasks")!=28:
        raise ValueError("All 28 paired generation tasks required")
    common=read(config["gates"]["common_review_content"]["receipt"]["path"])
    if common.get("status")!="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY":
        raise ValueError("Common review is not content accepted")
    if common.get("independent_experimental_validation") is not False:
        raise ValueError("Unsupported experiment claim")
    source=read(config["gates"]["source_release"]["receipt"]["path"])
    if source.get("working_tree_clean") is not True or not re.fullmatch(r"[0-9a-f]{40}",source.get("commit","")):
        raise ValueError("Committed clean source release required")
    actual_commit=subprocess.check_output(["git","-C",str(root/"source"),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root/"source"),"status","--porcelain"],text=True)
    if actual_commit!=source["commit"] or dirty.strip():raise ValueError("Live source commit/clean-tree gate differs")
    inclusion=read(verify(source["source_inclusion"],root))
    if inclusion["status"]!="SOURCE_INCLUSION_AUDIT_PASS":raise ValueError("Complete source-inclusion audit required")
    for item in inclusion["files"]:
        destination=root/"source"/item["repository_relative"]
        if rec(destination)["sha256"]!=item["source"]["sha256"]:raise ValueError("Published source bytes differ from validated support")
        subprocess.check_output(["git","-C",str(root/"source"),"cat-file","-e",source["commit"]+":"+item["repository_relative"]])
    files={};dependencies={}
    for dependency in config.get("conditional_inference_dependencies",[]):
        r=dependency["receipt"]
        if not dependency.get("reason") or dependency.get("included_in_package") is not False:
            raise ValueError("Conditional dependency must explicitly describe exclusion")
        dependencies[r["path"]]=dependency
    for item in config["files"]:
        if item["classification"] not in ("SOURCE","EVIDENCE","AUDIT","HUMAN_REPORT","AUTHORITY_SNAPSHOT","ENGINEERING_HISTORY"):
            raise ValueError("Unknown evidence file class")
        path=verify(item["receipt"],root);relative=path.relative_to(root).as_posix()
        if relative in files:raise ValueError("Duplicate packaged path")
        if path.is_symlink() or ".git" in path.parts or path.suffix==".whl" or "id_ed25519" in path.name:
            raise ValueError("Disallowed packaged file")
        files[relative]=item
    # Every receipt in packaged JSON is archived or an explicit conditional runtime dependency.
    closure_errors=[]
    def walk(obj,parent,trail=()):
        if isinstance(obj,dict):
            if obj.get("scope")=="ENGINEERING_HISTORY" and obj.get("historical_unresolved"):
                history_scope.metadata(obj["historical_unresolved"]);return
            if obj.get("status")=="HISTORICAL_UNRESOLVED_PROVENANCE":
                history_scope.metadata(obj);return
            if {"path","sha256"}<=set(obj) and isinstance(obj["path"],str):
                p=Path(obj["path"])
                if (str(p),obj["sha256"]) in resolver.unresolved:
                    if not history_scope.edge(obj,parent,trail):closure_errors.append({"parent":parent,"field":list(trail),"path":str(p),"reason":"HISTORICAL_UNRESOLVED_PROVENANCE_CANNOT_SATISFY_CURRENT"})
                    return
                try:relative=p.relative_to(root).as_posix()
                except ValueError:closure_errors.append({"parent":parent,"path":str(p),"reason":"OUTSIDE_AUTHORITY_RECEIPT"});return
                if relative not in files and str(p) not in dependencies and (str(p),obj["sha256"]) not in resolver.entries:
                    closure_errors.append({"parent":parent,"path":str(p),"reason":"RECEIPT_NOT_PACKAGED_OR_DECLARED"})
                elif relative in files and files[relative]["receipt"]["sha256"]!=obj["sha256"] and (str(p),obj["sha256"]) not in resolver.entries:
                    closure_errors.append({"parent":parent,"path":str(p),"reason":"CONFLICTING_IMMUTABLE_HASH"})
            for name,value in obj.items():walk(value,parent,trail+(str(name),))
        elif isinstance(obj,list):
            for i,value in enumerate(obj):walk(value,parent,trail+(str(i),))
    for key,entry in resolver.entries.items():
        archived=entry["archived"];relative=Path(archived["path"]).relative_to(root).as_posix()
        if relative not in files or files[relative]["receipt"]["sha256"]!=archived["sha256"]:
            raise ValueError("Alias bytes not packaged")
        resolver.verify(entry["original"])
    for key,entry in resolver.unresolved.items():
        if entry.get("current_PASS_allowed") is not False:
            raise ValueError("Historical unresolved cannot become current PASS")
    for relative,item in files.items():
        if relative.endswith(".json") and item["classification"]!="ENGINEERING_HISTORY":
            for logical_parent in history_scope.logical_parents(item["receipt"]["path"],item["receipt"]["sha256"]):
                walk(read(item["receipt"]["path"]),logical_parent)
    if closure_errors:raise ValueError("Evidence closure incomplete: "+json.dumps(closure_errors[:12]))
    if config["previous_active"]["path"] not in [v["receipt"]["path"] for v in files.values()]:
        raise ValueError("Prior ACTIVE bytes must be archived")
    result={"schema":"benchmark-delivery-validation.v1","status":"FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",
            "created_utc":now(),"allocation":allocation,"config":rec(config_path),"authority_root":str(root),
            "phase_id":config["phase_id"],"previous_active":config["previous_active"],"source_commit":source["commit"],
            "files":files,"conditional_inference_dependencies":list(dependencies.values()),"gates":gates,
            "file_count":len(files),"total_bytes":sum(v["receipt"]["bytes"] for v in files.values()),
            "unresolved_scientific_scope":["experimental binding","functional PPI blockade","clinical efficacy","generalization to arbitrary protein pairs"],
            "resource_aliases":config.get("resource_aliases"),"historical_provenance_policy":config.get("historical_provenance_policy"),"restore_required":True}
    dump(out,result);return result
def package(validation_path,out,part_mib):
    cpu();validation=read(validation_path)
    if validation["status"]!="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY":raise ValueError("Content validation required")
    verify(validation["config"]);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    root=Path(validation["authority_root"]);manifest=[]
    entries=dict(validation["files"])
    for extra in (validation_path,validation["config"]["path"]):
        path=Path(extra);relative=path.relative_to(root).as_posix()
        entries[relative]={"receipt":rec(path),"classification":"AUDIT"}
    tarpath=out/"evidence.tar"
    with tarfile.open(tarpath,"w",format=tarfile.PAX_FORMAT) as tar:
        for relative,item in sorted(entries.items()):
            path=verify(item["receipt"],root);info=tar.gettarinfo(str(path),arcname=relative)
            info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
            with path.open("rb") as f:tar.addfile(info,f)
            manifest.append({"relative":relative,"receipt":item["receipt"],"classification":item["classification"]})
    limit=int(part_mib)*1024*1024
    if limit<1024*1024:raise ValueError("Part size too small")
    parts=[]
    with tarpath.open("rb") as src:
        i=0
        while True:
            block=src.read(limit)
            if not block:break
            p=out/("evidence.tar.part%03d"%i)
            with p.open("xb") as dst:dst.write(block)
            parts.append(rec(p));i+=1
    archive_hash=rec(tarpath);tarpath.unlink()
    receipt={"schema":"benchmark-delivery-package.v1","status":"PACKAGED_AWAITING_INDEPENDENT_RESTORE",
             "created_utc":now(),"validation":rec(validation_path),"authority_root":str(root),
             "config":validation["config"],"phase_id":validation["phase_id"],"archive_bytes":archive_hash["bytes"],"archive_sha256":archive_hash["sha256"],"parts":parts,"manifest":manifest,
             "scientific_scope":"COMPUTATIONAL_ONLY","storage_tier":"SAME_LUSTRE_FILESYSTEM_ARCHIVE_NOT_OFFSITE",
             "conditional_inference_dependencies":validation["conditional_inference_dependencies"]}
    dump(out/"packaging_receipt.json",receipt);return receipt
def extract(package_path,restore):
    cpu();pkg=read(package_path)
    if pkg["status"]!="PACKAGED_AWAITING_INDEPENDENT_RESTORE":raise ValueError("Package status mismatch")
    restore=Path(restore);restore.mkdir(parents=True,exist_ok=False)
    archive=restore.parent/(restore.name+".tar.partial");h=hashlib.sha256();n=0
    with archive.open("xb") as f:
        for r in pkg["parts"]:
            with verify(r).open("rb") as part:
                for block in iter(lambda:part.read(1048576),b""):
                    f.write(block);h.update(block);n+=len(block)
    if h.hexdigest()!=pkg["archive_sha256"] or n!=pkg["archive_bytes"]:raise ValueError("Concatenated archive hash mismatch")
    expected={v["relative"]:v for v in pkg["manifest"]}
    with tarfile.open(archive,"r:") as tar:
        seen=set()
        for m in tar:
            if not m.isfile() or m.name.startswith("/") or ".." in Path(m.name).parts or m.name not in expected or m.name in seen:
                raise ValueError("Unsafe/unexpected archive member")
            dest=restore/m.name;dest.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(m) as src,dest.open("xb") as out:shutil.copyfileobj(src,out)
            a=rec(dest);e=expected[m.name]["receipt"]
            if a["sha256"]!=e["sha256"] or a["bytes"]!=e["bytes"]:raise ValueError("Restore file identity mismatch")
            dest.chmod(m.mode & 0o777)
            seen.add(m.name)
    if seen!=set(expected):raise ValueError("Restore manifest denominator mismatch")
    archive.unlink()
    result={"status":"RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING","package":rec(package_path),
            "restore_root":str(restore),"authority_root":pkg["authority_root"],"files_verified":len(seen),
            "storage_tier":pkg["storage_tier"],"frozen_plan_bytes_changed":False,
            "conditional_inference_dependencies":pkg["conditional_inference_dependencies"]}
    dump(restore/"RESTORE_HASH_ACCEPTANCE.json",result);return result
def publish(validation_path,restore_acceptance_path,phase_path,active_path):
    cpu();v=read(validation_path);r=read(restore_acceptance_path);phase=read(phase_path);active=Path(active_path)
    if v["status"]!="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY":
        raise ValueError("Final content validation required")
    if r["status"]!="INDEPENDENT_RESTORE_RAW_CONTENT_RECOMPUTATION_ACCEPTED":
        raise ValueError("Raw-content restore recomputation required")
    if r["phase_id"]!=v["phase_id"] or phase["phase_id"]!=v["phase_id"]:
        raise ValueError("Phase identity mismatch")
    if phase["status"]!="MATCHED_BENCHMARK_ACCEPTED_COMPUTATIONAL_ONLY" or phase["scientific_scope"]!="COMPUTATIONAL_ONLY":
        raise ValueError("Unsupported publication status")
    if phase["delivery_validation"]!=rec(validation_path) or phase["independent_restore"]!=rec(restore_acceptance_path):
        raise ValueError("Phase acceptance pointers differ")
    root=Path(v["authority_root"]);verify(v["previous_active"],root)
    package_record=read(verify(r["package"],root))
    if package_record["validation"]!=rec(validation_path):raise ValueError("Restore belongs to another final validation")
    for name in ("recomputed_budget","recomputed_common","recomputed_statistics"):verify(r[name],root)
    for item in v["files"].values():verify(item["receipt"],root)
    if rec(active)!=v["previous_active"]:raise ValueError("Authority advanced; refuse stale promotion")
    verify(phase["human_report"],root);verify(phase["source_release"],root)
    backup=root/"00_admin/benchmark_snapshots"/v["phase_id"]
    backup.mkdir(parents=True,exist_ok=False)
    previous=read(active)
    paths=[active]+[verify(previous[k],root) for k in ("current_phase","reconstruction","human_report")]
    saved=[]
    for p in paths:
        dest=backup/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        if rec(dest)["sha256"]!=rec(p)["sha256"]:raise ValueError("Prior authority backup mismatch")
        saved.append({"original":rec(p),"archived":rec(dest)})
    dump(backup/"archive_manifest.json",{"phase_id":previous["phase_id"],"files":saved,"recoverable":True})
    proposed={"project_id":previous["project_id"],"authority":previous["authority"],"updated_utc":now(),
              "phase_id":v["phase_id"],"current_phase":rec(phase_path),"reconstruction":previous["reconstruction"],
              "status":phase["status"],"human_report":phase["human_report"],
              "previous_phase_archive":rec(backup/"archive_manifest.json")}
    temporary=active.with_name(active.name+".benchmark-publication.partial")
    with temporary.open("x") as f:json.dump(proposed,f,indent=2,ensure_ascii=False);f.write("\n");f.flush();os.fsync(f.fileno())
    try:
        os.replace(temporary,active)
        published=read(active)
        for key in ("current_phase","reconstruction","human_report","previous_phase_archive"):verify(published[key],root)
    except Exception:
        rollback=active.with_name(active.name+".rollback.partial")
        shutil.copyfile(backup/active.relative_to(root),rollback);os.replace(rollback,active)
        raise
    return dump(backup/"publication_receipt.json",{"status":"SINGLE_ACTIVE_PHASE_PUBLISHED_HASH_VERIFIED",
          "active":rec(active),"previous_active":v["previous_active"],"phase_id":v["phase_id"],"archive":rec(backup/"archive_manifest.json")})
def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest="cmd",required=True)
    s=sp.add_parser("source-audit");s.add_argument("--root",required=True);s.add_argument("--out",required=True);s.add_argument("--apply",action="store_true");s.add_argument("--runtime-settings",default="pilot_v7")
    s=sp.add_parser("validate");s.add_argument("--config",required=True);s.add_argument("--out",required=True)
    s=sp.add_parser("package");s.add_argument("--validation",required=True);s.add_argument("--out",required=True);s.add_argument("--part-mib",type=int,default=512)
    s=sp.add_parser("extract");s.add_argument("--package",required=True);s.add_argument("--restore-root",required=True)
    s=sp.add_parser("publish")
    for name in ("validation","restore-acceptance","phase","active"):s.add_argument("--"+name,required=True)
    a=p.parse_args()
    if a.cmd=="source-audit":result=source_audit(a.root,a.out,a.apply,a.runtime_settings)
    elif a.cmd=="validate":result=validate(a.config,a.out)
    elif a.cmd=="package":result=package(a.validation,a.out,a.part_mib)
    elif a.cmd=="extract":result=extract(a.package,a.restore_root)
    else:result=publish(a.validation,a.restore_acceptance,a.phase,a.active)
    print(result.get("status") if isinstance(result,dict) else result)
if __name__=="__main__":main()

