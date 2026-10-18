#!/usr/bin/env python3
"""CPU Rosetta interface diagnostics. Scores are not physical binding free energy."""
import hashlib, json, os, sys
from pathlib import Path
import pyrosetta as pr

plan_path, index, output_dir = sys.argv[1:4]
plan = json.loads(Path(plan_path).read_text())
entry = plan["entries"][int(index)]
src = Path(entry["input"]["path"]); out = Path(output_dir)
out.mkdir(parents=True, exist_ok=False)
def receipt(p):
    p=Path(p); b=p.read_bytes()
    return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
assert receipt(src) == entry["input"], "Input receipt mismatch"
assert receipt(plan["environment_freeze"]["path"]) == plan["environment_freeze"], "Environment freeze changed"
seed=entry["seed"]
pr.init("-mute all -constant_seed -jran "+str(seed)+" -relax:default_repeats 1")
pose=pr.pose_from_pdb(str(src))
assert pose.num_chains()==2, "Exactly two chains required"
def chainseq(p):
    return [p.sequence()[p.chain_begin(i)-1:p.chain_end(i)] for i in (1,2)]
before=chainseq(pose)
assert before == entry["sequences"], "PyRosetta input sequences mismatch"
assert {pose.pdb_info().chain(i) for i in range(1,pose.total_residue()+1)}=={"A","B"}
score=pr.create_score_function("ref2015")
mm=pr.rosetta.core.kinematics.MoveMap()
mm.set_bb(True); mm.set_chi(True); mm.set_jump(False)
relax=pr.rosetta.protocols.relax.FastRelax()
relax.set_scorefxn(score); relax.set_movemap(mm)
relax.max_iter(200); relax.min_type("lbfgs_armijo_nonmonotone")
relax.constrain_relax_to_start_coords(True); relax.apply(pose)
assert chainseq(pose)==before
dest=out/"relaxed.pdb"; pose.dump_pdb(str(dest))
iam=pr.rosetta.protocols.analysis.InterfaceAnalyzerMover()
typ=getattr(pr.rosetta.core.pose,"DockingPartners",None)
iam.set_interface(typ.docking_partners_from_string("A_B") if typ else "A_B")
iam.set_scorefunction(score); iam.set_compute_packstat(True)
iam.set_compute_interface_energy(True); iam.set_calc_dSASA(True)
iam.set_calc_hbond_sasaE(True); iam.set_compute_interface_sc(True)
iam.set_pack_separated(True); iam.apply(pose)
d=iam.get_all_data()
buns=pr.rosetta.protocols.rosetta_scripts.XmlObjects.static_get_filter(
 '<BuriedUnsatHbonds report_all_heavy_atom_unsats="true" scorefxn="scorefxn" ignore_surface_res="false" use_ddG_style="true" dalphaball_sasa="0" probe_radius="1.1" burial_cutoff_apo="0.2" confidence="0" />')
result=dict(status="COMPUTED_NOT_EXPERIMENTAL_VALIDATION", identity=entry["identity"],
 seed=seed, input=entry["input"], plan=receipt(plan_path),
 environment_freeze=plan["environment_freeze"], runtime_version=pr.version(),
 scorefunction="ref2015", fastrelax_repeats=1, max_iter=200, rigid_body_jumps_fixed=True,
 coordinate_constraints_to_input=True, buried_unsatisfied_sasa_method="Rosetta default SASA",
 dG_separated=float(iam.get_interface_dG()), dSASA=float(iam.get_interface_delta_sasa()),
 shape_complementarity=float(d.sc_value), packstat=float(iam.get_interface_packstat()),
 hbond_count=float(d.interface_hbonds), buried_unsatisfied=float(buns.report_sm(pose)),
 dG_per_area_x100=float(d.dG_dSASA_ratio)*100, relaxed_pdb=receipt(dest),
 sequences=before, energy_units="Rosetta energy units, not physical binding free energy",
 slurm_job_id=os.environ.get("SLURM_JOB_ID"), slurm_array_task_id=os.environ.get("SLURM_ARRAY_TASK_ID"))
(out/"result.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
print(json.dumps(result,allow_nan=False))

