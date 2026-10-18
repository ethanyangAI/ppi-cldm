import shutil,requests
from util import *
run=Run(R,"89_strengthening_positive_control",[record_file(S/"protocol.json")]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 p,m=one("82_strengthening_extensions","EXTENSION_INPUTS_READY");plan=read_json(verify_file(m["outputs"]["plan"]));h=next(v for v in plan["homologs"] if v["name"]=="KLHL12")
 response=requests.get("https://files.rcsb.org/download/6TTK-assembly1.cif",timeout=90);response.raise_for_status();f=run.path/"outputs/6TTK.cif";f.write_bytes(response.content)
 cs=chains(f);short=[c for c in cs if 5<=len(c["sequence"])<=40];require(short,"NATIVE_DVL1","No peptide")
 seqs={c["sequence"] for c in short};require(len(seqs)==1,"AMBIGUOUS_PEPTIDE",str(seqs))
 from Bio import Align
 aligner=Align.PairwiseAligner(mode="local",match_score=2,mismatch_score=-4,open_gap_score=-6,extend_gap_score=-.5)
 accepted=False
 for c in cs:
  if len(c["sequence"])<200:continue
  al=aligner.align(h["sequence"],c["sequence"])[0];pairs=[(int(a),int(b)) for a,b in al.indices.T if a>=0 and b>=0]
  if len(pairs)/len(h["sequence"])>.9 and sum(h["sequence"][a]==c["sequence"][b] for a,b in pairs)/len(pairs)>.98:accepted=True
 require(accepted,"KLHL12_CONTEXT_IDENTITY","6TTK versus frozen KLHL12 construct")
 entry=dict(id="native_KLHL12_DVL1",parent="native",kind="specificity_positive_control",target_sequence=h["sequence"],sequence=next(iter(seqs)),target="KLHL12",msa_mode="single",msa=None,slot=113,source=record_file(f))
 atomic_json(run.path/"outputs/entry.json",entry);run.output("entry",run.path/"outputs/entry.json");run.output("structure",f)
 print(run.finish("HOMOLOG_POSITIVE_CONTROL_READY","experimental_reference_not_predicted_result"),flush=True)
except Exception as x:run.fail(x);raise

