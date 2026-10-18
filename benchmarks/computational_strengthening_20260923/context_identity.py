import requests,shutil
from util import *
run=Run(R,"91_strengthening_context_identity",[record_file(SETUP)]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 _,m=one("82_strengthening_extensions","EXTENSION_INPUTS_READY");plan=read_json(verify_file(m["outputs"]["plan"]));rows=[]
 for pdb in ("2FLU","1X2R","2DYH","3WN7","4CH9","2VPJ"):
  entry=read_json(verify_file(plan["fetches"][pdb+"_entry.json"]["file"]))
  for entity in entry["rcsb_entry_container_identifiers"]["polymer_entity_ids"]:
   url=f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb}/{entity}";response=requests.get(url,timeout=60);response.raise_for_status();data=response.json()
   path=run.path/"outputs"/f"{pdb}_{entity}.json";atomic_json(path,data)
   rows.append(dict(pdb=pdb,entity=entity,description=data.get("rcsb_polymer_entity",{}).get("pdbx_description"),organisms=data.get("rcsb_entity_source_organism",[]),references=data.get("rcsb_polymer_entity_container_identifiers",{}).get("reference_sequence_identifiers",[]),mutations=data.get("entity_poly",{}).get("rcsb_mutation_count"),source=record_file(path),url=url))
 atomic_json(run.path/"outputs/results.json",rows);run.output("results",run.path/"outputs/results.json")
 print(run.finish("CONTEXT_IDENTITIES_RECORDED","reference_metadata"),flush=True)
except Exception as x:run.fail(x);raise

