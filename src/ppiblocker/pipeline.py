from __future__ import annotations
import json
import shutil
from pathlib import Path
import numpy as np
import yaml
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from .common import *
from .identity import Repository, resolve_protein, search_experimental_pair
from .structure import read_structure, choose_pair, write_pdb, interface, superpose, competition, match_chain
from .backends import boltz_predict, confidence_metrics, confidence_reasons, rfd_mpnn
from .pose_physical_gate import POLICY, physical_pose_reasons, physical_pose_record

def config_read(path):
    return validate_config(yaml.safe_load(Path(path).read_text()))

def validate_config(data):
    require(isinstance(data,dict) and len(data.get("proteins",[]))==2,"INVALID_CONFIG","Exactly two ordered proteins: target, native partner")
    require(data.get("modality","protein_binder")=="protein_binder","UNSUPPORTED_MODALITY","This validated route is for protein binders, not small molecules")
    for name in ("structure","context_review","prediction","refold","design"):
        require(isinstance(data.get(name,{}),dict),"INVALID_CONFIG",f"{name} must be a mapping")
    require("target_msa" not in data.get("prediction",{}),"INVALID_MSA_CONFIG","Use proteins[0/1].msa for native-pair prediction; refold.target_msa for candidate refolding")
    boolean_fields={"structure":["experimental"],
                    "context_review":["native_interaction_supported","soluble_construct","no_required_unmodelled_context"],
                    "prediction":["allow_external_msa","allow_single_sequence"],
                    "refold":["allow_external_msa","allow_single_sequence"]}
    for section,fields in boolean_fields.items():
        for key in fields:
            if key in data.get(section,{}): strict_bool(data[section][key],f"{section}.{key}")
    mode=data.get("structure",{}).get("mode","retrieve")
    require(mode in {"retrieve","predict_only"},"INVALID_STRUCTURE_MODE","Use retrieve or predict_only")
    if mode=="predict_only":
        require(not any(k in data.get("structure",{}) for k in ("pdb","path","assembly","chains","provenance","experimental")),
                "BLIND_STRUCTURE_LEAKAGE","predict_only cannot carry reference coordinates or identity hints")
        require(not any(k in data.get("prediction",{}) for k in ("templates","template","constraints","contacts")),
                "BLIND_STRUCTURE_LEAKAGE","No templates or interface constraints in blind native-pose prediction")
    gates=data.get("gates",{})
    require(isinstance(gates,dict),"INVALID_GATES","gates must be a mapping")
    for key,value in gates.items():
        require(isinstance(value,(int,float)) and not isinstance(value,bool) and np.isfinite(value) and value>=0,
                "INVALID_GATE",f"{key} must be a finite nonnegative number")
        if key in {"min_identity","min_coverage","min_pair_iptm","min_plddt","min_partner_plddt","min_interface_plddt","min_interface_overlap"}:
            require(value<=1,"INVALID_GATE",f"{key} must be between zero and one")
    require(gates.get("min_identity",.95)>=.9 and gates.get("min_coverage",.8)>=.5,
            "UNSAFE_IDENTITY_GATE","Identity must be >=0.9 and construct coverage >=0.5")
    require(gates.get("min_interface_residues",3)>=1 and gates.get("min_partner_residues",3)>=1 and 3<=gates.get("contact_cutoff",5)<=8,
            "INVALID_INTERFACE_GATE","Require physical contact residues and a 3-8 angstrom cutoff")
    for name in ("prediction","refold"):
        settings=data.get(name,{})
        for key in ("samples","recycles","sampling_steps"):
            if key in settings:
                require(isinstance(settings[key],int) and not isinstance(settings[key],bool) and settings[key]>0,
                        "INVALID_CONFIG",f"{name}.{key} must be a positive integer")
    settings=data.get("design",{})
    for key,default in (("backbones",4),("sequences_per_backbone",4),("binder_length",65)):
        value=settings.get(key,default)
        require(type(value) is int and value>0,"INVALID_CONFIG",f"design.{key} must be a positive non-boolean integer")
    require(1<=settings.get("backbones",4)<=1000,"INVALID_DESIGN_COUNT","Backbones must be 1-1000")
    require(30<=settings.get("binder_length",65)<=200,"UNSUPPORTED_BINDER_LENGTH","Supported miniprotein length 30-200")
    temperature=settings.get("temperature",.1)
    valid_temperature=isinstance(temperature,(int,float)) and not isinstance(temperature,bool)
    if valid_temperature:
        try:valid_temperature=bool(np.isfinite(float(temperature))) and temperature>0
        except (OverflowError,ValueError,TypeError):valid_temperature=False
    require(valid_temperature,
            "INVALID_DESIGN_TEMPERATURE","design.temperature must be one finite positive numeric sampling temperature")
    return data

