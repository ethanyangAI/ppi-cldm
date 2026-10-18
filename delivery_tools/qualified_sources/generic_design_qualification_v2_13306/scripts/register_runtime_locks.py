"""Explicit immutable runtime baseline registration; never called by inference."""
import argparse
import hashlib
import json
import os
import tarfile
import uuid
from pathlib import Path
from ppiblocker.common import collect_runtime,read_json,digest,require

COMPONENTS=("core","rfd","boltz")

def verify_boltz_archive(root):
    archive=root/"assets/boltz/mols.tar"
    receipt=read_json(archive.with_suffix(".tar.receipt.json"))
    require(digest(archive)==receipt["sha256"],"MOLECULE_ARCHIVE_CORRUPT",str(archive))
    seen=set()
    with tarfile.open(archive) as tar:
        for member in tar:
            if not member.isfile():continue
            path=(archive.parent/member.name).resolve()
            require(path.is_relative_to((archive.parent/"mols").resolve()),"UNEXPECTED_ARCHIVE_PATH",member.name)
            h=hashlib.sha256()
            with tar.extractfile(member) as stream:
                for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
            require(path.is_file() and digest(path)==h.hexdigest(),"MOLECULE_PAYLOAD_MISMATCH",str(path))
            seen.add(path)
    require(seen=={p.resolve() for p in (archive.parent/"mols").rglob("*") if p.is_file()},"MOLECULE_PAYLOAD_MISMATCH","Unexpected molecule payload files")
    print("Official molecule archive matches extracted files:",len(seen),flush=True)

def write_new_lock(path,state):
    """Publish complete JSON atomically without overwriting an existing baseline."""
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+"."+uuid.uuid4().hex+".tmp")
    try:
        with tmp.open("x") as handle:
            json.dump(state,handle,indent=2,allow_nan=False)
            handle.write("\n");handle.flush();os.fsync(handle.fileno())
        try:os.link(tmp,path)
        except FileExistsError:
            require(False,"LOCK_ALREADY_EXISTS","Refusing to overwrite reviewed runtime baseline: "+str(path))
    finally:
        if tmp.exists():tmp.unlink()

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",required=True)
    parser.add_argument("--initialize-reviewed",action="store_true",required=True)
    parser.add_argument("--component",action="append",choices=COMPONENTS,
                        help="Register only selected missing component(s); repeatable. Default: all three.")
    args=parser.parse_args(argv);root=Path(args.root).resolve()
    components=list(dict.fromkeys(args.component or COMPONENTS))
    locks=[root/"source/environment"/f"runtime-lock-{c}.json" for c in components]
    require(not any(p.exists() for p in locks),"LOCK_ALREADY_EXISTS",
            "Refusing to overwrite reviewed selected runtime baseline(s)")
    if "boltz" in components:verify_boltz_archive(root)
    states=[collect_runtime(root,c) for c in components]
    for path,state in zip(locks,states):
        write_new_lock(path,state);print("Registered",path,flush=True)
    return 0

if __name__=="__main__":raise SystemExit(main())
