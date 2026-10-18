#!/usr/bin/env python3
import gc,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import torch
import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf
from rfdiffusion.inference import utils as iu
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/current_rfd_readiness_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
assert not torch.cuda.is_available() and torch.cuda.device_count()==0 and os.environ["CUDA_VISIBLE_DEVICES"]==""
def rec(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for block in iter(lambda:f.read(4*1024*1024),b""):h.update(block)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
runtime=R/"steps/22_matched_benchmark/settings/pilot_v7/source/benchmark_runtime.py";assert rec(runtime)["sha256"]=="1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17"
checkpoint=R/"assets/rfdiffusion/Complex_base_ckpt.pt";assert rec(checkpoint)["sha256"]=="76e4e260aefee3b582bd76b77ab95d2592e64f00c51bf344968ab9239f3250bc"
overrides=["inference.ckpt_override_path="+str(checkpoint),"inference.schedule_directory_path="+str(S/"work/rfd_schedules")]
started=time.time()
with hydra.initialize_config_dir(config_dir=str(R/"vendor/RFdiffusion/config/inference"),version_base=None):
 conf=hydra.compose(config_name="base",overrides=overrides,return_hydra_config=True)
HydraConfig.instance().set_config(conf);conf=OmegaConf.masked_copy(conf,[key for key in conf if key!="hydra"])
sampler=iu.sampler_selector(conf);assert sampler.device.type=="cpu"
assert sampler.model is not None
rfd={"status":"OFFICIAL_RFD_CHECKPOINT_AND_SELFCONDITIONING_CONSTRUCTOR_CPU_PASS","class":type(sampler).__name__,"device":str(sampler.device),"seconds":time.time()-started,"checkpoint":rec(checkpoint),"scientific_inference_run":False}
del sampler;gc.collect()
sys.path.insert(0,str(R/"vendor/ProteinMPNN"))
from protein_mpnn_utils import ProteinMPNN
weight=R/"vendor/ProteinMPNN/vanilla_model_weights/v_48_020.pt";ckpt=torch.load(weight,map_location="cpu")
mpnn=ProteinMPNN(num_letters=21,node_features=128,edge_features=128,hidden_dim=128,num_encoder_layers=3,num_decoder_layers=3,augment_eps=0.,k_neighbors=ckpt["num_edges"]);mpnn.load_state_dict(ckpt["model_state_dict"])
assert all(torch.isfinite(v).all() for v in mpnn.state_dict().values())
result={"status":"CURRENT_RFD_AND_ORIGINAL_MPNN_CPU_CONSTRUCTORS_PASS","rfd":rfd,"mpnn":{"status":"PASS","weight":rec(weight),"state_tensors":len(mpnn.state_dict())},"runtime_source":rec(runtime),"helper_source":rec(Path(__file__)),"cpu_only":True,"job":os.environ["SLURM_JOB_ID"]}
(O/"acceptance.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))

