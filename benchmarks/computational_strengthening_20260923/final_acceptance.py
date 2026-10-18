import json,hashlib,statistics,datetime,shutil,os
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/"reports/computational_strengthening_20260923"
report=R/"steps/90_strengthening_report/runs/20260927T145421Z_8b26f313d73b/manifest.json"
trajectory=R/"steps/93_strengthening_trajectory_review/runs/20260927T145417Z_4f3d93a7ef8a/manifest.json"
verified={}
def read(p): return json.loads(Path(p).read_text())
def check(rec):
 p=Path(rec["path"])
 if str(p) not in verified:
  h=hashlib.sha256()
  with p.open("rb") as f:
   for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
  verified[str(p)]=h.hexdigest()
 assert verified[str(p)]==rec["sha256"],str(p)
 return p
def record(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
m=read(report);assert m["status"]=="ALL_COMPUTATIONAL_STRENGTHENING_COMPLETE"
for v in m["outputs"].values():check(v)
for v in m["inputs"]:
 p=check(v)
 if p.name=="manifest.json":
  upstream=read(p)
  for x in upstream.get("outputs",{}).values():check(x)
summary=read(check(m["outputs"]["summary"]))
t=read(trajectory);assert t["status"]=="ALL_TRAJECTORIES_VERIFIED"
tr=read(check(t["outputs"]["results"]))["trajectories"]
assert len(tr)==9 and len({(x["id"],x["seed"]) for x in tr})==9
assert all(x["frames"]==100 and x["final_pdb_rmsd"]<.002 for x in tr)
for x in tr:
 check(x["trajectory"]);check(x["topology"]);check(x["raw_manifest"])
counts={}
physics=[]
for stage,status,n in [("83_strengthening_extension_predict","EXTENSION_PREDICTION_COMPLETE",129),("87_strengthening_extension_score","EXTENSION_SCORED",129),("84_strengthening_physics","PHYSICS_COMPLETE",114)]:
 paths=[p for p in (R/"steps"/stage/"runs").glob("*/manifest.json") if read(p)["status"]==status]
 assert len(paths)==n,(stage,len(paths))
 counts[stage]=len(paths)
 for p in paths:
  mm=read(p)
  for x in mm.get("outputs",{}).values():check(x)
  if stage.startswith("84"):physics.append(read(mm["outputs"]["results"]["path"]))
# Interface ratio zeros are reported, never interpreted as favorable binding.
physflags=[]
for x in physics:
 for a in x["models"]:
  if a.get("dSASA",1)<=0 or a.get("dG_per_area_x100",1)==0:
   physflags.append(dict(id=x["entry"]["id"],seed=a.get("seed"),dSASA=a.get("dSASA"),ratio=a.get("dG_per_area_x100")))
maxerr=max(x["final_pdb_rmsd"] for x in tr)
text="""# 计算加强结果：科学审阅与最终交付

日期：2026-09-27。范围为 COMPUTATIONAL-STRENGTHENING-20260923 已冻结的计算加强方案，配套《计算加强完整报告》和《执行方案与方法说明》。本轮预定计算及内容验收全部完成；科学目标“对任意蛋白对可靠设计阻断剂并证明方法优越”尚未确立。

## 可以据此作出的决定

1. **优先保留 bb145 作为后续实验候选。** 游离模型 pLDDT 中位数82.247，结合构象支持9/15；三条MD末200ps姿态RMSD中位数分别1.742、2.188、1.979 Å，折叠RMSD1.209–1.630 Å，初始原子接触保留52.1%–62.5%。这些结果支持本次固定起始构象的短时局部稳定性，不证明结合或阻断。
2. **bb1144 暂不作为与 bb145 等级相同的优先候选。** 三条MD姿态RMSD为4.458、11.985、4.711 Å，接触保留28.7%–49.5%，显示本次起始姿态明显更不一致。但游离折叠和MD使用的固定 model1/seed1042 结合参考属于此前AF2复核中的异常姿态；0/15游离支持不能等价于整个候选无法折叠。需要以主构象簇代表重评后才可作全面淘汰判断。
3. **bb144 保留为结构不确定候选。** 游离pLDDT73.979，固定参照支持0/15；没有纳入本轮预定9条MD，不能误写为已通过或未通过MD。

MD的原生NRF2短肽对照姿态RMSD4.473–4.972 Å，接触保留65.5%–68.4%。短肽与设计蛋白的长度和柔性不同；不能因为bb145 RMSD更低就声称其亲和力或阻断效力优于天然配体。接触保留率也不等于亲和力。

## 方法优越性：本轮没有得到支持

78条对照中38阳性、40阴性。四家族留出置信度方案召回52.6%、假阳性率17.5%；加ipSAE后召回47.4%、假阳性率仍17.5%；加折叠物理后召回仅7.9%、假阳性率10.0%。新增严格联合过滤未显示整体收益，不能宣传为已提高成功率。建议将折叠、物理和竞争几何作为独立诊断证据，不以本次联合门槛作唯一淘汰条件。

这些数值来自回顾性结合标签，不是阻断标签。仅4个家族，60条仍待原始来源核验，18条虽有核心序列核验但完整实验构建体和标签细节未齐；标签与入库表一致不等于独立核实原文。未完成同预算的RFdiffusion/ProteinMPNN、BindCraft等生成方法前瞻头对头比较，因此本轮完成不等于任意蛋白对泛化benchmark完成。

## 特异性、消融及全长背景的实际限制

KLHL3–WNK4和KLHL12–DVL1原生阳性对照ipTM分别0.210和0.280，双向ipSAE最小值均为0。候选对这些同源靶标的低分因此不能当作无脱靶证据。匹配单序列KEAP1输入也只有ipTM0.14–0.17、ipSAE0，提示输入信息不足或方法敏感性问题；不能用其与主方案的分数差推导生物学选择性。

完整KEAP1预测的ipTM均0.12、ipSAE0，全长构象支持未建立。结构投影未见额外结构域严重碰撞仅是几何检查；域间位置不确定，不能推导天然二聚体中的可达性。自缔合低置信度也不能排除实验聚集。

15条消融序列的游离/该突变体固定结合参照支持均0/15，多条还伴随显著低游离置信度或构象变化。其结合评分变化混合了折叠改变与界面改变，不能当作位点能量因果证据。即使打乱序列仍有较高覆盖，也说明几何覆盖不是独立的阻断功能判据。

## Rosetta诊断异常必须保留

多条扰动或背景复合物的单位面积界面能为0或很大的正值（如基序扰动893.421、侧翼打乱649.978；原生NRF2预测94.571）。这些输出不具备直接进行亲和力排名的条件。零值须结合原始埋藏面积和界面形成情况判读，不能解释为有利或中性结合；大正值标记构象/松弛异常。114项是技术成功数，不是114项结构通过数。Rosetta三重复仅改变随机种子，固定同一起始构象，不能替代姿态集合验收。

## 完整性与证据边界

- 129项扩展预测、129项评分、114项物理检查均为唯一成功项；失败和取消记录保留。
- 9/9 MD均100ps平衡加1ns生产，全部CPU，每条100帧，共900帧。独立DCD复算通过，末帧与最终PDB逐原子一致性通过。
- MD三个种子来自同一起始结构，参考为生产第一个保存帧10ps；不能排除更长时间失稳或证明收敛。
- 127项工程测试通过；这些测试不构成实验验证。
- 本轮未缩短模拟、未切换GPU、未重跑成功非MD模块。

后续科学工作应聚焦：补齐原始标签和实验构建体；用有效同源阳性校准特异性预测；消除bb1144异常参考并作多起始姿态敏感性检查；在预先冻结且有阻断终点的独立集合进行等预算生成方法比较；对优先候选开展结合、竞争和功能实验。这些是本轮结论之后的新验证阶段，不能冒充为本轮已完成内容。
"""
text+=f"\n独立验收最大末帧PDB RMSD：{maxerr:.8f} Å（阈值0.002 Å）。完整文件哈希验收数：{len(verified)}。\n"
out=D/"科学审阅与交付结论.md";out.write_text(text)
S=R/"source/benchmarks/computational_strengthening_20260923"
shutil.copy2(out,S/out.name)
receipt=R/"steps/79_strengthening_setup/final_acceptance_20260927.json"
receipt.write_text(json.dumps(dict(status="SCIENTIFIC_REVIEW_COMPLETE",counts=counts,md=9,dcd_frames=900,max_final_pdb_rmsd=maxerr,verified_files=len(verified),physics_zero_or_nonpositive_area=physflags,report_manifest=record(report),trajectory_manifest=record(trajectory),reports=[record(p) for p in sorted(D.glob("*.md"))]),ensure_ascii=False,indent=2))
registry=R/"00_admin/strengthening_20260923.json"
old=read(registry)
backup=registry.with_name("strengthening_20260923.before_final_delivery.json")
if not backup.exists():shutil.copy2(registry,backup)
old.update(state="COMPUTATIONAL_COMPLETE_SCIENTIFIC_REVIEWED",updated=datetime.datetime.now(datetime.timezone.utc).isoformat(),report_manifest=record(report),trajectory_manifest=record(trajectory),final_acceptance=record(receipt),human_reports=[record(p) for p in sorted(D.glob("*.md"))],limitations=["No experimental binding or blockade proof","No workflow superiority","Primary label and full construct qualification remains incomplete"],local_delivery="PENDING_HASH_VERIFICATION")
temp=registry.with_suffix(".tmp");temp.write_text(json.dumps(old,ensure_ascii=False,indent=2));os.replace(temp,registry)
print(receipt.read_text())

