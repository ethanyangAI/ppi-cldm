#!/usr/bin/env python3
"""Only six exact retained BBF13226 output edges; never a general relative resolver."""
import hashlib,json,re
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/23_common_review/bbf_diagnostics/scientific_review"
PARENT={"path":str(S/"runs/review_13226/manifest.json"),"bytes":4108,"sha256":"d2d9093ee2dbe7f14a395457275ccfdd72b1e14221f50a2d18a1c01cf1e4af0f"}
OUTPUTS=(
 ("metrics.json",54610,"069fd75a563a0920b68146798ebf37841cf7e04c33e0ee258ca5f1aced0950d1"),
 ("model_crosschecks.json",123769,"97010f22373eea440f54b5b7cb44091a9bdb2ac3b44e420a5edccf3ffb415a2c"),
 ("cases.tsv",4153,"99467a182086b1dd1fba1ea65ac41cc6d32b9feb0d0170084fe2c12d46793677"),
 ("paired_changes.tsv",818,"1abfb387468aded6165aa07073e77d395b27dc7a7b7473cac46b0e6f0b11757e"),
 ("original_labels.tsv",2468,"f4c1c2aef76133b38ce2b15e525337a4963a7480ecb30c042705b85c68d51b18"),
 ("REPORT_ZH.md",5869,"fd7c05de59549d477d68b7961173030ebdf89256c9f718a79e07567b537aa2af"),
)
def need(value,message):
 if not value:raise ValueError(message)
def pinned_rows():
 return [{"path":"runs/review_13226/"+name,"bytes":n,"sha256":sha}for name,n,sha in OUTPUTS]
def byte_verify(path,receipt):
 p=Path(path)
 need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink(),"Context bytes outside exact authority or symlink")
 need(p.is_file(),"Context bytes absent")
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 need(p.stat().st_size==receipt["bytes"]and h==receipt["sha256"],"Exact inherited context bytes drift")
 return p
class ExactRelativeContext:
 def __init__(self,verify=byte_verify,reader=None):
  self.verify=verify
  self.reader=reader or(lambda p:json.loads(Path(p).read_text()))
  self.applied={}
 def parent_readback(self):
  self.verify(PARENT["path"],PARENT)
  obj=self.reader(PARENT["path"])
  need(obj.get("job_id")=="13226"and obj.get("status")=="BBF110_INDEPENDENT_DEVELOPMENT_DIAGNOSIS_CONTENT_ACCEPTED","Pinned intermediate manifest role differs")
  need(obj.get("outputs")==pinned_rows(),"Pinned intermediate outputs differ")
  return obj
 def normalize(self,receipt,parent,trail):
  if Path(receipt["path"]).is_absolute():return receipt,None
  # Permission is edge-specific and is checked even after other edges used this node.
  need(parent==PARENT["path"],"Unknown relative receipt parent")
  fields=tuple(trail)
  need(len(fields)==2 and fields[0]=="outputs"and fields[1]in {str(i)for i in range(6)},"Unknown relative receipt field")
  i=int(fields[1]);expected=pinned_rows()[i]
  need(receipt==expected,"Exact relative receipt identity differs")
  self.parent_readback()
  canonical={"path":str(S/expected["path"]),"bytes":expected["bytes"],"sha256":expected["sha256"]}
  self.verify(canonical["path"],canonical)
  row={"source_parent":PARENT["path"],"source_field":list(fields),"original_relative_path":expected["path"],"expected_bytes":expected["bytes"],"expected_sha256":expected["sha256"],"canonical_receipt":canonical}
  self.applied[i]=row
  return canonical,row
 def complete_mapping(self):
  for i,r in enumerate(pinned_rows()):self.normalize(r,PARENT["path"],("outputs",str(i)))
  need(set(self.applied)==set(range(6)),"All six inherited outputs required")
  return {"schema":"exact-context-relative-receipts.v1","status":"EXACT_BBF13226_SIX_RELATIVE_OUTPUTS_CPU_VERIFIED_ORIGINAL_JSON_UNCHANGED","parent_manifest":dict(PARENT),"declared_relative_root":str(S),"entries":[self.applied[i]for i in range(6)],"original_json_unchanged":True,"parent_and_all_six_child_bytes_verified":True,"scope":"SUPERSEDED_BBF13226_INTERMEDIATE_OUTPUT_PATH_SEMANTICS_ONLY","scientific_settings_changed":False,"models_recomputed":False}