def put(run,name,data):
    path=run.path/"outputs"/(name+".json");atomic_json(path,data);run.output(name,path);return path

def attach_models(run,prefix,models):
    for i,m in enumerate(models):
        for key in ("structure","confidence","pae"): run.output(f"{prefix}_{i}_{key}",m[key]["path"])

def validate_entity_species(path,entry,proteins,pair,repo):
    cif=MMCIF2Dict(str(path))
    mapping=dict(zip(cif["_struct_asym.id"],cif["_struct_asym.entity_id"]))
    evidence=[]
    for key,p in zip(("target_match","partner_match"),proteins):
        entity=mapping.get(pair[key]["chain"])
        require(entity is not None,"ENTITY_MAPPING_MISSING",pair[key]["chain"])
        data=repo.entity(entry,entity)
        taxa={int(x["ncbi_taxonomy_id"]) for x in data.get("rcsb_entity_source_organism",[]) if x.get("ncbi_taxonomy_id")}
        if p.get("taxon"):
            require(int(p["taxon"]) in taxa,"STRUCTURE_SPECIES_MISMATCH",f"{entry} entity {entity}: {taxa}")
        refs=data.get("rcsb_polymer_entity_container_identifiers",{}).get("reference_sequence_identifiers",[])
        accessions={x.get("database_accession") for x in refs if x.get("database_name")=="UniProt"}
        if p.get("uniprot"):
            require(p["uniprot"].split("-")[0] in {str(x).split("-")[0] for x in accessions},
                    "STRUCTURE_ACCESSION_MISMATCH",f"{entry} entity {entity}: {accessions}")
        evidence.append({"entity":entity,"taxa":sorted(taxa),"uniprot_accessions":sorted(accessions)})
    return evidence

