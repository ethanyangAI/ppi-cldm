from collections import Counter
from util import *
summary={}
for stage in ("80_strengthening_predict","81_strengthening_score","83_strengthening_extension_predict","84_strengthening_physics","85_strengthening_md","87_strengthening_extension_score","88_strengthening_calibration"):
 counts=Counter();failed=[]
 for p in (R/"steps"/stage/"runs").glob("*/manifest.json"):
  m=read_json(p);counts[m["status"]]+=1
  if m["status"]=="FAILED":failed.append(dict(id=m.get("entry_id"),error=m.get("error"),manifest=str(p)))
 summary[stage]=dict(counts=dict(counts),failures=failed[-5:])
print(__import__("json").dumps(summary,indent=2))

