#!/usr/bin/env python3
"""Capture one report-request descriptor. Do not follow receipt children."""
import argparse, hashlib, importlib.util, json, math, os, re, stat, subprocess, sys
from pathlib import Path, PurePosixPath

R = Path("/lustre/users/u21111210118/projects/test9")
S = R / "steps/24_benchmark_delivery"
P = S / "pending/report_request_descriptor_capture_v1"
D = Path(__file__).absolute().parent
FILES = ("capture.py", "capture_cpu.sbatch", "HANDOFF.md")
REQUEST = S / "submissions/final_scientific_report_request_from14706_fullcost14576/request.json"
JOB_NAME = "test9_report_request_descriptor_capture_v1"
STATUS = "ACTUAL_REPORT_REQUEST_DESCRIPTOR_CPU_ACCEPTED_NOT_REPORT_OR_SCIENCE"
CORE = R / "env/core/bin/python"
CORE_REAL = R / "env/core/bin/python3.11"
CORE_BYTES = 25916456
CORE_SHA = "76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"

def need(value, message):
    if not value:
        raise ValueError(message)

def lexical(value):
    """Pure string/path-shape check; never access a receipt child's filesystem."""
    need(isinstance(value, str) and value.startswith("/"), "Absolute path string required")
    need(all(x not in ("", ".", "..") for x in value.split("/")[1:]), "Noncanonical path components")
    q = PurePosixPath(value)
    need(q.is_relative_to(PurePosixPath(str(R))), "Path outside exact logical authority")
    return Path(value)

def ancestry(p):
    p = lexical(str(p))
    for q in (p, *p.parents):
        if q == R.parent:
            break
        need(not q.is_symlink(), "Symbolic input/source/output ancestry rejected")
    return p

def file_metadata(p):
    p = ancestry(p)
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode) and not (s.st_mode & 0o222), "Readonly regular file required")
    return dict(path=str(p), bytes=s.st_size, inode=s.st_ino,
                mtime_ns=s.st_mtime_ns, mode=stat.S_IMODE(s.st_mode))

def read_ro(p):
    p = ancestry(p)
    before = file_metadata(p)
    data = p.read_bytes()
    need(file_metadata(p) == before and len(data) == before["bytes"], "File metadata changed during read")
    receipt = dict(path=str(p), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return receipt, data, before

def strict_json(data):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, "Duplicate JSON key")
            value[key] = item
        return value
    def constant(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    def number(value):
        parsed = float(value)
        need(math.isfinite(parsed), "Nonfinite JSON number")
        return parsed
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)

def tuple_shape(r):
    need(type(r) is dict and set(r) == {"path", "bytes", "sha256"}, "Exact receipt keys required")
    need(type(r["bytes"]) is int and r["bytes"] >= 0, "Integer nonnegative receipt bytes required")
    need(type(r["sha256"]) is str and re.fullmatch("[0-9a-f]{64}", r["sha256"]), "Exact SHA256 shape")
    lexical(r["path"])  # SHAPE ONLY: no stat/open/hash/resolve of the child's path.

def request_shape(obj):
    keys = {"schema", "software_acceptance", "common_successor", "root_gpu_cost",
            "scientific_scope", "experimental_binding_or_blockade"}
    need(type(obj) is dict and set(obj) == keys, "Exact six report-request keys required")
    need(obj["schema"] == "final-scientific-report-request.v1" and
         obj["scientific_scope"] == "COMPUTATIONAL_ONLY" and
         obj["experimental_binding_or_blockade"] is False, "Computational report request only")
    for key in ("software_acceptance", "common_successor", "root_gpu_cost"):
        tuple_shape(obj[key])

def tres(value):
    fields = {}
    for token in value.split(","):
        need("=" in token, "Malformed allocated TRES")
        key, val = token.split("=", 1)
        need(key and val and key not in fields, "Duplicate/empty allocated TRES")
        fields[key] = val
    need(fields.get("cpu") == "1", "Actual allocated CPU1 required")
    for key, val in fields.items():
        if key == "gpu" or key.startswith(("gres/gpu", "gres:gpu")):
            need(re.fullmatch(r"(?:gpu|gres/gpu|gres:gpu)(?::[A-Za-z0-9_.-]+)?", key) and
                 val.isdigit() and int(val) == 0, "GPU allocation or malformed GPU namespace")
    return fields

