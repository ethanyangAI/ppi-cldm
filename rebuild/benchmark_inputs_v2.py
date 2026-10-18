"""Auditable benchmark inputs v2: official native target A and binder B chain metadata."""
from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path
from collections import Counter
import numpy as np
from Bio.PDB import PDBParser, PDBIO
from Bio.SeqUtils import seq1, seq3

def receipt(path):
    p=Path(path).resolve()
    return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

def verify(r):
    p=Path(r["path"])
    if receipt(p)!=r: raise ValueError("Receipt mismatch: "+str(p))
    return p

def save(path,value):
    p=Path(path)
    if p.exists(): raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
    return receipt(p)

def residues(path,chain="A"):
    return [r for r in PDBParser(QUIET=True).get_structure("input",path)[0][chain] if r.id[0]==" "]

def sequence(rs):
    return "".join(seq1(r.resname) for r in rs)

def repair(identity_path,out,seed):
    """Fill missing internal target residues using target-only PDBFixer/OpenMM Reference."""
    import openmm
    from openmm import app, unit
    from pdbfixer import PDBFixer
    identity_path=Path(identity_path).resolve(); ident=json.loads(identity_path.read_text())
    if ident["status"]!="TARGET_ONLY_COORDINATE_REPAIR_REQUIRED": raise ValueError("Repair requires typed coordinate deficiency")
    ctx=ident["target_context"]; mapping=ctx["mapping"]; seq=ctx["coordinate_required_sequence"]
    missing=ctx["internal_missing_label_seq_ids"]
    if missing!=[64,65] or len(seq)!=166 or ctx["source_chain"]!="A": raise ValueError("Only frozen HRAS 64/65 minimal gap repair is authorized")
    original=verify(ident["design_structure"]); out=Path(out).resolve()
    if out.exists(): raise FileExistsError(out)
    out.mkdir(parents=True)
    structure=PDBParser(QUIET=True).get_structure("target_only",original)
    chain=structure[0]["A"]; rs=list(chain.get_residues())
    if sequence(rs)!=ctx["selected_sequence"]: raise ValueError("Original target sequence mismatch")
    # Reconstruct deposited full-query numbering; partner coordinates are never read.
    for r in rs: r.id=(" ",r.id[1]+10000," ")
    for r,m in zip(rs,mapping): r.id=(" ",int(m["label_seq_id"])," ")
    io=PDBIO();io.set_structure(structure);atomfile=out/"numbered_target_atoms.pdb";io.save(str(atomfile))
    names=[seq3(a).upper() for a in seq]
    headers=["SEQRES %3d A %4d  %s" % (i//13+1,len(seq)," ".join(names[i:i+13])) for i in range(0,len(names),13)]
    infile=out/"target_only_with_seqres.pdb";infile.write_text("\n".join(headers)+"\n"+atomfile.read_text())
    platform=openmm.Platform.getPlatformByName("Reference")
    fixer=PDBFixer(filename=str(infile))
    fixer.findMissingResidues()
    expected={(0,63):["TYR","SER"]}
    if fixer.missingResidues!=expected: raise ValueError("Unexpected missing-residue request: "+repr(fixer.missingResidues))
    fixer.findMissingAtoms()
    missing_atoms={str(r.id):[a.name for a in v] for r,v in fixer.missingAtoms.items()}
    missing_terminals={str(r.id):list(v) for r,v in fixer.missingTerminals.items()}
    original_context=openmm.Context
    def cpu_context(system,integrator,*args,**kwargs):
        if args or kwargs: raise ValueError("Unexpected implicit Context platform")
        return original_context(system,integrator,platform)
    openmm.Context=cpu_context
    try: fixer.addMissingAtoms(seed=int(seed))
    finally: openmm.Context=original_context
    # Relax only modeled residues while every observed heavy atom stays fixed.
    # Hydrogen preparation is followed by explicit heavy-coordinate restoration.
    unrelaxed=out/"target_gapfilled_unrelaxed.pdb"
    with unrelaxed.open("w") as handle: app.PDBFile.writeFile(fixer.topology,fixer.positions,handle,keepIds=False)
    import random
    random.seed(int(seed));np.random.seed(int(seed))
    ff=app.ForceField("amber14-all.xml")
    modeller=app.Modeller(fixer.topology,fixer.positions)
    heavy={(a.residue.index,a.name):fixer.positions[a.index].value_in_unit(unit.nanometer) for a in fixer.topology.atoms()}
    modeller.addHydrogens(ff,pH=7.0,platform=platform)
    positions=list(modeller.positions.value_in_unit(unit.nanometer))
    for a in modeller.topology.atoms():
        if (a.residue.index,a.name) in heavy: positions[a.index]=heavy[(a.residue.index,a.name)]
    system=ff.createSystem(modeller.topology,nonbondedMethod=app.NoCutoff,constraints=None,rigidWater=False)
    for a in modeller.topology.atoms():
        if a.element.symbol!="H" and a.residue.index+1 not in missing:system.setParticleMass(a.index,0*unit.dalton)
    integrator=openmm.VerletIntegrator(0.001*unit.picosecond)
    context=openmm.Context(system,integrator,platform)
    context.setPositions(positions*unit.nanometer)
    initial_energy=context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    openmm.LocalEnergyMinimizer.minimize(context,10*unit.kilojoule_per_mole/unit.nanometer,2000)
    state=context.getState(getPositions=True,getEnergy=True)
    final_energy=state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    full=out/"target_gapfilled_relaxed_hydrogens.pdb"
    with full.open("w") as handle:app.PDBFile.writeFile(modeller.topology,state.getPositions(),handle,keepIds=False)
    del context,integrator
    relaxed=PDBParser(QUIET=True).get_structure("relaxed",full)
    for rr0 in relaxed[0]["A"]:
        for a0 in list(rr0):
            if a0.element=="H":rr0.detach_child(a0.id)
    io=PDBIO();io.set_structure(relaxed);repaired=out/"target_complete.pdb";io.save(str(repaired))
    relaxation={"forcefield":"amber14-all.xml","platform":platform.getName(),"variable_heavy_residues":missing,
                "all_observed_heavy_atoms_fixed":True,"max_iterations":2000,"initial_energy_kJ_per_mol":initial_energy,
                "final_energy_kJ_per_mol":final_energy}
    rr=residues(repaired)
    if len(rr)!=166 or sequence(rr)!=seq: raise ValueError("Repaired full target identity mismatch")
    # Every original experimental atom must retain its exact coordinate within PDB precision.
    shifts=[]
    for r,m in zip(rs,mapping):
        new=rr[int(m["label_seq_id"])-1]
        for atom in r:
            if atom.name not in new: raise ValueError("Observed atom disappeared")
            shifts.append(float(np.linalg.norm(atom.coord-new[atom.name].coord)))
    if max(shifts,default=0)>0.002: raise ValueError("Minimal gap repair shifted observed experimental coordinates")
    closure=[]
    for a,b in [(63,64),(64,65),(65,66)]:
        d=float(np.linalg.norm(rr[a-1]["C"].coord-rr[b-1]["N"].coord))
        closure.append({"from":a,"to":b,"C_N_angstrom":d})
        if not 1.05<=d<=1.65: raise ValueError("Gap peptide bond failed geometry gate: "+str(d))
    added=[(i,a) for i in missing for a in rr[i-1] if a.element!="H"]
    outside=[(r.id[1],a) for r in rr if r.id[1] not in missing for a in r if a.element!="H"]
    severe=[]
    for i,a in added:
        for j,b in outside:
            if abs(i-j)<=1: continue
            d=float(np.linalg.norm(a.coord-b.coord))
            if d<1.5: severe.append({"added_residue":i,"atom":a.name,"observed_residue":j,"observed_atom":b.name,"distance":d})
    save(out/"geometry_diagnostics.json",{"severe":severe,"closure":closure,"relaxation":relaxation})
    if severe: raise ValueError("Severe non-neighbor gap atom clash")
    result={"schema":"target_only_coordinate_repair.v1","status":"TARGET_ONLY_MINIMAL_GAP_REPAIR_ACCEPTED",
            "identity_receipt":receipt(identity_path),"source_structure":ident["design_structure"],
            "target_pdb":receipt(repaired),"target_sequence":seq,"missing_label_seq_ids":missing,
            "method":"PDBFixer1.9 addMissingAtoms; OpenMM Reference platform",
            "seed":int(seed),"platform":platform.getName(),"no_partner_coordinates":True,"relaxation":relaxation,
            "observed_max_displacement_angstrom":max(shifts,default=0),"peptide_closure":closure,
            "other_missing_atoms":missing_atoms,"other_missing_terminal_atoms":missing_terminals,
            "severe_non_neighbor_clashes":severe,"package_source_receipts":[],
            "scientific_boundary":"Missing loop remains computationally modeled; observed GNP-bound coordinates retained with cofactors omitted identically in both methods",
            "source_entry":receipt(__file__),"slurm_job_id":os.environ.get("SLURM_JOB_ID")}
    import inspect
    import pdbfixer.pdbfixer
    result["package_source_receipts"]=[receipt(inspect.getfile(pdbfixer.pdbfixer))]
    save(out/"repair_receipt.json",result)
    return result

def bridge(inventory_path,out,repair_path=None):
    inventory_path=Path(inventory_path).resolve()
    inventory=json.loads(inventory_path.read_text());out=Path(out).resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    repair_record=json.loads(Path(repair_path).read_text()) if repair_path else None
    prepared=[];pending=[]
    for ident in inventory["targets"]:
        spec=ident["spec"];target_id=spec["target_id"];ctx=ident["target_context"]
        identity_path=inventory_path.parent/"targets"/target_id/"identity.json"
        stored=json.loads(identity_path.read_text())
        expected={k:v for k,v in ident.items() if k!="identity_receipt"}
        if stored!=expected:raise ValueError("Inventory/identity content mismatch")
        verify(ident["identity_receipt"])
        identity_receipt=receipt(identity_path)
        seq=ctx["coordinate_required_sequence"]
        target_pdb=ident["design_structure"]
        design_map=dict(ident["design_to_reference_indices"])
        repair_receipt=None
        if ident["status"]=="TARGET_ONLY_COORDINATE_REPAIR_REQUIRED":
            if repair_record is None:
                pending.append({"target_id":target_id,"status":ident["status"],"full_query_length":len(seq)})
                continue
            if repair_record["status"]!="TARGET_ONLY_MINIMAL_GAP_REPAIR_ACCEPTED" or repair_record["identity_receipt"]!=identity_receipt:
                raise ValueError("Repair does not match frozen identity")
            if repair_record["target_sequence"]!=seq:raise ValueError("Repair sequence mismatch")
            target_pdb=repair_record["target_pdb"];repair_receipt=receipt(repair_path)
            # Reference indices are observed coordinates; missing residues have no reference.
            lo=min(m["label_seq_id"] for m in ctx["mapping"])
            by_label={m["label_seq_id"]:m["normalized_index"] for m in ident["reference_target_context"]["mapping"]}
            design_map={str(i+1):by_label[lo+i] for i in range(len(seq)) if lo+i in by_label}
        elif ident["status"]!="INPUT_QUALIFIED":raise ValueError("Unexpected target status")
        verify(target_pdb);verify(ident["reference_complex"])
        actual=residues(target_pdb["path"])
        if sequence(actual)!=seq or [r.id[1] for r in actual]!=list(range(1,len(seq)+1)):
            raise ValueError("Full sequence/contiguous target numbering gate failed "+target_id)
        ref=residues(ident["reference_complex"]["path"])
        for i,j in design_map.items():
            if not 1<=int(i)<=len(seq) or not 1<=int(j)<=len(ref) or seq[int(i)-1]!=seq1(ref[int(j)-1].resname):
                raise ValueError("Mapped reference residue identity mismatch")
        # Recover hotspots from deposited reference contacts by number of partner residue contacts, identity-independent.
        counts=Counter(int(x[0]) for x in ident["reference_5A_residue_pairs"])
        reverse={int(v):int(k) for k,v in design_map.items()}
        hotspots=[reverse[i] for i,_ in sorted(counts.items(),key=lambda x:(-x[1],x[0])) if i in reverse][:3]
        if len(hotspots)!=3:raise ValueError("Insufficient reference interface hotspots")
        partner=ident["reference_partner_context"]
        pseq=partner["coordinate_required_sequence"]
        lo_p=min(m["label_seq_id"] for m in partner["mapping"])
        partner_map={str(m["label_seq_id"]-lo_p+1):m["normalized_index"] for m in partner["mapping"]}
        manifest={"schema":"prepared_benchmark_target.v1","status":"FROZEN_INPUT_READY",
                  "target_id":target_id,"family":spec["family"],"analysis_role":spec["analysis_role"],
                  "target_pdb":target_pdb,"target_sequence":seq,"residue_count":len(seq),
                  "input_target_chain":"A","rfd_output_target_chain":"A","rfd_binder_chain":"B",
                  "common_target_chain":"A","common_binder_chain":"B",
                  "rfd_contig":"A1-"+str(len(seq))+"/0 65-65","hotspots":hotspots,
                  "binder_length":65,"reference_complex":ident["reference_complex"],
                  "design_to_reference_indices":design_map,"reference_target_chain":"A","reference_partner_chain":"B",
                  "reference_partner_sequence":pseq,"partner_to_reference_indices":partner_map,
                  "identity_receipt":identity_receipt,"repair_receipt":repair_receipt,
                  "synthetic_target":spec["family"]=="BBF","context":spec["context"],
                  "source_matrix_receipt":inventory["matrix_receipt"],"source_entry":receipt(__file__),
                  "scientific_scope":"COMPUTATIONAL_ONLY"}
        path=out/target_id/"input_manifest.json";mr=save(path,manifest)
        prepared.append({"target_id":target_id,"family":spec["family"],"analysis_role":spec["analysis_role"],"input_manifest":mr})
    result={"schema":"benchmark_input_bridge.v1","status":"ALL_TARGET_INPUTS_ACCEPTED" if not pending else "PARTIAL_PREPARED_INPUTS_WITH_TYPED_REPAIR_PENDING",
            "prepared":prepared,"pending":pending,"inventory_receipt":receipt(inventory_path),
            "source_entry":receipt(__file__),"slurm_job_id":os.environ.get("SLURM_JOB_ID")}
    save(out/"prepared_inputs.json",result)
    return result

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="command",required=True)
    p=sub.add_parser("bridge");p.add_argument("--inventory",required=True);p.add_argument("--out",required=True);p.add_argument("--repair")
    p=sub.add_parser("repair");p.add_argument("--identity",required=True);p.add_argument("--out",required=True);p.add_argument("--seed",type=int,default=21101)
    ns=ap.parse_args()
    result=bridge(ns.inventory,ns.out,ns.repair) if ns.command=="bridge" else repair(ns.identity,ns.out,ns.seed)
    print(json.dumps({"status":result["status"],"job":os.environ.get("SLURM_JOB_ID")}))
if __name__=="__main__": main()

