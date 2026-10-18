import struct
import numpy as np
def read_openmm_dcd(path):
 with open(path,"rb") as f:
  def record():
   b=f.read(4)
   if len(b)!=4:raise ValueError("Truncated DCD record marker")
   n=struct.unpack("<i",b)[0]
   if n<0 or n>100000000:raise ValueError("Invalid DCD record length")
   data=f.read(n);end=f.read(4)
   if len(data)!=n or len(end)!=4 or struct.unpack("<i",end)[0]!=n:raise ValueError("Truncated/mismatched DCD record")
   return data
  h=record()
  if len(h)!=84 or h[:4]!=b"CORD":raise ValueError("Only standard OpenMM coordinate DCD supported")
  frames=struct.unpack("<i",h[4:8])[0];box=struct.unpack("<i",h[44:48])[0]
  if box not in (0,1):raise ValueError("Unsupported box flag")
  record();n=struct.unpack("<i",record())[0];rows=[]
  for _ in range(frames):
   if box:record()
   coords=[]
   for axis in range(3):
    b=record()
    if len(b)!=4*n:raise ValueError("DCD atom count mismatch")
    coords.append(np.frombuffer(b,dtype="<f4").astype(float))
   rows.append(np.stack(coords,axis=1))
  if f.read(1):raise ValueError("Unexpected trailing DCD data")
 out=np.array(rows)
 if not np.isfinite(out).all():raise ValueError("Nonfinite DCD")
 return out

