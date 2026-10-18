#!/usr/bin/env python3
"""Source-preserving partner-pose geometric interpretation of accepted native74 and BBF b4."""
import argparse,collections,csv,hashlib,json,math,os,re,statistics,subprocess,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
STEP=R/"steps/23_common_review/bbf_diagnostics/scientific_review"
N=R/"steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/scored"
B=STEP/"runs/review_13230"
def req(v,s):
 if not v:raise ValueError(s)
def rec(p):
 p=Path(p).absolute();req(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(R),"Regular project file")
 return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def verify(v):req(rec(v["path"])==v,"Receipt mismatch "+v["path"]);return Path(v["path"])
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def pose(partner_rmsd,f1):
 if not finite(partner_rmsd) or not finite(f1):return None
 req(partner_rmsd>=0 and 0<=f1<=1,"Geometry units/range")
 return partner_rmsd<=2 and f1>=.5
def summarize(values,expected):
 req(len(values)==expected,"Full model denominator")
 valid=[v for v in values if finite(v)]
 if len(valid)!=expected:return dict(n_expected=expected,n_valid=len(valid),median=None,q25=None,q75=None)
 ordered=sorted(valid)
 def quant(q):
  x=(expected-1)*q;i=int(x);j=min(i+1,expected-1);return ordered[i]+(x-i)*(ordered[j]-ordered[i])
 return dict(n_expected=expected,n_valid=expected,median=statistics.median(valid),q25=quant(.25),q75=quant(.75))
class Contracts(unittest.TestCase):
 def test_pose_boundary(self):self.assertTrue(pose(2,.5))
 def test_target_proxy_not_partner(self):
  self.assertFalse(pose(6,.8));self.assertTrue(1<=2 and .8>=.5)
 def test_missing_abstain(self):self.assertIsNone(pose(None,.9))
 def test_f1_required(self):self.assertFalse(pose(1,.49))
 def test_continuous_full_models(self):
  self.assertIsNone(summarize([1,None,2],3)["median"]);self.assertEqual(summarize([1,2,3],3)["median"],2)
