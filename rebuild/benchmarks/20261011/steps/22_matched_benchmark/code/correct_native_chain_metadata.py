#!/usr/bin/env python3
"""Correct RFdiffusion native chain labels without regenerating target geometry."""
import argparse,copy,hashlib,json,os
from pathlib import Path
def receipt(p):
 p=Path(p).resolve(); return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def checked(r):
 p=Path(r["path"])
 if receipt(p)!=r: raise ValueError("Receipt mismatch: "+str(p))
 return p
def save(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x") as f: json.dump(obj,f,indent=2,sort_keys=True);f.write("\n")
 return receipt(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--previous",required=True);ap.add_argument("--native-proof",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args(); old_path=Path(a.previous).resolve();old=json.loads(old_path.read_text());proof=receipt(a.native_proof)
 # Only a content-accepted seven-target bridge may receive this metadata correction.
 if old["status"]!="ALL_TARGET_INPUTS_ACCEPTED" or old["pending"] or len(old["prepared"])!=7:raise ValueError("Seven complete previous inputs required")
 out=Path(a.out).resolve()
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True)
 prepared=[];audits=[]
 for entry in old["prepared"]:
  path=checked(entry["input_manifest"]);prior=json.loads(path.read_text())
  if prior["input_target_chain"]!="A" or prior["rfd_contig"]!=f'A1-{prior["residue_count"]}/0 65-65':raise ValueError("Unsupported original chain or contig")
  if (prior["rfd_output_target_chain"],prior["rfd_binder_chain"])!=("B","A"):raise ValueError("Expected historical metadata only")
  # Recursively reverify every embedded receipt. The old bridge remains unchanged.
  def verify_nested(value):
   if isinstance(value,dict):
    if {"path","bytes","sha256"}<=value.keys():checked({k:value[k] for k in ("path","bytes","sha256")})
    for v in value.values():verify_nested(v)
   elif isinstance(value,list):
    for v in value:verify_nested(v)
  verify_nested(prior)
  new=copy.deepcopy(prior);new["rfd_output_target_chain"]="A";new["rfd_binder_chain"]="B"
  new["native_chain_metadata_correction"]={"previous_manifest":entry["input_manifest"],"official_output_proof":proof,
    "source_entry":receipt(__file__),"reason":"Official Sampler.sample_init overwrites ContigMap chain_idx, preserves receptor input chain A and assigns de novo binder chain B.",
    "target_coordinates_regenerated":False,"target_sequence_changed":False,"hotspots_changed":False,"reference_maps_changed":False,
    "actual_fixed_target_backbone_reconstruction":"Native all-atom reconstruction may cause small target coordinate changes; identities and mapping are checked and displacement remains diagnostic."}
  check=copy.deepcopy(new);check.pop("native_chain_metadata_correction");check["rfd_output_target_chain"]="B";check["rfd_binder_chain"]="A"
  if check!=prior:raise ValueError("Unexpected non-chain field change")
  mr=save(out/entry["target_id"]/"input_manifest.json",new)
  e=copy.deepcopy(entry);e["input_manifest"]=mr;prepared.append(e)
  audits.append({"target_id":entry["target_id"],"previous_manifest":entry["input_manifest"],"new_manifest":mr,
    "all_other_original_fields_identical":True,"target_pdb":prior["target_pdb"],"geometry_regenerated":False})
 result={"schema":"benchmark_input_bridge.v1","status":"ALL_TARGET_INPUTS_ACCEPTED","prepared":prepared,"pending":[],
  "inventory_receipt":old["inventory_receipt"],"previous_bridge":receipt(old_path),"source_entry":receipt(__file__),
  "slurm_job_id":os.environ.get("SLURM_JOB_ID"),"native_chain_correction_proof":proof,"metadata_audit":audits}
 save(out/"prepared_inputs.json",result);save(out/"metadata_acceptance.json",{
  "status":"ALL7_CHAIN_METADATA_CORRECTED_OTHER_ORIGINAL_FIELDS_BYTE_EQUIVALENT","prepared_bridge":receipt(out/"prepared_inputs.json"),
  "gpu_tres":0,"target_coordinate_regeneration":False,"audits":audits,"official_output_proof":proof})
 print(json.dumps({"status":result["status"],"path":str(out/"prepared_inputs.json")}))
if __name__=="__main__":main()

