#!/usr/bin/env python3
"""Exact (logical path, SHA) aliases; unavailable history never becomes PASS."""
import hashlib,json,os,shutil
from pathlib import Path
class HistoricalUnresolvedProvenance(ValueError):pass
class AmbiguousReceiptPath(ValueError):pass
def checksum(path):
    p=Path(path);h=hashlib.sha256();n=0
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
    return {"path":str(p),"sha256":h.hexdigest(),"bytes":n}
class ReceiptResolver:
    def __init__(self,authority_root,restore_root=None,index=None):
        self.authority=Path(authority_root).absolute()
        self.restore=Path(restore_root).absolute() if restore_root else None
        self.entries={};self.unresolved={}
        obj=index or {}
        if isinstance(obj,(str,Path)):obj=json.loads(Path(obj).read_text())
        for entry in obj.get("aliases",[]):
            original=entry["original"];archived=entry["archived"];key=(original["path"],original["sha256"])
            if original["sha256"]!=archived["sha256"] or original.get("bytes",archived["bytes"])!=archived["bytes"]:
                raise ValueError("Alias changes frozen content")
            if key in self.entries and self.entries[key]["archived"]!=archived:raise ValueError("Duplicate conflicting alias")
            if entry["status"]!="READONLY_BYTE_IDENTICAL_ALIAS":raise ValueError("Alias is not accepted")
            self.entries[key]=entry
        for entry in obj.get("historical_unresolved",[]):
            if entry["status"]!="HISTORICAL_UNRESOLVED_PROVENANCE":raise ValueError("Historical unknown typed incorrectly")
            r=entry["original"];self.unresolved[(r["path"],r["sha256"])]=entry
    def map_path(self,logical):
        p=Path(logical)
        if not p.is_absolute():raise ValueError("Only absolute authority paths allowed")
        if self.restore is None:
            relative=p.relative_to(self.authority);physical=self.authority/relative
        elif p.is_relative_to(self.restore):physical=p
        else:physical=self.restore/p.relative_to(self.authority)
        boundary=self.restore or self.authority
        if not physical.resolve().is_relative_to(boundary.resolve()) or physical.is_symlink():
            raise PermissionError("Alias/restore escapes boundary")
        return physical
    def resolve(self,logical,expected_sha=None,scope="CURRENT"):
        if expected_sha is not None:
            key=(str(logical),expected_sha)
            if key in self.unresolved:
                if scope=="HISTORICAL":return None
                raise HistoricalUnresolvedProvenance("Unrecoverable historical bytes cannot satisfy current proof: "+str(logical))
            if key in self.entries:
                p=self.map_path(self.entries[key]["archived"]["path"])
                r=checksum(p);a=self.entries[key]["archived"]
                if r["sha256"]!=a["sha256"] or r["bytes"]!=a["bytes"]:raise ValueError("Alias bytes changed")
                if p.stat().st_mode & 0o222:raise ValueError("Alias archive must be readonly")
                return p
            p=self.map_path(logical)
            r=checksum(p)
            if r["sha256"]!=expected_sha:raise ValueError("Exact receipt unavailable; no nearest-version fallback")
            return p
        keys=[k for k in self.entries if k[0]==str(logical)]
        if len(keys)>1:raise AmbiguousReceiptPath("SHA required for multiple historical versions")
        p=self.map_path(logical)
        if p.exists():return p
        if keys:raise AmbiguousReceiptPath("Alias resolution requires the expected SHA")
        return p
    def verify(self,r,scope="CURRENT"):
        p=self.resolve(r["path"],r["sha256"],scope)
        if p is None:return None
        a=checksum(p)
        if "bytes" in r and a["bytes"]!=r["bytes"]:raise ValueError("Receipt size mismatch")
        return p
def archive_alias(original,archived_source,archive_dir,role):
    actual=checksum(archived_source)
    if actual["sha256"]!=original["sha256"] or actual["bytes"]!=original.get("bytes",actual["bytes"]):
        raise ValueError("Historical source snapshot does not match requested bytes")
    archive_dir=Path(archive_dir);archive_dir.mkdir(parents=True,exist_ok=True)
    dest=archive_dir/(original["sha256"]+"_"+Path(original["path"]).name)
    if dest.exists():
        if checksum(dest)["sha256"]!=original["sha256"]:raise ValueError("Alias destination collision")
    else:shutil.copyfile(archived_source,dest)
    dest.chmod(0o444)
    return {"original":original,"archived":checksum(dest),"status":"READONLY_BYTE_IDENTICAL_ALIAS","role":role,"source_snapshot":checksum(archived_source)}
def aliases_from_closure(closure,archive_dir):
    result=[]
    for entry in closure["resources"]:
        if entry.get("scope")=="RECOMPUTE_DEPENDENCY" or not entry.get("copied"):continue
        result.append(archive_alias(entry["original"],entry["copy"]["path"],archive_dir,
                                   "HASH_IDENTICAL_SCIENTIFIC_RESOURCE_ALIAS"))
    return result

