#!/usr/bin/env python3
"""CPU-only concrete entrypoint/weight/source/binary acceptance."""
import gc,hashlib,importlib.util,io,json,os,subprocess,sys,tarfile,time,urllib.request
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/current_bc_readiness_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
assert os.environ.get("JAX_PLATFORMS")=="cpu" and os.environ.get("CUDA_VISIBLE_DEVICES")=="";assert sys.prefix==str(R/"env/bindcraft")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def command(a):
 p=subprocess.run(a,text=True,capture_output=True);return {"argv":a,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
def write(name,v):(O/name).write_text(json.dumps(v,indent=2)+"\n")
source_freeze=json.loads((S/"runs/source_12947/outputs/sources.json").read_text())
for name,v in source_freeze.items():
 p=Path(v["path"])
 assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=p,text=True).strip()==v["revision"]
 for rel,x in v["files"].items():
  file=p/rel;assert file.stat().st_size==x["bytes"] and sha(file)==x["sha256"],(name,rel)
print("BINDCRAFT_COLABDESIGN_FROZEN_SOURCE_BYTES_VERIFIED",flush=True)
write("current_official_bc_sources.json",source_freeze)
archives=S/"source_archives";archives.mkdir(exist_ok=True);upstream=[]
vendor_lock=json.loads((R/"source/environment/vendor-lock.json").read_text())
for name,v in vendor_lock.items():
 parts=v["repository"].rstrip("/").split("/");org,repo=parts[-2:];url=f"https://codeload.github.com/{org}/{repo}/tar.gz/{v['commit']}"
 p=archives/f"{name}-{v['commit']}.tar.gz"
 if not p.exists():
  partial=p.with_suffix(".partial")
  with urllib.request.urlopen(url,timeout=180) as response,open(partial,"wb") as out:
   while True:
    block=response.read(4*1024*1024)
    if not block:break
    out.write(block)
  partial.replace(p)
 receipt=rec(p);assert receipt["sha256"]==v["sha256"],(name,"historical official tar mismatch",receipt)
 mismatches=[];checked=0
 with tarfile.open(p,"r:gz") as tar:
  for member in tar:
   if not member.isfile():continue
   relative=Path(member.name).parts[1:];local=R/"vendor"/name/Path(*relative);expected=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
   if not local.is_file() or sha(local)!=expected:mismatches.append(str(Path(*relative)))
   checked+=1
 item={"name":name,"repository":v["repository"],"revision":v["commit"],"archive_url":url,"archive":receipt,"files_checked":checked,"mismatches":mismatches};upstream.append(item)
 print("UPSTREAM_SOURCE",name,"files",checked,"mismatches",mismatches,flush=True)
write("upstream_sources.json",upstream)
assert all(not x["mismatches"] for x in upstream),upstream
import importlib.metadata as md
installed=Path(md.distribution("colabdesign").locate_file("colabdesign"));vendor=R/"vendor/ColabDesign/colabdesign";matched=[];omitted=[]
# Pip wheels include only declared packages; vendor legacy modules need not be shipped.
for dest in sorted(installed.rglob("*")):
 if not dest.is_file() or dest.suffix not in [".py",".pkl"]:continue
 relative=dest.relative_to(installed);source=vendor/relative
 assert source.is_file() and dest.read_bytes()==source.read_bytes(),str(relative)
 matched.append({"relative":str(relative),"installed":rec(dest),"official":rec(source)})
for source in sorted(vendor.rglob("*")):
 if source.is_file() and source.suffix in [".py",".pkl"] and not (installed/source.relative_to(vendor)).exists():omitted.append(str(source.relative_to(vendor)))
assert all((installed/relative).is_file() for relative in ["af/model.py","af/inputs.py","af/loss.py","mpnn/model.py","mpnn/modules.py","shared/model.py"])
write("current_installed_colabdesign_byte_equivalence.json",{"status":"PASS","files":matched,"vendor_files_not_shipped_by_pip":omitted,"scope":"every actual installed .py/.pkl is byte-identical to pinned official vendor; all required AF/MPNN/shared entry modules present; omitted vendor legacy/nonpackage files declared"})
import jax,numpy as np
assert jax.default_backend()=="cpu",jax.devices()
from colabdesign.af.alphafold.model.data import get_model_haiku_params
params=[];started=time.time()
for suffix in ["ptm","multimer_v3"]:
 for n in range(1,6):
  name=f"model_{n}_{suffix}";value=get_model_haiku_params(name,str(R/"assets/colabfold"))
  assert value and all(value.values()),name
  tensors=[x for block in value.values() for x in block.values()]
  assert tensors and all(np.asarray(x).size>0 and np.isfinite(np.asarray(x)).all() for x in tensors),name
  params.append({"model_name":name,"tensor_count":len(tensors),"scalar_count":sum(np.asarray(x).size for x in tensors),"parameter_file":rec(R/f"assets/colabfold/params/params_{name}.npz")})
  del tensors,value;gc.collect();print("AF2_WEIGHT_READ",name,flush=True)
