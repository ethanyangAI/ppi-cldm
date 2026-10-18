import sys
from openmm import app,unit,Vec3
from pathlib import Path
p=Path(sys.argv[1]);p.mkdir(exist_ok=True)
t=app.Topology();c=t.addChain("A");r=t.addResidue("GLY",c);t.addAtom("CA",app.element.carbon,r);t.addAtom("N",app.element.nitrogen,r)
with (p/"fixture.dcd").open("wb") as f:
 d=app.DCDFile(f,t,.002*unit.picoseconds,interval=5000)
 d.writeModel([Vec3(.1,.2,.3),Vec3(.4,.5,.6)]*unit.nanometer)
 d.writeModel([Vec3(.2,.3,.4),Vec3(.5,.6,.7)]*unit.nanometer)

