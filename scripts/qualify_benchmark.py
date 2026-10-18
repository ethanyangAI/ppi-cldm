"""Qualification inventory. No sequence design; preserve every exclusion and network failure."""
import argparse,itertools,json,re,shutil
from pathlib import Path
import numpy as np
from ppiblocker.common import Run,record_file,atomic_json,EvidenceError
from ppiblocker.identity import Repository,resolve_protein,search_experimental_pair
from ppiblocker.structure import read_structure,match_chain,interface
from ppiblocker.pipeline import validate_entity_species

def qualify_case(row, repo):
    cid,a,b,family,geom,background,tier,pdb,role,obstacle,priority,split,_,url=row
    result=dict(case_id=cid,target=a,partner=b,family=family,tier=tier,background=background,
                priority=priority,split="DEVELOPMENT" if cid=="P01" else "UNASSIGNED",
                status="REVIEW_REQUIRED",proteins=[],entries=[],structural_candidates=[],errors=[])
    if cid.startswith("Q"):
        result.update(status="NEGATIVE_IDENTITY_SENTINEL",reference_pdb=pdb,
                      expected="Do not accept as human binary complex")
        return result
    curated={"P20":{b:"P62805"},"P21":{b:"P68431"},"P22":{b:"P68431"},
             "P25":{"PAK1":"Q13153"},"P39":{"IL7RA":"P16871"}}
    for gene in (a,b):
        accession=curated.get(cid,{}).get(gene)
        if accession:
            try:
                protein=resolve_protein(dict(uniprot=accession,taxon=9606),repo)
                result["proteins"].append(protein)
                result.setdefault("identity_adjudication",[]).append(dict(input=gene,accession=accession,
                    source=f"https://rest.uniprot.org/uniprotkb/{accession}.json",
                    scope="H4 canonical / H3.1 for histone cases; primary PAK1; IL7R alpha chain"))
            except Exception as e:
                result["errors"].append(dict(code=getattr(e,"code","IDENTITY_ERROR"),message=str(e)))
                return result
            continue
        if not re.fullmatch("[A-Z0-9]+",gene):
            result["errors"].append(dict(code="EXACT_GENE_OR_ISOFORM_REQUIRED",gene=gene))
            return result
        try: result["proteins"].append(resolve_protein(dict(gene=gene,taxon=9606),repo))
        except Exception as e:
            result["errors"].append(dict(code=getattr(e,"code","NETWORK_OR_PARSE_ERROR"),gene=gene,message=str(e)))
            return result
    proteins=result["proteins"]
    try:
        entries=search_experimental_pair(proteins,repo,limit=12 if tier!="C2" else 2)
    except Exception as e:
        entries=[];result["errors"].append(dict(code=getattr(e,"code","SEARCH_ERROR"),message=str(e)))
    if cid=="P04":pdb="2XA0"
    if re.fullmatch("[0-9][A-Za-z0-9]{3}",pdb): entries=[pdb]+[x for x in entries if x!=pdb]
    result["entries"]=entries
    if tier=="C2":
        # No attempt to reduce physiological context to two chains.
        result.update(status="CONTEXT_EXTENSION_REQUIRED",exclusion=background)
        return result
    for entry_id in entries:
        try:
            entry=repo.entry(entry_id)
            assemblies=entry.get("rcsb_entry_container_identifiers",{}).get("assembly_ids",[])
            for assembly in assemblies[:4]:
                try:
                    raw=repo.get(f"https://files.rcsb.org/download/{entry_id}-assembly{assembly}.cif",binary=True)
                    chains,context=read_structure(raw)
                    matches=[[match_chain(c,p,.95,.001) for c in chains] for p in proteins]
                    for i,j in itertools.permutations(range(len(chains)),2):
                        if not (matches[0][i]["accepted"] and matches[1][j]["accepted"]):continue
                        contact=interface(chains[i],chains[j],5)
                        if min(len(contact["target_residues"]),len(contact["partner_residues"]))<3:continue
                        pair=dict(target_match=matches[0][i],partner_match=matches[1][j])
                        reasons=[]
                        try: entity=validate_entity_species(raw,entry_id,proteins,pair,repo)
                        except EvidenceError as e:
                            entity=None;reasons.append(e.code)
                        if len(chains)!=2:reasons.append("EXTRA_PROTEIN_CHAINS")
                        if context:reasons.append("NONPROTEIN_CONTEXT")
                        for chain in (chains[i],):
                            if any(not {"N","CA","C","O"}<=set(x[0] for x in atoms) for atoms in chain["atoms"]):
                                reasons.append("INCOMPLETE_BACKBONE")
                            distances=np.linalg.norm(np.diff(np.array([r["ca"] for r in chain["residues"]]),axis=0),axis=1)
                            if np.any((distances>4.5)|(distances<2.5)):reasons.append("BACKBONE_GAP_OR_GEOMETRY")
                        bounds=[]
                        for m in (matches[0][i],matches[1][j]):
                            positions=[r["canonical_position"] for r in m["residue_mapping"]]
                            bounds.append([min(positions),max(positions)])
                            if len(set(positions))/(max(positions)-min(positions)+1)<.8:
                                reasons.append("CONSTRUCT_COVERAGE_BELOW_PIPELINE_GATE")
                        result["structural_candidates"].append(dict(pdb=entry_id,assembly=assembly,
                            chains=[chains[i]["id"],chains[j]["id"]],construct_bounds=bounds,
                            sequences=[chains[i]["sequence"],chains[j]["sequence"]],
                            source=record_file(raw),identity=entity,context=context,protein_chain_count=len(chains),
                            contact_pairs=len(contact["residue_pairs"]),reasons=sorted(set(reasons)),
                            resolution=entry.get("rcsb_entry_info",{}).get("resolution_combined"),
                            disposition="STRUCTURAL_GATE_PASS_CONTEXT_REVIEW_PENDING" if not reasons else "EXCLUDED_CURRENT_GATE"))
                except Exception as e:
                    result["errors"].append(dict(pdb=entry_id,assembly=assembly,code=getattr(e,"code","ENTRY_ERROR"),message=str(e)))
        except Exception as e:result["errors"].append(dict(pdb=entry_id,code=getattr(e,"code","ENTRY_ERROR"),message=str(e)))
        # Enough for qualification once a structurally acceptable reference is found; still pending context review.
        if any(not c["reasons"] for c in result["structural_candidates"]):break
    good=[c for c in result["structural_candidates"] if not c["reasons"]]
    result["status"]="STRUCTURAL_GATE_PASS_CONTEXT_REVIEW_PENDING" if good else "NO_CURRENT_GATE_REFERENCE"
    if not entries:result["status"]="RETRIEVAL_UNRESOLVED" if result["errors"] else "NO_REFERENCE_IN_BOUNDED_SEARCH"
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("root");p.add_argument("matrix");args=p.parse_args()
    run=Run(args.root,"06_benchmark_qualification",[record_file(args.matrix)])
    snapshot=run.path/"qc/qualification_source.py"
    shutil.copy2(__file__,snapshot);run.output("qualification_source",snapshot)
    repo=Repository(Path(args.root)/"cache/identity_structure")
    matrix=json.loads(Path(args.matrix).read_text())
    rows=next(s["rows"] for s in matrix["sheets"] if s["name"]=="靶标池")
    results=[]
    for row in rows:
        print("START",row[0],row[1:3],flush=True)
        try:r=qualify_case(row,repo)
        except Exception as e:r=dict(case_id=row[0],status="QUALIFICATION_ERROR",error=str(e))
        results.append(r)
        atomic_json(run.path/"outputs/qualification.json",dict(cases=results,planned=len(rows),complete=len(results)==len(rows)))
        print("DONE",r["case_id"],r["status"],len(r.get("structural_candidates",[])),flush=True)
    atomic_json(run.path/"outputs/retrieval_receipts.json",repo.receipts)
    run.output("qualification",run.path/"outputs/qualification.json")
    run.output("receipts",run.path/"outputs/retrieval_receipts.json")
    print(run.finish("QUALIFICATION_INVENTORY_COMPLETE","metadata_and_structure_audit",dict(case_count=len(results),pilot_frozen=False)),flush=True)
if __name__=="__main__":main()