write("af2_parameter_loaders.json",{"status":"ALL_TEN_OFFICIAL_AF2_PARAMETER_FILES_FULLY_READ_FINITE","seconds":time.time()-started,"backend":jax.default_backend(),"models":params})
from colabdesign import mk_afdesign_model,mk_mpnn_model
for multimer,name,initial_guess in [(False,"model_1_ptm",True),(False,"model_1_ptm",False),(False,"model_2_ptm",False),(True,"model_1_multimer_v3",False)]:
 started=time.time();model=mk_afdesign_model(protocol="binder",use_multimer=multimer,use_initial_guess=initial_guess,use_initial_atom_pos=False,num_recycles=3,data_dir=str(R/"assets/colabfold"),model_names=[name])
 model.prep_inputs(pdb_filename=str(R/"vendor/BindCraft/example/PDL1.pdb"),chain="A",binder_len=65,rm_target_seq=False,rm_target_sc=False,seed=1042)
 print("REAL_AF2_BINDER_ENTRYPOINT_CONSTRUCTED_CPU",name,"seconds",time.time()-started,flush=True)
 del model;gc.collect()
mpnn=[]
for weights in ["original","soluble"]:
 model=mk_mpnn_model(weights=weights,seed=1042)
 assert model._model.params
 mpnn.append({"weights":weights,"status":"CPU_CHECKPOINT_AND_MODEL_CONSTRUCTION_PASS"})
 del model;gc.collect()
write("entrypoints.json",{"status":"AF2_PTM_MULTIMER_AND_ORIGINAL_SOLUBLE_MPNN_CPU_CONSTRUCTORS_PASS","mpnn":mpnn,"inference_run":False,"gpu_requested":False})
import pyrosetta
pyrosetta.init("-mute all -ignore_unrecognized_res -ignore_zero_occupancy")
pose=pyrosetta.pose_from_pdb(str(R/"vendor/BindCraft/example/PDL1.pdb"));assert pose.total_residue()>0
binary=[]
for name in ["dssp","DAlphaBall.gcc"]:
 p=R/"vendor/BindCraft/functions"/name;ldd=command(["ldd",str(p)])
 assert "not found" not in ldd["stdout"],(name,ldd)
 binary.append({"name":name,"file":rec(p),"ldd":ldd})
dssp=R/"vendor/BindCraft/functions/dssp"
version=command([str(dssp),"--version"]);assert version["returncode"]==0,version
from Bio.PDB import PDBParser,DSSP
structure=PDBParser(QUIET=True).get_structure("PDL1",str(R/"vendor/BindCraft/example/PDL1.pdb"))
dssppose=DSSP(structure[0],str(R/"vendor/BindCraft/example/PDL1.pdb"),dssp=str(dssp));assert len(dssppose)>0
ffmpeg=command([str(R/"env/bindcraft/bin/ffmpeg"),"-version"]);assert ffmpeg["returncode"]==0,ffmpeg
write("structure_scoring_binaries.json",{"status":"PYROSETTA_POSE_AND_DSSP_FUNCTIONAL_DALPHABALL_LINKAGE_PASS","pyrosetta_version":pyrosetta.version(),"pose_residues":pose.total_residue(),"dssp_residues":len(dssppose),"dssp_version":version,"binaries":binary,"ffmpeg":ffmpeg})
p=O/"alphafold_official_README.md";historical_license=S/"runs/readiness_12980/outputs/alphafold_official_README.md";p.write_bytes(historical_license.read_bytes())
license_metadata=json.loads((S/"runs/readiness_12980/outputs/licenses.json").read_text())["alphafold_parameters"]
revision=license_metadata["revision"];url=license_metadata["source_url"];assert "CC BY 4.0" in p.read_text()
write("licenses.json",{"status":"OFFICIAL_LICENSE_SOURCES_RECORDED","alphafold_parameters":{"license":"CC BY 4.0","source_url":url,"revision":revision,"receipt":rec(p),"source_page":"https://github.com/google-deepmind/alphafold"},"rfdiffusion":{"license":"BSD, includes code and model weights","source_page":"https://github.com/RosettaCommons/RFdiffusion","receipt":rec(R/"vendor/RFdiffusion/LICENSE")},"protein_mpnn":{"license":"MIT","source_page":"https://github.com/dauparas/ProteinMPNN"},"bindcraft":{"license":"MIT","source_page":"https://github.com/martinpacesa/BindCraft"},"pyrosetta":{"asset_receipt":rec(R/"assets/pyrosetta/receipt.json"),"scope":"Existing academic-access release; no commercial license claim; no new credential required for this private installation"}})
pip=command([sys.executable,"-m","pip","check"]);assert pip["returncode"]==0,pip;write("pip_check.json",pip)
write("current_helper_source.json",{"helper":rec(Path(__file__))})
ps=[p for p in O.iterdir() if p.is_file()]
write("acceptance.json",{"status":"BOTH_PRIVATE_METHOD_RUNTIMES_CPU_READY_GPU_ENGINEERING_PILOT_PENDING","job_id":os.environ["SLURM_JOB_ID"],"gpu_requested":False,"inference_run":False,"records":[rec(p) for p in sorted(ps)],"current_official_source_verification":rec(O/"current_official_bc_sources.json"),"adapter_source":rec(R/"steps/22_matched_benchmark/settings/pilot_v7/source/benchmark_runtime.py"),"pending":["actual GPU/JAX CUDA compatibility and full engineering attempt for each method","native RF output chain identity and AF2 full validation on prepared target"],"credentials_required_now":[]})
print("BOTH_PRIVATE_METHOD_RUNTIMES_CPU_READY_GPU_ENGINEERING_PILOT_PENDING",flush=True)


