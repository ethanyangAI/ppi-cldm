"""Explicit FP32 compatibility profile for pre-Ampere GPUs; never a silent precision change."""
import sys,json
from pathlib import Path
import torch
out=Path(sys.argv[1]);sys.argv=[sys.argv[0]]+sys.argv[2:]
assert torch.cuda.is_available(),"Allocated CUDA GPU required"
probe=dict(torch=torch.__version__,cuda=torch.version.cuda,device=torch.cuda.get_device_name(0),capability=list(torch.cuda.get_device_capability(0)),bf16_supported=torch.cuda.is_bf16_supported())
if not probe["bf16_supported"]:
 original=torch.amp.autocast
 class FullPrecisionCUDA(original):
  def __init__(self,device_type,dtype=None,enabled=True,cache_enabled=None):
   if device_type=="cuda" and dtype==torch.bfloat16:enabled=False
   super().__init__(device_type,dtype=dtype,enabled=enabled,cache_enabled=cache_enabled)
 torch.amp.autocast=FullPrecisionCUDA
 torch.autocast=FullPrecisionCUDA
 from rfd3.model.layers.pairformer_layers import AttentionPairBiasPairformerDeepspeed
 previous=AttentionPairBiasPairformerDeepspeed.__init__
 def initialize(self,*args,**kwargs):
  previous(self,*args,**kwargs);self.force_bfloat16=False
 AttentionPairBiasPairformerDeepspeed.__init__=initialize
 probe["profile"]="FP32_PRE_AMPERE_COMPATIBILITY"
 probe["changes"]=["disable CUDA BF16 autocast","disable Pairformer forced BF16 input cast"]
else:probe["profile"]="OFFICIAL_DEFAULT_PRECISION"
out.write_text(json.dumps(probe,indent=2));print("RUNTIME_PROFILE",probe,flush=True)
from rfd3.cli import app
app()
