#!/usr/bin/env python3
"""CPU final evidence composer. Existing delivery/restore APIs and science stay unchanged."""
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=Path(__file__).resolve().parent
LIB=R/"steps/24_benchmark_delivery/frozen/history_policy_13223/code"
FILES=("final_delivery_composer.py","test_final_delivery_composer.py","composer_bootstrap.py","composer_cpu.sbatch","composer_contracts_cpu.sbatch","HANDOFF.md","composer_context_api.py","relative_archive_restore.py")
MAPPER_STATUS="EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED"
SOFTWARE_TESTS=66
PINS={
 "delivery_core.py":(21656,"5e1e1f3f2e8a5f2c5771508b7e9433139ee36d58d5b2cc6514bf97333973ca4c"),
 "delivery_core_v2.py":(21981,"eb46c9adf772433e06851f2328f47bd5b2b11a101288d97cce9424cea718eb06"),
 "delivery_graph_v2.py":(8774,"e14b12e01c8e2b9a70ecb30d70d2194bbe89147c01eb02dd305be4075276f98d"),
 "provenance_aliases_v2.py":(5048,"1de9f0ba13cf8774f6de0fbe4410fd41b8dacf5e9e6d5f1f969b9842f1d8bd01"),
 "historical_scope_v2.py":(3163,"b8070b30e4633cc6e7d92ffc678fb921a325e96e51aa852bf7fd8b748213c735"),
 "native_resource_closure_v2.py":(20444,"33a1a8103efbf5d467e9e8360b9bac2f04624e1f1a5929caaa3cc282c6a66c48"),
 "restore_resolver_v2.py":(4979,"1618974ee343570adf82ad70ac56a0fcfe0a1eac8274476e81ef05691190689c"),
 "restore_verify_v2.py":(3526,"f052c3bb2f75f6cbd6c7d923df2fb40274cd7a088c62e5386627400d5059e0bf"),
 "common_review_independent_v2.py":(18822,"e42fc17a996e0fddf5c9d9f0cda6fbee4487ae0577f69b4c1ed3c17ee1a96919"),
 "target_statistics_v2.py":(8723,"cdad0d2dfb2005c2704178a641c48b40a5268b464cab9587d72ddcdc89f4bf73"),
 "github_export_verify.py":(11733,"157c9311f0b40dfbdd9114511741e32b5894f57fa8f02b68a66c3eb2da0978bd"),
}
SOFTWARE_STATUS="FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE"
ALLOCATION_STATUS="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED"
GATES=("screening_content","bbf_input_sensitivity_content","target_identity","runtime_gpu_pilot","generation_accounting","common_review_content","independent_score_recomputation","scientific_report_content","source_release")
ROLES={"formal_generation","common_raw","native_raw","bbf_raw","screening","reference_free_terminal","supplemental","reports","source_export"}
SECRET=re.compile(rb"(?im)(?:password|access_token|secret_key|api_key|private_key)\s*[:=]\s*[\x22\x27]?(?!None\b|null\b|os\.|env\b|\$\{|<|YOUR_|getenv\b)[A-Za-z0-9+/=_-]{12,}")
KEY=b"-----BEGIN "+b"OPENSSH PRIVATE KEY-----"
def need(v,msg):
    if not v:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text())
def safe(p):
    p=Path(p);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink(),"Outside authority or symbolic path")
    return p
def shape(r):
    need(isinstance(r,dict)and {"path","bytes","sha256"}<=r.keys(),"Exact receipt required")
    safe(r["path"]);need(isinstance(r["bytes"],int)and not isinstance(r["bytes"],bool)and r["bytes"]>=0,"Invalid receipt bytes")
    need(isinstance(r["sha256"],str)and re.fullmatch("[0-9a-f]{64}",r["sha256"])is not None,"Invalid exact SHA")
    return r
def key(r):return(r["path"],r["sha256"])
def identity(r):return(r["bytes"],r["sha256"])
def rec(p):
    p=safe(p);h=hashlib.sha256();n=0
    with p.open("rb")as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
    return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def verify(r,readonly=False):
    shape(r);p=safe(r["path"]);need(p.is_file()and identity(rec(p))==identity(r),"Exact bytes unavailable: "+str(p))
    need(not readonly or not(p.stat().st_mode&0o222),"Readonly archive required");return p
