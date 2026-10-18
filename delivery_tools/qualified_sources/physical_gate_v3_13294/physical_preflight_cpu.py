"""CPU-only freeze, independent atom audit and declared raw-prediction requalification."""
from __future__ import annotations
import argparse, compileall, hashlib, importlib, importlib.util, json, os, re, shutil, subprocess, sys, time, traceback
from pathlib import Path
from unittest.mock import patch

ROOT=Path("/lustre/users/u21111210118/projects/test9")
OLD=ROOT/"steps/02_predict/runs/20261002T121305Z_be69fbefc530/manifest.json"
OLD_SHA="a1096d4e0a31c174f67ca86fb403a44a71adc6e5d81678f1e612907b11d6fc40"
BASE_SHA="c3d528bb6801a7a571cdd20bfd90652e397a8540a136e1f0510ef0ccc5488dde"
PREP=ROOT/"steps/01_pose/runs/20261002T121202Z_7f2aa04cc5b0/manifest.json"
PREP_SHA="2c8b2b9b6efe6ac2762c8bda1360585a0cc9ef65a1047b808e3e617762677bb4"
SCHEMA="REFERENCE_FREE_E2E_PHYSICAL_GATE_PREFLIGHT_AND_CPU_REQUALIFICATION_V3"
AA={"ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP","TYR","VAL","MSE"}

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def rec(p):return dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))
def put(p,x):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+"\n")
def tree_sha(source):
    files=sorted((source/"src").rglob("*.py"))
    return hashlib.sha256("".join(str(p.relative_to(source))+sha(p) for p in files).encode()).hexdigest()

