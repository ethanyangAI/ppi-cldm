#!/usr/bin/env python3
"""Executing exact mapperV4 fourteen-source dependency bundle; no schema emulation."""
import importlib.util,sys
from pathlib import Path
NAMES=("exact_relative_bbf_context.py","test_exact_relative_bbf_context.py","context_mapper_audit_cpu.py","context_mapper_cpu.sbatch","context_consumer.py","HANDOFF.md","historical_annotation_context.py","test_historical_annotation_context.py","recovered_five_context.py","test_recovered_five_context.py","archive_member_context.py","test_archive_member_context.py","finite_source_context.py","test_finite_source_context.py")
def need(v,message):
 if not v:raise ValueError(message)
def root():return Path(__file__).resolve().parent.parent/"context_mapper_v4"
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def load_bundle():
 d=root();need(d.is_dir()and d.resolve()==d and not(d.stat().st_mode&0o222),"Readonly explicit mapperV4 source dependency required")
 for name in NAMES:
  p=d/name;need(p.is_file()and p.resolve()==p and not(p.stat().st_mode&0o222),"Readonly whole mapper14 dependency required")
 b=module("exact_relative_bbf_context",d/NAMES[0]);h=module("historical_annotation_context",d/"historical_annotation_context.py");f=module("recovered_five_context",d/"recovered_five_context.py");a=module("archive_member_context",d/"archive_member_context.py");s=module("finite_source_context",d/"finite_source_context.py");c=module("context_consumer",d/"context_consumer.py")
 return type("ActualContextBundle",(),dict(b=b,h=h,f=f,a=a,s=s,c=c,directory=d))()
def source_records(rec,verify):
 return [rec(verify(rec(root()/n),True))for n in NAMES]
def executed_mapper_binding(accepted_sources,executing_sources,identity):
 need(len(accepted_sources)==len(executing_sources)==14 and {Path(r["path"]).name for r in accepted_sources}==set(NAMES)and {Path(r["path"]).name for r in executing_sources}==set(NAMES),"Whole actual accepted/executed mapper14 differs")
 by={Path(r["path"]).name:r for r in accepted_sources}
 need(all(identity(r)==identity(by[Path(r["path"]).name])for r in executing_sources),"Executing mapper source differs from actual accepted mapper bytes")
 return dict(accepted_source_files=accepted_sources,executed_source_files=executing_sources,whole14_same_bytes=True)
