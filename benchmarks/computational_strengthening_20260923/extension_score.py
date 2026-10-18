import shutil,re
from Bio.PDB import ShrakeRupley,PDBParser
from util import *
from ppiblocker.af2_review import atom_overlap
slot=int(sys.argv[1]);run=Run(R,"87_strengthening_extension_score",[]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 found=[(p,read_json(p)) for p in (R/"steps/83_strengthening_extension_predict/runs").glob("*/manifest.json") if read_json(p)["status"]=="EXTENSION_PREDICTION_COMPLETE" and read_json(p)["slot"]==slot]
 require(len(found)==1,"EXTENSION_UNIQUE",str(slot));p,m=found[0];data=read_json(verify_file(m["outputs"]["results"]));e=data["entry"];run.manifest.update(inputs=[record_file(p)],entry_id=e["id"],slot=slot);run.save()
 _,sm=one("79_strengthening_setup","STRENGTHENING_INPUTS_READY");ipsae=verify_file(read_json(verify_file(sm["outputs"]["ipsae_source"]))["files"]["ipsae.py"])
 bound=None
 if e["kind"]=="monomer":
  for stage in ("74_af2_review_predict","80_strengthening_predict","83_strengthening_extension_predict"):
   for pp in (R/"steps"/stage/"runs").glob("*/manifest.json"):
    mm=read_json(pp)
    if mm["status"] in ("AF2_REVIEW_PREDICTION_COMPLETE","EXTENSION_PREDICTION_COMPLETE") and mm.get("entry_id")==e["parent"]:
     dd=read_json(verify_file(mm["outputs"].get("predictions",mm["outputs"].get("results"))));zz=next(v for v in dd.get("expanded",dd.get("models")) if v["weight"]==1 and v["seed"]==1042);bound=chains(verify_file(zz["pdb"]))[1]
  require(bound is not None,"BOUND_REFERENCE",e["parent"])
 rows=[]
 for z in data["models"]:
  f=verify_file(z["pdb"]);s=read_json(verify_file(z["scores"]));cs=chains(f);row=dict(weight=z["weight"],seed=z["seed"],pdb=z["pdb"])
  total=sum(len(c["sequence"]) for c in cs)
  require(np.asarray(s["plddt"]).shape==(total,) and np.asarray(s["pae"]).shape==(total,total),"CONFIDENCE_SHAPE",e["id"])
  require(np.isfinite(s["plddt"]).all() and np.isfinite(s["pae"]).all(),"NONFINITE_CONFIDENCE",e["id"])
  if e["kind"]=="monomer":
   reference=chains(verify_file(e["reference"]))[1];require(reference["sequence"]==e["sequence"] or e["parent"].startswith("dev_"),"MONOMER_REFERENCE_IDENTITY",e["id"])
   row.update(plddt=float(np.mean(s["plddt"])),design_fold_rmsd=superpose(ca(cs[0]),ca(reference))[2],bound_fold_rmsd=superpose(ca(cs[0]),ca(bound))[2])
   structure=PDBParser(QUIET=True).get_structure("mono",str(f));ShrakeRupley(n_points=100).compute(structure,level="R")
   vals=[(r,float(r.sasa)) for r in structure.get_residues() if "CA" in r];total=sum(v for r,v in vals);hydro=sum(v for r,v in vals if r.resname in ("ALA","VAL","ILE","LEU","MET","PHE","TRP","TYR"))
   row.update(total_sasa_A2=total,hydrophobic_sasa_A2=hydro,hydrophobic_sasa_fraction=hydro/max(total,1),aggregation_interpretation="surface exposure diagnostic, not measured solubility")
  else:
   n=len(e["target_sequence"]);pae=np.asarray(s["pae"]);it=interface(*cs);pairs=it["residue_pairs"];pos=[n+j-1 for j in it["partner_residues"]]
   row.update(iptm=float(s["iptm"]),binder_plddt=float(np.mean(s["plddt"][n:]))/100,interface_pae=float(np.mean([v for i,j in pairs for v in (pae[i-1,n+j-1],pae[n+j-1,i-1])])) if pairs else None,interface_binder_plddt=float(np.mean(np.asarray(s["plddt"])[pos]))/100 if pos else None,contacts=len(pairs),sterics=atom_overlap(*cs))
   case=run.path/"work"/f'{z["weight"]}_{z["seed"]}';case.mkdir();model=case/"model.pdb";shutil.copy2(f,model)
   checked_command([R/"env/core/bin/python",ipsae,verify_file(z["scores"]),model,"10","15"],case,run.path/"logs"/f'{z["weight"]}_{z["seed"]}.log',env(),timeout=120)
   values=[]
   for line in (case/"model_10_15.txt").read_text().splitlines():
    a=line.split()
    if len(a)>6 and a[0] in ("A","B") and a[1] in ("A","B") and a[4]=="asym":values.append(float(a[5]))
   require(len(values)==2,"IPSAE_DIRECTIONAL",str(values));row["ipsae_min"]=min(values);row["ipsae_max"]=max(values)
  if e["kind"]!="monomer" and e["target_sequence"]==baseplan()["candidates"][0]["target_sequence"]:
   native=chains(verify_file(baseplan()["candidates"][0]["native"]));ni=interface(*native);pi=interface(*cs);nr=set(ni["target_residues"])
   r,t,tr=superpose(ca(cs[0]),ca(native[0]));projected=transform(cs[1],r,t)
   row["competition_geometry"]=dict(native_coverage=len(nr&set(pi["target_residues"]))/max(1,len(nr)),target_rmsd=tr,partner_overlap=atom_overlap(native[1],projected))
  rows.append(row)
 atomic_json(run.path/"outputs/results.json",dict(entry=e,models=rows));run.output("results",run.path/"outputs/results.json")
 print(run.finish("EXTENSION_SCORED","computational_only"),flush=True)
except Exception as x:run.fail(x);raise

