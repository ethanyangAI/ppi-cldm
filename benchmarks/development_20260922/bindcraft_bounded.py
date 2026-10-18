"""Pinned BindCraft runner with an attempt cap independent of relaxed-design count."""
import sys,runpy,os,json,random
from pathlib import Path
vendor=Path(sys.argv[1]);seed=int(sys.argv[2]);cap=int(sys.argv[3]);events=Path(sys.argv[4]);args=sys.argv[5:]
sys.path.insert(0,str(vendor))
import numpy as np
import functions
np.random.seed(seed);random.seed(seed)
attempts=0
def attempt_limit(paths,advanced):
 global attempts
 stop=attempts>=cap
 with events.open("a") as f:f.write(json.dumps(dict(attempts_started=attempts,cap=cap,stop=stop))+"\n")
 if stop:
  print(f"INDEPENDENT_ATTEMPT_CAP reached: {attempts}/{cap}",flush=True);return True
 attempts+=1
 return False
functions.check_n_trajectories=attempt_limit
sys.argv=[str(vendor/"bindcraft.py")]+args
runpy.run_path(str(vendor/"bindcraft.py"),run_name="__main__")
