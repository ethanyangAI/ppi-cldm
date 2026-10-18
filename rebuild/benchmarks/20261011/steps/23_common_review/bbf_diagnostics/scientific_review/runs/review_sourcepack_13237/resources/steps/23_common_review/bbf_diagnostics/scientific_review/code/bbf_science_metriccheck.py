#!/usr/bin/env python3
"""Independent stdlib case/unit/rank verification of BBF110 diagnostic receipts."""
import csv,hashlib,json,math,os,re,statistics,subprocess,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
STEP=R/"steps/23_common_review/bbf_diagnostics/scientific_review"
IN=STEP/"runs/review_13230"
def req(v,msg):
 if not v:raise ValueError(msg)
def rec(p):
 p=Path(p).absolute();req(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(R),"Regular project file")
 return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def verify(r):req(rec(r["path"])==r,"Changed receipt "+r["path"]);return Path(r["path"])
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def table(p):
 with Path(p).open() as f:return list(csv.DictReader(f,delimiter="\t"))
def auc_rank(labels,scores):
 req(len(labels)==len(scores) and all(math.isfinite(v) for v in scores),"Missing score")
 ranked=sorted(enumerate(scores),key=lambda v:v[1]);ranks={}
 i=0
 while i<len(ranked):
  j=i+1
  while j<len(ranked) and ranked[j][1]==ranked[i][1]:j+=1
  for k in range(i,j):ranks[ranked[k][0]]=(i+1+j)/2
  i=j
 np_=sum(labels);nn=len(labels)-np_;req(np_>0 and nn>0,"Both labels required")
 return (sum(ranks[i] for i,l in enumerate(labels) if l)-np_*(np_+1)/2)/(np_*nn)
def label_gate(label,scores):
 p=[v>=1 for v in scores]
 return dict(TP=sum(l and v for l,v in zip(label,p)),FN=sum(l and not v for l,v in zip(label,p)),
 FP=sum(not l and v for l,v in zip(label,p)),TN=sum(not l and not v for l,v in zip(label,p)))
class Contracts(unittest.TestCase):
 def test_average_ties(self):self.assertEqual(auc_rank([1,0,1,0],[0,0,0,0]),.5)
 def test_reverse_labels(self):
  self.assertEqual(auc_rank([1,1,0,0],[4,3,2,1]),1);self.assertEqual(auc_rank([0,0,1,1],[4,3,2,1]),0)
 def test_null_cannot_be_zero(self):
  with self.assertRaises(ValueError):auc_rank([1,0],[1,float("nan")])
 def test_boundary(self):self.assertEqual(label_gate([1,0],[1,1]),dict(TP=1,FN=0,FP=1,TN=0))
 def test_no_model_pseudoreplication(self):
  case_scores=[statistics.median([.1,.2,.3,.4,.5]),statistics.median([.8,.9,1,1.1,1.2])]
  self.assertEqual(len(case_scores),2);self.assertEqual(auc_rank([1,0],case_scores),0)
