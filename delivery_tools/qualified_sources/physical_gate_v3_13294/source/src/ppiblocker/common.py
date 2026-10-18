from __future__ import annotations
import hashlib
import json
import os
import resource
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

class EvidenceError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def require(condition, code, message):
    if not condition:
        raise EvidenceError(code, message)

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temp.open("w") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)

def record_file(path):
    path = Path(path).resolve()
    require(path.is_file(), "MISSING_ARTIFACT", str(path))
    return {"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}

def verify_file(item):
    path = Path(item["path"])
    require(path.is_file() and digest(path) == item["sha256"],
            "INTEGRITY_FAILURE", f"Artifact changed or missing: {path}")
    return path

def read_json(path):
    with open(path) as f:
        return json.load(f)

def checked_command(argv, directory, log, env=None, timeout=86400):
    """Durable command and resource receipt, including failed/timeout invocations."""
    import time
    directory, log = Path(directory), Path(log)
    directory.mkdir(parents=True, exist_ok=True);log.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(log.with_suffix(".command.json"), {"argv": list(map(str,argv)), "cwd":str(directory)})
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={"started_utc":datetime.now(timezone.utc).isoformat(),"timeout_seconds":timeout,
             "slurm_job_id":os.environ.get("SLURM_JOB_ID"),"allocated_gpus":os.environ.get("SLURM_GPUS_ON_NODE"),
             "status":"RUNNING","returncode":None}
    started=time.monotonic()
    try:
        with log.open("w") as f:
            result=subprocess.run(list(map(str,argv)),cwd=directory,env=env,stdout=f,
                                  stderr=subprocess.STDOUT,timeout=timeout,check=False)
        receipt.update(returncode=result.returncode,status="COMPLETE" if result.returncode==0 else "FAILED")
        require(result.returncode==0,"BACKEND_FAILED",f"Exit {result.returncode}; log={log}")
    except (OSError,subprocess.TimeoutExpired) as error:
        receipt.update(status="TIMEOUT" if isinstance(error,subprocess.TimeoutExpired) else "LAUNCH_FAILED",error=str(error))
        raise EvidenceError("BACKEND_FAILED",f"{error}; log={log}") from error
    finally:
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt.update(wall_seconds=time.monotonic()-started,
                       child_user_cpu_seconds=after.ru_utime-before.ru_utime,
                       child_system_cpu_seconds=after.ru_stime-before.ru_stime,
                       child_maxrss_process_highwater_kb=after.ru_maxrss,
                       maxrss_semantics="process child high-water mark, not isolated per command",
                       gpu_utilization_measured=False,ended_utc=datetime.now(timezone.utc).isoformat())
        atomic_json(log.with_suffix(".resources.json"),receipt)
    return record_file(log)

def source_provenance():
    source = Path(__file__).resolve().parents[2]
    py = sorted((source / "src").rglob("*.py"))
    tree = hashlib.sha256("".join(str(p.relative_to(source)) + digest(p) for p in py).encode()).hexdigest()
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=source, text=True))
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {"git_commit": commit, "dirty": dirty, "python_source_sha256": tree,
            "python": sys.version, "executable": sys.executable}

class Run:
    def __init__(self, root, step, inputs=None):
        self.root = Path(root).resolve()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.id = stamp + "_" + uuid.uuid4().hex[:12]
        self.path = self.root / "steps" / step / "runs" / self.id
        self.path.mkdir(parents=True, exist_ok=False)
        for name in ("outputs", "work", "logs", "qc"):
            (self.path / name).mkdir()
        self.manifest = {"schema_version": 1, "run_id": self.id, "step": step,
                         "created_utc": stamp, "status": "RUNNING",
                         "source": source_provenance(), "inputs": inputs or [],
                         "execution": {"slurm_job_id": os.environ.get("SLURM_JOB_ID"),
                                       "slurm_nodes": os.environ.get("SLURM_JOB_NODELIST"),
                                       "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
                                       "allocated_memory_mb": os.environ.get("SLURM_MEM_PER_NODE"),
                                       "address_space_limits_bytes": list(resource.getrlimit(resource.RLIMIT_AS))},
                         "outputs": {}, "evidence_tier": "engineering_only",
                         "claims": {"experimental_binding": False, "experimental_blockade": False}}
        self.save()

    def save(self):
        atomic_json(self.path / "manifest.json", self.manifest)

    def output(self, name, path):
        self.manifest["outputs"][name] = record_file(path)
        self.save()

    def finish(self, status, tier, details=None):
        self.manifest["file_inventory"]=[record_file(p) for folder in ("outputs","work","logs","qc") for p in sorted((self.path/folder).rglob("*")) if p.is_file()]
        self.manifest.update(status=status, evidence_tier=tier)
        if details:
            self.manifest.update(details)
        self.save()
        return self.path / "manifest.json"

    def fail(self, error):
        self.manifest["error"] = {"code": getattr(error, "code", "UNEXPECTED_ERROR"), "message": str(error)}
        self.finish("FAILED", "not_accepted")

def load_run(path, accepted_statuses):
    m = read_json(path)
    require(m["status"] in accepted_statuses, "UPSTREAM_NOT_ACCEPTED", m["status"])
    for artifact in list(m["outputs"].values())+m.get("file_inventory",[])+m.get("inputs",[]):
        verify_file(artifact)
    for artifact in file_references(m.get("runtime",{})):
        verify_file(artifact)
    # v2 snapshots preserve historical state. The next model job validates its live environment.
    return m

