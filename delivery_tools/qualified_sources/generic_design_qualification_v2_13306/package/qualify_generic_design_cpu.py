"""PureCPU qualification of narrow generic design validation on accepted Physical V3."""
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,traceback
import xml.etree.ElementTree as ET
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
NAMES=("patch_generic_design.py","test_generic_design.py","qualify_generic_design_cpu.py","generic_design_cpu.sbatch","HANDOFF.md")
GENERIC=("test_af2_review.py","test_audit_regressions.py","test_benchmark.py","test_construct_contract.py","test_development_regressions.py","test_runtime_registration.py","test_scientific_contracts.py")
PHYSICAL=(("physical","test_pose_physical_gate.py",25),("resource","test_e2e_resource_policy.py",9),("design","test_e2e_design_contracts.py",8),("staged_selector","test_common_runtime_selector.py",15))
STATUS="GENERIC_DESIGN_INPUT_AND_NONEMPTY_POOL_WITH_REGRESSION_DEPENDENCY_V2_CPU_ACCEPTED"
def need(v,message):
    if not v:raise ValueError(message)
def rec(p):
    p=Path(p);h=hashlib.sha256();n=0
    with p.open("rb")as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block);n+=len(block)
    return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def verify(r,readonly=True):
    need(isinstance(r,dict)and set(r)>={"path","bytes","sha256"}and type(r["bytes"])is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact receipt required")
    p=Path(r["path"]);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink()and p.is_file(),"Exact nonsymlink authority file required")
    need(not readonly or not(p.stat().st_mode&0o222),"Readonly qualification input required")
    need(rec(p)=={k:r[k]for k in ("path","bytes","sha256")},"Qualification input bytes changed: "+str(p));return p
def read(r,readonly=True):return json.loads(verify(r,readonly).read_text())
def dump(p,obj):
    p=Path(p)
    with p.open("x")as f:json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write("\n")
    p.chmod(0o444);return rec(p)
def terminal(jid,state,name):
    need(isinstance(jid,str)and jid.isdigit(),"Actual numeric CPU job identity required")
    raw=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
    rows=[line.split("|")for line in raw.splitlines()if line.split("|",1)[0]==jid]
    need(len(rows)==1 and len(rows[0])>=9,"Unique actual CPU accounting required")
    job,actual,exitcode,elapsed,tres,user,account,jobname,partition=rows[0][:9]
    need(actual==state and (state!="COMPLETED"or exitcode=="0:0")and elapsed.isdigit()and user==account=="u21111210118"and partition=="organ"and jobname==name,"Actual CPU owner/name/state differs")
    vals={}
    for token in tres.split(","):
        need("="in token,"Numeric allocated CPU TRES missing")
        k,v=token.split("=",1);need(k not in vals,"Duplicate allocation TRES");vals[k]=v
    def n(k):
        value=vals.get(k,"0");need(re.fullmatch("[0-9]+",value),"Integer CPU/GPU TRES required");return int(value)
    need(n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"Real CPU allocation with GPU0 required")
    return dict(job_id=job,state=actual,exit_code=exitcode,elapsed_seconds=int(elapsed),allocated_CPUs=n("cpu"),allocated_GPUs=0,raw=raw,row=rows[0])
def cpu():
    need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and not os.environ.get("PYTHONPATH"),"Isolated actual CPU job required before hashing")
    return terminal(os.environ.get("SLURM_JOB_ID",""),"RUNNING","test9_generic_design_guard_v2")
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def tree_sha(source,common_override=None):
    payload=[]
    for p in sorted((Path(source)/"src").rglob("*.py")):
        digest=rec(common_override)["sha256"]if common_override is not None and p.relative_to(source).as_posix()=="src/ppiblocker/common.py"else rec(p)["sha256"]
        payload.append(str(p.relative_to(source))+digest)
    return hashlib.sha256("".join(payload).encode()).hexdigest()
def immutable_tree(root):
    for p in root.rglob("*"):
        if p.is_file():p.chmod(0o444)
    for p in sorted((x for x in root.rglob("*")if x.is_dir()),key=lambda p:len(p.parts),reverse=True):p.chmod(0o555)
    root.chmod(0o555)
