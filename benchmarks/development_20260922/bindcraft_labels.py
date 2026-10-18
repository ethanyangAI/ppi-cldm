import csv,collections,shutil,xml.etree.ElementTree as ET,json
from pathlib import Path
from ppiblocker.common import Run,record_file,read_json,verify_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
primary=root/"steps/47_publisher_supplements/runs/20260922T103153Z_d35874272d99/outputs/41586_2025_9429_MOESM4_ESM.csv"
secondary=root/"steps/39_method_sources/runs/20260922T100916Z_e4a43583a04e/outputs/DigBioLab_de_novo_binder_scoring/analysis/data/bindcraft_predicted_and_experimental_data.csv"
if not secondary.exists():
 secondary=next((root/"steps/39_method_sources/runs/20260922T100916Z_e4a43583a04e").rglob("bindcraft_predicted_and_experimental_data.csv"))
run=Run(root,"51_bindcraft_labels",[record_file(primary),record_file(secondary)])
shutil.copy2(__file__,run.path/"qc/driver.py")
with primary.open() as f:a=list(csv.DictReader(f))
with secondary.open() as f:b=list(csv.DictReader(f))
print("PRIMARY_TARGETS",dict(collections.Counter(x["Target"] for x in a)),flush=True)
print("PRIMARY_BINDING",dict(collections.Counter(x["Binding"] for x in a)),flush=True)
print("SECONDARY_TARGETS",dict(collections.Counter(x.get("target_id_generic") for x in b)),flush=True)
by=collections.defaultdict(list)
for x in b:by[x["A_seq"]].append(x)
rows=[]
for x in a:
 matches=by[x["Sequence"]]
 rows.append(dict(primary_target=x["Target"],primary_name=x["DesignName"],primary_binding=x["Binding"],affinity_nM=x["Affinity_nM"],sequence=x["Sequence"],
   matches=[{k:y.get(k) for k in ["binder_id","binder","expression","target_id_generic","A_seq","B_seq","target_subchain_B_seq","target_chains","source","kd","method"]} for y in matches]))
atomic_json(run.path/"outputs/label_join.json",rows);run.output("labels",run.path/"outputs/label_join.json")
xml=root/"steps/34_calibration_assets/runs/20260922T100035Z_9d23276b14e3/outputs/bindcraft.xml"
doc=ET.parse(xml).getroot()
texts=[]
for sec in doc.iter("sec"):
 title=sec.find("title")
 if title is not None and any(w in "".join(title.itertext()).lower() for w in ["experimental","expression","binding","purification","cloning","biolayer","surface plasmon"]):
  texts.append(" ".join("".join(sec.itertext()).split()))
p=run.path/"outputs/assay_methods.txt";p.write_text("\n\n".join(texts));run.output("methods",p)
print("MATCH_COUNTS",dict(collections.Counter(len(r["matches"]) for r in rows)),flush=True)
for target in sorted({x["Target"] for x in a}):
 rr=[x for x in a if x["Target"]==target];print(target,dict(collections.Counter(x["Binding"] for x in rr)),flush=True)
print(run.finish("BINDCRAFT_PRIMARY_LABELS_JOINED","primary_labels_pending_assay_construct"),flush=True)