def independent_atoms(path):
    groups={}
    lines=Path(path).read_text().splitlines()
    if sum(line[:6].strip()=="MODEL" for line in lines)>1 or sum(line[:6].strip()=="ENDMDL" for line in lines)>1:
        raise RuntimeError("Multiple coordinate models are unsupported by this fixed independent audit")
    has_model=any(line[:6].strip()=="MODEL" for line in lines)
    inside=not has_model;seen=set()
    for line in lines:
        if line[:6].strip()=="MODEL":inside=True;continue
        if line[:6].strip()=="ENDMDL":inside=False;continue
        if line[:6].strip() not in {"ATOM","HETATM"}:continue
        if not inside:raise RuntimeError("Atom coordinates outside declared single model")
        if line[16].strip():raise RuntimeError("Alternate atom locations require explicit audited selection; unsupported here")
        element=line[76:78].strip()
        if not element:raise RuntimeError("Missing atom element, cannot establish heavy-atom definition")
        resname=line[17:20].strip()
        key=(line[21],line[22:26].strip(),line[26].strip(),resname)
        duplicate_key=(key[0],key[1],key[2],line[12:16].strip())
        if resname in AA and element not in {"H","D"}:
            if duplicate_key in seen:raise RuntimeError("Duplicate protein heavy atom identifier")
            seen.add(duplicate_key)
        atom=dict(chain=key[0],author_residue=key[1],insertion_code=key[2],resname=resname,
                  atom=line[12:16].strip(),element=element,altloc=line[16].strip(),
                  xyz=[float(line[30:38]),float(line[38:46]),float(line[46:54])])
        groups.setdefault(key,[]).append(atom)
    chains={}
    extra=[]
    for key,atoms in groups.items():
        if key[3] in AA and any(a["atom"]=="CA" for a in atoms):
            for a in atoms:
                if a["element"] not in {"H","D"}:chains.setdefault(a["chain"],[]).append(a)
        elif key[3] not in {"HOH","WAT"}:extra.append(key)
    if set(chains)!={"A","B"} or extra:raise RuntimeError("Independent read expected A/B protein only")
    import numpy as np
    aa,bb=chains["A"],chains["B"]
    xa=np.array([a["xyz"] for a in aa]);xb=np.array([a["xyz"] for a in bb])
    distances=np.linalg.norm(xa[:,None,:]-xb[None,:,:],axis=-1)
    idx=np.unravel_index(int(distances.argmin()),distances.shape)
    return dict(minimum_distance_angstrom=float(distances[idx]),
                closest_atoms=[aa[int(idx[0])],bb[int(idx[1])]],
                target_heavy_atom_count=len(aa),partner_heavy_atom_count=len(bb),
                atom_pair_count_below_1_5_angstrom=int((distances<1.5).sum()),
                hydrogen_deuterium_excluded=True,interchain_covalent_bond_modelled=False,
                diagnostic_count_is_not_the_gate=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--request",required=True);args=parser.parse_args()
    job=os.environ.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Actual Slurm CPU allocation required")
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="" or os.environ.get("SLURM_JOB_GPUS") or os.environ.get("SLURM_GPUS_ON_NODE") not in {None,"","0"}:
        raise RuntimeError("Pure CPU allocation with no GPU GRES required")
    pending=Path(__file__).resolve().parent
    sys.path.insert(0,str(pending));from patch_common_runtime_selector import current_cpu_guard, accounting, patch as patch_selector
    allocation=current_cpu_guard(job)
    run=ROOT/"steps/25_reference_free_e2e"/"runs"/("physical_preflight_"+job)
    frozen=ROOT/"steps/25_reference_free_e2e"/"frozen"/("physical_gate_v3_"+job)
    run.mkdir(parents=True,exist_ok=False);frozen.mkdir(parents=True,exist_ok=False)
    status=dict(schema=SCHEMA,status="RUNNING",slurm_job_id=job,GPU_requested=False,native_inference_performed=False,
                formal_benchmark_mutated=False,started_epoch=time.time(),stage="snapshot")
    put(run/"status.json",status)
    try:
        request=Path(args.request);need=lambda v,m: (_ for _ in ()).throw(RuntimeError(m))if not v else None
        need(request.is_absolute()and request.is_relative_to(ROOT)and request.resolve()==request and request.is_file()and not(request.stat().st_mode&0o222),"Readonly root physicalV3 request required")
        q=json.loads(request.read_text())
        need(q.get("schema")=="physical-materialized-runtime-request.v3"and q.get("root_owned")is True and q.get("default_write_allowed")is False,"Distinct root-owned no-default-write physicalV3 request required")
        def verify(r,readonly=True):
            path=Path(r["path"])
            need(path.is_absolute()and path.is_relative_to(ROOT)and path.resolve()==path and path.is_file()and rec(path)==r,"Exact current artifact required")
            need(not readonly or not(path.stat().st_mode&0o222),"Accepted input must be readonly");return path
        generic_path=verify(q["generic_repair_acceptance"]);generic=json.loads(generic_path.read_text())
        need(generic.get("schema")=="generic-report-materialized-runtime-repair-acceptance.v3"and generic.get("status")=="GENERIC_REPORT_CONTENT_AND_MATERIALIZED_RUNTIME_V3_CPU_REPAIR_ACCEPTED_FAILED13263_13286_13287_PRESERVED"and generic.get("original13263_failure_preserved")is True and generic.get("failed13286_13287_preserved")is True,"Actual new full generic/report repair required")
        contracts=json.loads(verify(generic["contracts"]).read_text())
        need(contracts.get("status")=="PASS"and contracts.get("tests")==105 and contracts.get("failures")==0 and contracts.get("errors")==0 and contracts.get("owned_python_compile_PASS")is True and contracts.get("bash_syntax_PASS")is True,"Actual105 generic repair/source contracts required")
        need(contracts.get("source_files")==generic.get("source_files"),"Generic tested source set differs from accepted source")
        for r in generic["source_files"]:verify(r)
        verify(contracts["log"])
        override_path=verify(q["runtime_override_acceptance"]);override=json.loads(override_path.read_text())
        need(generic.get("reviewed_runtime_override_acceptance")==q["runtime_override_acceptance"],"Generic and runtime override receipt differ")
        need(override.get("schema")=="reviewed-runtime-override-acceptance.v1"and override.get("status")=="REVIEWED_FULL_MATERIALIZED_RFD_RUNTIME_OVERRIDE_CPU_ACCEPTED_DEFAULT_UNCHANGED"and override.get("default_runtime_locks_unchanged")is True and override.get("cache_excluded_from_new_lock")is False,"Actual reviewed full-cache override required")
        need(set(override["runtime_locks"])=={"core","rfd","boltz"}and set(override["original_default_locks"])=={"core","rfd","boltz"},"Exact three runtime locks required")
        need(generic.get("failed13286_13287_history")==override.get("failed13286_13287_history"),"One exact failed13286/13287 history proof required")
        failed_history_receipt=generic["failed13286_13287_history"];failed_history=json.loads(verify(failed_history_receipt).read_text())
        need(failed_history.get("status")=="REAL_FAILED13286_AND_CAPTUREONLY_FAILED13287_PRESERVED_NOT_ACCEPTED"and failed_history.get("original13263_also_failed")is True and len(failed_history.get("jobs",[]))==2 and {x.get("job_id")for x in failed_history["jobs"]}=={"13286","13287"},"Real failed predecessors cannot be missing or promoted")
        for x in failed_history["jobs"]:
            t=x.get("terminal",{})
            need(t.get("job_id")==x["job_id"]and t.get("state")=="FAILED"and t.get("exit_code")=="1:0"and type(t.get("allocated_CPUs"))is int and t["allocated_CPUs"]>=1 and t.get("allocated_GPUs")==0 and t.get("user")==t.get("account")=="u21111210118"and t.get("partition")=="organ"and x.get("acceptance_claimed")is False,"Exact failed predecessor numeric CPU/GPU/owner content required")

        need(q["materialization_acceptance"]==generic["materialization_acceptance"]==override["materialization_acceptance"],"One actual13281 materialization identity required")
        materialization=json.loads(verify(q["materialization_acceptance"]).read_text())
        helper=next(r for r in generic["source_files"]if Path(r["path"]).name=="science13263_content_barrier.py")
        spec=importlib.util.spec_from_file_location("accepted_generic_repair",verify(helper));gm=importlib.util.module_from_spec(spec);spec.loader.exec_module(gm)
        gm.materialization_contract(materialization)
        def history_references(v):
            if isinstance(v,dict):
                if {"path","bytes","sha256"}<=v.keys():yield v
                else:
                    for item in v.values():yield from history_references(item)
            elif isinstance(v,list):
                for item in v:yield from history_references(item)
        for rr in history_references(failed_history):gm.verify_receipt(rr,False)

        need(generic["slurm_job_id"]==override["slurm_job_id"],"Generic/override CPU job differs")
        terminal=gm.terminal_repair(run,"13281")
        # Generic is a distinct actual COMPLETED0 CPU job, not an original13263 upgrade.
        raw=subprocess.check_output(["sacct","-X","-j",str(generic["slurm_job_id"]),"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
        row=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==str(generic["slurm_job_id"])]
        need(len(row)==1 and row[0][1:3]==["COMPLETED","0:0"]and row[0][7]=="test9_generic_materialized_repair_v3","Actual terminal generic repair required")
        from patch_common_runtime_selector import accounting as parse_cpu
        parsed=parse_cpu(raw,generic["slurm_job_id"],expected_state="COMPLETED")
        generic_terminal={"raw":raw,"terminal_row":row[0],"allocated_CPUs":parsed["allocated_CPUs"],"allocated_GPUs":parsed["allocated_GPUs"]}
        old_cancel_raw=subprocess.check_output(["sacct","-X","-j","13267","--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
        old_cancel=accounting(old_cancel_raw,"13267",True);verify(q["original13267_cancellation_history"])
        override_directory=Path(override["runtime_override_directory"])
        need(override_directory==ROOT/"steps/24_benchmark_delivery/runs"/("generic_runtime_repair_"+str(generic["slurm_job_id"]))/"frozen/runtime_override"and override_directory.resolve()==override_directory and override_directory.is_dir()and not(override_directory.stat().st_mode&0o222),"Exact immutable accepted generic-job override directory required")
        need({p.name for p in override_directory.iterdir()}=={"runtime-lock-core.json","runtime-lock-rfd.json","runtime-lock-boltz.json"},"Exactly three accepted override files required")
        for c,r in override["runtime_locks"].items():
            need(r["path"]==str(override_directory/("runtime-lock-"+c+".json")),"Selector directory and accepted lock descriptor differ");verify(r)
        for c,r in override["original_default_locks"].items():
            need(r["path"]==str(ROOT/"source/environment"/("runtime-lock-"+c+".json")),"Wrong old default runtime path");verify(r,False)
        arrays=gm.reverify_materialization_arrays(materialization)
        runtime_inputs=dict(failed13286_13287_history=failed_history_receipt,request=rec(request),generic_repair_acceptance=q["generic_repair_acceptance"],runtime_override_acceptance=q["runtime_override_acceptance"],materialization_acceptance=q["materialization_acceptance"],accepted_generic_helper=helper,generic_terminal_accounting=generic_terminal,materialization_terminal=terminal,old13267_cancellation=old_cancel,old13267_cancellation_raw=old_cancel_raw,old13267_cancellation_history=q["original13267_cancellation_history"],actual_five_array_repeat=arrays)
        put(run/"runtime_override_inputs.json",runtime_inputs)
        policy={
            "schema":"reference_free_e2e_predeclared_scope.v1",
            "declared_epoch":time.time(),"frozen_before_actual_requalification":True,"old_prediction_manifest":{"path":str(OLD),"sha256":OLD_SHA},
            "original_prepare_manifest":{"path":str(PREP),"sha256":PREP_SHA},
            "all_three_original_raw_models_required":True,"old_native_model_zero_is_never_manually_replaced":True,
            "physical_policy":"Fixed interchain protein heavy-atom minimum strictly <1.5 Angstrom rejects before eligibility",
            "ensemble_rule":"Original max compatible neighborhood / first ties; >=60% of all requested models and >=2",
            "new_native_inference":False,"new_seed_search":False,"new_coordinates_or_reference_template":False,
            "design":dict(backbones=1,sequences_per_backbone=1,binder_length=65,seed=42,temperature=.1),
            "refold":dict(samples=3,seed=1042,recycles=3,allow_external_msa=False,allow_single_sequence=True),
            "comparison_scope":"Separate engineering E2E complement; not formal 28-task benchmark or holdout",
            "existing_model_stage_CPU_bookkeeping":"May run inside allocated true model-stage job; independent audit remains CPU only",
            "GPU_for_metadata_or_scoring_kernels":False,"reviewed_runtime_override_acceptance":q["runtime_override_acceptance"],"materialization_acceptance":q["materialization_acceptance"],"default_source_and_three_old_locks_unchanged":True,
            "engineering_resource_policy":dict(scheduler_CPUs=3,GPU_count=1,requested_memory_GiB=64,OMP_NUM_THREADS=4,GPU_name="NVIDIA A100-PCIE-40GB",GPU_memory_MiB=40960),
        }
        put(frozen/"predeclared_scope.json",policy)
        for p in sorted(pending.iterdir()):
            if p.is_file():
                need(not(p.stat().st_mode&0o222)and not p.is_symlink(),"Reviewed physicalV3 files must be readonly")
                shutil.copyfile(p,frozen/p.name)
        source=ROOT/"source"
        if tree_sha(source)!=BASE_SHA:raise RuntimeError("Required current generic source differs from exact original c3d528 source tree")
        shutil.copytree(source/"src",frozen/"base_source"/"src",ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        shutil.copytree(source/"src",frozen/"source"/"src",ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        sys.path.insert(0,str(frozen));from patch_pipeline import patch as patch_text
        p=frozen/"source/src/ppiblocker/pipeline.py";p.chmod(0o644);p.write_text(patch_text(p.read_text()))
        shutil.copy2(frozen/"pose_physical_gate.py",frozen/"source/src/ppiblocker/pose_physical_gate.py")
        common_path=frozen/"source/src/ppiblocker/common.py";original_common=rec(frozen/"base_source/src/ppiblocker/common.py")
        common_path.chmod(0o644);patched_common,selector=patch_selector(common_path.read_text(),override["runtime_override_directory"]);common_path.write_text(patched_common)
        selector.update(original_common=original_common,staged_common=rec(common_path),default_common_unchanged=rec(ROOT/"source/src/ppiblocker/common.py"))
        def default_tree_sha():
            files=sorted((frozen/"source/src").rglob("*.py"))
            payload=[]
            for path in files:
                digest=sha(frozen/"base_source/src/ppiblocker/common.py")if path==common_path else sha(path)
                payload.append(str(path.relative_to(frozen/"source"))+digest)
            return hashlib.sha256("".join(payload).encode()).hexdigest()
        default_python_sha=default_tree_sha()
        default_promotions=[dict(repository_relative="src/ppiblocker/"+name,source=rec(frozen/"source/src/ppiblocker"/name))for name in ("pipeline.py","pose_physical_gate.py")]
        launcher=frozen/"e2e_gpu_stage.sbatch"
        launcher_text=launcher.read_text()
        if launcher_text.count("__FROZEN_MODEL_STAGE_ENTRY__")!=1:raise RuntimeError("GPU launcher must have one frozen absolute entry marker")
        launcher.write_text(launcher_text.replace("__FROZEN_MODEL_STAGE_ENTRY__",str(frozen/"e2e_model_stage.py")))
        final_launcher=frozen/"e2e_final_audit_cpu.sbatch"
        final_text=final_launcher.read_text()
        if final_text.count("__FROZEN_FINAL_CPU_ENTRY__")!=1:raise RuntimeError("Final CPU launcher must have one frozen absolute entry marker")
        final_launcher.write_text(final_text.replace("__FROZEN_FINAL_CPU_ENTRY__",str(frozen/"e2e_final_audit_cpu.py")))
        design_launcher=frozen/"e2e_design_audit_cpu.sbatch"
        design_text=design_launcher.read_text()
        if design_text.count("__FROZEN_DESIGN_CPU_ENTRY__")!=1:raise RuntimeError("Design CPU launcher must have one frozen absolute entry marker")
        design_launcher.write_text(design_text.replace("__FROZEN_DESIGN_CPU_ENTRY__",str(frozen/"e2e_design_audit_cpu.py")))
        sys.path.insert(0,str(frozen));from e2e_resource_policy import BUDGET
        if rec(BUDGET["path"])!=BUDGET:raise RuntimeError("Accepted GPU ownership source changed")
        # Freeze source before any model-derived eligibility is inspected.
        records=[rec(p) for p in sorted(frozen.rglob("*")) if p.is_file()]
        put(frozen/"source_manifest.json",dict(schema="physical_gate_source_snapshot.v1",frozen_epoch=time.time(),base_python_source_sha256=BASE_SHA,
            patched_python_source_sha256=tree_sha(frozen/"source"),files=records,external_dependencies=[BUDGET,failed_history_receipt,q["generic_repair_acceptance"],q["runtime_override_acceptance"],q["materialization_acceptance"],helper,q["original13267_cancellation_history"],*override["runtime_locks"].values(),materialization["original_cache"],materialization["regenerated_cache"]],
            runtime_override_inputs=rec(run/"runtime_override_inputs.json"),failed13286_13287_history=failed_history_receipt,reviewed_runtime_override_acceptance=q["runtime_override_acceptance"],staged_runtime_selector=selector,default_python_source_sha256_without_staged_runtime_selector=default_python_sha,default_promotion_files=default_promotions,default_common_selector_is_original=True,
            exact_edit_scope=["pipeline.predict confidence+physical eligibility and provenance","pipeline.validate_design_pose actual-coordinate physical gate","new fixed physical policy module","STAGED ONLY common runtime selector to exact accepted override directory"]))
        for p in frozen.rglob("*"):
            if p.is_file():p.chmod(0o444)
        for p in sorted([p for p in frozen.rglob("*") if p.is_dir()],key=lambda p:len(p.parts),reverse=True):p.chmod(0o555)
        frozen.chmod(0o555)
        for py in sorted(frozen.rglob("*.py")):compile(py.read_text(),str(py),"exec")
        shell_parse=subprocess.run(["bash","-n",str(frozen/"e2e_gpu_stage.sbatch")],capture_output=True,text=True)
        if shell_parse.returncode:raise RuntimeError("Frozen GPU launcher shell syntax failed")
        final_shell_parse=subprocess.run(["bash","-n",str(frozen/"e2e_final_audit_cpu.sbatch")],capture_output=True,text=True)
        if final_shell_parse.returncode:raise RuntimeError("Frozen final CPU launcher shell syntax failed")
        if subprocess.run(["bash","-n",str(frozen/"e2e_design_audit_cpu.sbatch")],capture_output=True,text=True).returncode:raise RuntimeError("Frozen design CPU launcher syntax failed")
        sys.path.insert(0,str(frozen/"source/src"))
        from ppiblocker import common, pipeline
        need(pipeline.runtime_provenance is common.runtime_provenance,"Pipeline must bind actual staged common runtime selector before import")
        status["stage"]="contracts";put(run/"status.json",status)
        result=subprocess.run([sys.executable,"-B",str(frozen/"test_pose_physical_gate.py")],
            env={**os.environ,"PYTHONPATH":str(frozen/"source/src")},capture_output=True,text=True)
        (run/"contracts.stdout.txt").write_text(result.stdout);(run/"contracts.stderr.txt").write_text(result.stderr)
        if result.returncode:raise RuntimeError("Frozen physical gate software contracts failed")
        result_resource=subprocess.run([sys.executable,"-B",str(frozen/"test_e2e_resource_policy.py")],capture_output=True,text=True)
        (run/"resource_contracts.stdout.txt").write_text(result_resource.stdout);(run/"resource_contracts.stderr.txt").write_text(result_resource.stderr)
        if result_resource.returncode:raise RuntimeError("Frozen engineering resource contracts failed")
        result_design=subprocess.run([sys.executable,"-B",str(frozen/"test_e2e_design_contracts.py")],capture_output=True,text=True)
        (run/"design_contracts.stdout.txt").write_text(result_design.stdout);(run/"design_contracts.stderr.txt").write_text(result_design.stderr)
        if result_design.returncode:raise RuntimeError("Frozen independent CPU design gate contracts failed")
        selector_test=subprocess.run([sys.executable,"-B",str(frozen/"test_common_runtime_selector.py")],capture_output=True,text=True)
        (run/"selector_contracts.stdout.txt").write_text(selector_test.stdout);(run/"selector_contracts.stderr.txt").write_text(selector_test.stderr)
        need(selector_test.returncode==0,"Frozen staged selector contracts failed")
        contract_rows=[]
        for name,proc,prefix in (("physical",result,"contracts"),("resource",result_resource,"resource_contracts"),("design",result_design,"design_contracts"),("staged_selector",selector_test,"selector_contracts")):
            counts=re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",proc.stdout+"\n"+proc.stderr)
            need(proc.returncode==0 and len(counts)==1 and int(counts[0])>0,"Actual software suite count/exit evidence required")
            contract_rows.append(dict(suite=name,tests=int(counts[0]),returncode=proc.returncode,stdout=rec(run/(prefix+".stdout.txt")),stderr=rec(run/(prefix+".stderr.txt"))))
        need(sum(x["tests"]for x in contract_rows)==57 and contract_rows[-1]["tests"]==15,"Actual frozen physical42 plus selector15 contracts required")
        software_contracts=run/"software_contracts.json";put(software_contracts,dict(status="PASS",tests=57,suites=contract_rows,source_manifest=rec(frozen/"source_manifest.json"),compiled_source=True,bash_syntax=True))
        status["stage"]="old_current_source_raw_runtime_closure";put(run/"status.json",status)
        if sha(OLD)!=OLD_SHA or sha(PREP)!=PREP_SHA:raise RuntimeError("Pinned original native prediction/preparation changed")
        old=common.load_run(OLD,{"POSE_ACCEPTED"});prepared=common.load_run(PREP,{"NEEDS_PREDICTION"})
        if old["source"]["python_source_sha256"]!=BASE_SHA:raise RuntimeError("Original generic source identity mismatch")
        old_runtime_references=[]
        for component,descriptors in old.get("runtime",{}).items():
            for kind in ("snapshot","lock"):
                item=descriptors[kind]
                for artifact in common.file_references(common.read_json(item["path"])):
                    common.verify_file(artifact)
                    old_runtime_references.append(dict(component=component,kind=kind,artifact=artifact))
        if not old_runtime_references:raise RuntimeError("Original inference runtime reference closure absent")
        put(run/"old_runtime_reference_closure.json",dict(status="EXACT_REQUIRED_REFERENCES_REVERIFIED_NO_WAIVERS",references=old_runtime_references))
        if len(old["inputs"])!=1 or old["inputs"][0]["path"]!=str(PREP) or old["inputs"][0]["sha256"]!=PREP_SHA:
            raise RuntimeError("Original exact preparation edge changed")
        if old["source"]["python_source_sha256"]!=tree_sha(frozen/"base_source"):raise RuntimeError("Original source not fully preserved")
        lock_rows=[]
        for component in ("core","rfd","boltz"):
            lock=Path(override["runtime_locks"][component]["path"])
            need(rec(lock)==override["runtime_locks"][component],"Accepted override lock changed")
            need(rec(ROOT/"source/environment"/("runtime-lock-"+component+".json"))==override["original_default_locks"][component],"Original default runtime lock changed")
            if not lock.is_file():raise RuntimeError("Current required runtime lock missing")
            expected=common.read_json(lock);actual=common.collect_runtime(ROOT,component)
            if expected!=actual:raise RuntimeError("Current "+component+" runtime drift; lock must not refresh automatically")
            snapshot=run/("live_runtime_"+component+".json");put(snapshot,actual)
            lock_rows.append(dict(component=component,lock=rec(lock),actual=rec(snapshot)))
        vendor_repeat=gm.historical225_recompute(common,json.loads(verify(override["original_default_locks"]["rfd"],False).read_text())["vendor_files"]["RFdiffusion"])
        put(run/"historical225_vendor_content_repeat.json",vendor_repeat)
        cfg=pipeline.validate_config(common.read_json(old["outputs"]["config"]["path"]))
        proteins=common.read_json(old["outputs"]["proteins"]["path"])
        if cfg!=common.read_json(prepared["outputs"]["config"]["path"]) or proteins!=common.read_json(prepared["outputs"]["proteins"]["path"]):
            raise RuntimeError("Prediction and preparation exact config/proteins differ")
        if cfg["prediction"]!=dict(samples=3,seed=42,allow_external_msa=False,allow_single_sequence=True,recycles=3):
            raise RuntimeError("Original fixed blind prediction settings changed")
        if cfg["design"]!=policy["design"] or cfg["refold"]!=policy["refold"]:raise RuntimeError("Fixed subsequent engineering settings changed")
        if [(p.get("uniprot"),p.get("canonical_start"),len(p["sequence"])) for p in proteins]!=[("Q00987",25,85),("P04637",17,13)]:
            raise RuntimeError("Original exact species/construct identity differs")
        models=[dict(model_index=i,**{key:old["outputs"][f"model_{i}_{key}"] for key in ("structure","confidence","pae")}) for i in range(3)]
        status["stage"]="independent_physical_audit";put(run/"status.json",status)
        rows=[]
        for model in models:
            independent=independent_atoms(model["structure"]["path"])
            a,b,pair,metrics=pipeline.model_pair(model,proteins,cfg.get("gates",{}))
            if abs(independent["minimum_distance_angstrom"]-pair["interface"]["minimum_distance"])>1e-4:
                raise RuntimeError("Independent float64 text parser and float32 Bio.PDB distance disagree")
            if (independent["minimum_distance_angstrom"]<1.5)!=(pair["interface"]["minimum_distance"]<1.5):
                raise RuntimeError("Independent gate classification disagreement")
            rows.append(dict(model=model["model_index"],structure=model["structure"],independent=independent,
                production_interface=pair["interface"],confidence=metrics,
                confidence_reasons=pipeline.confidence_reasons(metrics,cfg.get("gates",{})),
                new_physical_reasons=pipeline.physical_pose_reasons(pair["interface"])))
        audit=run/"old_all_three_physical_audit.json";put(audit,dict(models=rows,original_selected_model=0,
            original_selected_model_disposition="HISTORICAL_CONFIDENCE_ENSEMBLE_ONLY_NOT_PHYSICALLY_QUALIFIED",
            biological_interaction_denied=False,original_manifest_unchanged=rec(OLD),original_pose=old["outputs"]["pose"]))
        status["stage"]="CPU_raw_pose_requalification";put(run/"status.json",status)
        real_runtime=common.runtime_provenance
        def cpu_runtime(run_obj,root,components):
            if components!=["boltz"]:raise RuntimeError("Unexpected replay component request")
            real_runtime(run_obj,root,["core"])
            run_obj.manifest.update(evaluation_mode="existing_raw_prediction_cpu_physical_requalification",
                native_inference_performed=False,old_inference_runtime_reference=rec(OLD),
                physical_requalification_scope=rec(frozen/"predeclared_scope.json"),
                independent_old_geometry_audit=rec(audit),frozen_source_manifest=rec(frozen/"source_manifest.json"),
                inference_model_artifact_identities=models,actual_native_inference_GPU_job="11801")
            run_obj.save()
        def cpu_raw_replay(root,work,requested_proteins,settings,log):
            if requested_proteins!=proteins or settings!=cfg["prediction"]:raise RuntimeError("Replay input drift")
            Path(log).write_text("CPU reuse of three pinned GPU11801 raw models. No new prediction, seed or model selection.\n")
            return models
        with patch.object(pipeline,"runtime_provenance",side_effect=cpu_runtime),patch.object(pipeline,"boltz_predict",side_effect=cpu_raw_replay):
            qualified_manifest=pipeline.predict(ROOT,PREP)
        qualified=common.read_json(qualified_manifest)
        result_row=dict(manifest=rec(qualified_manifest),status=qualified["status"])
        if qualified["status"]=="POSE_ACCEPTED":
            common.load_run(qualified_manifest,{"POSE_ACCEPTED"})
            _,pose,_=pipeline.validate_design_pose(qualified)
            result_row.update(selected_model=pose["source"]["model"],support=pose["ensemble_support_model_indices"],design_entry_gate=pose["design_entry_physical_gate"],
                              next_step="root-owned new design from this exact manifest only")
        elif qualified["status"]=="POSE_REJECTED":
            result_row.update(next_step="terminal physical/ensemble reject; do not design from rejected pose")
        else:raise RuntimeError("Requalification is incomplete; missing models may not be promoted")
        acceptance=dict(schema=SCHEMA,status="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED",
            source_manifest=rec(frozen/"source_manifest.json"),predeclared_scope=rec(frozen/"predeclared_scope.json"),
            contracts_stdout=rec(run/"contracts.stdout.txt"),contracts_stderr=rec(run/"contracts.stderr.txt"),
            original_prediction=rec(OLD),original_preparation=rec(PREP),old_all_three_physical_audit=rec(audit),
            old_runtime_reference_closure=rec(run/"old_runtime_reference_closure.json"),contracts_count=57,software_contracts=rec(software_contracts),allocation=allocation,
            selector_contracts_stdout=rec(run/"selector_contracts.stdout.txt"),selector_contracts_stderr=rec(run/"selector_contracts.stderr.txt"),runtime_override_inputs=rec(run/"runtime_override_inputs.json"),failed13286_13287_history=failed_history_receipt,reviewed_runtime_override_acceptance=q["runtime_override_acceptance"],generic_report_repair_acceptance=q["generic_repair_acceptance"],materialization_acceptance=q["materialization_acceptance"],historical225_vendor_content_repeat=rec(run/"historical225_vendor_content_repeat.json"),default_runtime_locks_unchanged=override["original_default_locks"],staged_runtime_selector=selector,default_python_source_sha256_without_staged_runtime_selector=default_python_sha,
            design_contracts_stdout=rec(run/"design_contracts.stdout.txt"),design_contracts_stderr=rec(run/"design_contracts.stderr.txt"),
            resource_contracts_stdout=rec(run/"resource_contracts.stdout.txt"),resource_contracts_stderr=rec(run/"resource_contracts.stderr.txt"),live_runtime_locks=lock_rows,qualified_prediction=result_row,slurm_job_id=job,GPU_allocated=0,
            native_inference_performed=False,new_design_performed=False,new_refold_performed=False,
            formal_benchmark_mutated=False,experimental_binding=False,experimental_blockade=False,
            completed_epoch=time.time())
        need(tree_sha(ROOT/"source")==BASE_SHA,"Default C3 changed during physicalV3")
        for component,r in override["original_default_locks"].items():need(rec(r["path"])==r,"Default runtime lock changed during physicalV3")
        from patch_common_runtime_selector import qualification_contract
        qualification_contract(acceptance,json.loads((frozen/"source_manifest.json").read_text()),json.loads(software_contracts.read_text()),runtime_inputs)
        put(run/"acceptance.json",acceptance)
        status.update(status=acceptance["status"],stage="COMPLETE",acceptance=rec(run/"acceptance.json"),completed_epoch=acceptance["completed_epoch"])
        put(run/"status.json",status)
        for p in run.iterdir():
            if p.is_file():p.chmod(0o444)
        print(json.dumps(acceptance,sort_keys=True))
    except Exception as e:
        status.update(status="CPU_PHYSICAL_PREFLIGHT_FAILED_NO_POSE_PROMOTION",error=str(e),traceback=traceback.format_exc(),completed_epoch=time.time())
        put(run/"status.json",status);print(json.dumps(status),file=sys.stderr);return 2
    return 0
if __name__=="__main__":raise SystemExit(main())
