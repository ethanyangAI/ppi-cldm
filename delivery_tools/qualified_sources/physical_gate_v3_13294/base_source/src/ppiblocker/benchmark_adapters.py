"""Explicit cross-method interchange; preparation is not method execution."""
from pathlib import Path
import hashlib,json,re,shutil
import yaml
from .common import Run,load_run,read_json,record_file,verify_file,atomic_json,require
from .structure import read_structure,write_pdb,interface
from .pipeline import validate_config,validate_design_pose

def export_inputs(root,pose_manifest,binder_length=65,count=64):
    require(type(binder_length) is int and 30<=binder_length<=200,"INVALID_LENGTH","Expected miniprotein length")
    require(type(count) is int and count>0,"INVALID_COUNT","Expected positive candidate budget")
    upstream=load_run(pose_manifest,{"POSE_ACCEPTED"})
    config,pose,_=validate_design_pose(upstream)
    run=Run(root,"08_benchmark_method_inputs",[record_file(pose_manifest)])
    try:
        chains,_=read_structure(upstream["outputs"]["native"]["path"]);target,partner=chains
        contacts=interface(target,partner)
        counts={}
        for a,b in contacts["residue_pairs"]:counts[a]=counts.get(a,0)+1
        anchors=sorted(counts,key=lambda a:(-counts[a],a))[:3]
        target_path=run.path/"outputs/target_only.pdb";write_pdb(target_path,[target]);run.output("target",target_path)
        bindcraft=dict(design_path=str(run.path/"work/bindcraft"),binder_name="benchmark",
                       starting_pdb=str(target_path),chains="A",target_hotspot_residues=",".join(f"A{x}" for x in anchors),
                       lengths=[binder_length,binder_length],number_of_final_designs=count)
        atomic_json(run.path/"outputs/bindcraft.target.json",bindcraft)
        boltzgen={"entities":[{"protein":{"id":"B","sequence":binder_length}},{"file":{"path":str(target_path),"include":[{"chain":{"id":"A"}}],"binding_types":[{"chain":{"id":"A","binding":",".join(map(str,anchors))}}]}}]}
        (run.path/"outputs/boltzgen.yaml").write_text(yaml.safe_dump(boltzgen,sort_keys=False))
        for name,file in (("bindcraft","bindcraft.target.json"),("boltzgen","boltzgen.yaml")):run.output(name,run.path/"outputs"/file)
        atomic_json(run.path/"outputs/contract.json",dict(target_sequence=target["sequence"],target_record=record_file(target_path),
             anchors=anchors,binder_length=binder_length,requested_pool_size=count,
             geometry_source=record_file(pose_manifest),input_track="same_native_interface",
             status="INPUTS_EXPORTED_NOT_EXECUTED",
             caveats=["BindCraft number_of_final_designs is an accepted-design stopping criterion, not a raw-candidate budget; needs trajectory/time cap.",
                      "BoltzGen num_designs counts backbone designs; budget counts selected output. Do not equate them.",
                      "RFD3 adapter and all external environments must pass actual CLI/output tests before a comparison.",
                      "Target-only coordinates are design inputs; original native complex is retained as explicit upstream evidence."]))
        run.output("contract",run.path/"outputs/contract.json")
        return run.finish("METHOD_INPUTS_EXPORTED","configuration_only")
    except Exception as e:run.fail(e);raise

def import_pool(root,pose_manifest,contract_path):
    upstream=load_run(pose_manifest,{"POSE_ACCEPTED"})
    validate_design_pose(upstream)
    contract=read_json(contract_path)
    require(contract.get("schema_version")==1,"INVALID_POOL_SCHEMA","Expected schema 1")
    require(contract.get("pose_manifest")==record_file(pose_manifest),"POSE_IDENTITY_MISMATCH","Different upstream pose")
    require(contract.get("method") and contract.get("code_revision") and contract.get("runtime_record") and contract.get("candidate_budget"),
            "METHOD_PROVENANCE_REQUIRED","Method, revision, runtime and budget required")
    verify_file(contract["runtime_record"])
    rows=contract.get("candidates",[])
    require(bool(rows) and len({r.get("id") for r in rows})==len(rows),"INVALID_POOL","Nonempty unique candidate IDs required")
    native,_=read_structure(upstream["outputs"]["native"]["path"]);target=native[0]
    run=Run(root,"03_design",[record_file(pose_manifest),record_file(contract_path)])
    try:
        result=[]
        for i,row in enumerate(rows):
            require(re.fullmatch(r"[A-Za-z0-9_-]+",row["id"]) is not None,"INVALID_CANDIDATE_ID","No paths in IDs")
            require(isinstance(row.get("sequence"),str) and 30<=len(row["sequence"])<=200 and
                    set(row["sequence"])<=set("ACDEFGHIKLMNPQRSTVWY"),"INVALID_DESIGN_SEQUENCE",row["id"])
            source=verify_file(row["backbone"]);chains,context=read_structure(source)
            require(len(chains)==2 and not context and [c["id"] for c in chains]==["A","B"],
                    "UNNORMALIZED_POOL","Interchange backbone must contain exactly target A and binder B")
            require(chains[0]["sequence"]==target["sequence"] and len(chains[1]["sequence"])==len(row["sequence"]),
                    "POOL_IDENTITY_MISMATCH",row["id"])
            dest=run.path/"outputs"/f"{row['id']}.pdb";shutil.copy2(source,dest);run.output(f"candidate_{i}_backbone",dest)
            result.append(dict(id=row["id"],sequence=row["sequence"],backbone=record_file(dest),
                               target_sequence=target["sequence"],method=contract["method"]))
        for key in ("config","native"):
            source=Path(upstream["outputs"][key]["path"]);dest=run.path/"outputs"/source.name
            shutil.copy2(source,dest);run.output(key,dest)
        atomic_json(run.path/"outputs/candidates.json",result);run.output("candidates",run.path/"outputs/candidates.json")
        # Include immutable external runtime snapshot in inventory, never just trust an unpinned path.
        dest=run.path/"qc/external_runtime.json";shutil.copy2(verify_file(contract["runtime_record"]),dest);run.output("external_runtime",dest)
        return run.finish("DESIGNS_GENERATED","unvalidated_external_sequences",
                          dict(candidate_count=len(result),method=contract["method"],code_revision=contract["code_revision"]))
    except Exception as e:run.fail(e);raise

