#!/usr/bin/env python3
"""Read-only CPU audit of recursive file provenance and target input identity."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
AA=set("ACDEFGHIKLMNPQRSTVWY")
RES=dict(zip(["ALA","CYS","ASP","GLU","PHE","GLY","HIS","ILE","LYS","LEU","MET","ASN","PRO","GLN","ARG","SER","THR","VAL","TRP","TYR"],"ACDEFGHIKLMNPQRSTVWY"))
def rec(path):
 p=Path(path);h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(4194304),b""):h.update(b)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def audit(paths):
 references,errors,targets,seen,repairs={},[],[],set(),[]
 def visit(value,location):
  if isinstance(value,dict):
   if {"path","bytes","sha256"}<=set(value):
    key=(value["path"],value["sha256"])
    if key in references:return
    try:
     actual=rec(value["path"]);status="VERIFIED_RECEIPT" if all(actual[k]==value[k] for k in ["bytes","sha256"]) else "RECEIPT_BYTES_OR_SHA_MISMATCH"
    except Exception as exc:actual=None;status="UNAVAILABLE_RECEIPT";errors.append({"location":location,"error":repr(exc)})
    references[key]={"location":location,"claimed":value,"actual":actual,"status":status}
    if status!="VERIFIED_RECEIPT":errors.append({"location":location,"status":status,"path":value["path"]})
    if actual and Path(value["path"]).suffix==".json":
     read_document(value["path"],location+"->"+value["path"])
    return

   if value.get("schema")=="target_only_coordinate_repair.v1":
    checks=[{"name":"repair_accepted","pass":value.get("status")=="TARGET_ONLY_MINIMAL_GAP_REPAIR_ACCEPTED"},
      {"name":"Reference_CPU_platform","pass":value.get("platform")=="Reference" and value.get("relaxation",{}).get("platform")=="Reference"},
      {"name":"no_partner_coordinates","pass":value.get("no_partner_coordinates") is True},
      {"name":"fixed_observed_heavy_gate","pass":value.get("relaxation",{}).get("all_observed_heavy_atoms_fixed") is True and value.get("observed_max_displacement_angstrom")==0},
      {"name":"only_missing_64_65_variable","pass":value.get("missing_label_seq_ids")==[64,65] and value.get("relaxation",{}).get("variable_heavy_residues")==[64,65]},
      {"name":"frozen_seed_and_forcefield","pass":value.get("seed")==21101 and value.get("relaxation",{}).get("forcefield")=="amber14-all.xml"},
      {"name":"no_reported_severe_clashes","pass":value.get("severe_non_neighbor_clashes")==[]},
      {"name":"peptide_gap_closure","pass":len(value.get("peptide_closure",[]))==3 and all(1.1<=x["C_N_angstrom"]<=1.6 for x in value.get("peptide_closure",[]))}]
    def heavy_atoms(path):
     atoms={}
     for line in Path(path).read_text().splitlines():
      if not line.startswith("ATOM"):continue
      element=line[76:78].strip();name=line[12:16].strip()
      if element in ["H","D"] or (not element and name.lstrip("0123456789").startswith(("H","D"))):continue
      key=(line[21],int(line[22:26]),line[26],name,line[16])
      atoms[key]=tuple(float(line[a:b]) for a,b in [(30,38),(38,46),(46,54)])
     return atoms
    try:
     original_compact=heavy_atoms(value["source_structure"]["path"]);repaired=heavy_atoms(value["target_pdb"]["path"])
     identity=json.loads(Path(value["identity_receipt"]["path"]).read_text())
     source_to_label={row["normalized_index"]:row["label_seq_id"] for row in identity["target_context"]["mapping"]}
     original={(key[0],source_to_label[key[1]],key[2],key[3],key[4]):xyz for key,xyz in original_compact.items()}
     missing=[key for key in original if key not in repaired]
     displacement=max((sum((original[key][i]-repaired[key][i])**2 for i in range(3))**.5 for key in original if key in repaired),default=None)
     checks.append({"name":"independently_recomputed_all_observed_heavy_unchanged","pass":bool(original) and not missing and displacement==0,
                    "n_original_heavy":len(original),"missing_original_atoms":len(missing),"max_displacement_angstrom":displacement})
    except Exception as exc:checks.append({"name":"independent_observed_atom_preservation","pass":False,"error":repr(exc)})
    repairs.append({"source_document":location,"checks":checks,"claimed_method":value.get("method")})
    if any(not x["pass"] for x in checks):errors.append({"source_document":location,"status":"REPAIR_GEOMETRY_OR_FIXED_ATOM_GATE_UNRESOLVED"})

   if value.get("schema")=="prepared_benchmark_target.v1":
    checks=[];seq=value.get("target_sequence","");n=value.get("residue_count")
    checks.append({"name":"canonical_sequence_length","pass":bool(seq) and set(seq)<=AA and len(seq)==n})
    checks.append({"name":"binder_length_65","pass":value.get("binder_length")==65})
    hotspots=value.get("hotspots",[])
    checks.append({"name":"hotspot_indices_in_target","pass":bool(hotspots) and all(type(x)is int and 1<=x<=n for x in hotspots)})
    mapping=value.get("design_to_reference_indices",{})
    modeled_without_reference=[]
    if value.get("repair_receipt"):
     repair_meta=json.loads(Path(value["repair_receipt"]["path"]).read_text())
     modeled_without_reference=repair_meta.get("missing_label_seq_ids",[])
    expected_mapped=set(range(1,n+1))-set(modeled_without_reference)
    checks.append({"name":"observed_target_reference_mapping","pass":set(map(int,mapping))==expected_mapped and len(set(mapping.values()))==len(mapping),
                   "n_observed_mapped":len(mapping),"n_modeled_without_reference":len(modeled_without_reference),
                   "modeled_without_reference_positions":modeled_without_reference})
    pdb_path=value.get("target_pdb",{}).get("path")
    try:
     residues={}
     for line in Path(pdb_path).read_text().splitlines():
      if line.startswith("ATOM") and line[12:16].strip()=="CA":
       key=(line[21],int(line[22:26]),line[26])
       if key in residues:continue
       residues[key]=RES.get(line[17:20].strip(),"?")
     chains=sorted({k[0] for k in residues})
     extracted="".join(residues[k] for k in sorted(residues))
     checks.append({"name":"input_single_target_chain","pass":chains==[value.get("input_target_chain")]})
     checks.append({"name":"pdb_CA_sequence_identity","pass":extracted==seq})
     checks.append({"name":"contiguous_design_target_numbering","pass":[k[1] for k in sorted(residues)]==list(range(1,n+1))})
    except Exception as exc:checks.append({"name":"pdb_target_identity","pass":False,"error":repr(exc)})
    targets.append({"target_id":value["target_id"],"analysis_role":value["analysis_role"],"family":value.get("family"),
      "scientific_scope":value.get("scientific_scope"),"checks":checks,
      "rfd_contig":value.get("rfd_contig"),"rfd_output_target_chain":value.get("rfd_output_target_chain"),
      "rfd_binder_chain":value.get("rfd_binder_chain"),
      "generation_output_chain_acceptance":"REQUIRES_PILOT_OUTPUT_PDB_IDENTITY_RECEIPT",
      "source_document":location})
    if any(not x["pass"] for x in checks):errors.append({"target_id":value["target_id"],"status":"TARGET_INPUT_IDENTITY_UNRESOLVED"})
   for k,v in value.items():visit(v,location+"/"+str(k))
  elif isinstance(value,list):
   for i,v in enumerate(value):visit(v,location+"/"+str(i))
 def read_document(path,location):
  key=str(Path(path).resolve())
  if key in seen:return
  seen.add(key)
  try:visit(json.loads(Path(path).read_text()),location)
  except Exception as exc:errors.append({"location":location,"error":repr(exc)})
 for path in paths:read_document(path,path)
 return {"schema":"paired-benchmark-provenance-audit.v1",
  "status":"SOURCE_AND_INPUT_PROVENANCE_PASS" if not errors else "SOURCE_OR_INPUT_PROVENANCE_UNRESOLVED",
  "root_documents":[rec(x) for x in paths],"checked_receipts":list(references.values()),
  "receipt_count":len(references),"targets":targets,"repairs":repairs,"errors":errors,
  "scope":"Recursive source/file receipts and exact input coordinate-sequence identity only; no model design or scientific outcomes"}
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--root-record",action="append",required=True);parser.add_argument("--output",required=True)
 args=parser.parse_args();jid=os.environ.get("SLURM_JOB_ID")
 if not jid:raise RuntimeError("Slurm CPU required")
 scheduler=subprocess.run(["scontrol","show","job",jid,"-o"],check=True,capture_output=True,text=True).stdout
 tres=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",scheduler)[1]
 if any(int(x)>0 for x in re.findall(r"(?:^|,)gres/gpu(?::[^,=]+)?=(\d+)",tres)):raise RuntimeError("Pure CPU audit allocation contains GPU")
 report=audit(args.root_record);report.update(slurm_job_id=jid,allocated_tres=tres,auditor=rec(__file__))
 out=Path(args.output)
 if out.exists():raise FileExistsError(out)
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("x")as f:json.dump(report,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
 print(json.dumps({"status":report["status"],"output":rec(out),"receipt_count":report["receipt_count"],"target_count":len(report["targets"]),"errors":report["errors"]},indent=2))
if __name__=="__main__":main()