def prepare(root,config_path):
    config=config_read(config_path)
    run=Run(root,"01_pose",[record_file(config_path)])
    try:
        runtime_provenance(run,root,["core"])
        pin_config_msas(run,config,Path(config_path).resolve().parent)
        repo=Repository(Path(root)/"cache/identity_structure")
        proteins=[resolve_protein(p,repo) for p in config["proteins"]]
        put(run,"config",config);put(run,"proteins",proteins)
        spec=config.get("structure",{})
        if spec.get("mode")=="predict_only":
            put(run,"retrieval",{"receipts":repo.receipts,"rejected":[],"search_performed":False,
                                "reason":"explicit_blind_prediction","experimental_coordinates_accessed":False})
            return run.finish("NEEDS_PREDICTION","blind_pose_input",
                              {"next_step":"predict","benchmark_track":"sequence_only",
                               "training_leakage_status":"unknown"})
        failed=[];accepted=None
        if spec.get("path"):
            path=Path(spec["path"]).expanduser().resolve()
            require(spec.get("provenance") and spec.get("experimental") is not None,"PROVENANCE_REQUIRED","Local structures require provenance and experimental true/false")
            run.manifest["inputs"].append(record_file(path))
            chains,context=read_structure(path)
            a,b,pair=choose_pair(chains,proteins,config.get("gates",{}),spec.get("chains"),exact_construct=True)
            require(spec["experimental"] is True,"PREDICTED_CONFIDENCE_REQUIRED","Use predict stage for unvalidated predicted coordinates")
            accepted=(path,a,b,pair,context,{"kind":"user_experimental","provenance":spec["provenance"]},len(chains))
        else:
            entries=[str(spec["pdb"]).upper()] if spec.get("pdb") else search_experimental_pair(proteins,repo)
            for pdb in entries:
                try:
                    entry=repo.entry(pdb)
                    assembly_ids=entry.get("rcsb_entry_container_identifiers",{}).get("assembly_ids",[])
                    if spec.get("assembly"): assembly_ids=[str(spec["assembly"])]
                    for assembly in assembly_ids:
                        try:
                            raw=repo.get(f"https://files.rcsb.org/download/{pdb}-assembly{assembly}.cif",binary=True)
                            chains,context=read_structure(raw)
                            a,b,pair=choose_pair(chains,proteins,config.get("gates",{}),spec.get("chains"),
                                validator=lambda pair: validate_entity_species(raw,pdb,proteins,pair,repo),exact_construct=True)
                            identity=pair["entity_identity"]
                            source={"kind":"rcsb_experimental_assembly","pdb":pdb,"assembly":assembly,
                                    "methods":entry.get("exptl",[]),"resolution":entry.get("rcsb_entry_info",{}).get("resolution_combined"),
                                    "entity_identity":identity}
                            accepted=(raw,a,b,pair,context,source,len(chains));break
                        except EvidenceError as e: failed.append({"pdb":pdb,"assembly":assembly,"code":e.code,"reason":str(e)})
                    if accepted: break
                except EvidenceError as e: failed.append({"pdb":pdb,"code":e.code,"reason":str(e)})
        put(run,"retrieval",{"receipts":repo.receipts,"rejected":failed,"search_limit":20})
        if accepted:
            raw,a,b,pair,context,source,nchains=accepted
            raw_copy=run.path/"outputs"/("source"+(".pdb" if Path(raw).suffix==".pdb" else ".cif"))
            shutil.copy2(raw,raw_copy);run.output("source_structure",raw_copy)
            normalized=run.path/"outputs/native.pdb";write_pdb(normalized,[a,b]);run.output("native",normalized)
            put(run,"pose",{"source":source,"pair":pair,"nonprotein_context":context,"protein_chain_count":nchains,
                            "normalized_chains":{"A":"target","B":"native_partner"},
                            "observed_target_sequence":a["sequence"],"observed_partner_sequence":b["sequence"],
                            "physiological_interaction_proven":False})
            return run.finish("POSE_ACCEPTED","structurally_observed_interface")
        require(not spec.get("pdb"),"REQUESTED_STRUCTURE_REJECTED","Requested PDB has no valid pair; see retrieval.json")
        return run.finish("NEEDS_PREDICTION","no_accepted_experimental_pose",
                          {"next_step":"predict","note":"Bounded search is not proof that no experimental complex exists"})
    except Exception as e:
        run.fail(e);raise

