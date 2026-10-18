#!/usr/bin/env python3
"""Resolve frozen authority paths inside an independently restored tree.

Logical path strings remain exactly the original frozen strings, while every
filesystem operation is resolved exclusively below restore_root. No frozen
plan, script or receipt is rewritten.
"""
import hashlib, importlib.util, json, os
from pathlib import Path
def path_factory(authority_root,restore_root):
    authority=Path(authority_root).absolute();restore=Path(restore_root).absolute()
    class RestoredPath:
        def __init__(self,*parts):
            if len(parts)==1 and isinstance(parts[0],RestoredPath):
                self.logical=parts[0].logical
            else:
                converted=[p.logical if isinstance(p,RestoredPath) else p for p in parts]
                self.logical=Path(*converted)
            if not self.logical.is_absolute():self.logical=restore/self.logical
            # Perform containment and symlink verification before every I/O.
        def physical(self):
            if self.logical.is_relative_to(restore):
                p=self.logical
            else:
                try:
                    rel=self.logical.relative_to(authority);p=restore/rel
                except ValueError:raise PermissionError("Restore cannot read original/outside evidence: "+str(self.logical))
            if p.resolve().is_relative_to(restore.resolve()) is False:
                raise PermissionError("Restore symlink escapes evidence tree")
            return p
        def __str__(self):return str(self.logical)
        def __repr__(self):return "RestoredPath("+repr(str(self.logical))+")"
        def __fspath__(self):return str(self.physical())
        def __truediv__(self,other):return RestoredPath(self.logical/str(other))
        def __eq__(self,other):
            try:return self.logical==RestoredPath(other).logical
            except (TypeError,ValueError):return False
        def __hash__(self):return hash(self.logical)
        @property
        def parent(self):return RestoredPath(self.logical.parent)
        @property
        def name(self):return self.logical.name
        @property
        def suffix(self):return self.logical.suffix
        @property
        def parts(self):return self.logical.parts
        def resolve(self,*a,**k):
            self.physical()
            return RestoredPath(self.logical.absolute())
        def relative_to(self,*args):
            return self.logical.relative_to(*[p.logical if isinstance(p,RestoredPath) else p for p in args])
        def with_name(self,name):return RestoredPath(self.logical.with_name(name))
        def with_suffix(self,suffix):return RestoredPath(self.logical.with_suffix(suffix))
        def open(self,*a,**k):return self.physical().open(*a,**k)
        def read_text(self,*a,**k):return self.physical().read_text(*a,**k)
        def read_bytes(self):return self.physical().read_bytes()
        def write_text(self,*a,**k):return self.physical().write_text(*a,**k)
        def exists(self):return self.physical().exists()
        def is_file(self):return self.physical().is_file()
        def stat(self):return self.physical().stat()
        def mkdir(self,*a,**k):return self.physical().mkdir(*a,**k)
        def glob(self,pattern):
            for p in self.physical().glob(pattern):
                rel=p.relative_to(restore)
                yield RestoredPath(authority/rel) if self.logical.is_relative_to(authority) else RestoredPath(p)
    return RestoredPath
def load_budget_auditor(source_receipt,authority_root,restore_root):
    P=path_factory(authority_root,restore_root);source=P(source_receipt["path"]).physical()
    b=source.read_bytes()
    if hashlib.sha256(b).hexdigest()!=source_receipt["sha256"]:raise ValueError("Independent budget auditor source hash mismatch")
    spec=importlib.util.spec_from_file_location("independent_restored_budget_auditor",source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.Path=P
    return module
def audit_budget(config,authority_root,restore_root):
    """No production orchestrator import, scheduler query or original evidence read."""
    module=load_budget_auditor(config["auditor_source"],authority_root,restore_root)
    result=module.audit(config["plan"],config["run_receipts"],config["sacct"],
                        config["producer_accounting"],config["producer_cohort"])
    if not result["complete_generation_matrix"] or result["expected_tasks"]!=28:
        raise ValueError("Independent restore requires complete 28-task matrix")
    result["restore_root"]=str(restore_root)
    result["frozen_bytes_changed"]=False
    result["evidence_reads"]="RESTORED_TREE_ONLY"
    return result

