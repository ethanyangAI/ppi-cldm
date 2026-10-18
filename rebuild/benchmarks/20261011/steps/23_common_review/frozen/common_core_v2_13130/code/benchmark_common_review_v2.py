#!/usr/bin/env python3
"""Independent, blinded common review. Prepare/score/verify on Slurm CPU only.
Inference workers consume fixed inputs and are submitted only by the root agent.
No experimental binding/blockade probability is produced.
"""
import importlib.util
import argparse,collections,datetime,hashlib,json,math,os,re,signal,subprocess,sys,time,unittest
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
_DEP_CODE=Path(__file__).resolve().parent
if not (_DEP_CODE/"src/ppiblocker").exists():_DEP_CODE=Path("/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13051/code")
sys.path.insert(0,str(_DEP_CODE))
from screening_transfer import rec,verify,read,dump,summary,components,parse_ipsae,REVISION
ROOT=Path("/lustre/users/u21111210118/projects/test9")
STEP=ROOT/"steps/23_common_review"
FROZEN_DIR=_DEP_CODE
HARDWARE_INVENTORY=dict(path=str(ROOT/"steps/23_common_review/inputs/proc_gpu_inventory_13044.json"),sha256="eb4a7eb9d026b85d228a2983e85c60a883a117c6438babadecbcbe106e1a29e7",bytes=3668)
GPU_GUARD_RECEIPT=dict(path=str(ROOT/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"),bytes=84446,sha256="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9")
sys.path.insert(0,str(FROZEN_DIR/"src"))
from ppiblocker.structure import read_structure,interface
AA=set("ACDEFGHIKLMNPQRSTVWY")
SETTINGS=dict(schema="common-review.v1",scope="COMPUTATIONAL_ONLY",boltz=dict(version="2.2.1",seeds=[31011,31012,31013],models_per_seed=1,recycles=3,sampling_steps=200,templates=False,initial_guess=False),af2=dict(model_type="alphafold2_multimer_v3",model_order=[1,2,3,4,5],seed=31021,recycles=3,early_stop_tolerance=.5,natural_max_msa="128:256",synthetic_max_msa="1:1",templates=False,initial_guess=False),ipsae=dict(revision=REVISION,PAE_cutoffs_A=[10,15],distance_cutoff_A=15),geometry=dict(contact_cutoff_A=5,partner_atom_overlap_A=2.5,contact_sensitivity_A=[4,8],native_recovery_target_RMSD_A=2,native_recovery_contact_target_F1=.5),primary_MSA_rule="natural: frozen target-only unpaired; synthetic_BBF: single; binder: single",primary_endpoint="R1_continuous",fixed_computational_recovery="R0_median_ge_1",operational_gate=None,probability=None)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def seqhash(x):return hashlib.sha256(x.encode()).hexdigest()
def seqcheck(x):
    if not isinstance(x,str) or not x or set(x)-AA:raise ValueError("Noncanonical/empty protein query")
    return x
def allocated_gpu_count(text):
    fields=dict(re.findall(r"(\w+)=(\S+)",text))
    tres=fields.get("AllocTRES") or fields.get("TRES")
    if tres is None:raise ValueError("No authoritative allocated TRES field")
    entries=dict(v.split("=",1) for v in tres.split(",") if "=" in v)
    if "gres/gpu" in entries:return int(entries["gres/gpu"])
    return sum(int(v) for k,v in entries.items() if k.startswith("gres/gpu:"))
def gpu_guard_module():
    spec=importlib.util.spec_from_file_location("common_core_guard_v4",GPU_GUARD_RECEIPT["path"])
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def selected_scheduler_receipt(text,expected_gpu,environment):
    g=gpu_guard_module();job=environment.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Production common review requires actual Slurm allocation")
    logical=None
    if environment.get("SLURM_ARRAY_JOB_ID") is not None or environment.get("SLURM_ARRAY_TASK_ID") is not None:
        if not environment.get("SLURM_ARRAY_JOB_ID") or environment.get("SLURM_ARRAY_TASK_ID") is None:raise ValueError("Incomplete invoking array identity")
        logical=environment["SLURM_ARRAY_JOB_ID"]+"_"+environment["SLURM_ARRAY_TASK_ID"]
    selected=g.select_scheduler_record(text,raw_job_id=job,logical_key=logical)
    identity=g.scheduler_allocation_identity(selected,logical_key=logical,env=environment)
    tres=g.validate_scheduler_gpu_allocation(selected,expected_gpu)
    return dict(job_id=job,expected_gpu=expected_gpu,allocated_gpu_count=expected_gpu,scheduler_record=selected,
                scheduler_record_full=text,selected_scheduler_record=selected,scheduler_alloc_tres=tres,
                raw_allocation_identity=identity,guard_source_receipt=GPU_GUARD_RECEIPT)
def allocation(expected_gpu):
    env=dict(os.environ);job=env.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Production common review requires actual Slurm allocation")
    pr=subprocess.run(["scontrol","show","job",job,"-o"],capture_output=True,text=True,check=True)
    result=selected_scheduler_receipt(pr.stdout,expected_gpu,env)
    if expected_gpu==1:
        g=gpu_guard_module();owned=g.gpu_ownership_guard(expected_count=1,expected_gpu_name="NVIDIA A100-PCIE-40GB",env=env)
        identity=g.scheduler_allocation_identity(owned["selected_scheduler_record"],env=env)
        tres=g.validate_scheduler_gpu_allocation(owned["selected_scheduler_record"],1)
        if identity!=result["raw_allocation_identity"] or tres!=result["scheduler_alloc_tres"]:raise ValueError("Scheduler/ownership identity or TRES mismatch")
        os.environ["CUDA_VISIBLE_DEVICES"]=owned["child_cuda_visible_devices"];result["owned_gpu_guard"]=owned
    return result
def require_immutable_source_context():
    if FROZEN_DIR!=Path(__file__).resolve().parent:raise RuntimeError("Prepare/worker requires frozen common_core_v2/code, not live source/rebuild")
    bundle=read(FROZEN_DIR.parent/"source_bundle.json")
    if bundle["source"]["path"]!=str(Path(__file__).resolve()):raise ValueError("Source bundle does not bind this actual corrected core")
    return bundle
def assigned_gpu_environment(inventory,environment,physical_minor_to_uuid=None):
    basis=next((k for k in ("SLURM_STEP_GPUS","SLURM_JOB_GPUS") if environment.get(k)),None)
    if basis is None:raise ValueError("No authoritative Slurm assigned global GPU IDs or UUID; bare CUDA visibility is not ownership")
    ids=[]
    for v in environment[basis].split(","):
        v=v.strip()
        if re.fullmatch(r"\d+-\d+",v):
            a,b=map(int,v.split("-"))
            if b<a:raise ValueError("Invalid assigned GPU range")
            ids.extend(str(i) for i in range(a,b+1))
        else:ids.append(v)
    if len(ids)!=1 or len(set(ids))!=1:raise ValueError("Exactly one actual Slurm assigned GPU required")
    physical_map=physical_minor_to_uuid if physical_minor_to_uuid is not None else {str(v["index"]):v["uuid"] for v in inventory}
    owned_uuid=ids[0] if ids[0].startswith("GPU-") else physical_map.get(ids[0])
    if owned_uuid not in physical_map.values():raise ValueError("Assigned Slurm physical ID/UUID absent from driver Device Minor ownership map")
    minor=next((k for k,v in physical_map.items() if v==owned_uuid),None)
    assigned=[v for v in inventory if v["uuid"]==owned_uuid]
    if len(assigned)!=1:raise ValueError("Assigned physical GPU not uniquely in NVML inventory")
    device=assigned[0]
    if device["name"]!="NVIDIA A100-PCIE-40GB":raise ValueError("Frozen common review requires exact NVIDIA A100-PCIE-40GB hardware")
    visible=environment.get("CUDA_VISIBLE_DEVICES")
    if visible is not None:
        vals=[v.strip() for v in visible.split(",") if v.strip()]
        if len(vals)>1:raise ValueError("CUDA exposes more than the assigned GPU")
        if not vals or vals[0] in {"-1","NoDevFiles"}:raise ValueError("GPU worker CUDA device disabled")
        if vals[0].startswith("GPU-") and vals[0]!=device["uuid"]:raise ValueError("Visible UUID is not allocated")
        if not vals[0].startswith("GPU-") and not re.fullmatch(r"\d+",vals[0]):raise ValueError("Unrecognized CUDA device identifier")
        # Slurm/CUDA numeric IDs may be local ordinals under cgroups. Canonical physical UUID
        # derives only from authoritative Slurm IDs; it never derives from an ambiguous CUDA ordinal.
        if vals[0].isdigit() and vals[0] not in {str(minor),"0"}:raise ValueError("Visible numeric device inconsistent with assigned single GPU/local ordinal0")
    return dict(device=device,assigned_physical_device_minor=minor,physical_minor_to_uuid_map=physical_map,assignment_basis=basis,assignment_environment={k:environment.get(k) for k in ["SLURM_STEP_GPUS","SLURM_JOB_GPUS","CUDA_VISIBLE_DEVICES"]},cuda_visible_before=visible,cuda_visible_after=device["uuid"],normalization="ASSIGNED_PHYSICAL_UUID_FROM_SLURM_IDS_NUMERIC_CUDA_ORDINAL_NOT_AUTHORITY")
def gpu_visibility_guard(engine):
    pr=subprocess.run(["nvidia-smi","--query-gpu=index,name,memory.total,uuid","--format=csv,noheader,nounits"],capture_output=True,text=True,check=True)
    inventory=[]
    for line in pr.stdout.strip().splitlines():
        cells=[v.strip() for v in line.split(",")]
        if len(cells)!=4:raise RuntimeError("Malformed physical GPU inventory")
        inventory.append(dict(index=int(cells[0]),name=cells[1],memory_total_mib=int(cells[2]),uuid=cells[3]))
    driver=read(HARDWARE_INVENTORY["path"]);physical_map={}
    for row in driver["rows"]:
        lines=dict(line.split(":",1) for line in row["text"].splitlines() if ":" in line)
        if lines.get("Model","").strip()!="NVIDIA A100-PCIE-40GB":raise RuntimeError("Unrecognized frozen physical GPU model")
        physical_map[lines["Device Minor"].strip()]=lines["GPU UUID"].strip()
    selected=assigned_gpu_environment(inventory,os.environ,physical_map)
    os.environ["CUDA_VISIBLE_DEVICES"]=selected["cuda_visible_after"]
    if engine=="boltz":
        python=ROOT/"env/boltz/bin/python";script='import json,torch; n=torch.cuda.device_count(); assert n==1,("visible CUDA devices",n); name=torch.cuda.get_device_name(0); assert name=="NVIDIA A100-PCIE-40GB",name; print(json.dumps({"engine":"boltz","actual_cuda_visible_count":n,"name":name}))'
    elif engine=="af2":
        python=ROOT/"env/colabfold/bin/python";script='import json,jax; ds=[d for d in jax.devices() if d.platform=="gpu"]; assert len(ds)==1,("visible CUDA devices",len(ds)); name=ds[0].device_kind; assert "A100" in name,name; print(json.dumps({"engine":"af2","actual_cuda_visible_count":len(ds),"name":name}))'
    else:raise ValueError("Unknown common review engine")
    runtime=subprocess.run([str(python),"-c",script],capture_output=True,text=True,timeout=180)
    if runtime.returncode:raise RuntimeError("Engine actual single-CUDA GPU guard failed: "+runtime.stdout+runtime.stderr)
    return dict(physical_inventory=inventory,assignment=selected,engine_cuda_probe=json.loads(runtime.stdout.strip().splitlines()[-1]),probe_stdout=runtime.stdout,probe_stderr=runtime.stderr)
def cpu():
    allocation(0)
    if os.environ.get("CUDA_VISIBLE_DEVICES","") not in ("","NoDevFiles","-1"):raise RuntimeError("CPU step must not expose CUDA devices")
def write_text(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x") as f:f.write(text)
    return rec(path)
def target_entries(obj):
    if isinstance(obj,list):return obj
    if "prepared" in obj:return obj["prepared"]
    if "targets" in obj:return obj["targets"]
    if "protocol" in obj and isinstance(obj["protocol"],dict) and "targets" in obj["protocol"]:return obj["protocol"]["targets"]
    if "entries" in obj:return obj["entries"]
    raise ValueError("Expected frozen target list")
def target_registry(path,out):
    cpu();source=read(path);targets=[]
    qualification=ROOT/"steps/14_control_qualification/bindcraft18/outputs/qualification_overlay.json"
    q=read(qualification)
    qr=q.get("entries",q.get("rows",[]))
    native_bbf=next((v for v in qr if v.get("id")=="bc_BBF_b4"),None)
    if native_bbf is None:
        # The authoritative qualification overlay uses designs in some schema versions.
        native_bbf=next(v for v in q.get("designs",[]) if v.get("id")=="bc_BBF_b4")
    for entry in target_entries(source):
        receipt=entry.get("input_manifest") or entry.get("identity")
        if not isinstance(receipt,dict):raise ValueError("Each target requires immutable input_manifest receipt")
        prepared=read(verify(receipt))
        if prepared.get("schema")=="prepared_benchmark_target.v1":
            if prepared["status"]!="FROZEN_INPUT_READY":raise ValueError("Prepared target not frozen ready")
            ident=read(verify(prepared["identity_receipt"]))
            ds=prepared["target_pdb"];rc=prepared["reference_complex"];sequence=seqcheck(prepared["target_sequence"])
            mapping=prepared["design_to_reference_indices"];repaired=prepared["repair_receipt"]
            native_sequence=seqcheck(prepared["reference_partner_sequence"]);partner_map=prepared["partner_to_reference_indices"]
        else:
            ident=prepared;tc=ident["target_context"]
            if ident.get("status") not in {"INPUT_QUALIFIED","TARGET_COORDINATE_REPAIR_ACCEPTED","INPUT_QUALIFIED_REPAIRED","TARGET_ONLY_REPAIR_ACCEPTED"}:raise ValueError("Target not content-qualified")
            sequence=seqcheck(ident.get("target_sequence") or tc.get("coordinate_required_sequence") or tc["selected_sequence"])
            ds=ident["design_structure"];rc=ident["reference_complex"]
            mapping=ident.get("query_to_reference_indices") or ident.get("design_to_reference_indices")
            repaired=ident.get("repair_acceptance") or ident.get("coordinate_repair_acceptance") or ident.get("repair")
            pc=ident.get("partner_context") or ident["reference_partner_context"]
            native_sequence=seqcheck(pc["coordinate_required_sequence"])
            lo=min(v["label_seq_id"] for v in pc["mapping"])
            partner_map={str(v["label_seq_id"]-lo+1):v["normalized_index"] for v in pc["mapping"]}
        spec=ident["spec"];tc=ident["target_context"];tid=entry.get("target_id",spec["target_id"])
        if tid!=spec["target_id"]:raise ValueError("Target ID mismatch")
        chains,_=read_structure(verify(rc));ref=[v for v in chains if v["id"]=="A"];partner=[v for v in chains if v["id"]=="B"]
        if len(ref)!=1 or len(partner)!=1:raise ValueError("Reference A/B chains required")
        from screening_transfer import chain_records
        design=chain_records(verify(ds))
        if len(design)!=1 or design[0]["sequence"]!=sequence:raise ValueError(tid+": repaired coordinate/query mismatch")
        if tc.get("internal_missing_label_seq_ids") and not repaired:raise ValueError(tid+": internal missing residues require repair acceptance")
        if isinstance(repaired,dict) and {"path","sha256"}<=repaired.keys():verify(repaired)
        if not mapping:raise ValueError("Explicit query to observed reference mapping required")
        mapping={int(k):int(v) for k,v in mapping.items()};assert_mapping(sequence,ref[0]["sequence"],mapping)
        if len(mapping)<3:raise ValueError("Insufficient observed target alignment anchors")
        synthetic=spec["family"].upper()=="BBF";native_scope="observed_span_with_internal_query_residues_restored; terminal context explicitly excluded"
        native_source=None
        if synthetic:
            native_sequence=seqcheck(native_bbf["sequence"])
            if seqhash(native_sequence)!=native_bbf["sequence_sha256"]:raise ValueError("Author BBF_b4 sequence receipt mismatch")
            pc=ident.get("partner_context") or ident["reference_partner_context"]
            if not pc["declared_sequence"].startswith(native_sequence):raise ValueError("Deposited BBF known binder does not match author full140 core")
            partner_map={str(v["label_seq_id"]):v["normalized_index"] for v in pc["mapping"] if v["label_seq_id"]<=len(native_sequence)}
            native_scope="author BBF_b4 full140 sequence; deposited terminal GSHHHHH excluded, internal gaps preserved in query"
            native_source=rec(qualification)
        partner_map={int(k):int(v) for k,v in partner_map.items()};assert_mapping(native_sequence,partner[0]["sequence"],partner_map)
        targets.append(dict(target_id=tid,family=spec["family"],analysis_role=spec["analysis_role"],sequence=sequence,sequence_sha256=seqhash(sequence),synthetic=synthetic,msa_policy="single" if synthetic else "target_only_unpaired",input_manifest=receipt,reference_complex=rc,native_partner_sequence=native_sequence,native_partner_sequence_sha256=seqhash(native_sequence),native_partner_query_to_reference_indices={str(k):v for k,v in sorted(partner_map.items())},native_partner_sequence_scope=native_scope,native_partner_source=native_source,query_to_reference_indices={str(k):v for k,v in sorted(mapping.items())},observed_alignment_residues=len(mapping),excluded_context=ident.get("excluded_nonprotein_components",[]),terminal_context_excluded=tc.get("terminal_context_excluded"),repair_receipt=repaired))
    if len({v["target_id"] for v in targets})!=len(targets):raise ValueError("Duplicate target")
    result=dict(status="FULL_QUERY_AND_REFERENCE_MAPPING_ACCEPTED" if not source.get("pending") else "AVAILABLE_QUERIES_ACCEPTED_REMAINDER_TYPED_PENDING",source=rec(path),created_utc=now(),targets=targets,pending=source.get("pending",[]))
    dump(out,result);return rec(out)
def assert_mapping(query,reference,mapping):
    if len(set(mapping.values()))!=len(mapping):raise ValueError("Reference mapping must be injective")
    for a,b in mapping.items():
        if not 1<=a<=len(query) or not 1<=b<=len(reference) or query[a-1]!=reference[b-1]:raise ValueError("Reference residue mapping identity/range mismatch")
def a3m_rows(text,query):
    rows=[];buf=[];seen=False
    for line in text.splitlines():
        if line.startswith(">"):
            if seen:rows.append("".join(buf));buf=[]
            seen=True
        elif seen and not line.startswith("#"):buf.append(line.strip())
    if seen:rows.append("".join(buf))
    aligned=["".join(c for c in r if not c.islower()) for r in rows]
    if not aligned or aligned[0]!=query or any(len(v)!=len(query) for v in aligned):raise ValueError("A3M exact query/aligned width mismatch")
    if any(set(v)-AA-set("BJOUXZ-") for v in aligned):raise ValueError("A3M unsupported residue outside common official parser alphabets")
    return dict(raw_rows=len(rows),unique_aligned_rows=len(set(aligned)),query_sha256=seqhash(query),length=len(query),ambiguous_aligned_residue_counts=dict(collections.Counter(c for row in aligned for c in row if c in "BJOUXZ")),ambiguity_policy="raw symbols retained; official engine encodings may differ")
def msa(path,out,reuse=None):
    cpu();registry=read(path);source_record=rec(__file__);directory=Path(out).parent/"a3m";directory.mkdir(parents=True,exist_ok=True);records=[]
    previous={v["target_id"]:v for v in read(reuse)["records"] if v.get("file")} if reuse else {}
    for t in registry["targets"]:
        dest=directory/(t["target_id"]+".a3m")
        try:
            prior=previous.get(t["target_id"])
            if prior:
                file=verify(prior["file"]);diagnostics=a3m_rows(file.read_text(),t["sequence"])
                if prior["diagnostics"]!=diagnostics:raise ValueError("Reuse MSA query/count mismatch")
                records.append(dict(prior,reuse_source=rec(reuse)));print("MSA_REUSED",t["target_id"],diagnostics,flush=True);continue
            if t["synthetic"]:write_text(dest,">query\n"+t["sequence"]+"\n");kind="SYNTHETIC_SINGLE_PREDECLARED"
            else:
                helper=r"""import signal,sys
from colabfold.colabfold import run_mmseqs2
signal.signal(signal.SIGALRM,lambda a,b:(_ for _ in ()).throw(TimeoutError("MMseqs2 query timeout")))
signal.alarm(2400)
seq=sys.argv[1];prefix=sys.argv[2]
text=run_mmseqs2([seq],prefix,use_env=True,use_filter=True,use_templates=False,use_pairing=False,host_url="https://api.colabfold.com",user_agent="PPICommonReview/1.1")[0]
with open(sys.argv[3],"x") as f:f.write(text)
"""
                env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",PYTHONNOUSERSITE="1")
                run=subprocess.run([str(ROOT/"env/colabfold/bin/python"),"-c",helper,t["sequence"],str(directory/(t["target_id"]+"_mmseqs")),str(dest)],env=env,capture_output=True,text=True,timeout=2450)
                write_text(directory/(t["target_id"]+".log"),run.stdout+"\n"+run.stderr)
                if run.returncode:raise RuntimeError("MSA_FAILED_NOT_REPLACED_BY_SINGLE: "+run.stderr[-1200:])
                kind="MMSEQS2_TARGET_ONLY_UNPAIRED"
            diagnostics=a3m_rows(dest.read_text(),t["sequence"])
            records.append(dict(target_id=t["target_id"],status="EXACT_QUERY_MSA_ACCEPTED",kind=kind,file=rec(dest),diagnostics=diagnostics,api_database_snapshot="NOT_PROVIDED_BY_API"))
            print("MSA_FROZEN",t["target_id"],diagnostics,flush=True)
        except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
            records.append(dict(target_id=t["target_id"],status="MSA_FAILED_NOT_REPLACED_BY_SINGLE",query_sha256=seqhash(t["sequence"]),file=None,reason=str(error)))
            print("MSA_TYPED_FAILURE",t["target_id"],str(error)[-500:],flush=True)
    complete=all(v.get("file") for v in records)
    dump(out,dict(status="ALL_TARGET_EXACT_QUERY_MSAS_FROZEN" if complete else "PARTIAL_MSAS_TYPED_FAILURES_NOT_FROZEN",registry=rec(path),source=source_record,records=records,created_utc=now(),reuse_source=rec(reuse) if reuse else None))
    if not complete:raise RuntimeError("MSA results retained with typed failures; retry only failed targets via --reuse")
    return rec(out)
def blind_entities(targets,cohorts):
    lookup={t["target_id"]:t for t in targets};entities={};members=[]
    for c in cohorts["selected"]:
        t=lookup[c["target_id"]];seq=seqcheck(c["sequence"])
        if c["sequence_sha256"]!=seqhash(seq):raise ValueError("Cohort sequence hash mismatch")
        key=digest([t["sequence_sha256"],seqhash(seq)]);bid="blind_"+key[:20]
        if bid in entities and entities[bid]["target_sequence"]!=t["sequence"]:raise ValueError("Blind digest collision")
        entities.setdefault(bid,dict(blind_id=bid,target_id=t["target_id"],target_sequence=t["sequence"],binder_sequence=seq,target_sequence_sha256=t["sequence_sha256"],binder_sequence_sha256=seqhash(seq)))
        members.append(dict(c,blind_id=bid))
    controls=[]
    for t in targets:
        seq=t["native_partner_sequence"];key=digest([t["sequence_sha256"],seqhash(seq)]);bid="blind_"+key[:20]
        entities.setdefault(bid,dict(blind_id=bid,target_id=t["target_id"],target_sequence=t["sequence"],binder_sequence=seq,target_sequence_sha256=t["sequence_sha256"],binder_sequence_sha256=seqhash(seq)))
        controls.append(dict(target_id=t["target_id"],blind_id=bid,control_type="REFERENCE_PARTNER_OBSERVED_CONSTRUCT_RECOVERY"))
    sensitive={v["blind_id"] for v in controls}
    uniform=collections.defaultdict(list)
    for m in members:
        if m["cohort"]=="uniform_all_complete":uniform[m["task_id"]].append(m)
    for task,rows in uniform.items():
        sensitive.add(min(rows,key=lambda v:(v["sampling_key"],v["sequence_sha256"]))["blind_id"])
    return sorted(entities.values(),key=lambda v:v["blind_id"]),members,controls,sensitive
def prepare(registry_path,msa_path,cohorts_path,out,gate_protocol):
    require_immutable_source_context();cpu();verify(GPU_GUARD_RECEIPT);registry=read(registry_path);m=read(msa_path);cohorts=read(cohorts_path)
    if m["status"]!="ALL_TARGET_EXACT_QUERY_MSAS_FROZEN":raise ValueError("MSA input is not fully frozen")
    query_registry=read(verify(m["registry"]));qlookup={t["target_id"]:t for t in query_registry["targets"]}
    if set(qlookup)!={t["target_id"] for t in registry["targets"]}:raise ValueError("MSA/full registry target matrix mismatch")
    for t in registry["targets"]:
        if qlookup[t["target_id"]]["sequence"]!=t["sequence"] or qlookup[t["target_id"]]["synthetic"]!=t["synthetic"]:raise ValueError("MSA/full repaired query identity or policy mismatch")
    msas={v["target_id"]:v for v in m["records"]};targets=registry["targets"];targetlookup={t["target_id"]:t for t in targets}
    gate=read(gate_protocol)
    # This specification must be frozen by root before generation. No retrospective threshold.
    if gate.get("common_review_gate")!={"score":"R0","threshold":1.0,"operator":">=","aggregation":"all_required_models_median","scope":"COMPUTATIONAL_ONLY"}:raise ValueError("Root generation protocol must freeze exact common_review_gate")
    entities,members,controls,sensitive=blind_entities(targets,cohorts)
    if len({t["sequence_sha256"] for t in targets})!=len(targets):raise ValueError("This reference-scoring matrix requires distinct target queries; shared exact queries need multi-reference analysis contract")
    hardware=read(verify(HARDWARE_INVENTORY))
    models=[next(line.split(":",1)[1].strip() for line in row["text"].splitlines() if line.startswith("Model:")) for row in hardware["rows"] if row["status"]=="READABLE_DRIVER_PHYSICAL_INFORMATION"]
    if len(models)!=4 or set(models)!={"NVIDIA A100-PCIE-40GB"}:raise ValueError("Frozen physical hardware receipt does not confirm exact PCIE model")
    lock=read(ROOT/"source/environment/runtime-lock-boltz.json");verify(lock["assets"]["boltz2_conf.ckpt"]);verify(lock["environment"]["executable"])
    for f in lock["environment"].get("model_distribution_files",[]):verify(f)
    inventory_path=ROOT/"steps/21_method_runtime/runs/inventory_12946/outputs/inventory.json"
    af2params=[v for v in read(inventory_path)["assets"] if Path(v["path"]).name in {"params_model_"+str(i)+"_multimer_v3.npz" for i in range(1,6)}]
    if len(af2params)!=5:raise ValueError("Five accepted AF2 multimer_v3 parameter receipts required")
    for receipt in af2params:verify(receipt)
    iprecord=rec(FROZEN_DIR/"vendor/ipsae.py")
    if iprecord["sha256"]!="10cf9b08c68c91e06cb28526cf2026f47a3980c9048fd3226d13e3304eaf1c27":raise ValueError("Pinned official ipSAE source changed")
    work=Path(out).parent;inputdir=work/"inference_inputs";inputdir.mkdir(exist_ok=False);jobs=[]
    for e in entities:
        t=targetlookup[e["target_id"]];mr=msas[t["target_id"]]
        verify(mr["file"]);a3m_rows(Path(mr["file"]["path"]).read_text(),e["target_sequence"])
        variants=["primary"]+(["single_sensitivity"] if e["blind_id"] in sensitive and not t["synthetic"] else [])
        e["primary_msa_kind"]=mr["kind"]
        for variant in variants:
            ed=inputdir/(e["blind_id"]+"_"+variant);ed.mkdir()
            targetmsa="empty" if variant=="single_sensitivity" or t["synthetic"] else mr["file"]["path"]
            yaml="version: 1\nsequences:\n  - protein:\n      id: A\n      sequence: "+e["target_sequence"]+"\n      msa: "+json.dumps(targetmsa)+"\n  - protein:\n      id: B\n      sequence: "+e["binder_sequence"]+"\n      msa: empty\n"
            yamlrec=write_text(ed/"complex.yaml",yaml)
            jobs.append(dict(job_key=e["blind_id"]+"_boltz_"+variant,blind_id=e["blind_id"],target_id=e["target_id"],engine="boltz",variant=variant,input=yamlrec,expected_models=3,slots=[dict(seed=s,model=0) for s in SETTINGS["boltz"]["seeds"]],target_msa=mr["file"] if targetmsa!="empty" else None))
            if variant=="primary":
                helper=r"""from colabfold.batch import msa_to_str
import sys
t,b,path,out=sys.argv[1:]
tm=open(path).read() if path!="empty" else ">query\n"+t+"\n"
text=msa_to_str([tm,">binder\n"+b+"\n"],[">101\n"+t+"\n",">102\n"+b+"\n"],[t,b],[1,1])
with open(out,"x") as f:f.write(text)
"""
                env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu")
                run=subprocess.run([str(ROOT/"env/colabfold/bin/python"),"-c",helper,e["target_sequence"],e["binder_sequence"],targetmsa,str(ed/"complex.a3m")],env=env,capture_output=True,text=True)
                if run.returncode:raise RuntimeError("AF2 feature construction failed:"+run.stderr[-1500:])
                jobs.append(dict(job_key=e["blind_id"]+"_af2_primary",blind_id=e["blind_id"],target_id=e["target_id"],engine="af2",variant="primary",input=rec(ed/"complex.a3m"),expected_models=5,slots=[dict(seed=31021,model=n) for n in [1,2,3,4,5]],target_msa=mr["file"] if targetmsa!="empty" else None,max_msa="1:1" if t["synthetic"] else "128:256"))
    inference=dict(status="FROZEN_COMMON_BLIND_INFERENCE_PLAN",created_utc=now(),settings=SETTINGS,entities=entities,jobs=jobs,registry=rec(registry_path),msa=rec(msa_path),generation_gate_protocol=rec(gate_protocol),source=rec(__file__),af2_parameter_receipts=af2params,runtime_locks=dict(gpu_ownership_guard=GPU_GUARD_RECEIPT,physical_hardware_inventory=HARDWARE_INVENTORY,runtime_inventory=rec(inventory_path),boltz=rec(ROOT/"source/environment/runtime-lock-boltz.json"),ipsae=iprecord,af2_inference_environment=rec(FROZEN_DIR/"runtime_entries/af2_inference_env.sh"),af2_entrypoint=rec(FROZEN_DIR/"runtime_entries/colabfold_batch"),screening_module=rec(FROZEN_DIR/"screening_transfer.py"),structure_module=rec(FROZEN_DIR/"src/ppiblocker/structure.py"),msa_roundtrip_module=rec(FROZEN_DIR/"control_msa_check.py")),method_origin_present=False,frozen_source_bundle=rec(FROZEN_DIR.parent/"source_bundle.json"))
    # No method/cohort/native/design/reference information appears in inference plan.
    if any(v in json.dumps(inference) for v in ['"method_id"','"native_score"','"reference_complex"','"hotspots"']):raise ValueError("Blinding violation")
    dump(out,inference)
    dump(work/"membership.json",dict(status="UNBLIND_ONLY_AFTER_SCORE_CONTENT_ACCEPTANCE",inference_plan=rec(out),cohorts=rec(cohorts_path),coverage=cohorts["coverage"],members=members,controls=controls,sensitivity_rule="all controls + predeclared minimum uniform hash per arm"))
    dump(work/"analysis_plan.json",dict(status="BLINDED_SCORER_REFERENCE_GEOMETRY_PLAN",inference_plan=rec(out),registry=rec(registry_path),targets=targets,native_recovery_controls=controls))
    return rec(out)
def job_signature(job):
    keys=["job_key","blind_id","target_id","engine","variant","expected_models","slots","max_msa"]
    value={k:job[k] for k in keys if k in job}
    value["input"]={k:job["input"][k] for k in ["sha256","bytes"]}
    value["target_msa"]={k:job["target_msa"][k] for k in ["sha256","bytes"]} if job.get("target_msa") else None
    return digest(value)
def worker(plan_path,index,out):
    require_immutable_source_context()
    allocated=allocation(1)
    plan=read(plan_path);job=plan["jobs"][index]
    if plan["source"]["path"]!=str(Path(__file__).resolve()) or plan["frozen_source_bundle"]["path"]!=str(FROZEN_DIR.parent/"source_bundle.json"):raise ValueError("GPU plan source does not bind this immutable corrected core")
    visible=gpu_visibility_guard(job["engine"])
    if plan["settings"]!=SETTINGS:raise ValueError("Unrecognized frozen engine settings")
    directory=Path(out)/job["job_key"];directory.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();runs=[]
    if job["engine"]=="boltz":
        for slot in job["slots"]:
            wd=directory/("seed_"+str(slot["seed"]));wd.mkdir();argv=[str(FROZEN_DIR/"runtime_entries/boltz"),"predict",job["input"]["path"],"--out_dir",str(wd),"--cache",str(ROOT/"assets/boltz"),"--model","boltz2","--output_format","pdb","--write_full_pae","--no_kernels","--seed",str(slot["seed"]),"--diffusion_samples","1","--recycling_steps","3","--sampling_steps","200","--devices","1","--num_workers","0","--max_parallel_samples","1"]
            with (wd/"run.log").open("x") as log:proc=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
            runs.append(dict(slot=slot,argv=argv,returncode=proc.returncode,output_directory=str(wd)))
    else:
        # Root wrapper must source accepted AF2 inference_env.sh before this CLI.
        wd=directory/"af2";wd.mkdir();argv=[str(FROZEN_DIR/"runtime_entries/colabfold_batch"),job["input"]["path"],str(wd),"--model-type","alphafold2_multimer_v3","--num-models","5","--model-order","1,2,3,4,5","--num-seeds","1","--random-seed","31021","--num-recycle","3","--recycle-early-stop-tolerance","0.5","--max-msa",job["max_msa"],"--msa-mode","mmseqs2_uniref_env","--num-relax","0","--data",str(ROOT/"assets/colabfold")]
        with (wd/"run.log").open("x") as log:proc=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
        runs.append(dict(slots=job["slots"],argv=argv,returncode=proc.returncode,output_directory=str(wd)))
    dump(directory/"worker.json",dict(status="RAW_WORKER_COMPLETED_PENDING_CPU_CONTENT_VALIDATION",job=job,job_id=os.environ["SLURM_JOB_ID"],created_utc=now(),settings=SETTINGS,elapsed_seconds=time.monotonic()-started,allocation=allocated,gpu_visibility=visible,runs=runs,source=plan["source"],frozen_source_bundle=plan["frozen_source_bundle"],runtime_locks=plan["runtime_locks"],receipt_policy="CPU_PRECOMPUTED_SOURCE_AND_DEPENDENCY_HASH_REFERENCES_NO_GPU_HASH_TASK"))
    print(job["job_key"],"RAW_COMPLETE",flush=True)
def units(plddt,pae,total,scale):
    pp=np.asarray(plddt,float);pa=np.asarray(pae,float)
    if pp.shape!=(total,) or pa.shape!=(total,total) or not np.isfinite(pp).all() or not np.isfinite(pa).all():raise ValueError("Missing/nonfinite/shape raw confidence")
    if pp.min()<0 or pp.max()>scale or pa.min()<0:raise ValueError("Wrong confidence units/range")
    return pp/scale,pa
def transform_fit(query,reference,mapping):
    x=np.array([query["residues"][a-1]["ca"] for a,b in sorted(mapping.items())]);y=np.array([reference["residues"][b-1]["ca"] for a,b in sorted(mapping.items())])
    xc=x.mean(0);yc=y.mean(0);u,s,vt=np.linalg.svd((x-xc).T@(y-yc));r=u@vt
    if np.linalg.det(r)<0:u[:,-1]*=-1;r=u@vt
    return r,yc-xc@r,float(np.sqrt(np.mean(np.sum((x@r+yc-xc@r-y)**2,axis=1))))
def geometry(target,binder,reference,partner,mapping,is_control=False,binder_mapping=None):
    assert_mapping(target["sequence"],reference["sequence"],mapping)
    r,t,rmsd=transform_fit(target,reference,mapping);native=interface(reference,partner,5);pred=interface(target,binder,5)
    covered={mapping[i] for i in pred["target_residues"] if i in mapping}
    nativeiface=set(native["target_residues"]);coverage=len(covered&nativeiface)/len(nativeiface) if nativeiface else None
    bb=np.concatenate(binder["heavy"])@r+t;nb=np.concatenate(partner["heavy"])
    neighbor=cKDTree(bb).query_ball_tree(cKDTree(nb),2.5)
    overlaps=sum(len(v) for v in neighbor)
    ca=np.array([v["ca"] for v in binder["residues"]])@r+t
    control_rmsd=None;recall=None
    if is_control:
        if binder_mapping is None:
            if binder["sequence"]!=partner["sequence"]:raise ValueError("Known partner recovery requires explicit full-query to observed mapping")
            binder_mapping={i:i for i in range(1,len(binder["sequence"])+1)}
        assert_mapping(binder["sequence"],partner["sequence"],binder_mapping)
        if len(binder_mapping)<3:raise ValueError("Insufficient observed partner CA recovery anchors")
        indices=sorted(binder_mapping.items())
        nativeca=np.array([partner["residues"][j-1]["ca"] for i,j in indices]);predca=np.array([ca[i-1] for i,j in indices])
        control_rmsd=float(np.sqrt(np.mean(np.sum((predca-nativeca)**2,axis=1))))
        nativepairs={tuple(v) for v in native["residue_pairs"]};mapped={(mapping[a],binder_mapping[b]) for a,b in pred["residue_pairs"] if a in mapping and b in binder_mapping}
        recall=len(nativepairs&mapped)/len(nativepairs) if nativepairs else None
    precision=len(covered&nativeiface)/len(covered) if covered else 0.
    recalltarget=len(covered&nativeiface)/len(nativeiface) if nativeiface else None
    f1=2*precision*recalltarget/(precision+recalltarget) if recalltarget is not None and precision+recalltarget>0 else (0. if recalltarget is not None else None)
    sensitivity={}
    for cutoff in (4,8):
        nc=interface(reference,partner,cutoff);pc=interface(target,binder,cutoff)
        cov={mapping[i] for i in pc["target_residues"] if i in mapping};truth=set(nc["target_residues"])
        sensitivity[str(cutoff)]=dict(native_interface_target_residue_n=len(truth),predicted_mapped_target_contact_residue_n=len(cov),native_interface_coverage=len(cov&truth)/len(truth) if truth else None)
    overlapped_native={j for js in neighbor for j in js}
    return dict(status="RIGID_OCCLUSION_PROXY_ONLY",target_observed_alignment_n=len(mapping),target_recovery_RMSD_A=rmsd,native_target_interface_residue_n=len(nativeiface),native_interface_coverage=coverage,contact_target_residue_precision=precision,contact_target_residue_recall=recalltarget,contact_target_residue_F1=f1,partner_atom_overlap_pairs_lt_2p5A=overlaps,binder_atoms_overlapping_native_partner=sum(bool(v) for v in neighbor),native_partner_atoms_overlapped=len(overlapped_native),native_partner_heavy_atom_n=len(nb),native_partner_atom_overlap_fraction=len(overlapped_native)/len(nb),contact_sensitivity=sensitivity,known_partner_target_aligned_CA_RMSD_A=control_rmsd,known_partner_native_contact_recall=recall,known_partner_observed_CA_n=len(binder_mapping) if is_control else None,known_partner_full_query_length=len(binder["sequence"]) if is_control else None,known_partner_structural_recovery=(rmsd<=2 and f1>=.5) if is_control and f1 is not None else None,experimental_blockade=False)
def find_raw(job,worker,slot):
    if job["engine"]=="boltz":
        d=Path(worker)/job["job_key"]/("seed_"+str(slot["seed"]))/"boltz_results_complex/predictions/complex"
        return d/"complex_model_0.pdb",d/"confidence_complex_model_0.json",d/"pae_complex_model_0.npz",d/"plddt_complex_model_0.npz"
    d=Path(worker)/job["job_key"]/"af2";pat="complex_unrelaxed_rank_*_alphafold2_multimer_v3_model_"+str(slot["model"])+"_seed_*.pdb"
    ps=list(d.glob(pat))
    if len(ps)!=1:raise ValueError("AF2 missing/duplicate fixed model")
    p=ps[0];sc=p.with_name(p.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json"))
    if "_seed_31021." not in p.name and "_seed_031021." not in p.name and "_seed_31021_" not in p.name:raise ValueError("Unexpected AF2 seed:"+p.name)
    return p,sc,None,None
def one_score(job,e,t,slot,worker,directory,is_control):
    p,sc,pa,nppl=find_raw(job,worker,slot);raw=read(sc)
    chains,_=read_structure(p)
    if len(chains)!=2 or chains[0]["id"]!="A" or chains[1]["id"]!="B" or chains[0]["sequence"]!=e["target_sequence"] or chains[1]["sequence"]!=e["binder_sequence"]:raise ValueError("Predicted chain identity/order mismatch")
    a,b=chains;total=len(a["sequence"])+len(b["sequence"]);na=len(a["sequence"])
    receipts=[rec(p),rec(sc)]
    if job["engine"]=="boltz":
        pae=np.load(pa,allow_pickle=False)["pae"];plddt=np.load(nppl,allow_pickle=False)["plddt"];pp,pae=units(plddt,pae,total,1);receipts += [rec(pa),rec(nppl)]
    else:pp,pae=units(raw["plddt"],raw["pae"],total,100)
    pdbpl=np.array([v["bfactor"] for ch in [a,b] for v in ch["residues"]])
    if np.max(np.abs(pdbpl-pp*100))>.02:raise ValueError("PDB/NPZ pLDDT residue alignment or units mismatch")
    iptm=float(raw["iptm"])
    if not math.isfinite(iptm) or not 0<=iptm<=1:raise ValueError("Invalid global ipTM")
    contacts=interface(a,b,5);pairs=contacts["residue_pairs"]
    if pairs:
        ai=sorted({x-1 for x,y in pairs});bi=sorted({na+y-1 for x,y in pairs})
        iplddt=float(pp[ai+bi].mean());cp=float(np.mean([pae[x-1,na+y-1] for x,y in pairs]+[pae[na+y-1,x-1] for x,y in pairs]))
        r0=components(iptm,float(pp[na:].mean()),iplddt,cp)
    else:iplddt=cp=None;r0=components(iptm,float(pp[na:].mean()),None,None)
    directory.mkdir(parents=True,exist_ok=False)
    os.link(p,directory/"model.pdb")
    dump(directory/"scores.json",dict(pae=pae.tolist(),plddt=(pp*100).tolist(),iptm=iptm))
    official={}
    for cut in (10,15):
        cmd=[str(ROOT/"env/core/bin/python"),str(FROZEN_DIR/"vendor/ipsae.py"),str(directory/"scores.json"),str(directory/"model.pdb"),str(cut),"15"]
        pr=subprocess.run(cmd,capture_output=True,text=True);write_text(directory/("ipsae_"+str(cut)+".log"),pr.stdout+"\n"+pr.stderr)
        if pr.returncode:raise ValueError("Official ipSAE failed:"+pr.stderr[-500:])
        table=directory/("model_"+str(cut)+"_15.txt");official[str(cut)]=parse_ipsae(table.read_text(),"A","B")
    refs,_=read_structure(verify(t["reference_complex"]));ar=[v for v in refs if v["id"]=="A"][0];br=[v for v in refs if v["id"]=="B"][0];mapping={int(k):int(v) for k,v in t["query_to_reference_indices"].items()}
    geo=geometry(a,b,ar,br,mapping,is_control,{int(k):int(v) for k,v in t.get("native_partner_query_to_reference_indices",{}).items()} if is_control and t.get("native_partner_query_to_reference_indices") else None)
    return dict(status="VALID" if pairs else "NO_INTERFACE",slot=slot,raw_files=receipts,derived_files=[rec(v) for v in sorted(directory.iterdir()) if v.is_file()],R0=r0["score"],R1=official["10"]["maximum"] if pairs else None,global_iptm=iptm,directional_pair_iptm=raw.get("pair_chains_iptm"),target_plddt_fraction=float(pp[:na].mean()),binder_plddt_fraction=float(pp[na:].mean()),interface_plddt_fraction=iplddt,bidirectional_contact_PAE_A=cp,contact_residue_pairs=pairs,components=r0,ipsae=official,geometry=geo)
def score(plan_path,analysis_path,worker,out):
    cpu();plan=read(plan_path);analysis=read(analysis_path)
    receipt=rec(plan_path)
    if analysis["inference_plan"]!=receipt:raise ValueError("Score input plan mismatch")
    if plan["settings"]!=SETTINGS:raise ValueError("Frozen settings mismatch")
    verify(plan["source"]);verify(plan["registry"]);verify(plan["msa"]);verify(plan["generation_gate_protocol"])
    for job in plan["jobs"]:verify(job["input"])
    for runtime_receipt in plan["runtime_locks"].values():verify(runtime_receipt)
    entities={v["blind_id"]:v for v in plan["entities"]};targets={v["target_id"]:v for v in analysis["targets"]};controls={v["blind_id"] for v in analysis["native_recovery_controls"]}
    directory=Path(out).parent;modelsdir=directory/"model_scores";modelsdir.mkdir(exist_ok=False);results=[]
    # Only analysis references/native blind IDs are available. No membership/method/native rank information is read.
    for job in plan["jobs"]:
        models=[];e=entities[job["blind_id"]];t=targets[e["target_id"]]
        wr=Path(worker)/job["job_key"]/"worker.json"
        worker_record=None
        if wr.exists():
            w=read(wr)
            if w["settings"]!=SETTINGS:raise ValueError("Cached worker engine settings mismatch")
            if job_signature(w["job"])!=job_signature(job):raise ValueError("Worker fixed job mismatch")
            allocated=w["allocation"]
            original=allocated.get("scheduler_record_full",allocated["scheduler_record"])
            raw_id=str(allocated.get("job_id",w["job_id"]))
            selected=gpu_guard_module().select_scheduler_record(original,raw_job_id=raw_id)
            gpu_guard_module().validate_scheduler_gpu_allocation(selected,1)
            worker_record=rec(wr)
        config_problem=None
        protocol_files=[]
        if worker_record and job["engine"]=="af2":
            try:
                config_path=Path(worker)/job["job_key"]/"af2/config.json";config=read(config_path);protocol_files.append(rec(config_path))
                fields={"model_type":"alphafold2_multimer_v3","num_models":5,"num_seeds":1,"random_seed":31021,"num_recycles":3,"num_relax":0,"use_templates":False}
                for key,value in fields.items():
                    aliases={"num_recycles":["num_recycles","num_recycle"],"random_seed":["random_seed"]}.get(key,[key])
                    actual_value=next((config[k] for k in aliases if k in config),None)
                    if actual_value!=value:raise ValueError("AF2 saved config mismatch "+key+": "+str(actual_value))
                actual_msa=Path(worker)/job["job_key"]/"af2/complex.a3m"
                helper=r"""import json,sys
sys.path.insert(0,sys.argv[1])
from control_msa_check import verify_roundtrip
print(json.dumps(verify_roundtrip(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]),sort_keys=True))
"""
                env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu")
                pr=subprocess.run([str(ROOT/"env/colabfold/bin/python"),"-c",helper,str(FROZEN_DIR),job["input"]["path"],str(actual_msa),e["target_sequence"],e["binder_sequence"]],env=env,capture_output=True,text=True)
                if pr.returncode:raise ValueError("Actual AF2 MSA semantics mismatch:"+pr.stderr[-800:])
                protocol_files.append(rec(actual_msa));dump(modelsdir/(job["job_key"]+"_msa_roundtrip.json"),json.loads(pr.stdout))
            except (FileNotFoundError,KeyError,ValueError) as error:config_problem=str(error)
        for slot in job["slots"]:
            try:
                if config_problem:raise ValueError(config_problem)
                if not worker_record:raise FileNotFoundError("Worker output missing")
                row=one_score(job,e,t,slot,worker,modelsdir/job["job_key"]/(str(slot["seed"])+"_"+str(slot["model"])),job["blind_id"] in controls)
            except (FileNotFoundError,KeyError,ValueError) as error:row=dict(status="MODEL_UNRESOLVED",slot=slot,R0=None,R1=None,reason=str(error))
            models.append(row)
        n=job["expected_models"];r0=summary([v["R0"] for v in models],n);r1=summary([v["R1"] for v in models],n)
        evaluable=r0["median"] is not None and r1["median"] is not None
        results.append(dict(job_key=job["job_key"],blind_id=job["blind_id"],target_id=job["target_id"],engine=job["engine"],variant=job["variant"],worker_record=worker_record,protocol_files=protocol_files,models=models,R0=r0,R1=r1,evaluable=evaluable,evaluable_R0=r0["median"] is not None,evaluable_R1=r1["median"] is not None,pass_computational_R0_ge_1=(r0["median"]>=1 if r0["median"] is not None else None),operational_pass=None,operational_reason="NEW_FAMILY_UNVALIDATED" if t["family"] not in ["MDM2","BBF"] else "UNVALIDATED_TRANSFER",experimental_probability=None,experimental_blockade=False))
        print("COMMON_SCORED",job["job_key"],r0["median"],r1["median"],flush=True)
    result=dict(status="BLINDED_COMMON_REVIEW_SCORED_PENDING_CONTENT_VALIDATION",plan=receipt,analysis_plan=rec(analysis_path),settings=SETTINGS,created_utc=now(),results=results,models_expected=sum(v["expected_models"] for v in plan["jobs"]),models_valid=sum(m["status"]=="VALID" for v in results for m in v["models"]),methods_hidden_from_scorer=True)
    dump(out,result)
    return rec(out)
def verify_result(path,membership_path,out):
    cpu();result=read(path);plan=read(verify(result["plan"]))
    if result["settings"]!=plan["settings"] or result["settings"]!=SETTINGS:raise ValueError("Frozen score settings mismatch")
    expected={v["job_key"]:v for v in plan["jobs"]};actual={v["job_key"]:v for v in result["results"]}
    if set(expected)!=set(actual) or len(actual)!=len(result["results"]):raise ValueError("Common review task denominator lost")
    for key,j in expected.items():
        v=actual[key]
        if {tuple(sorted(m["slot"].items())) for m in v["models"]}!={tuple(sorted(s.items())) for s in j["slots"]}:raise ValueError("Missing/duplicate fixed slots")
        for axis in ("R0","R1"):
            if v[axis]!=summary([m[axis] for m in v["models"]],j["expected_models"]):raise ValueError("Wrong ensemble denominator/summary")
        if v["evaluable_R0"]!=(v["R0"]["median"] is not None) or v["evaluable_R1"]!=(v["R1"]["median"] is not None) or v["evaluable"]!=(v["evaluable_R0"] and v["evaluable_R1"]):raise ValueError("Score completeness/evaluability mismatch")
        if v["pass_computational_R0_ge_1"]!=(v["R0"]["median"]>=1 if v["evaluable_R0"] else None):raise ValueError("Wrong frozen computational gate")
        for f in v.get("protocol_files",[]):verify(f)
        for m in v["models"]:
            for f in m.get("raw_files",[])+m.get("derived_files",[]):verify(f)
            if m["status"] in {"VALID","NO_INTERFACE"}:
                recomputed=components(m["global_iptm"],m["binder_plddt_fraction"],m["interface_plddt_fraction"],m["bidirectional_contact_PAE_A"])
                if recomputed!=m["components"] or m["R0"]!=recomputed["score"]:raise ValueError("R0 component recomputation mismatch")
                tables={Path(f["path"]).name:f for f in m["derived_files"]}
                for cutoff in ("10","15"):
                    parsed=parse_ipsae(Path(tables["model_"+cutoff+"_15.txt"]["path"]).read_text(),"A","B")
                    if parsed!=m["ipsae"][cutoff]:raise ValueError("Official directional ipSAE output mismatch")
                if m["R1"]!=(m["ipsae"]["10"]["maximum"] if m["status"]=="VALID" else None):raise ValueError("R1/no-interface mismatch")
        if v["operational_pass"] is not None:raise ValueError("Unsupported family transfer operational gate")
        if v.get("experimental_probability") is not None or v["experimental_blockade"]:raise ValueError("Unsupported experimental claim")
    tests=run_tests()
    # Unblind only after every score/input/raw/derived/content check above has passed.
    membership=read(membership_path)
    if membership["inference_plan"]!=result["plan"]:raise ValueError("Unblind receipt mismatch")
    by={(v["blind_id"],v["engine"],v["variant"]):v for v in actual.values()};outcomes={}
    for engine in ["boltz","af2"]:
        outcomes[engine]=[dict(cohort_record_id=m["cohort_record_id"],blind_id=m["blind_id"],evaluable=by[(m["blind_id"],engine,"primary")]["evaluable_R0"],pass_computational=by[(m["blind_id"],engine,"primary")]["pass_computational_R0_ge_1"],**{"pass":by[(m["blind_id"],engine,"primary")]["pass_computational_R0_ge_1"]}) for m in membership["members"]]
    native=[dict(c,engines={eng:by[(c["blind_id"],eng,"primary")] for eng in ["boltz","af2"]}) for c in membership["controls"]]
    grouped=collections.defaultdict(list)
    for m in membership["members"]:
        for engine in ["boltz","af2"]:
            v=by[(m["blind_id"],engine,"primary")]
            grouped[(m["target_id"],m["method_id"],m["seed"],m["cohort"],engine)].append(v)
    cohort_summaries=[]
    for (target,method,seed,cohort,engine),rows in sorted(grouped.items()):
        r1=[v["R1"]["median"] for v in rows]
        cohort_summaries.append(dict(target_id=target,method_id=method,seed=seed,cohort=cohort,engine=engine,n_selected=len(rows),n_R1_complete=sum(v is not None for v in r1),R1_candidates=summary(r1,len(rows)),R0_candidates=summary([v["R0"]["median"] for v in rows],len(rows)),model_coverage=dict(expected=sum(v["R1"]["n_expected"] for v in rows),valid=sum(v["R1"]["n_valid"] for v in rows)),operational_pass=None))
    acceptance=dict(status="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",result=rec(path),membership=rec(membership_path),created_utc=now(),n_jobs=len(actual),n_models_expected=result["models_expected"],n_models_valid=result["models_valid"],n_unresolved_or_no_interface=result["models_expected"]-result["models_valid"],coverage=membership["coverage"],outcomes=outcomes,cohort_summaries=cohort_summaries,native_recovery_controls=native,tests=tests,all78_scope="DEVELOPMENT_ONLY",independent_experimental_validation=False)
    dump(out,acceptance)
    lines=["# 同靶标共同复核报告","","全部推断采用固定协议；生成方法/cohort/native分数在评分阶段隐藏。天然靶标使用冻结target-only unpaired MSA，BBF按人工靶点身份使用single；binder均single。Boltz primary与AF2 secondary结果分开。","",f"预定模型 {result['models_expected']}，有效接触模型 {result['models_valid']}，未解决或无界面 {acceptance['n_unresolved_or_no_interface']}。预定模型缺失不补零，不删除分母。","", "二元端点为提前冻结的计算R0中位数≥1；R1是连续官方ipSAE10-max。二者均不代表实验结合/阻断、亲和力或概率。原生伙伴恢复失败会限制对应靶标解释。","","|target|引擎|原生伙伴R0|R1|有效模型/预定|伙伴RMSD中位数 Å|contact recall中位数|","|---|---|---:|---:|---:|---:|---:|"]
    fmt=lambda x:"不可估计" if x is None else f"{x:.3f}"
    for c in native:
        for eng,v in c["engines"].items():
            gs=[m.get("geometry",{}) for m in v["models"]];n=v["R0"]["n_expected"]
            r=summary([g.get("known_partner_target_aligned_CA_RMSD_A") for g in gs],n)["median"];cr=summary([g.get("known_partner_native_contact_recall") for g in gs],n)["median"]
            lines.append(f"|{c['target_id']}|{eng}|{fmt(v['R0']['median'])}|{fmt(v['R1']['median'])}|{v['R0']['n_valid']}/{n}|{fmt(r)}|{fmt(cr)}|")
    lines += ["","几何遮挡只按观察到的实验残基对齐，记录原伙伴5 Å界面覆盖、<2.5 Å刚性原子重叠与原伙伴atom fraction，4/8 Å contact sensitivity；缺失loop无实验坐标，不作为真实阻断证据。","","完整cohort分母、各arm短缺、评分失败、source/input/raw output hashes见acceptance与manifest。独立实验成功率和新家族泛化目前不可估计。",""]
    report=Path(out).parent/"REPORT.md";write_text(report,"\n".join(lines))
    manifest=dict(status=acceptance["status"],source=rec(__file__),score=rec(path),inference_plan=result["plan"],analysis_plan=result["analysis_plan"],membership=rec(membership_path),outputs=[rec(out),rec(report)],settings=SETTINGS)
    dump(Path(out).parent/"manifest.json",manifest)
    return rec(out)
def run_tests():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);r=unittest.TextTestRunner(verbosity=2).run(suite)
    if not r.wasSuccessful():raise RuntimeError("Common review meaningful tests failed")
    return dict(status="PASSED",n_tests=r.testsRun)
class Tests(unittest.TestCase):
    def test_cgroup_nvml_index_remap_uses_driver_minor_uuid(self):
        inv=[dict(index=0,uuid="GPU-3",name="NVIDIA A100-PCIE-40GB")]
        physical={"0":"GPU-0","1":"GPU-1","2":"GPU-2","3":"GPU-3"}
        v=assigned_gpu_environment(inv,dict(SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES="0"),physical)
        self.assertEqual(v["cuda_visible_after"],"GPU-3");self.assertEqual(v["assigned_physical_device_minor"],"3")
        with self.assertRaises(ValueError):assigned_gpu_environment(inv,dict(SLURM_JOB_GPUS="0",CUDA_VISIBLE_DEVICES="0"),physical)

    def test_assigned_uuid_normalization_not_nvml_visibility(self):
        inv=[dict(index=i,uuid="GPU-"+str(i),name="NVIDIA A100-PCIE-40GB") for i in range(4)]
        env=dict(SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES="0")
        v=assigned_gpu_environment(inv,env)
        self.assertEqual(v["device"]["index"],3);self.assertEqual(v["cuda_visible_after"],"GPU-3")
        self.assertEqual(assigned_gpu_environment(inv,dict(SLURM_STEP_GPUS="3",CUDA_VISIBLE_DEVICES="GPU-3"))["cuda_visible_after"],"GPU-3")
    def test_unallocated_or_multiple_visible_devices_rejected(self):
        inv=[dict(index=i,uuid="GPU-"+str(i),name="NVIDIA A100-PCIE-40GB") for i in range(4)]
        for env in [dict(SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES="0,1"),dict(SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES="GPU-2"),dict(SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES="2"),dict(SLURM_JOB_GPUS="0,3"),dict(SLURM_JOB_GPUS="7"),dict(CUDA_VISIBLE_DEVICES="0")]:
            with self.assertRaises(ValueError):assigned_gpu_environment(inv,env)
    def test_assigned_gpu_hardware_uuid_fallback_and_no_cuda(self):
        inv=[dict(index=3,uuid="GPU-3",name="NVIDIA A100-PCIE-40GB")]
        self.assertEqual(assigned_gpu_environment(inv,dict(SLURM_JOB_GPUS="GPU-3",CUDA_VISIBLE_DEVICES="GPU-3"))["cuda_visible_after"],"GPU-3")
        with self.assertRaises(ValueError):assigned_gpu_environment(inv,dict(CUDA_VISIBLE_DEVICES="GPU-3"))
        with self.assertRaises(ValueError):assigned_gpu_environment([dict(index=3,uuid="GPU-3",name="V100")],dict(SLURM_JOB_GPUS="3"))
        with self.assertRaises(ValueError):assigned_gpu_environment(inv,dict(SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES=""))

    def test_allocated_gpu_count_not_driver_visibility(self):
        self.assertEqual(allocated_gpu_count("JobId=1 TRES=cpu=2,node=1,billing=2"),0)
        self.assertEqual(allocated_gpu_count("JobId=1 AllocTRES=cpu=2,gres/gpu=1,gres/gpu:a100=1"),1)
        self.assertEqual(allocated_gpu_count("JobId=1 TRES=cpu=2,gres/gpu:a100=2"),2)
        with self.assertRaises(ValueError):allocated_gpu_count("JobId=1 ReqTRES=cpu=2,gres/gpu=1")
    def test_full_query_mapping_reject_deletion_mismatch(self):
        assert_mapping("ACDEFG","ACEFG",{1:1,2:2,4:3,5:4,6:5})
        with self.assertRaises(ValueError):assert_mapping("ACDEFG","ACEFG",{3:3})
        with self.assertRaises(ValueError):assert_mapping("AAA","AAA",{1:1,2:1})
    def test_msa_query_and_width(self):
        d=a3m_rows(">q\nACDE\n>x\nACd-E\n>unknown\nAXBZ\n","ACDE");self.assertEqual(d["raw_rows"],3);self.assertEqual(d["ambiguous_aligned_residue_counts"],{"X":1,"B":1,"Z":1})
        with self.assertRaises(ValueError):a3m_rows(">q\nACE\n","ACDE")
        with self.assertRaises(ValueError):a3m_rows(">q\nACDE\n>x\nAC-EF\n","ACDE")
    def test_blinding_dedup_and_uniform_preselection(self):
        target=dict(target_id="T",sequence="ACDE",sequence_sha256=seqhash("ACDE"),native_partner_sequence="AG")
        rows=[]
        for meth in ["rfd","bindcraft"]:
            for coh in ["uniform_all_complete","native_fixed_top_k"]:
                rows.append(dict(target_id="T",sequence="AC",sequence_sha256=seqhash("AC"),method_id=meth,cohort=coh,task_id=meth,sampling_key="00",cohort_record_id=meth+coh))
        es,ms,cs,s=blind_entities([target],dict(selected=rows))
        self.assertEqual(len(es),2);self.assertEqual(len(ms),4);self.assertEqual(len(s),2)
        self.assertNotIn("method_id",json.dumps(es));self.assertEqual(len({v["blind_id"] for v in ms}),1)
    def test_units_nulls_and_zero_pae(self):
        pp,pa=units([80,90],[[0,2],[1,0]],2,100);self.assertEqual(pp.tolist(),[.8,.9])
        with self.assertRaises(ValueError):units([80,90],[[0,2],[1,0]],2,1)
        with self.assertRaises(ValueError):units([.8,float("nan")],[[0,2],[1,0]],2,1)
        self.assertIsNone(summary([1,None,1],3)["median"])
        self.assertEqual(components(.9,.8,.8,0)["score"],1)
    def test_geometry_rigid_invariant_and_native_recovery(self):
        def chain(id,seq,xyz):
            return dict(id=id,sequence=seq,residues=[dict(ca=np.array(v,float)) for v in xyz],heavy=[np.array([v],float) for v in xyz])
        a=chain("A","ACD",[[0,0,0],[2,0,0],[0,2,0]]);b=chain("B","AGF",[[0,0,3],[1,0,3],[0,1,3]])
        rot=np.array([[0,-1,0],[1,0,0],[0,0,1]],float)
        ap=chain("A","ACD",np.array([v["ca"] for v in a["residues"]])@rot+7);bp=chain("B","AGF",np.array([v["ca"] for v in b["residues"]])@rot+7)
        g=geometry(ap,bp,a,b,{1:1,2:2,3:3},True)
        self.assertLess(g["target_recovery_RMSD_A"],1e-10);self.assertLess(g["known_partner_target_aligned_CA_RMSD_A"],1e-10);self.assertEqual(g["known_partner_native_contact_recall"],1)
        self.assertEqual(g["native_interface_coverage"],1);self.assertFalse(g["experimental_blockade"])
    def test_no_interface_typed_not_negative(self):
        r=components(.9,.9,None,None);self.assertIsNone(r["score"])
        self.assertIsNone(summary([None]*5,5)["median"])
    def test_full_binder_query_internal_gaps_are_mapped_not_deleted(self):
        def chain(id,seq,xyz):
            return dict(id=id,sequence=seq,residues=[dict(ca=np.array(v,float)) for v in xyz],heavy=[np.array([v],float) for v in xyz])
        a=chain("A","ACD",[[0,0,0],[2,0,0],[0,2,0]])
        refb=chain("B","ACG",[[0,0,3],[1,0,3],[0,1,3]])
        full=chain("B","ACDEG",[[0,0,3],[1,0,3],[20,0,0],[25,0,0],[0,1,3]])
        g=geometry(a,full,a,refb,{1:1,2:2,3:3},True,{1:1,2:2,5:3})
        self.assertEqual(g["known_partner_observed_CA_n"],3);self.assertEqual(g["known_partner_full_query_length"],5)
        self.assertLess(g["known_partner_target_aligned_CA_RMSD_A"],1e-10);self.assertEqual(g["known_partner_native_contact_recall"],1)
        with self.assertRaises(ValueError):geometry(a,full,a,refb,{1:1,2:2,3:3},True)
    def test_worker_reuse_requires_same_content_protocol(self):
        j=dict(job_key="x",blind_id="b",target_id="t",engine="boltz",variant="primary",expected_models=3,slots=[dict(seed=1,model=0)],input=dict(path="/a",sha256="123",bytes=2),target_msa=None)
        j2=json.loads(json.dumps(j));j2["input"]["path"]="/b"
        self.assertEqual(job_signature(j),job_signature(j2));j2["slots"][0]["seed"]=2
        self.assertNotEqual(job_signature(j),job_signature(j2))
    def test_technical_replicate_denominator(self):
        self.assertIsNone(summary([1]*2,3)["median"]);self.assertEqual(summary([1]*5,5)["median"],1)
def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest="command",required=True)
    for name in ["targets","msa"]:
        s=sp.add_parser(name);s.add_argument("--input",required=True);s.add_argument("--out",required=True)
        if name=="msa":s.add_argument("--reuse")
    s=sp.add_parser("prepare")
    for name in ["registry","msa","cohorts","out","gate-protocol"]:s.add_argument("--"+name,required=True)
    s=sp.add_parser("worker");s.add_argument("--plan",required=True);s.add_argument("--index",type=int,required=True);s.add_argument("--out",required=True)
    s=sp.add_parser("score")
    for name in ["plan","analysis","worker","out"]:s.add_argument("--"+name,required=True)
    s=sp.add_parser("verify")
    for name in ["input","membership","out"]:s.add_argument("--"+name,required=True)
    s=sp.add_parser("test");s.add_argument("--out",required=True)
    a=p.parse_args()
    if a.command=="targets":res=target_registry(a.input,a.out)
    elif a.command=="msa":res=msa(a.input,a.out,a.reuse)
    elif a.command=="prepare":res=prepare(a.registry,a.msa,a.cohorts,a.out,a.gate_protocol)
    elif a.command=="worker":worker(a.plan,a.index,a.out);return
    elif a.command=="score":res=score(a.plan,a.analysis,a.worker,a.out)
    elif a.command=="verify":res=verify_result(a.input,a.membership,a.out)
    else:cpu();res=run_tests();dump(a.out,dict(res,source=rec(__file__),settings=SETTINGS,created_utc=now()))
    print(json.dumps(res,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()