def command(argv,env,out,name,expected=None,pytest_xml=False):
    result=subprocess.run([str(a)for a in argv],env=env,cwd=out,capture_output=True,text=True)
    files=[]
    for suffix,value in (("stdout",result.stdout),("stderr",result.stderr)):
        p=out/(name+"."+suffix);p.write_text(value);p.chmod(0o444);files.append(rec(p))
    need(result.returncode==0,"CPU software suite failed: "+name)
    if pytest_xml:
        p=out/(name+".xml");root=ET.parse(p).getroot();suites=list(root.iter("testsuite"))
        need(len(suites)==1,"Unique actual pytest suite accounting required")
        s=suites[0];counts={k:int(s.attrib.get(k,"0"))for k in ("tests","failures","errors","skipped")}
        need(counts["tests"]>0 and not any(counts[k]for k in ("failures","errors","skipped")),"Actual pytest suite failures/errors/skips")
        p.chmod(0o444);extra=dict(junit=rec(p),**counts)
    else:
        matches=re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",result.stdout+"\n"+result.stderr)
        need(len(matches)==1,"Actual unittest count missing");extra=dict(tests=int(matches[0]),failures=0,errors=0,skipped=0)
    need(expected is None or extra["tests"]==expected,"Software suite count differs: "+name)
    return dict(suite=name,argv=[str(a)for a in argv],returncode=result.returncode,stdout=files[0],stderr=files[1],**extra)
DEPENDENCY_RELATIVE="scripts/register_runtime_locks.py"
DEPENDENCY_ROLE="UNCHANGED_GENERIC_RUNTIME_REGISTRATION_TEST_IMPORT_DEPENDENCY"
def freeze_source_dependencies(source_root,out):
    source_root=Path(source_root);out=Path(out)
    need(source_root==R/"source" and source_root.resolve()==source_root and not source_root.is_symlink(),"Only exact current source regression dependency root allowed")
    original=source_root/DEPENDENCY_RELATIVE
    need(original.is_file()and not original.is_symlink()and original.resolve()==original,"Exact named regression dependency absent or symlink")
    before=rec(original)
    target=out/DEPENDENCY_RELATIVE;target.parent.mkdir(exist_ok=False)
    shutil.copyfile(original,target);target.chmod(0o444)
    frozen=rec(target)
    need(before["bytes"]==frozen["bytes"]and before["sha256"]==frozen["sha256"],"Regression dependency bytecopy differs")
    target.parent.chmod(0o555)
    return [dict(relative_path=DEPENDENCY_RELATIVE,role=DEPENDENCY_ROLE,original=before,frozen=frozen)]
def verify_source_dependencies(rows,source_root,out):
    source_root=Path(source_root);out=Path(out)
    need(source_root==R/"source"and source_root.resolve()==source_root and not source_root.is_symlink(),"Exact original regression dependency root changed")
    need(isinstance(rows,list)and len(rows)==1,"Exactly one named regression source dependency required")
    row=rows[0]
    need(isinstance(row,dict)and row.get("relative_path")==DEPENDENCY_RELATIVE and row.get("role")==DEPENDENCY_ROLE,"Unknown regression source dependency")
    need(row.get("original",{}).get("path")==str(source_root/DEPENDENCY_RELATIVE)and row.get("frozen",{}).get("path")==str(out/DEPENDENCY_RELATIVE),"Regression dependency exact sibling path differs")
    verify(row["original"],False);verify(row["frozen"])
    need(row["original"]["bytes"]==row["frozen"]["bytes"]and row["original"]["sha256"]==row["frozen"]["sha256"],"Regression dependency original/frozen bytes differ")
    need({p.name for p in (out/"scripts").iterdir()}=={"register_runtime_locks.py"}and not((out/"scripts").stat().st_mode&0o222),"Exact readonly named scripts universe required")
    return True
def failed_predecessor(q):
    receipt=q["failed_predecessor_incomplete"];prior=read(receipt)
    need(prior.get("schema")=="generic-design-input-empty-pool-incomplete.v1"and prior.get("status")=="GENERIC_DESIGN_DERIVED_PIPELINE_NOT_QUALIFIED"and prior.get("failed_stage")=="actual_50_owned_generic7_and_physical_suites"and prior.get("allocation",{}).get("job_id")=="13303"and prior.get("model_inference_performed")is False and prior.get("default_mutated")is False and prior.get("formal_benchmark_mutated")is False,"Exact failed V1 qualification history required")
    numeric=terminal("13303","FAILED","test9_generic_design_guard_v1")
    need(numeric["exit_code"]=="1:0","Original13303 must remain actual FAILED1:0")
    return dict(schema="generic-design-qualification-failed-v1-history.v1",status="ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED",incomplete=receipt,terminal_numeric_accounting=numeric,repair_identity_is_distinct=True,old_acceptance_used=False)