def cpu():
    jid = os.environ.get("SLURM_JOB_ID", "")
    need(jid.isdigit() and int(jid) > 0, "Actual named CPU allocation required before hashing")
    for key, val in {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu",
                     "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
                     "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                     "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}.items():
        need(os.environ.get(key) == val, "Pure CPU import/thread isolation differs")
    need("PYTHONPATH" not in os.environ, "Injected PYTHONPATH")
    argv = ["scontrol", "show", "job", jid, "-o"]
    proc = subprocess.run(argv, capture_output=True, text=True)
    need(proc.returncode == 0, "Current own allocation query failed")
    rows = [line for line in proc.stdout.splitlines()
            if re.search(r"\bJobId=" + re.escape(jid) + r"(?:\s|$)", line)]
    need(len(rows) == 1, "Unique actual numeric current allocation")
    fields = {}
    for key, val in re.findall(r"(\w+)=(\S*)", rows[0]):
        need(key not in fields, "Duplicate scheduler field")
        fields[key] = val
    need(fields.get("JobState") == "RUNNING" and fields.get("JobName") == JOB_NAME and
         fields.get("UserId", "").startswith("u21111210118(") and
         fields.get("Account") == "u21111210118" and fields.get("Partition") == "organ" and
         fields.get("NumCPUs") == "1" and fields.get("NumTasks") == "1",
         "Actual named owner/account/organ CPU1 required")
    reps = [tres(fields[key]) for key in ("TRES", "AllocTRES") if key in fields]
    need(reps and all(row == reps[0] for row in reps), "Missing/inconsistent actual allocated TRES")
    return dict(job_id=jid, allocated_CPUs=1, allocated_GPUs=0, query_argv=argv,
                returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)

def runtime_core():
    need(CORE.is_symlink() and os.readlink(CORE) == "python3.11" and
         CORE.resolve() == CORE_REAL and Path(sys.executable).resolve() == CORE_REAL,
         "Exact conditional core interpreter/link required")
    ancestry(CORE_REAL)
    s = CORE_REAL.lstat()
    need(stat.S_ISREG(s.st_mode) and s.st_size == CORE_BYTES, "Conditional binary shape differs")
    digest = hashlib.sha256(CORE_REAL.read_bytes()).hexdigest()
    need(digest == CORE_SHA, "Conditional binary byte identity differs")
    link = CORE.lstat()
    return dict(scope="CONDITIONAL_INSTALLED_CPU_RUNTIME_NOT_ARCHIVE_SOURCE",
                logical_interpreter=str(CORE), resolved_interpreter=str(CORE_REAL),
                link_target=os.readlink(CORE), link_inode=link.st_ino,
                link_mtime_ns=link.st_mtime_ns, binary_inode=s.st_ino,
                binary_mtime_ns=s.st_mtime_ns, binary_mode=stat.S_IMODE(s.st_mode),
                bytes_as_scalar=s.st_size, sha256_as_scalar=digest,
                included_in_package=False)

def source_rows(directory):
    directory = ancestry(directory)
    need(directory.is_dir() and not (directory.stat().st_mode & 0o222) and
         {p.name for p in directory.iterdir()} == set(FILES), "Exact readonly OWN3 source universe")
    values = [read_ro(directory / name) for name in FILES]
    return [r for r, b, m in values], [m for r, b, m in values]