def main(args):
 req(os.environ.get("SLURM_JOB_ID") and os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU Slurm")
 raw=subprocess.check_output(["scontrol","show","job",os.environ["SLURM_JOB_ID"],"-o"],text=True)
 own=[v for v in raw.splitlines() if re.search(r"\bJobId="+os.environ["SLURM_JOB_ID"]+r"\b",v)]
 req(len(own)==1,"One scheduler CPU job");fields=dict(re.findall(r"(\w+)=(\S*)",own[0]));tres=fields.get("AllocTRES",fields.get("TRES",""))
 req(fields["JobState"]=="RUNNING" and not re.search(r"(?:^|,)gres/gpu[^=]*=[1-9]",tres),"Actual GPU0")
 out=STEP/("runs/partner_pose_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
 nm=read(N/"manifest.json");np=verify(nm["score"]);req(nm["score"]["sha256"]=="cf5163b4e19adee5b0266ef3541e5b82f1e22be61f64d21fcd0bc7e763673d55","Authoritative native74 score")
 verify(nm["source"]);ns=read(np);req(ns["models_expected"]==ns["models_valid"]==74,"74 full model denominator")
 bb=read(B/"metrics.json");req(bb["counts"]["models_independently_checked"]==110,"BBF110 content audit")
 metric_accept=read(STEP/"runs/metric_verify_13232/acceptance.json");verify(metric_accept["review_metrics"]);verify(metric_accept["independent_metrics"])
 protocol=Path(args.protocol).absolute() if args.protocol else R/"steps/23_common_review/PROTOCOL.md"
 ptext=protocol.read_text();protocolrec=rec(protocol)
 timing=args.timing
 original_protocol=R/"steps/23_common_review/PROTOCOL.md"
 original_text=original_protocol.read_text();req("targetmappedCA RMSD<=2" in original_text,"Original target/interface proxy wording preserved")
 modelrows=[];groups=[];seen=set()
 for group in ns["results"]:
  expected=3 if group["engine"]=="boltz" else 5
  req(len(group["models"])==expected,"Fixed engine count")
  native=[]
  for m in group["models"]:
   key=(group["job_key"],m["slot"]["model"],m["slot"]["seed"]);req(key not in seen,"Duplicate native slot");seen.add(key)
   g=m["geometry"];legacy=g["target_recovery_RMSD_A"]<=2 and g["contact_target_residue_F1"]>=.5
   req(legacy==g["known_partner_structural_recovery"],"Legacy target/interface definition changed")
   truepose=pose(g["known_partner_target_aligned_CA_RMSD_A"],g["contact_target_residue_F1"])
   req(m["status"]=="VALID" and truepose is not None and g["known_partner_observed_CA_n"]>=3,"Complete actual native geometry")
   row=dict(target_id=group["target_id"],engine=group["engine"],variant=group["variant"],job_key=group["job_key"],slot=m["slot"],
    target_CA_RMSD_A=g["target_recovery_RMSD_A"],partner_target_aligned_CA_RMSD_A=g["known_partner_target_aligned_CA_RMSD_A"],
    contact_target_F1=g["contact_target_residue_F1"],known_partner_observed_CA_n=g["known_partner_observed_CA_n"],legacy_target_interface_proxy=legacy,
    true_partner_pose_recovery=truepose,R0=m["R0"],R1=m["R1"])
   modelrows.append(row);native.append(row)
  groups.append(dict(target_id=group["target_id"],engine=group["engine"],variant=group["variant"],n_expected=expected,n_valid=expected,
    true_partner_pose_recovery_n=sum(v["true_partner_pose_recovery"] for v in native),legacy_target_interface_proxy_n=sum(v["legacy_target_interface_proxy"] for v in native),
    partner_CA_RMSD_A=summarize([v["partner_target_aligned_CA_RMSD_A"] for v in native],expected),
    target_CA_RMSD_A=summarize([v["target_CA_RMSD_A"] for v in native],expected),target_contact_F1=summarize([v["contact_target_F1"] for v in native],expected),
    R0=summarize([v["R0"] for v in native],expected),R1=summarize([v["R1"] for v in native],expected)))
 req(len(modelrows)==74 and len(groups)==20,"All20 jobs74 fixed native slots")
 bmodels=read(B/"model_crosschecks.json");bgroups=[];brows=[]
 for arm in bb["fixed_settings"]["arms"]:
  selected=[v for v in bmodels if v["id"]=="bc_BBF_b4" and v["arm"]==arm];req(len(selected)==5,"BBF b4 5")
  for m in selected:
   brows.append(dict(arm=arm,model=m["model"],seed=m["seed"],target_query_length=112,author_binder_query_length=140,
    target_CA_RMSD_A=m["target_RMSD_A"],partner_target_aligned_CA_RMSD_A=m["known_b4_partner_CA_RMSD_A"],contact_target_F1=m["interface_F1"],
    legacy_target_interface_proxy=m["native_pose_criterion_met"],true_partner_pose_recovery=pose(m["known_b4_partner_CA_RMSD_A"],m["interface_F1"])))
  bgroups.append(dict(arm=arm,n_expected=5,n_valid=5,legacy_target_interface_proxy_n=sum(m["native_pose_criterion_met"] for m in selected),
   true_partner_pose_recovery_n=sum(pose(m["known_b4_partner_CA_RMSD_A"],m["interface_F1"]) for m in selected),
   partner_CA_RMSD_A=summarize([m["known_b4_partner_CA_RMSD_A"] for m in selected],5),target_contact_F1=summarize([m["interface_F1"] for m in selected],5)))
 test=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));req(test.wasSuccessful(),"Contracts")
 result=dict(status="NATIVE74_AND_BBF_B4_PARTNER_POSE_SUPPLEMENT_CONTENT_ACCEPTED",scope="Computational geometric interpretation only; no new predictions or primary R1 changes",
  source=rec(__file__),cpu_allocation=dict(job_id=os.environ["SLURM_JOB_ID"],record=own[0],allocated_gpu_count=0),
  inputs=dict(native_score=rec(np),native_score_manifest=rec(N/"manifest.json"),BBF_science_metrics=rec(B/"metrics.json"),
   BBF_model_crosschecks=rec(B/"model_crosschecks.json"),BBF_science_acceptance=rec(STEP/"runs/metric_verify_13232/acceptance.json"),endpoint_protocol=protocolrec,original_frozen_protocol_semantics=rec(original_protocol)),
  endpoint=dict(name="true_partner_pose_recovery",partner_target_aligned_CA_RMSD_max_A=2,contact_target_F1_min=.5,operator="both inclusive",
   timing=timing,protocol_role="Current mutable draft is explanatory only, not pre-native preregistration; original PROTOCOL v1.2 demonstrates target/interface proxy semantics",threshold_fit=False,confidence_not_used=True,legacy_definition="target CA RMSD<=2 and F1>=0.5; retains original accepted score field as target/interface proxy"),
  native_groups=groups,native_models=modelrows,BBF_b4_groups=bgroups,BBF_b4_models=brows,
  counts=dict(native_jobs=20,native_models_expected=74,native_models_valid=74,BBF_b4_models_expected=10,BBF_b4_models_valid=10),
  tests=dict(n=test.testsRun,passed=True),old_source_and_scores_modified=False,formal_primary_modified=False,experimental_probability=None)
 dump(out/"partner_pose.json",result)
 lines=["# 已知伙伴pose几何补充审读（source-preserving）","",
 "原字段known_partner_structural_recovery实际以target CA RMSD≤2 Å与target接口F1≥0.5判断，明确保留并改称target/interface proxy。下列伙伴pose端点另以target配准后的partner CA RMSD≤2 Å且target interface F1≥0.5判断；两门均含等号，不依赖R0/R1、不拟合阈值。此为计算结构比较，不表示实验结合或功能验证。","",
 "原74模型评分、源码、GPU推断均保持原字节/hash。完整20job/74模型及BBF110中b4两臂10模型有真实有限几何值，无missing当negative或补0。统计单位仍是模型技术重复；不同engine/variant分列，不混成实验样本。","",
 "端点登记/解释时序："+timing+"。所绑定protocol见JSON receipt；凡旧文本明定target RMSD，不能称其早已定义partner门。","",
 "|target|engine|variant|有效/预定|伙伴RMSD median [Q25,Q75] Å|target F1 median|伙伴pose计数|旧target/interface proxy计数|","|---|---|---|---:|---:|---:|---:|---:|"]
 for g in groups:
  p=g["partner_CA_RMSD_A"];f=g["target_contact_F1"]
  lines.append(f"|{g['target_id']}|{g['engine']}|{g['variant']}|{g['n_valid']}/{g['n_expected']}|{p['median']:.3f} [{p['q25']:.3f},{p['q75']:.3f}]|{f['median']:.3f}|{g['true_partner_pose_recovery_n']}/{g['n_expected']}|{g['legacy_target_interface_proxy_n']}/{g['n_expected']}|")
 lines+=["","## BBF b4开发输入诊断单列","",
 "|arm|伙伴RMSD median [Q25,Q75] Å|target F1 median|伙伴pose/5|旧target/interface proxy/5|","|---|---:|---:|---:|---:|"]
 for g in bgroups:
  p=g["partner_CA_RMSD_A"];f=g["target_contact_F1"]
  lines.append(f"|{g['arm']}|{p['median']:.3f} [{p['q25']:.3f},{p['q75']:.3f}]|{f['median']:.3f}|{g['true_partner_pose_recovery_n']}/5|{g['legacy_target_interface_proxy_n']}/5|")
 lines+=["","BBF110的target112/seed31031/ColabDesign backend与native74的target111/Boltz3seed或AF2seed31021不同，不能合并为配对第三臂。旧5/5 target/interface检查不能写成5/5完整伙伴pose恢复；全部逐模型target RMSD、partner RMSD及F1见JSON。BBF仍为开发数据，无天然PPI/blockade标签。","",
 "本补充对6个天然target与1个BBF诊断均完整列出固定模型分母；主R1 endpoint、MSA/模板规则、候选采样与方法比较未调整。它只修正几何语义，不证明workflow优越或未见家族泛化。"]
 (out/"REPORT_POSE_ZH.md").write_text("\n".join(lines)+"\n")
 dump(out/"acceptance.json",dict(status=result["status"],source=result["source"],inputs=result["inputs"],counts=result["counts"],
  result=rec(out/"partner_pose.json"),report=rec(out/"REPORT_POSE_ZH.md"),tests=result["tests"],scientific_endpoints=result["endpoint"],old_source_and_scores_modified=False))
 print(json.dumps(dict(status=result["status"],native_groups=groups,BBF_b4_groups=bgroups,acceptance=rec(out/"acceptance.json")),ensure_ascii=False,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--protocol");p.add_argument("--timing",default="RETROSPECTIVE_CONTROL_GEOMETRY_DIAGNOSTIC; native74/BBF development; no cutoff fitting, no pre-native preregistration claim");main(p.parse_args())