def strict_bool(value, name):
    require(type(value) is bool,"INVALID_BOOLEAN",f"{name} requires a YAML boolean, not {type(value).__name__}")
    return value

def pin_config_msas(run, config, base):
    """Copy caller MSAs once; downstream consumes immutable run snapshots."""
    import shutil
    slots=[(p,"msa",f"protein_{i}") for i,p in enumerate(config["proteins"])]
    slots += [(config[s],"target_msa",s+"_target") for s in ("refold",) if s in config]
    origins=[]
    for obj,key,label in slots:
        if not obj.get(key):continue
        source=Path(obj[key]).expanduser()
        if not source.is_absolute():source=base/source
        require(source.suffix in {".a3m",".csv"},"MSA_FORMAT_UNSUPPORTED","Boltz accepts .a3m or .csv; preserve the source format")
        origin=record_file(source)
        dest=run.path/"outputs"/(label+source.suffix)
        shutil.copy2(source,dest)
        pinned=record_file(dest)
        require(pinned["sha256"]==origin["sha256"],"INTEGRITY_FAILURE","MSA changed while snapshotting")
        obj[key]=str(dest);obj[key+"_record"]=pinned
        run.output(label+"_msa",dest)
        origins.append({"input_name":label,"original_source":origin,"snapshot":pinned})
    if origins:
        path=run.path/"outputs/msa_sources.json";atomic_json(path,origins);run.output("msa_sources",path)

def file_references(value):
    if isinstance(value,dict):
        if {'path','sha256'}<=set(value):yield value
        else:
            for item in value.values():yield from file_references(item)
    elif isinstance(value,list):
        for item in value:yield from file_references(item)

def tree_records(path):
    return [record_file(p) for p in sorted(Path(path).rglob('*'))
            if p.is_file() and not any(x in p.parts for x in ('.git','__pycache__')) and p.suffix!='.pyc']

def collect_runtime(root, component):
    root=Path(root)
    python=root/'env'/component/'bin/python'
    if component=='core':
        require(Path(sys.executable).resolve()==python.resolve(),'ENVIRONMENT_INTERPRETER_MISMATCH','Core checks must execute in the project core Python, not only probe it')
    env=os.environ.copy();env['PYTHONNOUSERSITE']='1';env.pop('PYTHONPATH',None)
    probe=Path(__file__).with_name('runtime_probe.py')
    result=subprocess.run([str(python),'-B',str(probe)],capture_output=True,text=True,env=env,check=True)
    state={'component':component,'environment':json.loads(result.stdout),'assets':{},'vendor_files':{}}
    if component=='rfd':
        for repo in ('RFdiffusion','ProteinMPNN','dllogger'):
            state['vendor_files'][repo]=tree_fingerprint(root/'vendor'/repo)
        state['assets']['checkpoint']=record_file(root/'assets/rfdiffusion/Complex_base_ckpt.pt')
        receipt=root/'assets/rfdiffusion/Complex_base_ckpt.receipt.json'
        state['assets']['receipt']=record_file(receipt)
        expected=read_json(receipt)
        require(state['assets']['checkpoint']['sha256']==expected['sha256'],'WEIGHT_INTEGRITY_FAILURE',str(receipt))
    elif component=='boltz':
        for filename in ('boltz2_conf.ckpt','boltz2_aff.ckpt'):
            state['assets'][filename]=record_file(root/'assets/boltz'/filename)
            receipt=root/'assets/boltz'/(filename.replace('.ckpt','.ckpt.receipt.json'))
            state['assets'][filename+'_receipt']=record_file(receipt)
            require(state['assets'][filename]['sha256']==read_json(receipt)['sha256'],'WEIGHT_INTEGRITY_FAILURE',filename)
        require((root/'assets/boltz/mols').is_dir(),'MOLECULE_LIBRARY_MISSING','Missing Boltz molecule directory')
        state['molecule_tree']=tree_fingerprint(root/'assets/boltz/mols')
        require(state['molecule_tree']['file_count'],'MOLECULE_LIBRARY_MISSING','Empty molecule library')
    return state

def runtime_provenance(run, root, components):
    """Measure actual executables, versions, model code/configs and assets at invocation."""
    for component in dict.fromkeys(["core",*components]):
        lock=Path('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_runtime_repair_13289/frozen/runtime_override')/f'runtime-lock-{component}.json'
        require(lock.exists(),'RUNTIME_LOCK_MISSING',str(lock))
        expected=read_json(lock)
        actual=collect_runtime(root,component)
        require(actual==expected,'RUNTIME_DRIFT',f'{component} differs from the reviewed runtime lock; do not refresh the lock automatically')
        snapshot=run.path/'qc'/f'runtime-{component}.json'
        atomic_json(snapshot,actual)
        lock_copy=run.path/'qc'/f'runtime-lock-{component}.json'
        atomic_json(lock_copy,expected)
        run.manifest.setdefault('runtime',{})[component]={'snapshot':record_file(snapshot),'lock':record_file(lock_copy)}
    run.manifest['runtime_validation']='live_capture_matches_reviewed_lock_v2'
    run.save()


def tree_fingerprint(path):
    path=Path(path).resolve()
    files=tree_records(path)
    payload=[{'relative_path':str(Path(f['path']).relative_to(path)),'sha256':f['sha256'],'bytes':f['bytes']} for f in files]
    return {'path_root':str(path),'file_count':len(files),'bytes':sum(f['bytes'] for f in files),
            'tree_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