def qualify(request_path,out):
    allocation=cpu();out=Path(out)
    need(out.is_absolute()and out.is_relative_to(R/"steps/24_benchmark_delivery/runs")and out.resolve()==out and not out.exists(),"Fresh root-owned CPU output required")
    out.mkdir();phase="owned_source_freeze"
    try:
        request_path=Path(request_path);need(request_path.is_absolute()and request_path.is_relative_to(R)and request_path.resolve()==request_path and request_path.is_file()and not request_path.is_symlink()and not(request_path.stat().st_mode&0o222),"Readonly exact root request required")
        q=json.loads(request_path.read_text());request=rec(request_path)
        need(q.get("schema")=="generic-design-input-empty-pool-request.v2"and q.get("root_owned")is True and q.get("default_write_allowed")is False and q.get("scientific_settings_change_allowed")is False,"Distinct narrow no-default-write request required")
        own=Path(__file__).resolve().parent;need(not(own.stat().st_mode&0o222),"Reviewed package must be readonly")
        need({p.name for p in own.iterdir()}==set(NAMES),"Exact whole five-file reviewed source package required")
        package=out/"package";package.mkdir();source_files=[]
        for name in NAMES:
            p=own/name;need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Whole readonly owned qualification package required")
            target=package/name;shutil.copyfile(p,target);target.chmod(0o444)
            need(rec(p)["sha256"]==rec(target)["sha256"],"Owned source bytecopy differs");source_files.append(rec(target))
        immutable_tree(package)
        for r in source_files:
            if Path(r["path"]).suffix==".py":compile(Path(r["path"]).read_bytes(),r["path"],"exec")
        shell=subprocess.run(["bash","-n",str(package/"generic_design_cpu.sbatch")],capture_output=True,text=True)
        need(shell.returncode==0,"Owned launcher syntax failed")
        dump(out/"owned_syntax.json",dict(compiled_owned_python=True,bash_returncode=shell.returncode,stdout=shell.stdout,stderr=shell.stderr,source_files=source_files))
        phase="preserve_actual_failed13303_v1"
        predecessor=failed_predecessor(q)
        phase="actual_PhysicalV3_parent_qualification"
        pre=read(q["parent_physical_preflight"]);snapshot=read(q["parent_source_manifest"])
        need(pre.get("source_manifest")==q["parent_source_manifest"],"Physical preflight/source receipt fork")
        contracts=read(pre["software_contracts"]);inputs=read(pre["runtime_override_inputs"])
        parent_root=Path(q["parent_source_manifest"]["path"]).parent
        records=snapshot.get("files",[]);need(records and len({r["path"]for r in records})==len(records),"Exact unique physical source universe required")
        expected={r["path"]for r in records}|{q["parent_source_manifest"]["path"]}
        actual={str(p)for p in parent_root.rglob("*")if p.is_file()}
        need(actual==expected,"Parent physical frozen file universe differs")
        for r in records:verify(r)
        for r in snapshot.get("external_dependencies",[]):verify(r,False)
        selector_helper=parent_root/"patch_common_runtime_selector.py"
        need(str(selector_helper)in expected,"Accepted physical qualification helper absent")
        helper=module("accepted_physical_selector_guard",selector_helper)
        helper.qualification_contract(pre,snapshot,contracts,inputs)
        parent_terminal=terminal(pre["slurm_job_id"],"COMPLETED","test9_native_physical_preflight_v3")
        for row in contracts["suites"]:
            for field in ("stdout","stderr"):verify(row[field])
        parent_source=parent_root/"source";base_common=verify(snapshot["staged_runtime_selector"]["original_common"])
        parent_pipeline=next(r for r in records if r["path"]==str(parent_source/"src/ppiblocker/pipeline.py"))
        need(tree_sha(parent_source)==snapshot["patched_python_source_sha256"]and tree_sha(parent_source,base_common)==snapshot["default_python_source_sha256_without_staged_runtime_selector"],"Actual accepted staged/default parent tree identity differs")
        for r in pre["default_runtime_locks_unchanged"].values():verify(r,False)
        default_before=tree_sha(R/"source")
        need(default_before==snapshot["base_python_source_sha256"],"Live default C3 already changed")
        phase="derive_pipeline_only_and_preserve_both_common_identities"
        derived=out/"derived_source";default=out/"default_candidate_source"
        for target in (derived,default):
            shutil.copytree(parent_source/"src",target/"src",ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        sys.path.insert(0,str(package));patcher=module("owned_generic_design_patch",package/"patch_generic_design.py")
        new=patcher.patch(verify(parent_pipeline).read_text())
        for target in (derived,default):
            pipeline=target/"src/ppiblocker/pipeline.py";pipeline.chmod(0o644);pipeline.write_text(new)
        default_common=default/"src/ppiblocker/common.py";default_common.chmod(0o644);shutil.copyfile(base_common,default_common)
        need(rec(derived/"src/ppiblocker/common.py")["sha256"]==snapshot["staged_runtime_selector"]["staged_common"]["sha256"],"Staged common changed by generic patch")
        need(rec(default_common)["sha256"]==rec(base_common)["sha256"],"Default candidate common is not original")
        immutable_tree(derived);immutable_tree(default)
        tests=out/"generic_tests";tests.mkdir();generic_records=[]
        for name in GENERIC:
            original=R/"source/tests"/name
            need(original.is_file()and not original.is_symlink()and original.resolve()==original,"Exact original generic regression file required")
            r=rec(original);target=tests/name;shutil.copyfile(original,target);target.chmod(0o444)
            need(rec(target)["sha256"]==r["sha256"],"Generic regression bytecopy mismatch")
            generic_records.append(dict(original=r,frozen=rec(target)))
        immutable_tree(tests)
        source_dependencies=freeze_source_dependencies(R/"source",out)
        verify_source_dependencies(source_dependencies,R/"source",out)
        for dependency in source_dependencies:compile(verify(dependency["frozen"]).read_bytes(),dependency["frozen"]["path"],"exec")
        for tree in (derived,default):
            for p in sorted((tree/"src").rglob("*.py")):compile(p.read_bytes(),str(p),"exec")
        for r in generic_records:compile(Path(r["frozen"]["path"]).read_bytes(),r["frozen"]["path"],"exec")
        derived_pipeline=rec(default/"src/ppiblocker/pipeline.py")
        manifest=dump(out/"derived_source_manifest.json",dict(schema="generic-design-derived-source.v2",parent_physical_preflight=q["parent_physical_preflight"],parent_source_manifest=q["parent_source_manifest"],original_physical_pipeline=parent_pipeline,derived_pipeline=derived_pipeline,source_files=source_files,generic_regression_sources=generic_records,source_dependencies=source_dependencies,failed_predecessor=predecessor,staged_source_files=[rec(p)for p in sorted((derived/"src").rglob("*"))if p.is_file()],default_candidate_source_files=[rec(p)for p in sorted((default/"src").rglob("*"))if p.is_file()],staged_python_source_sha256=tree_sha(derived),default_python_source_sha256_without_staged_runtime_selector=tree_sha(default),staged_common=rec(derived/"src/ppiblocker/common.py"),default_common_original=rec(base_common),default_common_candidate=rec(default_common),physical_helper_unchanged=rec(parent_source/"src/ppiblocker/pose_physical_gate.py"),edit_scope=["pipeline.validate_config design count and single temperature validation","pipeline.design nonempty output guard","pipeline.evaluate nonempty imported pool guard"],formal28_112_empty_null_semantics_changed=False,experimental_binding=False,experimental_blockade=False))
        phase="actual_50_owned_generic7_and_physical_suites"
        env={**os.environ,"PYTEST_DISABLE_PLUGIN_AUTOLOAD":"1","GENERIC_PATCH_PARENT_PIPELINE":parent_pipeline["path"],"PYTHONPATH":os.pathsep.join([str(default/"src"),str(tests),str(package),str(parent_root)])}
        test_rows=[]
        for name,paths,count,selection in (("owned_design_validation",[package/"test_generic_design.py"],50,"not regression_dependency"),("owned_source_dependencies",[package/"test_generic_design.py"],12,"regression_dependency"),("generic_seven",[tests/n for n in GENERIC],None,None)):
            argv=[sys.executable,"-B","-m","pytest","-q","-p","no:cacheprovider","--basetemp="+str(out/("tmp_"+name)),"--junitxml="+str(out/(name+".xml"))]
            if selection is not None:argv.extend(["-k",selection])
            test_rows.append(command([*argv,*paths],env,out,name,count,True))
        for suite,file,count in PHYSICAL:
            child_env={**env,"PYTHONPATH":os.pathsep.join([str(derived/"src"),str(parent_root)])}
            test_rows.append(command([sys.executable,"-B",parent_root/file],child_env,out,"staged_selector"if suite=="staged_selector"else"staged_"+suite,count))
        child_env={**env,"PYTHONPATH":os.pathsep.join([str(default/"src"),str(parent_root)])}
        test_rows.append(command([sys.executable,"-B",parent_root/"test_pose_physical_gate.py"],child_env,out,"default_physical",25))
        qualification=module("derived_pipeline_module_identity_probe",package/"patch_generic_design.py")
        need(qualification.patch(verify(parent_pipeline).read_text())==verify(derived_pipeline).read_text(),"Derived pipeline source relation changed during tests")
        for r in source_files:verify(r)
        for r in (q["parent_physical_preflight"],q["parent_source_manifest"],pre["software_contracts"],pre["runtime_override_inputs"]):verify(r)
        for r in snapshot.get("external_dependencies",[]):verify(r,False)
        for r in records:verify(r)
        for row in generic_records:verify(row["original"],False);verify(row["frozen"])
        verify_source_dependencies(source_dependencies,R/"source",out)
        verify(q["failed_predecessor_incomplete"])
        need(failed_predecessor(q)==predecessor,"Original failed predecessor accounting changed during qualification")
        for r in pre["default_runtime_locks_unchanged"].values():verify(r,False)
        need(tree_sha(R/"source")==default_before,"Default source changed during generic qualification")
        m=read(manifest)
        need(tree_sha(derived)==m["staged_python_source_sha256"]and tree_sha(default)==m["default_python_source_sha256_without_staged_runtime_selector"],"Derived tested trees changed")
        saved_contracts=dump(out/"contracts.json",dict(status="PASS",suites=test_rows,owned_tests=50,owned_dependency_tests=12,source_dependency_count=1,source_dependencies=source_dependencies,compiled_named_regression_dependencies=True,source_dependencies_readback_before_and_after_tests=True,generic_regression_file_count=7,staged_physical_suite_tests=57,default_physical_suite_tests=25,models_called=False,compiled_owned_and_derived=True,bash_syntax=True,source_files=source_files,derived_source_manifest=manifest))
        accepted=dict(schema="generic-design-input-empty-pool-qualification.v2",status=STATUS,request=request,parent_physical_preflight=q["parent_physical_preflight"],parent_source_manifest=q["parent_source_manifest"],parent_terminal_accounting=parent_terminal,original_physical_pipeline=parent_pipeline,derived_pipeline=derived_pipeline,derived_source_manifest=manifest,source_files=source_files,contracts=saved_contracts,source_dependencies=source_dependencies,failed_predecessor=predecessor,allocation=allocation,slurm_job_id=allocation["job_id"],staged_python_source_sha256=m["staged_python_source_sha256"],default_python_source_sha256_without_staged_runtime_selector=m["default_python_source_sha256_without_staged_runtime_selector"],physical_helper_unchanged=m["physical_helper_unchanged"],default_common_original=m["default_common_original"],staged_common_unchanged=m["staged_common"],default_source_unchanged=True,default_runtime_locks_unchanged=pre["default_runtime_locks_unchanged"],model_inference_performed=False,formal_benchmark_mutated=False,scientific_scope="COMPUTATIONAL_ONLY",experimental_binding=False,experimental_blockade=False,source_staged=False)
        r=dump(out/"acceptance.json",accepted)
        print(json.dumps(dict(status=STATUS,acceptance=r,derived_pipeline=derived_pipeline,default_python_source_sha256_without_staged_runtime_selector=accepted["default_python_source_sha256_without_staged_runtime_selector"]),sort_keys=True),flush=True)
        return accepted
    except Exception as error:
        r=dump(out/"typed_incomplete.json",dict(schema="generic-design-input-empty-pool-incomplete.v2",status="GENERIC_DESIGN_DERIVED_PIPELINE_NOT_QUALIFIED",failed_stage=phase,error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc(),allocation=allocation,default_mutated=False,formal_benchmark_mutated=False,model_inference_performed=False))
        print(json.dumps(r),flush=True);raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--request",required=True);p.add_argument("--out",required=True);a=p.parse_args();qualify(a.request,a.out)