def model_pair(model,proteins,gates):
    chains,context=read_structure(model["structure"]["path"])
    require(len(chains)==2 and [c["id"] for c in chains]==["A","B"],"MODEL_CHAIN_MAPPING","Expected exactly A/B protein chains")
    require(not context,"MODEL_UNSUPPORTED_CONTEXT","Expected protein-only output without extra context")
    a,b=chains
    require(a["sequence"]==proteins[0]["sequence"] and b["sequence"]==proteins[1]["sequence"],
            "MODEL_SEQUENCE_MISMATCH","Predicted sequences must equal submitted sequences")
    pair={"interface":interface(a,b,gates.get("contact_cutoff",5)),
          "target_match":match_chain(a,proteins[0],1,1),"partner_match":match_chain(b,proteins[1],1,1)}
    metrics=confidence_metrics(model,len(a["sequence"]),len(b["sequence"]),pair["interface"])
    metrics["partner_plddt"]=float(np.mean([r["bfactor"] for r in b["residues"]]))/100
    residues=[a["residues"][i-1]["bfactor"] for i in pair["interface"]["target_residues"]]+[b["residues"][i-1]["bfactor"] for i in pair["interface"]["partner_residues"]]
    metrics["interface_plddt"]=float(np.mean(residues))/100 if residues else None
    metrics["interface_target_residues"]=len(pair["interface"]["target_residues"])
    metrics["interface_partner_residues"]=len(pair["interface"]["partner_residues"])
    require(all(np.isfinite(v) for v in metrics.values() if v is not None),"INVALID_CONFIDENCE","Invalid per-residue confidence")
    require(all(0<=metrics[k]<=1 for k in ("partner_plddt","interface_plddt") if metrics[k] is not None),
            "INVALID_CONFIDENCE","Per-residue confidence outside 0-100 PDB scale")
    return a,b,pair,metrics

def predict(root,upstream):
    m=load_run(upstream,{"NEEDS_PREDICTION"})
    run=Run(root,"02_predict",[record_file(upstream)])
    try:
        config=validate_config(read_json(m["outputs"]["config"]["path"])); proteins=read_json(m["outputs"]["proteins"]["path"])
        runtime_provenance(run,root,["boltz"])
        settings=config.get("prediction",{})
        require(settings.get("samples",3)>=3,"INSUFFICIENT_ENSEMBLE","At least three sampled poses required")
        models=boltz_predict(root,run.path/"work/boltz",proteins,settings,run.path/"logs/boltz.log")
        attach_models(run,"model",models)
        rows=[];passing=[]
        for i,model in enumerate(models):
            try:
                a,b,pair,metrics=model_pair(model,proteins,config.get("gates",{}))
                confidence_gate_reasons=confidence_reasons(metrics,config.get("gates",{}))
                physical_gate=physical_pose_record(pair["interface"])
                reasons=confidence_gate_reasons+physical_gate["reasons"]
                rows.append({"model":i,"metrics":metrics,"reasons":reasons,"interface":pair["interface"],
                             "confidence_gate_reasons":confidence_gate_reasons,"physical_gate":physical_gate})
                if not reasons:passing.append((i,a,b,pair,metrics))
            except Exception as e: rows.append({"model":i,"status":"MODEL_EVALUATION_FAILED","reasons":[getattr(e,"code","MODEL_OUTPUT_INVALID")],"message":str(e)})
        # Require consistent partner pose after target alignment, not just a high global score.
        best=None;support=[]
        for reference in passing:
            compatible=[]
            _,a,b,pair,_=reference
            for candidate in passing:
                idx,aa,bb,pp,mm=candidate
                ca=lambda c:np.array([r["ca"] for r in c["residues"]])
                r,t,_=superpose(ca(aa),ca(a))
                rmsd=float(np.sqrt(np.mean(np.sum((ca(bb)@r+t-ca(b))**2,axis=1))))
                s1={tuple(x) for x in pair["interface"]["residue_pairs"]};s2={tuple(x) for x in pp["interface"]["residue_pairs"]}
                jac=len(s1&s2)/max(len(s1|s2),1)
                if rmsd<=config.get("gates",{}).get("max_ensemble_partner_rmsd",5) and jac>=.5: compatible.append(idx)
            if len(compatible)>len(support):best,support=reference,compatible
        put(run,"ensemble",{"models":rows,"convergent_model_indices":support,"iptm_is_probability":False,
                            "pose_physical_policy":POLICY,
                            "eligible_model_indices":[x[0] for x in passing],
                            "selection_rule":"unchanged maximum compatible neighborhood after target alignment; first representative wins ties",
                            "minimum_support":max(2,int(np.ceil(len(models)*.6))),
                            "support_denominator":"all requested models, including physical rejects",
                            "alternate_compatible_neighborhoods_are_not_complete_linkage_clusters":True})
        put(run,"config",config);put(run,"proteins",proteins)
        if any(row.get("status")=="MODEL_EVALUATION_FAILED" for row in rows):
            return run.finish("PREDICTION_INCOMPLETE","not_evaluable")
        if len(support)<max(2,int(np.ceil(len(models)*.6))):
            return run.finish("POSE_REJECTED","uncertain_interaction_pose")
        i,a,b,pair,metrics=best
        path=run.path/"outputs/native.pdb";write_pdb(path,[a,b]);run.output("native",path)
        put(run,"pose",{"source":{"kind":"boltz2_predicted","model":i},"pair":pair,"confidence":metrics,
                        "protein_chain_count":2,"nonprotein_context":[],"physiological_interaction_proven":False,
                        "normalized_chains":{"A":"target","B":"native_partner"},
                        "observed_target_sequence":a["sequence"],"observed_partner_sequence":b["sequence"],
                        "physical_gate":physical_pose_record(pair["interface"]),
                        "ensemble_support_model_indices":support})
        return run.finish("POSE_ACCEPTED","computational_interaction_hypothesis")
    except Exception as e:run.fail(e);raise

