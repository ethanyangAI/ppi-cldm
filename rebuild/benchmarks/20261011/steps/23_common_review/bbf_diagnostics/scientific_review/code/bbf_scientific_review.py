#!/usr/bin/env python3
"""Independent BBF110 developer diagnosis; no training, threshold choice, or GPU."""
import argparse,collections,csv,hashlib,importlib.util,json,math,os,re,subprocess,unittest
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
R=Path("/lustre/users/u21111210118/projects/test9")
STEP=R/"steps/23_common_review/bbf_diagnostics/scientific_review"
EVID=R/"steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125"
FROZEN=R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061"
ARMS=("single_no_template","single_target_only_9HAG_template")
ATOMS="N CA C CB O CG CG1 CG2 OG OG1 SG CD CD1 CD2 ND1 ND2 OD1 OD2 SD CE CE1 CE2 CE3 NE NE1 NE2 OE1 OE2 CH2 NH1 NH2 OH CZ CZ2 CZ3 NZ OXT".split()
AA="ARNDCQEGHILKMFPSTWYV"
AA3=dict(zip("ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split(),AA))
def require(v,msg):
 if not v:raise ValueError(msg)
def dump(p,v):
 p=Path(p);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def read(p):return json.loads(Path(p).read_text())
def rec(p):
 p=Path(p);require(p.is_file() and not p.is_symlink(),"Regular project file required")
 require(p.resolve().is_relative_to(R),"Outside project")
 return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def verify(v):
 require(rec(v["path"])==v,"Receipt changed: "+v["path"]);return Path(v["path"])
def cpu():
 guard=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
 spec=importlib.util.spec_from_file_location("cpu_scheduler_guard",guard);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 raw=subprocess.check_output(["scontrol","show","job",os.environ["SLURM_JOB_ID"],"-o"],text=True)
 selected=m.select_scheduler_record(raw,raw_job_id=os.environ["SLURM_JOB_ID"])
 if isinstance(selected,dict):selected=selected.get("selected_scheduler_record",selected.get("scheduler_record"))
 fields=dict(re.findall(r"(\w+)=(\S*)",selected))
 tres=fields.get("AllocTRES",fields.get("TRES",""))
 require(fields["JobState"]=="RUNNING" and not re.search(r"(?:^|,)gres/gpu(?:[^=]*)=[1-9]",tres),"CPU allocation must be running GPU0")
 require(os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU visibility must be empty")
 return dict(raw=raw,selected=selected,allocated_gpu_count=0,job_id=os.environ["SLURM_JOB_ID"],guard=rec(guard))
def finite(v):
 return isinstance(v,(float,int,np.number)) and not isinstance(v,(bool,np.bool_)) and math.isfinite(float(v))
def complete(values,n=5):
 require(len(values)==n and all(finite(v) for v in values),"Missing/nonfinite required model")
 return dict(median=float(np.median(values)),q25=float(np.quantile(values,.25)),q75=float(np.quantile(values,.75)),
             min=float(min(values)),max=float(max(values)),n=n)
def auc_pair(labels,scores):
 require(len(labels)==len(scores) and all(finite(v) for v in scores),"AUC denominator/missing")
 pos=[s for s,l in zip(scores,labels) if l];neg=[s for s,l in zip(scores,labels) if not l]
 require(pos and neg,"AUC needs both labels")
 terms=[int(p>n)+.5*int(p==n) for p in pos for n in neg]
 return float(sum(terms)/len(terms))
def auc_ranks(labels,scores):
 ranks=rankdata(scores,method="average");np_=sum(labels);nn=len(labels)-np_
 return float((sum(r for r,l in zip(ranks,labels) if l)-np_*(np_+1)/2)/(np_*nn))
def fixed_gate(labels,scores):
 passed=[s>=1 for s in scores]
 return dict(threshold=1.,direction="R0_case_median>=1",TP=sum(l and p for l,p in zip(labels,passed)),
 FN=sum(l and not p for l,p in zip(labels,passed)),FP=sum(not l and p for l,p in zip(labels,passed)),
 TN=sum(not l and not p for l,p in zip(labels,passed)),TPR=sum(l and p for l,p in zip(labels,passed))/sum(labels),
 FPR=sum(not l and p for l,p in zip(labels,passed))/(len(labels)-sum(labels)))
def pdb(path):
 out=collections.OrderedDict()
 for line in Path(path).read_text().splitlines():
  if line.startswith("ENDMDL"):break
  if not line.startswith("ATOM  "):continue
  chain=line[21];key=(line[22:26],line[26]);name=line[12:16].strip();element=(line[76:78].strip() or name[0])
  if element in ("H","D"):continue
  row=out.setdefault(chain,collections.OrderedDict()).setdefault(key,dict(aa=AA3[line[17:20]],atoms={},best={}))
  occ=float(line[54:60] or 0);alt=line[16];priority=(occ,alt==" ",alt=="A")
  if name not in row["best"] or priority>row["best"][name]:
   row["best"][name]=priority;row["atoms"][name]=np.array([float(line[30:38]),float(line[38:46]),float(line[46:54])])
 return {k:list(v.values()) for k,v in out.items()}
def sequence(chain):return "".join(v["aa"] for v in chain)
def fit(a,b):
 require(a.shape==b.shape and a.ndim==2 and a.shape[1]==3,"Alignment shape")
 ac=a.mean(0);bc=b.mean(0);u,s,vt=np.linalg.svd((a-ac).T@(b-bc));rot=u@np.diag([1,1,np.linalg.det(u@vt)])@vt
 fitted=(a-ac)@rot+bc
 return rot,bc-ac@rot,float(np.sqrt(np.mean(np.sum((fitted-b)**2,axis=1))))
def ca(chain):return np.asarray([v["atoms"]["CA"] for v in chain])
def contacts(a,b,cut=5):
 xa=[];ia=[];xb=[];ib=[]
 for i,v in enumerate(a):
  for p in v["atoms"].values():xa.append(p);ia.append(i)
 for j,v in enumerate(b):
  for p in v["atoms"].values():xb.append(p);ib.append(j)
 xa=np.asarray(xa);xb=np.asarray(xb);pairs=set()
 for start in range(0,len(xa),256):
  ids=np.argwhere(np.sum((xa[start:start+256,None,:]-xb[None,:,:])**2,axis=2)<cut*cut)
  pairs.update((ia[start+int(i)],ib[int(j)]) for i,j in ids)
 return pairs
def official(path):
 h=None;rows={};maxrow=None
 for line in Path(path).read_text().splitlines():
  x=line.split()
  if not x:continue
  if x[0]=="Chn1":h=x;continue
  if h is None:continue
  require(len(x)==len(h),"Official ipSAE row shape")
  d=dict(zip(h,x));require(d["PAE"]=="10" and d["Dist"]=="15","Wrong fixed ipSAE cutoff")
  if d["Type"]=="asym":rows[(d["Chn1"],d["Chn2"])]=float(d["ipSAE"])
  if d["Type"]=="max":maxrow=float(d["ipSAE"])
 require(set(rows)=={("A","B"),("B","A")} and maxrow==max(rows.values()),"Official directional score")
 return maxrow
def template_arrays(job,f,source):
 data=np.load(verify(f["features"]),allow_pickle=False);T=len(job["target_sequence"]);B=len(job["binder_sequence"]);L=T+B
 query="".join(AA[int(i)] for i in data["query_aatype"])
 require(query==job["target_sequence"]+job["binder_sequence"],"Actual query deletion/change")
 require(data["msa_feat"].shape[:2]==(1,L),"Single MSA required")
 # AF2's MSA columns use HHblits alphabet; compare literal one-hot first row.
 hh="ACDEFGHIKLMNPQRSTVWYX-"
 require("".join(hh[int(i)] for i in data["msa_feat"][0,:,:22].argmax(-1))==query,"MSA query differs")
 mapping={int(k)-1:int(v)-1 for k,v in job["target_query_to_template_indices"].items()}
 rawmask=np.zeros((L,37),np.float32);rawpos=np.zeros((L,37,3),np.float32)
 for qi,si in mapping.items():
  require(query[qi]==source[si]["aa"],"Template source mapping changed")
  for name,coord in source[si]["atoms"].items():
   if name in ATOMS:rawmask[qi,ATOMS.index(name)]=1;rawpos[qi,ATOMS.index(name)]=coord
 require(np.array_equal(data["batch_all_atom_mask"],rawmask),"Raw mask differs from unbound target-only atoms")
 require(np.allclose(data["batch_all_atom_positions"],rawpos,atol=1e-5,rtol=0),"Raw positions differ from unbound target-only atoms")
 mask=data["template_all_atom_mask"];pos=data["template_all_atom_positions"]
 wanted=rawmask if job["target_template_enabled"] else np.zeros_like(rawmask)
 require(mask.shape==(1,L,37) and np.array_equal(mask[0],wanted),"Effective target-only ablation mask")
 require(np.allclose(pos[0],rawpos*wanted[...,None],atol=1e-5,rtol=0),"Effective coordinate channel leaked")
 for k in ("template_pseudo_beta_mask","template_pseudo_beta"):
  require(not np.count_nonzero(data[k][:,T:]),"Binder pseudo-beta leaked")
  if not job["target_template_enabled"]:require(not np.count_nonzero(data[k]),"No-template pseudo-beta leaked")
 require(not np.count_nonzero(data["prev_pos"]),"Initial guess leaked")
 require(f["actual_validated_model_slots"]==job["slots"] and f["all_models_feature_arrays_identical"],"All 5 actual model features required")
 return dict(job_key=job["job_key"],features=f["features"],target_template_atoms=int(mask.sum()),binder_template_atoms=0,
             raw_target_source_match=True,prev_pos_nonzero=0,query_length=L,n_models_bound=5)
def cif_origin(path,chain,normalized,label_offset=1):
 data=MMCIF2Dict(str(path));n=len(data["_atom_site.Cartn_x"]);coords=collections.defaultdict(list)
 for i in range(n):
  if data["_atom_site.group_PDB"][i]!="ATOM" or data["_atom_site.auth_asym_id"][i]!=chain:continue
  label=data["_atom_site.label_seq_id"][i]
  if label in (".","?"):continue
  key=(int(label)-label_offset-1,data["_atom_site.label_atom_id"][i])
  coords[key].append(np.array([float(data["_atom_site.Cartn_"+c][i]) for c in "xyz"]))
 count=0;maxerr=0.
 for j,res in enumerate(normalized):
  for name,v in res["atoms"].items():
   require((j,name) in coords,"Normalized atom absent from original CIF")
   err=min(float(np.max(np.abs(v-c))) for c in coords[(j,name)])
   require(err<=.00051,"Normalized target source differs from original 9HAG")
   maxerr=max(maxerr,err);count+=1
 return dict(n_checked_atoms=count,max_absolute_coordinate_error_A=maxerr,source=rec(path),auth_chain=chain,label_positions="2-112 core; initiator/tag scope separate")
class Contracts(unittest.TestCase):
 def test_tie_and_rank_auc(self):
  self.assertEqual(auc_pair([1,0],[0,0]),.5);self.assertEqual(auc_ranks([1,0],[0,0]),.5)
 def test_direction(self):
  self.assertEqual(auc_pair([1,1,0,0],[3,4,1,2]),1);self.assertEqual(auc_pair([1,1,0,0],[1,2,3,4]),0)
 def test_missing_not_zero(self):
  with self.assertRaises(ValueError):complete([1,1,1,1,None])
 def test_required_fifth(self):
  with self.assertRaises(ValueError):complete([1,1,1,1])
 def test_no_single_class_auc(self):
  with self.assertRaises(ValueError):auc_pair([1,1],[1,2])
 def test_fixed_gate_boundary(self):
  self.assertEqual(fixed_gate([1,0],[1,.999])["TP"],1)
 def test_proper_rotation(self):
  a=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]])
  b=a@np.array([[0,1,0],[-1,0,0],[0,0,1]])+2
  rot,t,rms=fit(a,b);self.assertLess(rms,1e-12);self.assertGreater(np.linalg.det(rot),.999)
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);allocation=cpu()
 score=read(EVID/"score.json");accepted=read(EVID/"acceptance.json")
 verify(accepted["score"]);require(accepted["n_models_accepted"]==110 and accepted["remaining_model_slots"]==0,"Full110 not accepted")
 planpath=verify(score["plan"]);plan=read(planpath);verify(score["raw"]);require(plan["settings"]==score["settings"],"Settings differ")
 qpath=verify(plan["inputs"]["qualification"]);q=read(qpath);epath=verify(plan["inputs"]["eligibility"]);e=read(epath)
 qualification={v["id"]:v for v in q["entries"] if v["target"]=="BBF-14"}
 eligibility={v["id"]:v for v in e["entries"] if v["target"]=="BBF-14"}
 controls={v["id"]:v for v in plan["controls"]}
 require(set(qualification)==set(eligibility)==set(controls) and len(controls)==11,"Fixed 11 qualification identities differ")
 primary=verify(q["sources"]["primary_table"]["artifact"])
 with primary.open() as f:csvrows=list(csv.DictReader(f))
 label_rows=[]
 for cid,c in controls.items():
  qr=qualification[cid];er=eligibility[cid];pr=csvrows[qr["source_csv_row"]-2]
  require(qr["source_id"]==pr["DesignName"]==c["source_id"]==er["source_id"],"Source design identity")
  require(qr["sequence"]==pr["Sequence"]==c["binder_sequence"]==er["sequence"],"Full author binder query")
  require(int(pr["Binding"])==qr["binary_binding_label"]==c["positive"]==er["positive"],"Original label mismatch")
  require(qr["sequence_sha256"]==c["binder_sequence_sha256"]==er["sequence_sha256"] and qr["target_sequence_sha256"]==c["target_sequence_sha256"]==er["target_sequence_sha256"],"Sequence hash qualification mismatch")
  require(er["main_eligible"] and er["screen_sensitivity_eligible"] and qr["adjudication"]["main_analysis_eligible"] and not er["blockade_eligible"],"Eligibility changed")
  require(hashlib.sha256(json.dumps(pr,sort_keys=True,separators=(",",":")).encode()).hexdigest()==c["source_row_sha256"],"Primary row receipt changed")
  label_rows.append(dict(id=cid,source_id=c["source_id"],positive=int(pr["Binding"]),source_csv_row=qr["source_csv_row"],
   main_eligible=er["main_eligible"],conditioned_endpoint=er["conditioned_endpoint"],binder_length=len(c["binder_sequence"]),
   target_length=len(c["target_sequence"]),sequence_sha256=er["sequence_sha256"],qualification_class=er["qualification_class"]))
 require(sum(v["positive"] for v in label_rows)==6,"6+/5- labels fixed")
 audit=read(EVID/"worker_audit.json");verify(accepted["worker_audit"]);auditrows={v["job_key"]:v for v in audit["rows"]}
 featurepath=FROZEN/"feature_manifest.json";features=read(featurepath);require(features["plan"]==rec(planpath),"Feature/plan receipt binding")
 verify(features["source"]);fa=read(FROZEN/"feature_acceptance.json");require(fa["features"]==rec(featurepath),"CPU feature acceptance binding")
 source=pdb(verify(plan["template_target"]));reference=pdb(verify(plan["reference_complex"]))
 require(set(source)=={"A"} and len(source["A"])==111,"Unbound target-only scope")
 manifest=read(verify(plan["inputs"]["input_manifest"]));identity=read(verify(manifest["identity_receipt"]))
 cif=verify(identity["sources"]["9HAG"]["cif"]);origin=cif_origin(cif,"A",source["A"])
 source_boundfit=fit(ca(source["A"]),ca(reference["A"]))
 sourceinfo=dict(unbound_9HAG_to_bound_9HAC_target_CA_RMSD_A=source_boundfit[2],n_CA=111,unbound_source=plan["template_target"],
 reference_complex=plan["reference_complex"],unbound_origin=origin,reference_target_sequence_identical=sequence(source["A"])==sequence(reference["A"]),
 native_binder_query_length=len(plan["native_partner_sequence"]),native_binder_observed_mapped_CA_n=len(plan["native_partner_query_to_reference_indices"]),
 original_declared_crystal_binder_length=147,author_core_length=140,internal_missing_query_positions=[i for i in range(1,141) if str(i) not in plan["native_partner_query_to_reference_indices"]])
 nativepairs=contacts(reference["A"],reference["B"]);nativecontact={i for i,j in nativepairs}
 featurechecks=[];modelrows=[];case_rows=[]
 fmap={v["job_key"]:v for v in features["jobs"]};smap={(v["id"],v["arm"]):v for v in score["results"]}
 require(len(smap)==22 and len(score["results"])==22,"Lost/duplicate control arms")
 for job in plan["jobs"]:
  cid=job["control_id"];arm=job["arm"];sr=smap[cid,arm];ar=auditrows[job["job_key"]];wp=verify(ar["worker"]);worker=read(wp)
  require(worker["features_source_receipt"]==features["source"] and worker["features_cpu_receipt"]==fmap[job["job_key"]]["features"],"GPU worker not bound to verified literal features")
  require(worker["settings"]==plan["settings"] and worker["status"]=="COMPLETE" and len(worker["models"])==5,"Worker protocol/completeness")
  require(worker["allocation"]["allocated_gpu_count"]==1,"Original worker allocation")
  for rr in (ar["worker_references"],ar["actual_guard_reference"]):verify(rr)
  featurechecks.append(template_arrays(job,fmap[job["job_key"]],source["A"]))
  require(sr["positive"]==controls[cid]["positive"],"Score label differs")
  rows=[];require(len(sr["models"])==5,"Required five model denominator")
  require(sorted(v["slot"]["model"] for v in sr["models"])==[1,2,3,4,5],"Fixed unique models")
  for m in sr["models"]:
   require(m["status"]=="VALID" and m["slot"]["seed"]==31031,"Model unresolved/protocol")
   ch=pdb(verify(m["pdb"]));conf=read(verify(m["scores"]));require(set(ch)=={"A","B"},"Chain scope")
   require(sequence(ch["A"])==job["target_sequence"] and sequence(ch["B"])==job["binder_sequence"],"Raw full query differs")
   T=len(ch["A"]);L=T+len(ch["B"]);pp=np.array(conf["plddt"],float)/100;pae=np.array(conf["pae"],float)
   require(pp.shape==(L,) and pae.shape==(L,L) and np.isfinite(pp).all() and np.isfinite(pae).all(),"Raw confidence null/dimensions")
   require(pp.min()>=0 and pp.max()<=1 and pae.min()>=0 and conf["plddt_units"]=="0-100" and "Angstrom" in conf["pae_units"],"Unit contract")
   require(conf["query"]==job["target_sequence"]+job["binder_sequence"] and not conf["initial_guess"] and not conf["initial_atom_pos"],"Raw inference query/guess")
   pairs=contacts(ch["A"],ch["B"]);ai=sorted({i for i,j in pairs});bi=sorted({T+j for i,j in pairs})
   require(bool(pairs),"Required interface absent")
   contactpae=float(np.mean([pae[i,T+j] for i,j in pairs]+[pae[T+j,i] for i,j in pairs]));inter=float(pp[ai+bi].mean())
   parts=dict(global_iptm=float(conf["iptm"])/.75,binder_plddt=float(pp[T:].mean())/.8,interface_plddt=inter/.8,
              contact_PAE=(8/contactpae if contactpae else None))
   r0=min(v for v in parts.values() if v is not None)
   require(math.isclose(r0,m["R0"],abs_tol=2e-7),"Independent raw R0 differs")
   require(math.isclose(contactpae,m["bidirectional_contact_PAE_A"],abs_tol=2e-6),"Contact PAE reconstruction differs")
   txt=next(v for v in m["official_files"] if v["path"].endswith("model_10_15.txt"));r1=official(verify(txt))
   require(r1==m["R1"],"Pinned official R1 differs")
   mapping={int(k)-1:int(v)-1 for k,v in job["target_query_to_template_indices"].items()}
   rot,shift,tarms=fit(np.array([ch["A"][i]["atoms"]["CA"] for i in mapping]),np.array([reference["A"][mapping[i]]["atoms"]["CA"] for i in mapping]))
   predcontact={mapping[i] for i in ai if i in mapping};tp=len(predcontact&nativecontact);f1=2*tp/(len(predcontact)+len(nativecontact))
   require(math.isclose(tarms,m["geometry"]["target_recovery_RMSD_A"],abs_tol=2e-6),"Independent target RMSD differs")
   require(math.isclose(f1,m["geometry"]["contact_target_residue_F1"],abs_tol=1e-12),"Independent interface F1 differs")
   native=job["binder_sequence"]==plan["native_partner_sequence"];brms=None
   if native:
    bmap={int(k)-1:int(v)-1 for k,v in plan["native_partner_query_to_reference_indices"].items()}
    require(all(ch["B"][i]["aa"]==reference["B"][j]["aa"] for i,j in bmap.items()),"Full-core observed binder map")
    brms=float(np.sqrt(np.mean(np.sum((np.array([ch["B"][i]["atoms"]["CA"] for i in bmap])@rot+shift-np.array([reference["B"][j]["atoms"]["CA"] for i,j in bmap.items()]))**2,axis=1))))
    require(math.isclose(brms,m["geometry"]["known_partner_target_aligned_CA_RMSD_A"],abs_tol=2e-6),"Known b4 target-aligned pose RMSD differs")
   row=dict(id=cid,arm=arm,positive=controls[cid]["positive"],model=m["slot"]["model"],seed=31031,R0=r0,R1=r1,
    R0_fixed_pass=r0>=1,target_RMSD_A=tarms,target_plddt_fraction=float(pp[:T].mean()),binder_plddt_fraction=float(pp[T:].mean()),
    interface_F1=f1,known_b4_partner_CA_RMSD_A=brms,native_pose_criterion_met=(tarms<=2 and f1>=.5) if native else None,
    limiting_components=[k for k,v in parts.items() if v is not None and math.isclose(v,r0,abs_tol=1e-12)],pdb=m["pdb"],raw_score=m["scores"])
   rows.append(row);modelrows.append(row)
  c=dict(id=cid,arm=arm,positive=controls[cid]["positive"],n_models=5)
  for axis in ("R0","R1"):
   stats=complete([v[axis] for v in rows]);require(math.isclose(stats["median"],sr[axis]["median"],abs_tol=2e-7),"Case median differs")
   c[axis]=stats["median"];c[axis+"_IQR"]=stats["q75"]-stats["q25"]
  c.update(R0_fixed_pass=c["R0"]>=1,R0_model_passes=sum(v["R0_fixed_pass"] for v in rows),target_RMSD_A=complete([v["target_RMSD_A"] for v in rows])["median"],
   target_plddt_fraction=complete([v["target_plddt_fraction"] for v in rows])["median"],
   binder_plddt_fraction=complete([v["binder_plddt_fraction"] for v in rows])["median"],
   known_b4_partner_CA_RMSD_A=complete([v["known_b4_partner_CA_RMSD_A"] for v in rows])["median"] if native else None,
   known_b4_pose_recovered_models=sum(v["native_pose_criterion_met"] for v in rows) if native else None)
  case_rows.append(c)
 metrics={}
 for arm in ARMS:
  rows=sorted((v for v in case_rows if v["arm"]==arm),key=lambda v:v["id"]);labels=[v["positive"] for v in rows]
  armmetrics={}
  for axis in ("R0","R1"):
   scores=[v[axis] for v in rows];ap=auc_pair(labels,scores);ar=auc_ranks(labels,scores);require(math.isclose(ap,ar,abs_tol=1e-12),"Two independent AUC formulations differ")
   ranks=rankdata([-v for v in scores],method="average")
   for v,rank in zip(rows,ranks):v[axis+"_descending_rank"]=float(rank)
   leave=[auc_pair([v for j,v in enumerate(labels) if j!=i],[v for j,v in enumerate(scores) if j!=i]) for i in range(11)]
   armmetrics[axis]=dict(case_n=11,positive_n=6,negative_n=5,AUC_pairwise=ap,AUC_rank_sum=ar,cliffs_delta=2*ap-1,
    positive_median=float(np.median([s for s,l in zip(scores,labels) if l])),negative_median=float(np.median([s for s,l in zip(scores,labels) if not l])),
    leave_one_case_out_AUC_range=[min(leave),max(leave)],model_slots_per_case=5,statistical_unit="published design/case; 5 models are technical repeats")
  armmetrics["fixed_R0_gate"]=fixed_gate(labels,[v["R0"] for v in rows])
  armmetrics["positive_target_RMSD_median_A"]=float(np.median([v["target_RMSD_A"] for v in rows if v["positive"]]))
  armmetrics["negative_target_RMSD_median_A"]=float(np.median([v["target_RMSD_A"] for v in rows if not v["positive"]]))
  metrics[arm]=armmetrics
 caseindex={(v["id"],v["arm"]):v for v in case_rows}
 paired=[dict(id=cid,positive=controls[cid]["positive"],delta_R0_template_minus_single=caseindex[cid,ARMS[1]]["R0"]-caseindex[cid,ARMS[0]]["R0"],
  delta_R1_template_minus_single=caseindex[cid,ARMS[1]]["R1"]-caseindex[cid,ARMS[0]]["R1"],
  delta_target_RMSD_A=caseindex[cid,ARMS[1]]["target_RMSD_A"]-caseindex[cid,ARMS[0]]["target_RMSD_A"]) for cid in sorted(controls)]
 test=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));require(test.wasSuccessful(),"Scientific contracts failed")
 result=dict(status="BBF110_INDEPENDENT_DEVELOPMENT_DIAGNOSIS_CONTENT_ACCEPTED",scope="ALL78_DEVELOPMENT; BBF11 same labels/cases reused, no untouched test",
   allocation=allocation,source=rec(__file__),inputs=dict(score=rec(EVID/"score.json"),acceptance=rec(EVID/"acceptance.json"),worker_audit=rec(EVID/"worker_audit.json"),
    plan=rec(planpath),qualification=rec(qpath),eligibility=rec(epath),primary_CSV=rec(primary),feature_manifest=rec(featurepath),feature_acceptance=rec(FROZEN/"feature_acceptance.json")),
   counts=dict(cases=11,positive=6,negative=5,arms=2,models_expected=110,models_independently_checked=len(modelrows),missing=0),
   fixed_settings=plan["settings"],labels=label_rows,metrics=metrics,paired_case_changes=paired,case_rows=case_rows,
   feature_checks=featurechecks,structure_context=sourceinfo,tests=dict(n=test.testsRun,passed=True),
   operational_R1_threshold=None,experimental_probability=None,workflow_superiority=None,protocol_modified=False)
 dump(out/"metrics.json",result);dump(out/"model_crosschecks.json",modelrows)
 for name,rows in (("cases.tsv",case_rows),("paired_changes.tsv",paired),("original_labels.tsv",label_rows)):
  fields=list(rows[0])
  with (out/name).open("w") as f:
   w=csv.DictWriter(f,fieldnames=fields,delimiter="\t");w.writeheader();w.writerows(rows)
 lines=["# BBF输入条件开发诊断：独立审读","","本轮110/110模型完成且通过独立内容复核。统计单位是11个既有设计（原资格化6个SPR检出、5个未检出），每个设计每臂5个AF2权重模型为技术重复。以下结果只解释已知BBF控制的输入敏感性。","",
 "原表标签、完整binder query、末端构建范围、main/sensitivity资格与冻结eligibility78逐条一致；无改标签、无删除案例、无模型择优、无重调cutoff。两臂都single target/binder MSA，5multimer_v3×seed31031×3recycles，仅target模板有无不同。","",
 "|输入臂|R0 AUC|R1 AUC|旧R0≥1 TP/FN|FP/TN|TPR|FPR|","|---|---:|---:|---:|---:|---:|---:|"]
 for arm in ARMS:
  m=metrics[arm];g=m["fixed_R0_gate"]
  lines.append(f"|{arm}|{m['R0']['AUC_pairwise']:.4f}|{m['R1']['AUC_pairwise']:.4f}|{g['TP']}/{g['FN']}|{g['FP']}/{g['TN']}|{g['TPR']:.3f}|{g['FPR']:.3f}|")
 lines+=["","AUC由正负案例所有30对的胜负（并列计半）与独立秩和公式交叉验证。病例汇总固定五模型中位数；原R0≥1仅作既定计算回收门诊断。R1始终连续，未创建实验检出概率或新阈值。","",
 "|原案例|原SPR标签|R0 single→target template|R1 single→target template|target RMSD Å single→template|",
 "|---|---:|---:|---:|---:|"]
 for cid in sorted(controls):
  a=caseindex[cid,ARMS[0]];b=caseindex[cid,ARMS[1]]
  lines.append(f"|{cid}|{int(a['positive'])}|{a['R0']:.3f}→{b['R0']:.3f}|{a['R1']:.3f}→{b['R1']:.3f}|{a['target_RMSD_A']:.2f}→{b['target_RMSD_A']:.2f}|")
 lines+=["","单序列无模板时，评分排序对作者SPR标签发生反向分离；加入实验unbound target-only模板后，连续排序在这11例内改善。固定旧R0门可能仍漏掉连续分数较高的阳性，因此不能将完美AUC写成全部回收，或从结果选择新门。11个病例不足以证明跨家族适用；未检出标签受原作者SPR条件、表达/纯度、构建与未知重复数限制，不表示所有条件下无亲和力。","",
 "## 结构解释与泄漏审查","",
 f"9HAG unbound核心与9HAC bound target为相同111残基；独立CA配准RMSD={sourceinfo['unbound_9HAG_to_bound_9HAC_target_CA_RMSD_A']:.4f} Å。模板每个原子坐标与原始9HAG CIF交叉匹配，未替换为9HAC bound复合体。"]
 for arm in ARMS:
  b4=caseindex["bc_BBF_b4",arm];bm=[v for v in modelrows if v["id"]=="bc_BBF_b4" and v["arm"]==arm]
  lines.append(f"- 已知b4，{arm}：target RMSD中位数{b4['target_RMSD_A']:.3f} Å；target配准后已观测binder CA RMSD中位数{b4['known_b4_partner_CA_RMSD_A']:.3f} Å；既定结构恢复判据满足{b4['known_b4_pose_recovered_models']}/5。")
 lines+=["","b4推理输入为作者完整140残基核心，晶体147残基的末端GSHHHHH单列；reference缺失的内部残基不从query删除，几何仅使用明确映射的观测CA。所有22个实际特征文件逐个重读：forward query与原表完整序列一致、single-row MSA一致；raw batch/effective template坐标只来自9HAG target，binder mask/position/pseudo-beta全零、prev_pos全零；无模板臂target mask/position/pseudo-beta也全零。所有GPU worker与同一immutable backend、该CPU feature hash及自身raw PDB/confidence绑定；GPU时未另行抓取每层中间张量，证明范围是固定源码/输入生成路径与CPU实际forward feature捕获的复用。9HAC/b4只用于事后结构比较，不在模板或initial guess输入内。","",
 "这支持一种解释：synthetic BBF缺少天然同源MSA，独立序列推断的target折叠/局部几何可使置信度排序失真；提供近似bound折叠的实验unbound target帮助恢复正确target先验及已知b4姿态。此为与观察一致的计算解释，不能单凭相关性确定因果，也不能证明其他BBF阳性的真实界面或功能。模板来自原设计同靶标结构，因此该臂是target-conditioned recovery，而不是完全sequence-only评估。","",
 "## 证据范围","",
 "旧15模型MSA/no-template结果仍保留为不同seed/模型预算的历史参考，不与本轮两臂混为第三个配对处理；本报告未改正式共同复核primary/secondary、目标MSA规则或候选采样方案。R0门只诊断历史计算回收，几何coverage/clash仍是proxy；BBF无已确立天然PPI伙伴或实验blockade标签。不能据此宣称RFdiffusion或BindCraft方法优越、跨家族泛化成功、亲和力或实验阻断。","",
 f"原子来源检查{origin['n_checked_atoms']}个9HAG核心原子；独立raw R0/固定官方R1/target RMSD/interface F1检查110模型；{test.testsRun}项meaningful contracts通过。完整分数、秩、paired delta、原标签与hash见同目录JSON/TSV。","",
 "依据：[BindCraft原论文](https://www.nature.com/articles/s41586-025-09429-6)说明BBF无天然同源、11个纯化设计6个检出，9HAG用于设计靶标及9HAC为b4晶体；[9HAG](https://www.rcsb.org/structure/9HAG)为1.86 Å monomer实验结构，[9HAC](https://www.rcsb.org/structure/9HAC)为3.10 Å复合体；[ipSAE固定官方revision](https://github.com/DunbrackLab/IPSAE/tree/6174cf9e71cb1bd660cc805856a18c4871a6dec3)作为既定连续置信度来源。"]
 (out/"REPORT_ZH.md").write_text("\n".join(lines)+"\n")
 manifestout=dict(status=result["status"],job_id=os.environ["SLURM_JOB_ID"],source=rec(__file__),inputs=result["inputs"],outputs=[rec(out/n) for n in ("metrics.json","model_crosschecks.json","cases.tsv","paired_changes.tsv","original_labels.tsv","REPORT_ZH.md")])
 dump(out/"manifest.json",manifestout)
 print(json.dumps(dict(status=result["status"],job_id=os.environ["SLURM_JOB_ID"],counts=result["counts"],metrics=metrics,structure_context=sourceinfo,manifest=rec(out/"manifest.json")),ensure_ascii=False,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output-dir",required=True);a=p.parse_args();run(a.output_dir)

