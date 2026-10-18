import random,hashlib,requests,shutil
from util import *
run=Run(R,"82_strengthening_extensions", [record_file(SETUP),record_file(S/"protocol.json")]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 bp=baseplan();cands=bp["candidates"];entries=[]
 for e in bp["all_controls"]+cands:entries.append(dict(id=e["id"]+"_mono",parent=e["id"],kind="monomer",sequence=e["sequence"],target_sequence="",reference=e["backbone"]))
 # Construct perturbations without using their predicted scores.
 for e in cands:
  seq=e["sequence"];start=seq.index("DEETGEFL");protected=set(range(start,start+8));design=chains(verify_file(e["backbone"]))
  counts={}
  for i,j in interface(*design)["residue_pairs"]:
   if j-1 not in protected and seq[j-1] not in "AG":counts[j-1]=counts.get(j-1,0)+1
  sites=sorted(counts,key=lambda i:(-counts[i],i))[:3]
  variants={}
  a=list(seq)
  for i in (start+2,start+5):a[i]="A"
  variants["motif_EE_AA"]="".join(a)
  a=list(seq)
  for i in sites:a[i]="A"
  variants["scaffold_contact_AAA"]="".join(a)
  for seed in (2142,2143):
   a=list(seq);idx=[i for i in range(len(seq)) if i not in protected];values=[a[i] for i in idx];random.Random(seed).shuffle(values)
   for i,v in zip(idx,values):a[i]=v
   variants["flank_shuffle_"+str(seed)]="".join(a)
  a=list(seq);random.Random(2144).shuffle(a);variants["full_shuffle"]="".join(a)
  for name,seqv in variants.items():entries.append(dict(id=e["id"]+"_"+name,parent=e["id"],kind="ablation",sequence=seqv,target_sequence=e["target_sequence"],group="P09",perturbation=name,scaffold_mutation_positions=[i+1 for i in sites],synthetic_control_label=None))
 native=chains(verify_file(cands[0]["native"]))
 entries.append(dict(id="native_NRF2_peptide",parent="native",kind="native",sequence=native[1]["sequence"],target_sequence=cands[0]["target_sequence"],group="P09"))
 receipts={};fails=[]
 def fetch(url,name):
  response=requests.get(url,timeout=90);response.raise_for_status();p=run.path/"outputs"/name;p.write_bytes(response.content);receipts[name]=dict(url=url,file=record_file(p));return p
 for pdb in ("2FLU","1X2R","2DYH","3WN7","4CH9","2VPJ"):
  try:
   fetch("https://files.rcsb.org/download/"+pdb+"-assembly1.cif",pdb+".cif")
   fetch("https://data.rcsb.org/rest/v1/core/entry/"+pdb,pdb+"_entry.json")
  except Exception as x:fails.append(dict(item=pdb,error=str(x)))
 for accession in ("Q14145","Q9UH77","Q53G59"):
  try:fetch("https://rest.uniprot.org/uniprotkb/"+accession+".json",accession+".json")
  except Exception as x:fails.append(dict(item=accession,error=str(x)))
 seqfull=read_json(run.path/"outputs/Q14145.json")["sequence"]["value"];require(cands[0]["target_sequence"] in seqfull,"TARGET_CANONICAL","KEAP1 domain mismatch")
 homologs=[]
 for name,pdb,acc in (("KLHL3","4CH9","Q9UH77"),("KLHL12","2VPJ","Q53G59")):
  raw=chains(run.path/"outputs"/(pdb+".cif"));full=read_json(run.path/"outputs"/(acc+".json"))["sequence"]["value"]
  # Observed chain may omit loops; use ordered subsequence identity, then contiguous canonical span.
  from Bio import Align
  aligner=Align.PairwiseAligner(mode="local",match_score=2,mismatch_score=-5,open_gap_score=-6,extend_gap_score=-.5)
  choices=[]
  for c in raw:
   if len(c["sequence"])<200:continue
   al=aligner.align(full,c["sequence"])[0];pairs=[(int(a),int(b)) for a,b in al.indices.T if a>=0 and b>=0]
   identity=sum(full[a]==c["sequence"][b] for a,b in pairs)/max(1,len(pairs))
   if identity>=.98 and len(pairs)/len(c["sequence"])>=.95:choices.append((c,pairs,identity))
  require(choices,"HOMOLOG_IDENTITY",name);c,pairs,identity=choices[0];lo=min(a for a,b in pairs);hi=max(a for a,b in pairs)+1;sequence=full[lo:hi]
  homologs.append(dict(name=name,pdb=pdb,accession=acc,start=lo+1,end=hi,sequence=sequence,observed_identity=identity))
 for e in cands:
  for h in homologs:entries.append(dict(id=e["id"]+"_"+h["name"],parent=e["id"],kind="specificity",target_sequence=h["sequence"],sequence=e["sequence"],target=h["name"],msa_mode="single"))
  for name,seqt in (("KEAP1_single",e["target_sequence"]),("KEAP1_full",seqfull),("homodimer",e["sequence"])):
   entries.append(dict(id=e["id"]+"_"+name,parent=e["id"],kind="self_association" if name=="homodimer" else "context",target_sequence=seqt,sequence=e["sequence"],target=name,msa_mode="single"))
 # Matched positive control for homolog sensitivity where an experimental partner is resolved.
 partner=min(chains(run.path/"outputs/4CH9.cif"),key=lambda c:len(c["sequence"]))
 require(5<len(partner["sequence"])<50,"HOMOLOG_NATIVE_PARTNER","4CH9")
 entries.append(dict(id="native_KLHL3_WNK4",parent="native",kind="specificity_positive_control",target_sequence=homologs[0]["sequence"],sequence=partner["sequence"],target="KLHL3",msa_mode="single"))
 try:
  p=fetch("https://alphafold.ebi.ac.uk/api/prediction/Q14145","KEAP1_AFDB.json");rows=read_json(p);fetch(rows[0]["pdbUrl"],"KEAP1_AFDB.pdb")
 except Exception as x:fails.append(dict(item="KEAP1_AFDB",error=str(x)))
 # Reuse pinned MSA only for ablation/native matched target.
 p=run.path/"outputs/msa_plan.json";atomic_json(p,dict(entries=[e for e in entries if e.get("group")=="P09"]))
 mp=R/"steps/24_target_msa/runs/20260922T053230Z_5f5d81e4f519/manifest.json"
 checked_command([R/"env/colabfold/bin/python",R/"source/benchmarks/runtime_pilot_20260922/serialize_msa_parallel.py",p,verify_file(read_json(mp)["outputs"]["receipt"]),run.path/"outputs/msa"],run.path/"work",run.path/"logs/msa.log",env(),timeout=900)
 mi=read_json(run.path/"outputs/msa/inputs.json")
 for i,e in enumerate(entries):e["slot"]=i;e["msa"]=mi.get(e["id"])
 # Asset reuse in a new directory; verify every npz is readable, preserve source files.
 import numpy as np
 asset=R/"assets/strengthening_af2";(asset/"params").mkdir(parents=True,exist_ok=True);weights=[]
 for suffix,source in (("ptm",R/"assets/bindcraft/params"),("multimer_v3",R/"assets/colabfold/params")):
  for k in range(1,6):
   p=source/f"params_model_{k}_{suffix}.npz"
   with np.load(p) as z:require(len(z.files)>100,"WEIGHT_ARCHIVE",str(p))
   dest=asset/"params"/p.name
   if not dest.exists():dest.symlink_to(p)
   weights.append(record_file(p))
 for marker in ("download_finished.txt","download_complexes_multimer_v3_finished.txt"):(asset/"params"/marker).write_text("Reused verified project weights; see stage82 receipt.\n")
 atomic_json(run.path/"outputs/plan.json",dict(entries=entries,homologs=homologs,fetches=receipts,fetch_failures=fails,weights=weights,assets=str(asset)))
 run.output("plan",run.path/"outputs/plan.json");run.manifest["entry_count"]=len(entries)
 print(run.finish("EXTENSION_INPUTS_READY","protocol_frozen",dict(fetch_failures=fails)),flush=True)
except Exception as x:run.fail(x);raise