def validate_design_pose(m):
    """Apply the same biological and exact-construct contract to every generator."""
    config=validate_config(read_json(m["outputs"]["config"]["path"]))
    pose=read_json(m["outputs"]["pose"]["path"])
    review=config.get("context_review",{})
    require(review.get("native_interaction_supported") is True and review.get("interaction_evidence"),
            "INTERACTION_EVIDENCE_REQUIRED","A predicted pose alone cannot establish a biological interaction")
    require(review.get("soluble_construct") is True and review.get("no_required_unmodelled_context") is True,
            "CONTEXT_REVIEW_REQUIRED","Membrane, glycan, cofactor, oligomer and construct context must be reviewed")
    require(not pose["nonprotein_context"] and pose["protein_chain_count"]==2,
            "UNSUPPORTED_ASSEMBLY_CONTEXT","This route cannot silently discard other protein chains or cofactors")
    require("proteins" in m["outputs"],"CONSTRUCT_PROVENANCE_MISSING","Re-prepare legacy poses without requested sequences")
    proteins=read_json(m["outputs"]["proteins"]["path"])
    native=Path(m["outputs"]["native"]["path"]);chains,context=read_structure(native)
    require(len(proteins)==len(chains)==2 and all(c["sequence"]==p["sequence"] for c,p in zip(chains,proteins)),
            "CONSTRUCT_SEQUENCE_MISMATCH","Observed target/partner must exactly equal the requested constructs; explicit variants require explicit sequence inputs")
    require([c["id"] for c in chains]==["A","B"] and not context,
            "NATIVE_POSE_CHAIN_OR_CONTEXT_INVALID","Native coordinates must contain only normalized target A and partner B")
    actual_interface=interface(chains[0],chains[1],config.get("gates",{}).get("contact_cutoff",5))
    physical_gate=physical_pose_record(actual_interface)
    require(not physical_gate["reasons"],"SEVERE_NATIVE_POSE_CLASH",
            "Actual native target/partner coordinates fail the existing <1.5 Angstrom heavy-atom criterion")
    pose={**pose,"design_entry_physical_gate":physical_gate}
    return config,pose,native

