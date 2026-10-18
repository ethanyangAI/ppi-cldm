import sys
from pathlib import Path
import numpy as np
from ppiblocker.common import Run,load_run,record_file,atomic_json,require
from ppiblocker.structure import read_structure,interface,superpose,transform
root=Path("/lustre/users/u21111210118/projects/test9")
experimental,predicted=sys.argv[1:3]
ref=load_run(experimental,{"POSE_ACCEPTED"});pred=load_run(predicted,{"POSE_ACCEPTED"})
run=Run(root,"05_validation",[record_file(experimental),record_file(predicted)])
try:
 a,b=read_structure(ref["outputs"]["native"]["path"])[0]
 ca=lambda c:np.array([r["ca"] for r in c["residues"]])
 native_pairs={tuple(x) for x in interface(a,b)["residue_pairs"]}
 rows=[]
 for i in range(3):
  aa,bb=read_structure(pred["outputs"][f"model_{i}_structure"]["path"])[0]
  require(a["sequence"]==aa["sequence"] and b["sequence"]==bb["sequence"],"BENCHMARK_SEQUENCE_MISMATCH","Constructs differ")
  r,t,trmsd=superpose(ca(aa),ca(a))
  prmsd=float(np.sqrt(np.mean(np.sum((ca(bb)@r+t-ca(b))**2,axis=1))))
  pairs={tuple(x) for x in interface(aa,bb)["residue_pairs"]}
  rows.append({"model":i,"target_ca_rmsd_angstrom":trmsd,
               "partner_ca_rmsd_after_target_alignment_angstrom":prmsd,
               "native_contact_recall":len(pairs&native_pairs)/len(native_pairs),
               "predicted_contact_precision":len(pairs&native_pairs)/len(pairs)})
 out=run.path/"outputs/benchmark_accuracy.json"
 atomic_json(out,{"experimental_reference":"1YCR biological assembly 1","protein_pair_count":1,
                  "sampled_model_count":3,"training_leakage_controlled":False,
                  "interpretation":"Engineering accuracy check on a familiar complex; not independent generalization evidence",
                  "models":rows})
 run.output("accuracy",out)
 print(run.finish("VALIDATION_COMPLETE","known_complex_engineering_check"))
except Exception as e:run.fail(e);raise