def main():
 req(os.environ.get("SLURM_JOB_ID") and os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU Slurm only")
 raw=subprocess.check_output(["scontrol","show","job",os.environ["SLURM_JOB_ID"],"-o"],text=True)
 own=[v for v in raw.splitlines() if re.search(r"\bJobId="+os.environ["SLURM_JOB_ID"]+r"\b",v)]
 req(len(own)==1,"One CPU allocation");fields=dict(re.findall(r"(\w+)=(\S*)",own[0]));tres=fields.get("AllocTRES",fields.get("TRES",""))
 req(fields["JobState"]=="RUNNING" and not re.search(r"(?:^|,)gres/gpu[^=]*=[1-9]",tres),"Actual GPU0")
 out=STEP/("runs/metric_verify_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
 manifest=read(IN/"manifest.json");verify(manifest["source"])
 for r in manifest["outputs"]:verify(r)
 for r in manifest["inputs"].values():verify(r)
 metrics=read(IN/"metrics.json");models=read(IN/"model_crosschecks.json");cases=table(IN/"cases.tsv");labels=table(IN/"original_labels.tsv")
 req(len(cases)==22 and len(models)==110 and len(labels)==11,"Fixed case/model denominator")
 labelmap={v["id"]:int(v["positive"]) for v in labels};req(len(labelmap)==11 and sum(labelmap.values())==6,"6+/5-")
 qualification=read(verify(metrics["inputs"]["qualification"]));qe={v["id"]:v for v in qualification["entries"] if v["target"]=="BBF-14"}
 req(set(qe)==set(labelmap),"Qualification identities")
 for cid,l in labelmap.items():req(qe[cid]["binary_binding_label"]==l,"Original SPR label")
 reconstructed={};rows=[]
 arms=metrics["fixed_settings"]["arms"]
 for arm in arms:
  sub=sorted((v for v in cases if v["arm"]==arm),key=lambda v:v["id"]);req(len(sub)==11,"Every arm full11")
  for axis in ("R0","R1"):
   ss=[]
   for v in sub:
    source=[x for x in models if x["id"]==v["id"] and x["arm"]==arm]
    req(len(source)==5 and {x["model"] for x in source}==set(range(1,6)),"All models before median")
    for m in source:
     verify(m["pdb"]);verify(m["raw_score"]);req(m["seed"]==31031,"Fixed seed")
    median=statistics.median(x[axis] for x in source);req(math.isclose(median,float(v[axis]),abs_tol=1e-12),"Independent median")
    ss.append(median)
   ls=[labelmap[v["id"]] for v in sub];auc=auc_rank(ls,ss)
   req(math.isclose(auc,metrics["metrics"][arm][axis]["AUC_pairwise"],abs_tol=1e-12),"Independent stdlib rank AUC")
   rows.append(dict(arm=arm,axis=axis,AUC=auc,cases=11,positive=6,negative=5))
  gt=label_gate(ls,[float(v["R0"]) for v in sub]);baseline=metrics["metrics"][arm]["fixed_R0_gate"]
  req(all(gt[k]==baseline[k] for k in gt),"Independent old R0 gate")
  reconstructed[arm]=dict(continuous=rows[-2:],fixed_R0_gate=gt)
 model_geometry=[]
 target_cut=metrics["native_control_context"]["settings"]["geometry"]["native_recovery_target_RMSD_A"]
 f1_cut=metrics["native_control_context"]["settings"]["geometry"]["native_recovery_contact_target_F1"]
 req(target_cut==2 and f1_cut==.5,"Original target/interface criteria")
 for arm in arms:
  selected=[v for v in models if v["id"]=="bc_BBF_b4" and v["arm"]==arm]
  req(len(selected)==5,"Known b4 five model context")
  for v in selected:
   flag=v["target_RMSD_A"]<=target_cut and v["interface_F1"]>=f1_cut
   req(v["native_pose_criterion_met"]==flag,"Original target/interface flag")
   model_geometry.append(dict(context="BBF110:"+arm,model=v["model"],seed=v["seed"],target_CA_RMSD_A=v["target_RMSD_A"],
    interface_target_F1=v["interface_F1"],partner_CA_RMSD_A=v["known_b4_partner_CA_RMSD_A"],fixed_target_and_interface_check=flag))
 for v in metrics["native_control_context"]["models"]:
  flag=v["target_RMSD_A"]<=target_cut and v["contact_target_F1"]>=f1_cut
  req(flag==v["structural_recovery"],"Original native target/interface flag")
  model_geometry.append(dict(context="native74:"+v["engine"],model=v["slot"]["model"],seed=v["slot"]["seed"],target_CA_RMSD_A=v["target_RMSD_A"],
   interface_target_F1=v["contact_target_F1"],partner_CA_RMSD_A=v["partner_CA_RMSD_A"],fixed_target_and_interface_check=flag))
 tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));req(tests.wasSuccessful(),"Independent contracts")
 report=(IN/"REPORT_ZH.md").read_text().replace("既定结构恢复判据满足","固定target backbone+interface几何检查满足").replace("既定结构恢复|","固定target+interface检查|").replace("结构恢复判据按target RMSD","原known_partner_structural_recovery字段实际按target RMSD")
 report+="\n## 已知b4逐模型几何核验：明确区别target与partner\n\n冻结门为target CA RMSD≤2 Å且target interface F1≥0.5；它没有partner CA RMSD门。因此BBF110模板臂5/5仅指target+interface几何检查，不能写为完整binder姿态达到≤2 Å。伙伴CA RMSD按target配准后独立计算、连续报告，未新增rescue cutoff或筛选规则。\n\n|上下文|model|seed|target CA RMSD Å|target interface F1|partner CA RMSD Å|原target+interface检查|\n|---|---:|---:|---:|---:|---:|---:|\n"
 for v in model_geometry:
  report+=f"|{v['context']}|{v['model']}|{v['seed']}|{v['target_CA_RMSD_A']:.4f}|{v['interface_target_F1']:.4f}|{v['partner_CA_RMSD_A']:.4f}|{int(v['fixed_target_and_interface_check'])}|\n"
 report+="\n独立stdlib verifier从110模型重建22个case中位数，另用排序并列平均秩重算AUC、重算固定R0混淆矩阵，逐文件hash核对，5项额外合同通过。早期13221 checker列顺序假设错误已保留原失败日志；没有改动原始推断、标签或分数。13226为中间审读，13230为数值/解释修订结果，当前审读入口由本acceptance明确绑定。\n"
 (out/"REPORT_AUDITED_ZH.md").write_text(report)
 dump(out/"independent_metrics.json",dict(reconstructed_metrics=reconstructed,known_b4_per_model_geometry=model_geometry,
  input_manifest=rec(IN/"manifest.json"),source=rec(__file__),tests=dict(n=tests.testsRun,passed=True),gpu_allocated=0,job_id=os.environ["SLURM_JOB_ID"]))
 accepted=dict(status="BBF110_SCIENTIFIC_DEVELOPMENT_REVIEW_INDEPENDENTLY_ACCEPTED",scope="DEVELOPMENT_ONLY_NO_NEW_HOLDOUT_THRESHOLD_OR_EXPERIMENT_PROBABILITY",
  job_id=os.environ["SLURM_JOB_ID"],source=rec(__file__),review_source=manifest["source"],review_manifest=rec(IN/"manifest.json"),review_metrics=rec(IN/"metrics.json"),
  report=rec(out/"REPORT_AUDITED_ZH.md"),independent_metrics=rec(out/"independent_metrics.json"),counts=metrics["counts"],
  tests=dict(prior=7,independent=tests.testsRun,all_passed=True),source_preserved=True,formal_protocol_modified=False,scientific_interpretation="Template condition improves target-conditioned development ordering but remains incomplete; target/interface recovery flag is not full partner RMSD recovery")
 dump(out/"acceptance.json",accepted)
 print(json.dumps(accepted,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