def design(root,upstream):
    m=load_run(upstream,{"POSE_ACCEPTED"});run=Run(root,"03_design",[record_file(upstream)])
    try:
        config,pose,native=validate_design_pose(m)
        runtime_provenance(run,root,["rfd"])
        candidates=rfd_mpnn(root,run.path/"work/design",native,config.get("design",{}),run.path/"logs",contact_cutoff=config.get("gates",{}).get("contact_cutoff",5))
        require(isinstance(candidates,list),"INVALID_DESIGN_POOL","The generic design pool must be a list")
        require(bool(candidates),"EMPTY_DESIGN_POOL","The generic workflow cannot accept or evaluate an empty design pool")
        put(run,"candidates",candidates);put(run,"config",config)
        shutil.copy2(native,run.path/"outputs/native.pdb");run.output("native",run.path/"outputs/native.pdb")
        for i,c in enumerate(candidates):
            for key in ("backbone","raw_backbone","mpnn_fasta"):run.output(f"candidate_{i}_{key}",c[key]["path"])
        fasta=run.path/"outputs/candidates.fasta"
        fasta.write_text("".join(f">{c['id']}\n{c['sequence']}\n" for c in candidates));run.output("fasta",fasta)
        return run.finish("DESIGNS_GENERATED","unvalidated_sequences",
                          {"candidate_count":len(candidates),"blockade_established":False})
    except Exception as e:run.fail(e);raise

def reevaluate(root,previous):
    old=load_run(previous,{"EVALUATION_COMPLETE"})
    require(old.get("step")=="04_evaluate","INVALID_REPLAY_SOURCE","Expected a full evaluation run")
    return evaluate(root,old["inputs"][0]["path"],reuse=previous)