def write_ro(p, obj):
    p = ancestry(p)
    with p.open("xb") as stream:
        stream.write((json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o444)
    return read_ro(p)[0]

def capture(args, allocation, original, original_before, frozen, frozen_before, runtime, syntax):
    need(D == S / "frozen" / ("report_request_descriptor_capture_v1_" + allocation["job_id"]) / "code",
         "Execute the actual current sealed source snapshot only")
    need(Path(__file__).absolute() == D / "capture.py", "Actual source entry mismatch")
    request = lexical(args.request)
    need(request == REQUEST, "Only the exact root-approved report request is capturable")
    rr, data, request_before = read_ro(request)
    obj = strict_json(data)
    request_shape(obj)
    out = ancestry(S / "runs" / ("report_request_descriptor_capture_" + allocation["job_id"]))
    out.mkdir(exist_ok=False)
    snapshot = write_ro(out / "source_snapshot.json", dict(
        schema="report-request-capture-source-snapshot.v1",
        original_executing_sources=original, frozen_source_files=frozen,
        original_metadata_before=original_before, frozen_metadata_before=frozen_before,
        compile_owned_Python=True, bash_syntax=syntax, allocation=allocation))
    original_after, original_meta = source_rows(P)
    frozen_after, frozen_meta = source_rows(D)
    need(original_after == original and original_meta == original_before and
         frozen_after == frozen and frozen_meta == frozen_before, "Whole OWN3 pre/post source drift")
    need(all((a["bytes"], a["sha256"]) == (b["bytes"], b["sha256"])
             for a, b in zip(original, frozen)), "Original/frozen byte mismatch")
    request_after, after_data, request_meta = read_ro(request)
    need(request_after == rr and after_data == data and request_meta == request_before,
         "Exact request pre/post byte/metadata drift")
    need(runtime_core() == runtime, "Conditional interpreter pre/post drift")
    result = dict(schema="report-request-descriptor-capture.v1", status=STATUS,
        actual_CPU_job_id=allocation["job_id"], allocation=allocation, request=rr,
        owned_executable_source_count=2, owned_source_count=3,
        request_schema=obj["schema"], exact_request_key_count=6,
        receipt_child_fields=["software_acceptance", "common_successor", "root_gpu_cost"],
        receipt_child_validation="PURE_SHAPE_ONLY_NO_CHILD_FILESYSTEM_ACCESS",
        receipt_children_opened_hashed_or_statted=False,
        request_metadata_before=request_before, request_metadata_after=request_meta,
        request_before_after_bytes_equal=True, original_executing_sources=original,
        source_files=frozen, source_snapshot=snapshot,
        original_metadata_before=original_before, original_metadata_after=original_meta,
        frozen_metadata_before=frozen_before, frozen_metadata_after=frozen_meta,
        original_and_frozen_sources_byte_identical=True,
        whole3_source_prepost_PASS=True, compiled_owned_Python=True, bash_syntax_PASS=True,
        conditional_core_runtime=runtime, conditional_runtime_prepost_PASS=True,
        report_build_or_QA_performed=False, science_accepted=False,
        Cost_or_scores_recomputed=False, new_GPU_submission=False,
        Git_changed=False, ACTIVE_changed=False, original_request_mutated=False)
    accepted = write_ro(out / "capture.json", result)
    final_request, final_data, final_meta = read_ro(request)
    need(final_request == rr and final_data == data and final_meta == request_before,
         "Request drift after capture output")
    need(source_rows(P) == (original, original_before) and
         source_rows(D) == (frozen, frozen_before), "Source drift after capture output")
    need(runtime_core() == runtime and read_ro(snapshot["path"])[0] == snapshot,
         "Runtime/source-snapshot drift after capture output")
    print(json.dumps(dict(status=STATUS, capture=accepted, request=rr), ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    allocation = cpu()  # Before any source/request/runtime hash or project-source loading.
    need(D == P and Path(__file__).absolute() == P / "capture.py", "Exact reviewed original source")
    runtime = runtime_core()
    original, before = source_rows(P)
    fd = ancestry(S / "frozen" / ("report_request_descriptor_capture_v1_" + allocation["job_id"]) / "code")
    fd.mkdir(parents=True, exist_ok=False)
    for name, row in zip(FILES, original):
        current, data, meta = read_ro(P / name)
        need(current == row, "Original changed before snapshot")
        target = fd / name
        with target.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
    fd.chmod(0o555)
    fd.parent.chmod(0o555)
    frozen, frozen_before = source_rows(fd)
    need(all((a["bytes"], a["sha256"]) == (b["bytes"], b["sha256"])
             for a, b in zip(original, frozen)), "Exact OWN3 snapshot equality")
    for row in frozen:
        if Path(row["path"]).suffix == ".py":
            compile(read_ro(row["path"])[1], row["path"], "exec", dont_inherit=True)
    proc = subprocess.run(["bash", "-n", str(fd / "capture_cpu.sbatch")],
                          capture_output=True, text=True)
    need(proc.returncode == 0, "Launcher Bash syntax")
    syntax = dict(argv=proc.args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    spec = importlib.util.spec_from_file_location("sealed_report_request_capture_" + allocation["job_id"],
                                                fd / "capture.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    need(Path(module.__file__).absolute() == fd / "capture.py", "Loaded sealed entry differs")
    module.capture(args, allocation, original, before, frozen, frozen_before, runtime, syntax)

if __name__ == "__main__":
    main()

