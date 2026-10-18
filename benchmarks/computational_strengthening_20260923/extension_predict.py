import re,shutil
from util import *
from ppiblocker.backends import require_gpu
slot=int(sys.argv[1]);run=Run(R,"83_strengthening_extension_predict",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 require_gpu();p,m=one("82_strengthening_extensions","EXTENSION_INPUTS_READY");plan=read_json(verify_file(m["outputs"]["plan"]));e=plan["entries"][slot] if slot<113 else read_json(verify_file(one("89_strengthening_positive_control","HOMOLOG_POSITIVE_CONTROL_READY")[1]["outputs"]["entry"])) if slot==113 else read_json(verify_file(one("92_strengthening_mutant_monomers","MUTANT_MONOMER_INPUTS_READY")[1]["outputs"]["plan"]))["entries"][slot-114]
 run.manifest.update(inputs=[record_file(p),record_file(S/"protocol.json")],entry_id=e["id"],slot=slot);run.save()
 for w in plan["weights"]:verify_file(w)
 inp=run.path/"work/inputs";inp.mkdir();out=run.path/"work/models"
 if e.get("msa"):shutil.copy2(verify_file(e["msa"]),inp/(e["id"]+".a3m"))
 else:(inp/(e["id"]+".fasta")).write_text(">"+e["id"]+"\n"+(e["target_sequence"]+":" if e["target_sequence"] else "")+e["sequence"]+"\n")
 model="alphafold2_ptm" if e["kind"]=="monomer" else "alphafold2_multimer_v3"
 args=[R/"env/colabfold/bin/colabfold_batch",inp,out,"--model-type",model,"--num-models","5","--model-order","1,2,3,4,5","--num-seeds","3","--random-seed","1042","--num-recycle","12","--recycle-early-stop-tolerance","0.5","--stop-at-score","100","--msa-mode","single_sequence","--max-msa","128:256","--num-relax","0","--data",plan["assets"]]
 checked_command(args,run.path/"work",run.path/"logs/predict.log",env(True),timeout=18000)
 rows=[];keys=set()
 for f in sorted(out.glob(e["id"]+"_unrelaxed_rank_*.pdb")):
  ma=re.search(r"model_(\d+).*seed_(\d+)",f.name);require(ma,"MODEL_NAME",f.name);key=tuple(map(int,ma.groups()));keys.add(key)
  cs=chains(f);expected=[e["target_sequence"],e["sequence"]] if e["target_sequence"] else [e["sequence"]]
  require([c["sequence"] for c in cs]==expected,"SEQUENCE_MISMATCH",e["id"])
  scores=f.with_name(f.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json"));verify_file(record_file(scores))
  rows.append(dict(pdb=record_file(f),scores=record_file(scores),weight=key[0],seed=key[1]))
 require(keys=={(i,j) for i in range(1,6) for j in (1042,1043,1044)},"ENSEMBLE_COVERAGE",str(keys))
 atomic_json(run.path/"outputs/results.json",dict(entry=e,models=rows));run.output("results",run.path/"outputs/results.json")
 print(run.finish("EXTENSION_PREDICTION_COMPLETE","computational_only",dict(models=15)),flush=True)
except Exception as x:run.fail(x);raise

