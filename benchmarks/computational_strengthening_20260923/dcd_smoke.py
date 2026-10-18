import shutil
from util import *
from dcd_reader import read_openmm_dcd
run=Run(R,"94_strengthening_dcd_smoke",[]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 checked_command([R/"env/bindcraft/bin/python",S/"dcd_fixture.py",run.path/"work/fixture"],run.path/"work",run.path/"logs/fixture.log",env(),timeout=120)
 f=run.path/"work/fixture/fixture.dcd";a=read_openmm_dcd(f)
 require(np.allclose(a,[[[1,2,3],[4,5,6]],[[2,3,4],[5,6,7]]]),"DCD_UNIT_OR_FRAME_ERROR",str(a))
 broken=run.path/"work/truncated.dcd";broken.write_bytes(f.read_bytes()[:-4]);caught=False
 try:read_openmm_dcd(broken)
 except ValueError:caught=True
 require(caught,"TRUNCATION_NOT_REJECTED","DCD validation");run.output("fixture",f)
 print(run.finish("DCD_READER_ROUNDTRIP_PASSED","engineering_only"),flush=True)
except Exception as x:run.fail(x);raise