def evaluate(root,upstream,reuse=None):
    m=load_run(upstream,{"DESIGNS_GENERATED"});run=Run(root,"04_evaluate",[record_file(upstream)])
    try:
        config=validate_config(read_json(m["outputs"]["config"]["path"]));candidates=read_json(m["outputs"]["candidates"]["path"])
        require(isinstance(candidates,list),"INVALID_DESIGN_POOL","The generic design pool must be a list")
        require(bool(candidates),"EMPTY_DESIGN_POOL","The generic workflow cannot accept or evaluate an empty design pool")
        reused=None
        if reuse is not None:
            reused=load_run(reuse,{"EVALUATION_COMPLETE"})
            require(reused["inputs"][0]["sha256"]==record_file(upstream)["sha256"],"REPLAY_INPUT_MISMATCH","Different design manifest")
            run.manifest["inputs"].append(record_file(reuse))
            run.manifest["evaluation_mode"]="existing_predictions_cpu_reanalysis"
            run.manifest["inference_runtime_reference"]={"manifest":record_file(reuse),"note":"Inference belongs to the original run, not this CPU reanalysis"}
            runtime_provenance(run,root,["core"])
        else:
            runtime_provenance(run,root,["boltz"])
        native,_=read_structure(m["outputs"]["native"]["path"]);nat,partner=native
        settings=config.get("refold",config.get("prediction",{}));gates=config.get("gates",{})
        require(settings.get("samples",3)>=3,"INSUFFICIENT_ENSEMBLE","At least three blind refold samples required")
        rows=[]
        for candidate in candidates:
            cid=candidate["id"];rows.append({"id":cid,"sequence":candidate["sequence"],"status":"RUNNING","models":[]})
            row=rows[-1]
            try:
                proteins=[{"sequence":nat["sequence"],"canonical_start":1,"msa":settings.get("target_msa"),"msa_record":settings.get("target_msa_record")},
                          {"sequence":candidate["sequence"],"canonical_start":1,"de_novo":True}]
                if reused is None:
                    models=boltz_predict(root,run.path/"work"/cid,proteins,settings,run.path/"logs"/f"{cid}.log")
                else:
                    prior=read_json(reused["outputs"]["evaluation"]["path"])["candidates"]
                    require([(r["id"],r["sequence"]) for r in prior]==[(c["id"],c["sequence"]) for c in candidates],
                            "REPLAY_CANDIDATES_MISMATCH","IDs and sequences must match exactly")
                    models=[{**{key:reused["outputs"][f"{cid}_{i}_{key}"] for key in ("structure","confidence","pae")},"model_index":i}
                            for i in range(settings.get("samples",3))]
                attach_models(run,cid,models)
                designed,_=read_structure(candidate["backbone"]["path"])
                for model in models:
                    try:
                        a,b,pair,metrics=model_pair(model,proteins,gates)
                        geom=competition(nat,partner,designed[0],designed[1],a,b,cutoff=gates.get("contact_cutoff",5))
                        reasons=confidence_reasons(metrics,gates)
                        if geom["predicted_complex_interface"]["minimum_distance"]<1.5:reasons.append("SEVERE_TARGET_BINDER_CLASH")
                        if geom["binder_ca_rmsd_after_target_alignment"]>gates.get("max_binder_rmsd",2):reasons.append("DESIGNED_POSE_NOT_RECOVERED")
                        if geom["target_ca_rmsd"]>gates.get("max_target_rmsd",2):reasons.append("TARGET_DISTORTED")
                        if geom["native_interface_coverage"]<gates.get("min_interface_overlap",.5):reasons.append("INSUFFICIENT_NATIVE_INTERFACE_OVERLAP")
                        if geom["partner_overlap_atom_count_2A"]<gates.get("min_partner_overlap_atoms",5):reasons.append("NO_STERIC_COMPETITION_SUPPORT")
                        row["models"].append({"index":model["model_index"],"metrics":metrics,"geometry":geom,"reasons":reasons})
                    except Exception as e:row["models"].append({"index":model["model_index"],"status":"MODEL_EVALUATION_FAILED","reasons":[getattr(e,"code","MODEL_OUTPUT_INVALID")],"message":str(e)})
                errors=sum(x.get("status")=="MODEL_EVALUATION_FAILED" for x in row["models"])
                n_pass=sum(not x["reasons"] for x in row["models"])
                row.update(passing_samples=n_pass,requested_samples=len(models),
                           evaluation_failed_samples=errors,
                           status="EVALUATION_FAILED" if errors else "COMPUTATIONAL_COMPETITION_CANDIDATE" if n_pass>=max(2,int(np.ceil(.6*len(models)))) else "REJECTED")
            except Exception as e:row.update(status="EVALUATION_FAILED",error={"code":getattr(e,"code","UNEXPECTED_ERROR"),"message":str(e)})
            put(run,"evaluation",{"candidates":rows,"specificity_assessed":False,"experimental_blockade":False,
                                  "thresholds_calibrated":False,"gates":gates})
        accepted=[r for r in rows if r["status"]=="COMPUTATIONAL_COMPETITION_CANDIDATE"]
        report=run.path/"outputs/report.md"
        lines=["# Protein-blocker computational evaluation","",
               "These are computational hypotheses. Binding, functional blockade, selectivity, expression and safety have not been demonstrated.",
               "Thresholds are configurable engineering triage gates, not calibrated probabilities.","",
               "|Candidate|Result|Passing refolds|","|---|---|---|"]
        for r in rows:lines.append(f"|{r['id']}|{r['status']}|{r.get('passing_samples',0)}/{settings.get('samples',3)}|")
        report.write_text("\n".join(lines)+"\n");run.output("report",report)
        failed=sum(r["status"]=="EVALUATION_FAILED" for r in rows)
        return run.finish("EVALUATION_INCOMPLETE" if failed else "EVALUATION_COMPLETE",
                          "computational_competition_candidates" if accepted else "no_accepted_candidate",
                          {"accepted_count":len(accepted),"failed_count":failed,"total_count":len(rows)})
    except Exception as e:run.fail(e);raise

def all_stages(root,config):
    first=prepare(root,config)
    if read_json(first)["status"]=="NEEDS_PREDICTION":first=predict(root,first)
    require(read_json(first)["status"]=="POSE_ACCEPTED","POSE_REJECTED",str(first))
    designs=design(root,first)
    return evaluate(root,designs)

