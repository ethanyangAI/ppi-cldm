import shutil
from Bio.PDB import PDBParser
from scipy.spatial import cKDTree
from util import *
from dcd_reader import read_openmm_dcd
run=Run(R,"93_strengthening_trajectory_review",[]);shutil.copy2(__file__,run.path/"qc/driver.py");shutil.copy2(S/"dcd_reader.py",run.path/"qc/dcd_reader.py")
try:
 rows=[]
 for p in (R/"steps/85_strengthening_md/runs").glob("*/manifest.json"):
  m=read_json(p)
  if m["status"]!="MD_DIAGNOSTIC_COMPLETE":continue
  raw=read_json(verify_file(m["outputs"]["results"]));dcd=verify_file(m["outputs"]["trajectory"]);xyz=read_openmm_dcd(dcd)
  require(xyz.shape[0]==100,"TRAJECTORY_FRAMES",str(p));prepared=p.parent/"work/md/prepared.pdb"
  model=PDBParser(QUIET=True).get_structure("prepared",str(prepared));atoms=list(model.get_atoms());require(len(atoms)==xyz.shape[1],"TOPOLOGY_ATOMS",str(p))
  cid=list(dict.fromkeys(a.get_parent().get_parent().id for a in atoms));require(len(cid)==2,"MD_CHAINS",str(cid))
  heavy=[[i for i,a in enumerate(atoms) if a.get_parent().get_parent().id==c and a.element not in ("H","D")] for c in cid]
  cas=[[i for i,a in enumerate(atoms) if a.get_parent().get_parent().id==c and a.name=="CA"] for c in cid]
  last=np.array([a.coord for a in PDBParser(QUIET=True).get_structure("final",str(verify_file(m["outputs"]["final"]))).get_atoms()],float)
  discrepancy=float(np.sqrt(np.mean(np.sum((xyz[-1]-last)**2,axis=1))));require(discrepancy<.002,"DCD_PDB_COORDINATES",str(discrepancy))
  ref=xyz[0];neighbors=cKDTree(ref[heavy[0]]).query_ball_tree(cKDTree(ref[heavy[1]]),5);contacts={(i,j) for i,js in enumerate(neighbors) for j in js};trace=[]
  for i,x in enumerate(xyz):
   r,t,tr=superpose(x[cas[0]],ref[cas[0]]);neighbors=cKDTree(x[heavy[0]]).query_ball_tree(cKDTree(x[heavy[1]]),5);now={(j,k) for j,ks in enumerate(neighbors) for k in ks}
   trace.append(dict(time_ps=(i+1)*10,target_ca_rmsd=tr,binder_pose_rmsd=float(np.sqrt(np.mean(np.sum((x[cas[1]]@r+t-ref[cas[1]])**2,axis=1)))),binder_fold_rmsd=superpose(x[cas[1]],ref[cas[1]])[2],initial_atom_contact_retention=len(contacts&now)/max(1,len(contacts)),atom_contacts=len(now)))
  entry=dict(id=m["entry_id"],seed=m["seed"],platform=raw["platform"],raw_manifest=record_file(p),topology=record_file(prepared),trajectory=m["outputs"]["trajectory"],frames=100,units="angstrom",reference="first saved production frame at10ps",final_pdb_rmsd=discrepancy,trace=trace)
  rows.append(entry);run.manifest["inputs"].append(record_file(p))
 require(len(rows)==9 and len({(v["id"],v["seed"]) for v in rows})==9,"TRAJECTORY_COVERAGE",str(len(rows)))
 atomic_json(run.path/"outputs/results.json",dict(trajectories=rows,analysis_rule="Recompute geometry from saved DCD independently; raw online trace preserved; final PDB must match last DCD within0.002A"));run.output("results",run.path/"outputs/results.json")
 print(run.finish("ALL_TRAJECTORIES_VERIFIED","computational_only"),flush=True)
except Exception as x:run.fail(x);raise

