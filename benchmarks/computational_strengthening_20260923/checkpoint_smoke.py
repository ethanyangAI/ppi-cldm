import ast,json,os,time,tempfile
from pathlib import Path
import openmm as mm
from openmm import app,unit
r=Path("/lustre/users/u21111210118/projects/test9")
tree=ast.parse((r/"source/benchmarks/computational_strengthening_20260923/md_worker.py").read_text())
node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="checkpoint")
top=app.Topology();chain=top.addChain();res=top.addResidue("ARG",chain);top.addAtom("CA",app.element.carbon,res)
system=mm.System();system.addParticle(12)
force=mm.CustomExternalForce("0.5*100*(x*x+y*y+z*z)");force.addParticle(0,[]);system.addForce(force)
integrator=mm.LangevinMiddleIntegrator(300*unit.kelvin,1/unit.picosecond,.002*unit.picoseconds)
integrator.setRandomNumberSeed(3142)
sim=app.Simulation(top,system,integrator,mm.Platform.getPlatformByName("CPU"),{"Threads":"8"})
sim.context.setPositions([[.1,0,0]]);sim.context.setVelocitiesToTemperature(300*unit.kelvin,3142);sim.step(10)
out=r/"steps/95_md_cpu_benchmark/checkpoint_smoke";out.mkdir(exist_ok=True)
seed=3142;platform_name="CPU"
exec(compile(ast.Module(body=[node],type_ignores=[]),"<worker_checkpoint>","exec"))
saved=sim.context.getState(getPositions=True,getVelocities=True)
saved_xyz=saved.getPositions(asNumpy=True).value_in_unit(unit.nanometer).copy()
saved_vel=saved.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond).copy()
checkpoint("equilibration")
assert json.loads((out/"progress.json").read_text())["step"]==10
sim.step(10);first=sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
sim.loadCheckpoint(str(out/"progress.chk"));assert sim.currentStep==10
restored=sim.context.getState(getPositions=True,getVelocities=True)
position_error=abs(restored.getPositions(asNumpy=True).value_in_unit(unit.nanometer)-saved_xyz).max()
velocity_error=abs(restored.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond)-saved_vel).max()
assert position_error<1e-12 and velocity_error<1e-12,(position_error,velocity_error)
sim.step(10);second=sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(unit.nanometer)
err=abs(first-second).max();assert float(err)<float("inf")
print(json.dumps(dict(status="CHECKPOINT_ROUNDTRIP_PASSED",restored_coordinate_error_nm=float(position_error),restored_velocity_error_nm_per_ps=float(velocity_error),future_trajectory_difference_nm=float(err),bitwise_stochastic_continuation_claimed=False,cpu_threads=8)))

