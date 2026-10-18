import sys,json,time,os
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import openmm as mm
from openmm import app,unit
from pdbfixer import PDBFixer
platform_name=sys.argv[4] if len(sys.argv)>4 else "CPU";assert platform_name in ("CPU","CUDA")
src,out,seed=sys.argv[1:4];out=Path(out);out.mkdir(exist_ok=True);seed=int(seed)
fix=PDBFixer(filename=src);fix.findMissingResidues();fix.missingResidues={};fix.findNonstandardResidues();fix.replaceNonstandardResidues();fix.removeHeterogens(False);fix.findMissingAtoms();fix.addMissingAtoms(seed=seed);fix.addMissingHydrogens(7.0)
ff=app.ForceField("amber14-all.xml","implicit/gbn2.xml")
system=ff.createSystem(fix.topology,nonbondedMethod=app.CutoffNonPeriodic,nonbondedCutoff=2*unit.nanometer,constraints=app.HBonds,soluteDielectric=1.0,solventDielectric=78.5)
pos=fix.positions.value_in_unit(unit.nanometer)
force=mm.CustomExternalForce("0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)");force.addGlobalParameter("k",1000);[force.addPerParticleParameter(x) for x in ("x0","y0","z0")]
for a in fix.topology.atoms():
 if a.element.symbol!="H":force.addParticle(a.index,list(pos[a.index]))
system.addForce(force)
integrator=mm.LangevinMiddleIntegrator(300*unit.kelvin,1/unit.picosecond,.002*unit.picoseconds);integrator.setRandomNumberSeed(seed)
(out/"system.xml").write_text(mm.XmlSerializer.serialize(system))
(out/"integrator.xml").write_text(mm.XmlSerializer.serialize(integrator))
sim=app.Simulation(fix.topology,system,integrator,mm.Platform.getPlatformByName(platform_name),{"Threads":os.environ.get("PPI_MD_THREADS","8")} if platform_name=="CPU" else {"Precision":"mixed"})
def checkpoint(phase):
 tmp=out/"progress.chk.tmp";sim.saveCheckpoint(str(tmp));tmp.replace(out/"progress.chk")
 data=dict(step=sim.currentStep,phase=phase,seed=seed,platform=platform_name,cpu_threads=os.environ.get("PPI_MD_THREADS","8"),wall_time=time.time(),checkpoint="progress.chk")
 tmp=out/"progress.json.tmp";tmp.write_text(json.dumps(data));tmp.replace(out/"progress.json")
with (out/"prepared.pdb").open("w") as f:app.PDBFile.writeFile(fix.topology,fix.positions,f)
print("START_MINIMIZATION",flush=True)
sim.context.setPositions(fix.positions);sim.minimizeEnergy(maxIterations=2000);sim.context.setVelocitiesToTemperature(300*unit.kelvin,seed)
checkpoint("minimized")
print("START_EQUILIBRATION",flush=True)
for _ in range(100):
 sim.step(500);checkpoint("equilibration")
sim.context.setParameter("k",0)
checkpoint("production_start")
print("START_PRODUCTION",flush=True)
initial=sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.angstrom)
np.save(out/"equilibration_reference_angstrom.npy",initial)
atomlist=list(fix.topology.atoms());chains=list(fix.topology.chains());assert len(chains)==2
ids=[[a.index for a in atomlist if a.residue.chain==c and a.element.symbol!="H"] for c in chains]
cas=[[a.index for a in atomlist if a.residue.chain==c and a.name=="CA"] for c in chains]
pairs=cKDTree(initial[ids[0]]).query_ball_tree(cKDTree(initial[ids[1]]),5.0);contacts={(i,j) for i,js in enumerate(pairs) for j in js}
def rmsd(a,b):
 cm=a.mean(0);cf=b.mean(0);u,s,v=np.linalg.svd((a-cm).T@(b-cf));d=np.eye(3);d[-1,-1]=np.linalg.det(u@v);r=u@d@v;t=cf-cm@r
 return r,t,float(np.sqrt(np.mean(np.sum((a@r+t-b)**2,axis=1))))
with (out/"prepared.pdb").open("w") as f:app.PDBFile.writeFile(fix.topology,fix.positions,f)
sim.reporters.append(app.DCDReporter(str(out/"trajectory.dcd"),5000))
trace=[]
for step in range(100):
 for chunk in range(10):
  sim.step(500)
  if chunk<9:checkpoint("production")
 state=sim.context.getState(getPositions=True,getEnergy=True);xyz=state.getPositions(asNumpy=True).value_in_unit(unit.angstrom);energy=state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole);assert np.isfinite(energy) and np.isfinite(xyz).all()
 r,t,tr=rmsd(xyz[cas[0]],initial[cas[0]]);pose=float(np.sqrt(np.mean(np.sum((xyz[cas[1]]@r+t-initial[cas[1]])**2,axis=1))))
 pp=cKDTree(xyz[ids[0]]).query_ball_tree(cKDTree(xyz[ids[1]]),5.0);now={(i,j) for i,js in enumerate(pp) for j in js}
 trace.append(dict(time_ps=(step+1)*10,potential_kJ_mol=energy,target_ca_rmsd=tr,binder_pose_rmsd=pose,binder_fold_rmsd=rmsd(xyz[cas[1]],initial[cas[1]])[2],initial_atom_contact_retention=len(contacts&now)/max(1,len(contacts)),atom_contacts=len(now)))
 (out/"trace.json").write_text(json.dumps(trace));checkpoint("production");print("PROGRESS_PS",(step+1)*10,flush=True)
sim.saveCheckpoint(str(out/"end.chk"))
with (out/"final.pdb").open("w") as f:app.PDBFile.writeFile(fix.topology,state.getPositions(),f)
(out/"result.json").write_text(json.dumps(dict(seed=seed,platform=platform_name,cpu_threads=os.environ.get("PPI_MD_THREADS","8") if platform_name=="CPU" else None,openmm_version=mm.__version__,solvent="implicit GBn2",forcefield="amber14-all",production_ps=1000,equilibration_ps=100,restraints_production=0,starting_contact_pairs=len(contacts),trace=trace,claims="short structural stability diagnostic; not affinity, residence time or convergence proof"),allow_nan=False))

