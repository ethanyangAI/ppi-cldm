import sys,time,json
from pathlib import Path
import openmm as mm
from openmm import app,unit
from pdbfixer import PDBFixer
src=sys.argv[1];out=Path(sys.argv[2]);out.mkdir(exist_ok=True)
print("START_PREP",flush=True);t=time.monotonic()
f=PDBFixer(filename=src);f.findMissingResidues();f.missingResidues={};f.findNonstandardResidues();f.replaceNonstandardResidues();f.removeHeterogens(False);f.findMissingAtoms();f.addMissingAtoms(seed=3142);f.addMissingHydrogens(7.0)
ff=app.ForceField("amber14-all.xml","implicit/gbn2.xml")
system=ff.createSystem(f.topology,nonbondedMethod=app.CutoffNonPeriodic,nonbondedCutoff=2*unit.nanometer,constraints=app.HBonds,soluteDielectric=1.,solventDielectric=78.5)
force=mm.CustomExternalForce("0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)");force.addGlobalParameter("k",1000)
for n in ("x0","y0","z0"):force.addPerParticleParameter(n)
p=f.positions.value_in_unit(unit.nanometer)
for a in f.topology.atoms():
 if a.element.symbol!="H":force.addParticle(a.index,list(p[a.index]))
system.addForce(force);print("PREP_SECONDS",time.monotonic()-t,flush=True)
records=[]
for threads in (1,2,4):
 integrator=mm.LangevinMiddleIntegrator(300*unit.kelvin,1/unit.picosecond,.002*unit.picoseconds);integrator.setRandomNumberSeed(3142)
 sim=app.Simulation(f.topology,system,integrator,mm.Platform.getPlatformByName("CPU"),{"Threads":str(threads)})
 sim.context.setPositions(f.positions);sim.minimizeEnergy(maxIterations=100)
 sim.context.setVelocitiesToTemperature(300*unit.kelvin,3142)
 sim.step(5);t=time.monotonic();sim.step(20);elapsed=time.monotonic()-t
 state=sim.context.getState(getEnergy=True)
 r=dict(threads=threads,steps=20,seconds=elapsed,seconds_per_step=elapsed/20,projected_550000_step_hours=elapsed/20*550000/3600,potential_kJ_mol=state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole))
 records.append(r);print(json.dumps(r),flush=True);del sim,integrator
 (out/"results.json").write_text(json.dumps(records,indent=2))

