import sys,json
from pathlib import Path
import pyrosetta as pr
src,out,seed=sys.argv[1:4];seed=int(seed);out=Path(out);out.mkdir(exist_ok=True)
pr.init("-mute all -constant_seed -jran "+str(seed)+" -holes:dalphaball /lustre/users/u21111210118/projects/test9/assets/bindcraft/bin/DAlphaBall.gcc -relax:default_repeats 1")
pose=pr.pose_from_pdb(src);score=pr.create_score_function("ref2015")
mm=pr.rosetta.core.kinematics.MoveMap();mm.set_bb(True);mm.set_chi(True);mm.set_jump(False)
relax=pr.rosetta.protocols.relax.FastRelax();relax.set_scorefxn(score);relax.set_movemap(mm);relax.max_iter(200);relax.min_type("lbfgs_armijo_nonmonotone");relax.constrain_relax_to_start_coords(True);relax.apply(pose)
dest=out/"relaxed.pdb";pose.dump_pdb(str(dest))
iam=pr.rosetta.protocols.analysis.InterfaceAnalyzerMover()
typ=getattr(pr.rosetta.core.pose,"DockingPartners",None);iam.set_interface(typ.docking_partners_from_string("A_B") if typ is not None else "A_B")
iam.set_scorefunction(score);iam.set_compute_packstat(True);iam.set_compute_interface_energy(True);iam.set_calc_dSASA(True);iam.set_calc_hbond_sasaE(True);iam.set_compute_interface_sc(True);iam.set_pack_separated(True);iam.apply(pose)
d=iam.get_all_data()
buns=pr.rosetta.protocols.rosetta_scripts.XmlObjects.static_get_filter('<BuriedUnsatHbonds report_all_heavy_atom_unsats="true" scorefxn="scorefxn" ignore_surface_res="false" use_ddG_style="true" dalphaball_sasa="0" probe_radius="1.1" burial_cutoff_apo="0.2" confidence="0" />')
result=dict(seed=seed,scorefunction="ref2015",buried_unsatisfied_sasa_method="Rosetta default SASA; DAlphaBall runtime failed in smoke",fastrelax_repeats=1,max_iter=200,dG_separated=float(iam.get_interface_dG()),dSASA=float(iam.get_interface_delta_sasa()),shape_complementarity=float(d.sc_value),packstat=float(iam.get_interface_packstat()),hbond_count=float(d.interface_hbonds),buried_unsatisfied=float(buns.report_sm(pose)),dG_per_area_x100=float(d.dG_dSASA_ratio)*100,relaxed_pdb=str(dest),energy_units="Rosetta energy units; not physical binding free energy",pyrosetta_version=pr.version())
(out/"result.json").write_text(json.dumps(result,indent=2,allow_nan=False))