def dump(p,o):
    p=safe(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x")as f:json.dump(o,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
    p.chmod(0o444);return rec(p)
def load(name,p):
    p=safe(p);sys.path.insert(0,str(p.parent));s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def sources():
    need(D.is_relative_to(R/"steps/24_benchmark_delivery/frozen")and not(D.stat().st_mode&0o222),"Actual sealed composer only")
    own=[rec(verify(rec(D/n),True))for n in FILES];deps=[]
    for name,(n,h)in PINS.items():
        r=dict(path=str(LIB/name),bytes=n,sha256=h);verify(r,True);deps.append(r)
    context=context_api().source_records(rec,verify)
    return dict(composer=own,existing_API_dependencies=deps,context_API_dependencies=context)
def cpu():
    need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu","Pure CPU mask required")
    need(os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ,"CPU isolation required")
    need(os.environ.get("OPENBLAS_NUM_THREADS")=="1","CPU thread guard required")
    return load("composer_cpu_core",LIB/"delivery_core_v2.py").cpu()
def edges(o,trail=()):
    if isinstance(o,dict):
        if {"path","sha256","bytes"}<=o.keys():yield shape(o),trail
        for n,v in o.items():yield from edges(v,trail+(str(n),))
    elif isinstance(o,list):
        for n,v in enumerate(o):yield from edges(v,trail+(str(n),))
def conditional(p):
    p=Path(p);parts=p.parts
    return "env"in parts or "site-packages"in parts or "weights"in parts or "params"in parts or p.suffix==".whl"or ("assets"in parts and any(n in parts for n in("boltz","colabfold","rfdiffusion","bindcraft","mmseqs")))
def scan(p):
    p=safe(p);need(not any(n in p.parts for n in(".git",".ssh",".aws",".azure"))and p.name not in("id_ed25519","id_rsa",".netrc",".git-credentials",".env"),"Credential/repository-private path excluded")
    # Scan every file in bounded chunks, including raw/log/opaque files; overlaps retain boundary matches.
    tail=b""
    with p.open("rb")as f:
        while True:
            b=f.read(1048576)
            if not b:break
            joined=tail+b;need(not SECRET.search(joined)and KEY not in joined,"Potential literal credential in evidence; root review required")
            tail=joined[-2048:]
def expect(r,values):
    o=read(verify(r));need(isinstance(values,dict)and isinstance(values.get("status"),str),"Explicit status content gate required")
    for dotted,wanted in values.items():
        actual=o
        for part in dotted.split("."):actual=actual[part]
        need(actual==wanted,"Actual accepted gate mismatch: "+dotted)
    return o
def software(r,source):
    o=expect(r,{"status":SOFTWARE_STATUS});need(o["source"]==source,"Actual tested composer source differs")
    t=read(verify(o["contracts"]));need(t["status"]=="PASS"and t["tests_run"]==SOFTWARE_TESTS and t["failures"]==0 and t["errors"]==0 and t.get("tested_source")==source and t.get("all_owned_and_context_python_compile_PASS")is True and t.get("all_launchers_bash_syntax_PASS")is True,"Actual66 software contracts required")
    return o
def request(o,mode):
    need(o.get("schema")=="final-delivery-"+mode+"-request.v1"and o.get("root_owned")is True,"Root explicit request required")
    need(o.get("formal_array_job_id")=="13260"and o.get("scientific_scope")=="COMPUTATIONAL_ONLY","Frozen formal scope differs")
def inventory_universe(io):
    declared={row["receipt"]["path"]for row in io["files"]}|{row["receipt"]["path"]for row in io["conditional_inference_dependencies"]}
    roots={row["scope_root"]for row in io["files"]}|{scope["root"]for scope in io.get("declared_directories",[])}
    need(roots,"No ordinary terminal evidence in inventory")
    observed=set()
    for root in sorted(roots):
        for p in safe(root).rglob("*"):
            safe(p)
            if p.is_file():observed.add(str(p))
            else:need(p.is_dir(),"Nonregular inventory entry")
    need(observed==declared,"Terminal file universe gained or lost unbound files")
    return observed
def inventory(args,out):
    a=cpu();s=sources();software(args.software,s);rr=rec(verify(args.request,True));q=read(verify(rr));request(q,"inventory")
    scopes=q["directories"];need(scopes and len({x["root"]for x in scopes})==len(scopes),"Explicit unique terminal directories required")
    rows=[];excluded=[];seen=set()
    for scope in scopes:
        root=safe(scope["root"]);need(root.is_dir()and scope["role"]in ROLES,"Invalid explicit terminal directory")
        expect(scope["terminal_gate"]["receipt"],scope["terminal_gate"]["expect"])
        binding=scope["root_binding"];bo=read(verify(binding["receipt"]))
        for part in binding["field"].split("."):bo=bo[int(part)]if isinstance(bo,list)else bo[part]
        bound=Path(bo).parent if binding.get("parent")is True else Path(bo)
        need(bound==root,"Explicit directory does not equal exact accepted metadata root")
        need(root!=R and not root.is_relative_to(R/"source")and not root.is_relative_to(R/"env"),"Whole project/source/env inventory forbidden")
        for p in sorted(root.rglob("*")):
            safe(p)
            if p.is_dir():continue
            need(p.is_file(),"Nonregular terminal evidence")
            if str(p)in seen:raise ValueError("Overlapping explicit terminal directories")
            seen.add(str(p));r=rec(p)
            if conditional(p):excluded.append(dict(receipt=r,reason="Explicit conditional inference/runtime asset; excluded from archive",included_in_package=False));continue
            scan(p);rows.append(dict(receipt=r,scope_root=str(root),role=scope["role"],relative=p.relative_to(root).as_posix()))
    return dump(out/"acceptance.json",dict(schema="final-terminal-file-inventory.v1",status="EXPLICIT_TERMINAL_FILE_UNIVERSE_CPU_SEALED_NOT_ARCHIVE_ACCEPTANCE",allocation=a,source=s,request=rr,declared_directories=scopes,files=rows,conditional_inference_dependencies=excluded,file_count=len(rows),no_mtime_selection=True,no_GPU_submission=True,no_source_or_ACTIVE_change=True))
def merge_alias(rows,aliases):
    for e in rows:
        shape(e["original"]);shape(e["archived"]);need(identity(e["original"])==identity(e["archived"])and e["status"]=="READONLY_BYTE_IDENTICAL_ALIAS","Alias changes bytes or status")
        verify(e["archived"],True);k=key(e["original"])
        if k in aliases:
            need(identity(aliases[k]["archived"])==identity(e["archived"]),"Conflicting exact alias")
            if e["archived"]["path"]<aliases[k]["archived"]["path"]:aliases[k]=e
        else:aliases[k]=e
def recomputation(collection,common_config,summary):
    need(collection["schema"]=="formal_postprocess_collection.v2"and collection["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED","Actual formal collection required")
    fields=collection["files"]
    return dict(generation=dict(auditor_source=collection["sources"]["independent"],plan=collection["plan"]["path"],run_receipts=fields["run_receipts"]["path"],sacct=read(verify(fields["accounting"]))["raw_sacct"]["path"],producer_accounting=fields["accounting"]["path"],producer_cohort=fields["cohorts"]["path"]),common=common_config,statistics=dict(aggregation_policy="complete_selected_candidate_median_then_both_replicate_mean",producer_summary=summary["path"],rf_method_id="rf_diffusion",bindcraft_method_id="bindcraft"))
def context_api():return load("composer_v4_context_api",D/"composer_context_api.py")
def context_template():return context_api().root()/"exact_relative_bbf_context.py"
def context_bindings(context_request):
    q=context_request;api=context_api();bundle=api.load_bundle()
    mapper,prerequisite=bundle.b.verify_mapper_acceptance(q["mapper_acceptance"],q["mapping"],q["base_acceptance"],q["historical_mapping"],q["current_recovered_mapping"],q["archive_member_mapping"])
    source_proof=api.executed_mapper_binding(mapper["source_files"],sources()["context_API_dependencies"],identity)
    sourcebase,sourceclosure=bundle.c.source_bundle(q["base_acceptance"],q["mapping"],q["historical_mapping"],lambda r:bundle.b.verify_bytes(r,True),q["current_recovered_mapping"],q["archive_member_mapping"])
    source_qualified,finite_proof=bundle.s.verify_saved_alias_proofs(mapper,sourcebase,sourceclosure,lambda r:bundle.b.verify_bytes(r,True))
    bundle.source_qualification=source_qualified
    return bundle,dict(mapper_acceptance=q["mapper_acceptance"],base_acceptance=q["base_acceptance"],mapping=q["mapping"],historical_mapping=q["historical_mapping"],current_recovered_mapping=q["current_recovered_mapping"],archive_member_mapping=q["archive_member_mapping"],accepted_mapper_sources=source_proof["accepted_source_files"],executed_mapper_sources=source_proof["executed_source_files"],actual_mapper_prerequisite=prerequisite,finite_source_artifacts={name:sourcebase[name]for name in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index")},finite_mapper_proofs={name:mapper[name]for name in ("finite_source_independent_verification","finite_source_read_view_proof")},finite_source_independent_qualification=finite_proof)

def validate_archive_context(api,config_path,out_path,reader,bindings):
    original=api.read
    try:
        api.read=reader
        result=api.validate(config_path,out_path)
    finally:api.read=original
    # Preserve the core output bytes; context proof is a separate delivery receipt.
    Path(out_path).chmod(0o444)
    if hasattr(reader,"require_both_used"):reader.require_both_used()
    proof=reader.proof()
    proof_receipt=dump(Path(out_path).with_name(Path(out_path).stem+"_context.json"),dict(status="EXACT_CONTEXT_FROZEN_VALIDATION_READ_VIEW_RECORDED",bindings=bindings,read_view_proof=proof,core_validation=rec(out_path),unchanged_frozen_API="delivery_core_v2.validate(config,out)",old_raw_JSON_bytes_changed=False))
    return result,proof_receipt

def mandatory_final_source_shape(accepted,inclusion,derived):
    need(accepted.get("schema")=="final-source-closure-acceptance.v3"and accepted.get("status")=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED"and accepted.get("source_inclusion")==inclusion and accepted.get("source_issues")==0,"Actual final source closure/inclusion required")
    proof=accepted.get("mandatory_derived_pipeline_qualification",{})
    need(proof.get("acceptance")==derived and proof.get("all_eight_actual_suite_rows_verified")is True and proof.get("derived_pipeline")is not None and len(proof.get("source_dependencies",[]))==1 and proof.get("failed_predecessor",{}).get("status")=="ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED","Final delivery requires actual mandatory derived input/pool qualification")
    return proof


CONTROLLER_AMENDMENT_ACCEPTANCE={"path":str(R/"steps/25_reference_free_e2e/runs/controller_metadata_amendment_13315/acceptance.json"),"bytes":3901,"sha256":"1d51a4002b690e569df1bbf6e07ac7fda62cd69dd05642535d064179eb93728d"}
CONTROLLER_JOURNAL4_PATH=str(R/"steps/24_benchmark_delivery/submissions/root_gpu_journal/0004_controller_metadata_amendment_13315.json")
def controller_amendment_content(qualification_receipt,a,amend,old,new,design,journal3,journal4):
    need(a.get("schema")=="root-controller-metadata-amendment-CPU-qualification.v1"and a.get("status")=="ROOT_ACTUAL_EVALUATE_CONTROLLER_SINGLE_DESCRIPTOR_ADDITION_CPU_ACCEPTED"and a.get("actual_job_id")=="13311"and a.get("all_original_submission_fields_and_journal_entries_unchanged")is True,"Actual controller amendment content qualification required")
    need(a.get("allocation",{}).get("slurm_job_id")=="13315"and a["allocation"].get("allocated_GPU_count")==0 and a["allocation"].get("allocated_CPU_count")==1,"Actual amendment CPU13315/GPU0 identity required")
    need(amend.get("schema")=="root-controller-traceable-metadata-only-amendment.v1"and amend.get("original_controller_exact_byte_archive")==a["archived_original_controller"]and amend.get("amended_controller")==a["amended_controller"]and amend.get("journal")==a["journal"],"Exact original/archive/current/journal amendment pointers differ")
    addition=dict(design_audit_acceptance=a["actual_design_CPU_acceptance"])
    need("design_audit_acceptance"not in old and set(new)==set(old)|{"design_audit_acceptance"}and all(new[k]==v for k,v in old.items())and new["design_audit_acceptance"]==addition["design_audit_acceptance"],"Controller object diff must be exactly one descriptor addition")
    need(amend.get("addition_only")==addition and amend.get("original_other_fields_unchanged")is True and amend.get("journal_bytes_unchanged")is True and amend.get("new_GPU_job_submitted")is False and amend.get("scientific_settings_changed")is False and amend.get("actual_original_GPU_job_id")=="13311","Only traceable metadata addition without new GPU/science allowed")
    need(old.get("schema")==new.get("schema")=="reference_free_root_model_submission.v1"and old.get("job_id")==new.get("job_id")=="13311"and old.get("stage")==new.get("stage")=="evaluate"and old.get("root_owned_primary")is True,"Original actual evaluate submission identity differs")
    need(amend.get("original_controller_logical_path")==a["amended_controller"]["path"]and new.get("design_audit_acceptance_path")==a["actual_design_CPU_acceptance"]["path"]and new.get("submit_argv",[])[-1:]==[a["actual_design_CPU_acceptance"]["path"]],"Actual unchanged argv/design audit descriptor path differs")
    need(design.get("schema")=="reference_free_e2e_design_cpu_gate.v1"and design.get("status")=="REFERENCE_FREE_E2E_ACTUAL_DESIGN_CPU_CONTENT_ACCEPTED"and design.get("slurm_CPU_job_id")=="13309"and design.get("GPU_allocated")==0 and design.get("actual_design_manifest")==new.get("upstream")and design.get("actual_design_stage_result")==new.get("design_stage_result")and design.get("source_manifest")==new.get("source_manifest")and design.get("preflight_acceptance")==new.get("preflight_acceptance"),"Actual design CPU content/lineage differs from evaluate submission")
    need(journal3.get("schema")==journal4.get("schema")=="root-current-gpu-submission-journal.v1"and journal3.get("entries")==journal4.get("entries")and journal3.get("authority_root")==journal4.get("authority_root")==str(R)and journal3.get("scope_start_utc")==journal4.get("scope_start_utc"),"Journal amendment must preserve exact submission/scientific universe")
    need(journal4.get("previous_journal_path")==a["journal"]["path"]and journal4.get("metadata_only_controller_amendment_CPU_qualifications")==[qualification_receipt],"Actual new journal must bind full amendment qualification/predecessor")
    matches=[e for e in journal4["entries"]if e.get("submission_id")=="e2e_evaluate_13311"]
    need(len(matches)==1 and matches[0].get("receipt_path")==a["amended_controller"]["path"],"Same actual evaluate controller must remain in journal universe")
    return dict(status="INDEPENDENT_ACTUAL13315_CONTROLLER_ONLY_ADDITION_AND_JOURNAL_UNIVERSE_CONTENT_VERIFIED",qualification=qualification_receipt,amendment=a["amendment"],original_controller_archive=a["archived_original_controller"],amended_controller=a["amended_controller"],actual_design_CPU_acceptance=a["actual_design_CPU_acceptance"],journal3=a["journal"],only_added_field="design_audit_acceptance",all_original_fields_and_argv_unchanged=True,submission_entries_unchanged=True,new_GPU_job_submitted=False,scientific_settings_changed=False)
def amendment_terminal(jid,name):
    raw=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
    rows=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==jid]
    need(len(rows)==1 and len(rows[0])>=9,"Unique amendment/design terminal accounting required")
    job,state,exitcode,elapsed,tres,user,account,jobname,partition=rows[0][:9]
    values=context_api().load_bundle().b.strict_tres(tres)
    need(state=="COMPLETED"and exitcode=="0:0"and elapsed.isdigit()and user==account=="u21111210118"and partition=="organ"and jobname==name and values["cpu"]==1,"Actual named terminal CPU1/GPU0 amendment/design qualification required")
    return dict(raw=raw,row=rows[0],allocated_CPUs=1,allocated_GPUs=0)
def qualify_controller_amendment(binding,read_exact=None,restore=False):
    need(isinstance(binding,dict)and binding.get("qualification")==CONTROLLER_AMENDMENT_ACCEPTANCE,"Exact actual13315 qualification tuple required")
    need(binding.get("journal4",{}).get("path")==CONTROLLER_JOURNAL4_PATH,"Exact journal004 identity required")
    need(not restore or read_exact is not None,"Controller restore requires explicit restored-index reader")
    exact=read_exact or(lambda r:verify(r,True));inputs=[]
    def data(r):
        p=exact(r);need(not(p.stat().st_mode&0o222),"Readonly controller amendment authority/source required");inputs.append(r);return json.loads(p.read_text())
    a=data(binding["qualification"]);amend=data(a["amendment"]);old=data(a["archived_original_controller"]);new=data(a["amended_controller"]);design=data(a["actual_design_CPU_acceptance"]);j3=data(a["journal"]);j4=data(binding["journal4"])
    proof=controller_amendment_content(binding["qualification"],a,amend,old,new,design,j3,j4)
    sources=a.get("source",[]);need(len(sources)==2 and {Path(r["path"]).name for r in sources}=={"amendment.py","amendment.sbatch"},"Exact actual amendment two-source universe required")
    for r in sources:exact(r);inputs.append(r)
    if restore:
        need(isinstance(binding.get("independent_proof"),dict),"Saved independent controller qualification required in restore")
        saved=data(binding["independent_proof"]);terminal=saved["actual_terminal_accounting"]
        for jid,name in (("13315","test9_controller_metadata_amendment"),("13309","test9_reference_free_design_audit")):
            row=terminal[jid]["row"];need(isinstance(row,list)and len(row)>=9 and "|".join(row)in terminal[jid]["raw"],"Saved actual numeric amendment/design row required")
            need(row[0]==jid and row[1:3]==["COMPLETED","0:0"]and row[3].isdigit()and row[5:9]==["u21111210118","u21111210118",name,"organ"],"Saved actual amendment/design terminal identity differs")
            vals=context_api().load_bundle().b.strict_tres(row[4]);need(vals["cpu"]==1 and terminal[jid].get("allocated_CPUs")==1 and terminal[jid].get("allocated_GPUs")==0,"Saved actual CPU1/GPU0 amendment/design accounting differs")
    else:terminal={jid:amendment_terminal(jid,name)for jid,name in (("13315","test9_controller_metadata_amendment"),("13309","test9_reference_free_design_audit"))}
    result=dict(proof,journal4=binding["journal4"],source_files=sources,actual_terminal_accounting=terminal,all_exact_inputs=inputs,restored_only=restore,no_live_fallback=restore)
    if restore:
        expected=dict(result,restored_only=False,no_live_fallback=False);expected["all_exact_inputs"]=[r for r in inputs if r!=binding["independent_proof"]]
        need(saved==expected,"Complete saved independent controller qualification missing/truncated/forked")
    for r in inputs:exact(r)
    return result

def compose(args,out):
    a=cpu();s=sources();sw=software(args.software,s);rr=rec(verify(args.request,True));q=read(verify(rr));request(q,"compose")
    need(set(q["gates"])==set(GATES)-{"source_release"},"Exactly8 existing scientific gates required")
    context,context_binding=context_bindings(q["relative_context"])
    controller_proof=qualify_controller_amendment(q["controller_metadata_amendment"])
    controller_proof_receipt=dump(out/"independent_controller_amendment_13315.json",controller_proof)
    context_binding["controller_metadata_amendment"]=dict(q["controller_metadata_amendment"],independent_proof=controller_proof_receipt)
    context_binding.update(composer_software=args.software,composer_source=s["composer"],existing_API_dependencies=s["existing_API_dependencies"],context_API_dependencies=s["context_API_dependencies"])
    mapping,map_proof=context.b.verify_mapping_receipt(q["relative_context"]["mapping"])
    historical_mapping,historical_proof=context.h.verify_mapping_receipt(q["relative_context"]["historical_mapping"])
    current_mapping,current_proof=context.f.verify_mapping_receipt(q["relative_context"]["current_recovered_mapping"])
    archive_mapping,archive_proof=context.a.verify_mapping_receipt(q["relative_context"]["archive_member_mapping"])
    archive_proof_receipt=dump(out/"archive_member_context_preflight.json",archive_proof)
    terminal_proof_receipt=dump(out/"mapper_terminal_qualification.json",context_binding["actual_mapper_prerequisite"])
    context_binding["mapper_terminal_qualification"]=terminal_proof_receipt
    historical_proof_receipt=dump(out/"historical_context_preflight.json",historical_proof)
    current_proof_receipt=dump(out/"current_recovered_context_preflight.json",current_proof)
    map_proof_receipt=dump(out/"relative_context_preflight.json",map_proof)
    for name,g in q["gates"].items():expect(g["receipt"],g["expect"])
    c=expect(q["common_successor"],{"status":"FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY","n_fixed_cohort_engine_rows":112,"n_primary_targets":6,"n_diagnostic_targets":1})
    need(q["gates"]["common_review_content"]["receipt"]==c["common_acceptance"],"Use inner accepted common content gate")
    need(q["gates"]["independent_score_recomputation"]["receipt"]==c["independent_common"],"Actual independent raw score gate differs")
    common_cfg=read(verify(q["common_config"]));need(common_cfg["producer_acceptance"]==c["common_acceptance"]["path"],"Common recomputation pointer differs")
    stats=read(verify(c["statistics"]));need(stats["n_cohort_engine_rows"]==112 and len(stats["rows"])==56 and stats["n_primary_targets"]==6 and stats["complete_matrix_macro_requires_all_six_pairs"]is True,"Frozen112/all6 statistics required")
    collection=read(verify(q["formal_collection"]));need(q["gates"]["generation_accounting"]["receipt"]==collection["files"]["accounting"],"Actual formal accounting gate differs")
    cost=expect(q["root_gpu_cost"],{"status":ALLOCATION_STATUS,"complete_root_gpu_submission_universe":True,"allocated_failure_before_manifest_cost_retained":True})
    need(isinstance(cost["root_gpu_submission_receipts"],list)and isinstance(cost["terminal_numeric_accounting_receipts"],list),"All root numeric cost receipts required")
    report=q["report_binding"];rq=read(verify(q["gates"]["scientific_report_content"]["receipt"]))
    need(rq["status"]=="FORMAL13260_FINAL_CHINESE_REPORT_AND_MATRIX_CPU_ACCEPTED","Actual final report QA required; old/PENDING/software reports cannot substitute")
    need(rq["report"]==report["report"]and rq["common_successor"]==q["common_successor"]and rq["statistics"]==c["statistics"]and rq["root_gpu_cost"]==q["root_gpu_cost"],"Final report actual common112/cost receipt binding differs")
    need(rq["n_fixed_cohort_engine_rows"]==112 and rq["n_primary_targets"]==6 and rq["scientific_scope"]=="COMPUTATIONAL_ONLY"and rq["experimental_binding_or_blockade"]is False,"Final report fixed-denominator/evidence scope differs")
    verify(report["report"])
    github=load("composer_independent_github",LIB/"github_export_verify.py")
    src=q["source_release"]
    final_source=read(verify(src["final_source_acceptance"],True));derived_proof=mandatory_final_source_shape(final_source,src["source_inclusion"],src["derived_pipeline_qualification"])
    derived=read(verify(src["derived_pipeline_qualification"],True));need(derived.get("schema")=="generic-design-input-empty-pool-qualification.v2"and derived.get("status")=="GENERIC_DESIGN_INPUT_AND_NONEMPTY_POOL_WITH_REGRESSION_DEPENDENCY_V2_CPU_ACCEPTED"and derived.get("derived_pipeline")==derived_proof["derived_pipeline"]and derived.get("source_dependencies")==derived_proof["source_dependencies"]and derived.get("failed_predecessor")==derived_proof["failed_predecessor"],"Actual derived pipeline content acceptance differs")
    need(re.fullmatch("[0-9a-f]{40}",src["expected_commit"])is not None,"Exact approved commit required")
    need(subprocess.check_output(["git","-C",str(R/"source"),"rev-parse","HEAD"],text=True).strip()==src["expected_commit"],"Current approved commit differs")
    need(not subprocess.check_output(["git","-C",str(R/"source"),"status","--porcelain","--untracked-files=all"],text=True).strip(),"Clean actual source tree required")
    bundle=verify(src["source_bundle"],True)
    checked=subprocess.run(["git","-C",str(R/"source"),"bundle","verify",str(bundle)],capture_output=True,text=True)
    (out/"source_bundle_verify.stdout").write_text(checked.stdout);(out/"source_bundle_verify.stderr").write_text(checked.stderr)
    need(checked.returncode==0,"Private source history bundle is not actually verified")
    heads=subprocess.check_output(["git","bundle","list-heads",str(bundle)],text=True)
    (out/"source_bundle_heads.txt").write_text(heads)
    need(src["expected_commit"]in {line.split()[0]for line in heads.splitlines()},"Private bundle lacks the exact approved final local commit")
    inclusion=expect(src["source_inclusion"],{"status":"SOURCE_INCLUSION_AUDIT_PASS","applied":False})
    need(not inclusion["issues"]and inclusion.get("formal_array_job_id")=="13260","Current final source closure required")
    for row in inclusion["files"]:
        dest=safe(R/"source"/row["repository_relative"]);verify(dict(row["source"],path=str(dest)))
        committed=subprocess.check_output(["git","-C",str(R/"source"),"cat-file","blob",src["expected_commit"]+":"+row["repository_relative"]])
        need(hashlib.sha256(committed).hexdigest()==row["source"]["sha256"]and len(committed)==row["source"]["bytes"],"Committed tree/source inclusion bytes differ")
    export=src["github"];manifest=read(verify(export["manifest"]));need(safe(export["export_dir"])/"export_manifest.json"==Path(export["manifest"]["path"]),"GitHub export manifest identity differs")
    need(export.get("published_ref")and export.get("api_responses"),"Actual API/readback plus fetched public ref required")
    readback=github.verify(export["export_dir"],str(R/"source"),read(verify(export["api_responses"])),export["published_ref"])
    need(readback["status"]=="PASS"and readback["local_commit_sha"]==src["expected_commit"]and readback["published_ref_verified"]==export["published_ref"]and readback["api_responses_verified"]is True,"Actual public source tree parity required")
    ghrec=dump(out/"github_source_readback.json",readback)
    source_release=dump(out/"source_release.json",dict(status="CLEAN_COMMITTED_PUBLIC_SOURCE_TREE_AND_INCLUSION_CPU_VERIFIED",working_tree_clean=True,commit=src["expected_commit"],source_inclusion=src["source_inclusion"],github_independent_readback=ghrec,export_manifest=export["manifest"],api_responses=export["api_responses"],verified_private_source_bundle=src["source_bundle"],private_source_bundle_head_log=rec(out/"source_bundle_heads.txt"),private_source_bundle_verifier_stdout=rec(out/"source_bundle_verify.stdout"),private_source_bundle_verifier_stderr=rec(out/"source_bundle_verify.stderr"),scientific_scope="COMPUTATIONAL_ONLY",ACTIVE_changed=False))
    gates=dict(q["gates"],source_release=dict(receipt=source_release,expect=dict(status="CLEAN_COMMITTED_PUBLIC_SOURCE_TREE_AND_INCLUSION_CPU_VERIFIED",working_tree_clean=True,commit=src["expected_commit"])))
    inventories=[]
    for ir in q["terminal_inventories"]:
        io=expect(ir,{"status":"EXPLICIT_TERMINAL_FILE_UNIVERSE_CPU_SEALED_NOT_ARCHIVE_ACCEPTANCE"})
        inventory_universe(io);inventories.append((ir,io))
    roles={r["role"]for _,io in inventories for r in io["files"]}
    need({"formal_generation","common_raw","native_raw","bbf_raw","screening","reports","source_export"}<=roles,"Explicit complete terminal evidence roles required")
    aliases={};unresolved={}
    for ar in q["alias_indices"]:
        ao=read(verify(ar));merge_alias(ao.get("aliases",[]),aliases)
        for e in ao.get("historical_unresolved",[]):
            k=key(e["original"]);need(k not in unresolved or unresolved[k]==e,"Conflicting historical declaration");unresolved[k]=e
    merge_alias(q.get("exact_aliases",[]),aliases)
    for row in inclusion["files"]:
        for original in [row["original_source"]]+row.get("logical_receipts",[]):
            merge_alias([dict(original=original,archived=row["source"],status="READONLY_BYTE_IDENTICAL_ALIAS",role="EXACT_FINAL_SOURCE_BYTES")],aliases)
    # Native raw/resource copies use unchanged exact old logical receipt strings.
    for nr in q.get("native_resource_closures",[]):
        no=read(verify(nr))
        merge_alias([dict(original=e["original"],archived=e["copy"],status="READONLY_BYTE_IDENTICAL_ALIAS",role="EXACT_NATIVE_RESOURCE_BYTES")for e in no["resources"]if e.get("copied")and e.get("scope")!="RECOMPUTE_DEPENDENCY"],aliases)
    aliaslib=load("composer_exact_aliases",LIB/"provenance_aliases_v2.py")
    resolver=aliaslib.ReceiptResolver(R,index=dict(aliases=list(aliases.values()),historical_unresolved=list(unresolved.values())))
    historylib=load("composer_exact_history",LIB/"historical_scope_v2.py");policy=read(verify(q["historical_provenance_policy"]))
    history=historylib.HistoricalScopeVerifier(resolver,policy)
    graph_reader=context.c.VerifiedContextReader(q["relative_context"]["mapper_acceptance"],q["relative_context"]["base_acceptance"],q["relative_context"]["mapping"],q["relative_context"]["historical_mapping"],read,[],[],q["relative_context"]["current_recovered_mapping"],[],q["relative_context"]["archive_member_mapping"],[])
    files={};deps={};seen=set();closure=[]
    def add_file(r,classification="EVIDENCE"):
        p=safe(r["path"]);verify(r);scan(p)
        if conditional(p):deps[key(r)]=dict(receipt=r,reason="Exact conditional inference/runtime dependency excluded from evidence archive",included_in_package=False);return
        old=files.get(str(p));need(old is None or identity(old["receipt"])==identity(r),"Two current byte identities at one physical path")
        files[str(p)]=dict(receipt=r,classification=classification if old is None else old["classification"])
    def enqueue(r,parent_descriptor=None,trail=()):
        r,relative_context=context.c.normalize_edge(r,parent_descriptor,trail,mapping,historical_mapping,current_mapping,archive_mapping)
        if r is None:
            closure.append(dict(scope="EXACT_HISTORICAL_ARCHIVE_NAMESPACE"if relative_context.get("role")==context.a.ROLE else"EXACT_NINE_NONOPERATIVE_UNRECOVERED_ANNOTATIONS",scalar_context=relative_context,parent=parent_descriptor,field=list(trail)));return
        parent=parent_descriptor["path"]if parent_descriptor else None
        shape(r)
        if key(r)in resolver.unresolved:
            need(history.edge(r,parent,trail),"Missing source not allowed at this exact current edge")
            history.metadata(resolver.unresolved[key(r)])
            closure.append(dict(scope="ENGINEERING_HISTORY",historical_unresolved=resolver.unresolved[key(r)],parent=parent,field=list(trail),role="EXACT_NONOPERATIVE_HISTORY_ONLY"));return
        if conditional(r["path"]):deps[key(r)]=dict(receipt=r,reason="Exact declared conditional inference/runtime dependency",included_in_package=False);return
        p=resolver.verify(r);physical=rec(p)
        add_file(physical,"SOURCE"if p.suffix in(".py",".sh",".sbatch")else"EVIDENCE")
        closure.append(dict(receipt=r,physical=physical,parent=parent,field=list(trail),role="EXACT_READBACK",relative_context=relative_context))
        if key(r)in seen:return
        seen.add(key(r))
        if p.suffix==".json":
            obj=graph_reader(p)
            def traverse(value,trail=()):
                if isinstance(value,dict):
                    if value.get("status")=="HISTORICAL_UNRESOLVED_PROVENANCE":history.metadata(value);return
                    if value.get("scope")=="ENGINEERING_HISTORY"and value.get("historical_unresolved"):history.metadata(value["historical_unresolved"]);return
                    if {"path","sha256"}<=value.keys():
                        child=dict(value)
                        if "bytes"not in child:
                            need(Path(child["path"]).is_absolute(),"Unknown relative receipt without exact byte count")
                            if conditional(child["path"]):
                                deps[key(child)]=dict(receipt=child,reason="Exact conditional runtime receipt has no byte-count in original metadata",included_in_package=False)
                                return
                            need(Path(child["path"]).is_relative_to(R),"Unknown current external receipt without byte count forbidden")
                            physical_child=resolver.resolve(child["path"],child["sha256"])
                            child["bytes"]=rec(physical_child)["bytes"]
                        enqueue(child,dict(path=r["path"],bytes=r["bytes"],sha256=r["sha256"]),trail)
                    for name,v in value.items():traverse(v,trail+(str(name),))
                elif isinstance(value,list):
                    for i,v in enumerate(value):traverse(v,trail+(str(i),))
            traverse(obj)
    seeds=[rr,rec(verify(args.software)),q["previous_active"],src["final_source_acceptance"],src["derived_pipeline_qualification"],q["common_successor"],q["common_config"],q["formal_collection"],q["root_gpu_cost"],q["historical_provenance_policy"],source_release,ghrec,c["statistics"],q["relative_context"]["mapper_acceptance"],q["relative_context"]["base_acceptance"],q["relative_context"]["mapping"],q["relative_context"]["historical_mapping"],q["relative_context"]["current_recovered_mapping"],q["relative_context"]["archive_member_mapping"],archive_proof_receipt,map_proof_receipt,historical_proof_receipt,current_proof_receipt,terminal_proof_receipt,context.b.PARENT,context.h.PARENT,context.f.PARENT]+[r for x in context.a.ARCHIVES for r in (x["parent_manifest"],x["archive_receipt"])]+[context.f.expected_entry(i)["canonical_receipt"]for i in range(5)]+q["evidence_seeds"]+q["alias_indices"]+q.get("native_resource_closures",[])+[g["receipt"]for g in gates.values()]+[r for r in s["composer"]+s["existing_API_dependencies"]+s["context_API_dependencies"]]
    for ir,io in inventories:
        seeds.append(ir)
        for row in io["files"]:seeds.append(row["receipt"])
        for e in io["conditional_inference_dependencies"]:deps[key(e["receipt"])]=e
    for e in aliases.values():seeds.append(e["archived"])
    seeds+=controller_proof["all_exact_inputs"]+[controller_proof_receipt]
    seeds+=context.s.required_parent_receipts(context.source_qualification)+context.source_qualification["canonical_source_and_provenance_inputs"]+list(context_binding["finite_source_artifacts"].values())+list(context_binding["finite_mapper_proofs"].values())
    for r in seeds:enqueue(r)
    graph_reader.require_both_used()
    finite_closure_proof=dump(out/"actual_finite_source_context_graph_proof.json",graph_reader.proof())
    add_file(finite_closure_proof,"AUDIT")
    aliasrec=dump(out/"resource_aliases.json",dict(schema="exact-resource-aliases.v2",aliases=sorted(aliases.values(),key=lambda e:key(e["original"])),historical_unresolved=sorted(unresolved.values(),key=lambda e:key(e["original"]))))
    add_file(aliasrec,"AUDIT")
    closerec=dump(out/"evidence_closure.json",dict(status="EXACT_ALL_RECEIPT_AND_TERMINAL_FILE_UNIVERSE_READ_BACK",edges=closure,explicit_terminal_inventories=q["terminal_inventories"],actual_gpu_cost=q["root_gpu_cost"],physical_observations=c["intrinsic_target_binder_physical_clearance"],all_failed_costs_retained=True,source_and_models_do_not_prove_binding=True,relative_context_mapping=q["relative_context"]["mapping"],relative_context_preflight=map_proof_receipt,current_recovered_context_mapping=q["relative_context"]["current_recovered_mapping"],current_recovered_context_preflight=current_proof_receipt,all_five_current_evidence_included=True,archive_member_context_mapping=q["relative_context"]["archive_member_mapping"],archive_member_preflight=archive_proof_receipt,all_two_archive_indices_and_tars_included=True,all588_archive_member_bytes_verified=True,archive_members_current_files=False))
    add_file(closerec,"AUDIT")
    config=dict(schema="benchmark-delivery.v2",scientific_scope="COMPUTATIONAL_ONLY",authority_root=str(R),phase_id=q["phase_id"],previous_active=q["previous_active"],gates=gates,resource_aliases=aliasrec,historical_provenance_policy=q["historical_provenance_policy"],files=sorted(files.values(),key=lambda e:e["receipt"]["path"]),conditional_inference_dependencies=sorted(deps.values(),key=lambda e:key(e["receipt"])),recomputation=recomputation(collection,common_cfg,c["statistics"]),exact_relative_context=dict(bindings=context_binding,preflight=map_proof_receipt))
    configrec=dump(out/"delivery_config.json",config)
    api=load("composer_actual_delivery_validation",LIB/"delivery_core_v2.py")
    def parent_aliases(parent):return [dict(logical=parent,physical=e["archived"])for e in aliases.values()if e["original"]==parent and e["archived"]["path"]!=parent["path"]]
    reader=context.c.VerifiedContextReader(q["relative_context"]["mapper_acceptance"],q["relative_context"]["base_acceptance"],q["relative_context"]["mapping"],q["relative_context"]["historical_mapping"],api.read,parent_aliases(context.b.PARENT),parent_aliases(context.h.PARENT),q["relative_context"]["current_recovered_mapping"],parent_aliases(context.f.PARENT),q["relative_context"]["archive_member_mapping"],[row for spec in context.a.ARCHIVES for row in parent_aliases(spec["parent_manifest"])],[row for parent in context.s.required_parent_receipts(context.source_qualification)for row in parent_aliases(parent)])
    _,validation_context=validate_archive_context(api,str(verify(configrec)),str(out/"delivery_validation.json"),reader,context_binding)
    return dump(out/"acceptance.json",dict(status="FINAL_DELIVERY_CONFIG_AND_UNIVERSE_CPU_VALIDATED_ARCHIVE_RESTORE_PUBLICATION_PENDING",allocation=a,source=s,request=rr,software=rec(verify(args.software)),config=configrec,validation=rec(out/"delivery_validation.json"),validation_context=validation_context,source_release=source_release,resource_aliases=aliasrec,evidence_closure=closerec,n_files=len(files),n_conditional_dependencies=len(deps),full_archive_complete=False,full_restore_complete=False,ACTIVE_changed=False,relative_context=dict(bindings=context_binding,preflight=map_proof_receipt),root_only_next="existing frozen delivery_core_v2 package -> extract -> relative_archive_restore restored-only context gate + existing restore_verify_v2 -> root publish"))
def main():
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("inventory","compose"));p.add_argument("--request",required=True);p.add_argument("--request-sha256",required=True);p.add_argument("--software",required=True);p.add_argument("--software-sha256",required=True);p.add_argument("--out",required=True);args=p.parse_args()
    cpu() # Reject login/GPU execution before any CLI hashing.
    args.request=rec(args.request);need(args.request["sha256"]==args.request_sha256,"Request exact CLI SHA differs")
    args.software=rec(args.software);need(args.software["sha256"]==args.software_sha256,"Software exact CLI SHA differs")
    out=safe(args.out);out.mkdir(parents=True,exist_ok=False)
    try:print(json.dumps(inventory(args,out)if args.mode=="inventory"else compose(args,out)))
    except Exception as e:dump(out/"typed_incomplete.json",dict(status="FINAL_COMPOSER_TYPED_INCOMPLETE_NO_ARCHIVE_OR_PROMOTION",stage=args.mode,reason_type=type(e).__name__,reason=str(e),partial_evidence_retained=True));raise
if __name__=="__main__":main()
