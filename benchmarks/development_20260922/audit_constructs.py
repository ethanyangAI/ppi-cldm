import csv,shutil,subprocess,tarfile,json,xml.etree.ElementTree as ET,collections
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require
from ppiblocker.structure import read_structure
root=Path("/lustre/users/u21111210118/projects/test9")
ap=root/"steps/34_calibration_assets/runs/20260922T100035Z_9d23276b14e3/manifest.json"
sp=root/"steps/36_public_label_audit/runs/20260922T100427Z_3b07bc685980/manifest.json"
mp=root/"steps/39_method_sources/runs/20260922T100916Z_e4a43583a04e/manifest.json"
run=Run(root,"41_control_constructs",[record_file(p) for p in [ap,sp,mp]])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 am=read_json(ap);sm=read_json(sp);mm=read_json(mp)
 candidates=read_json(verify_file(sm["outputs"]["local_controls"]))["entries"]
 wanted={r["binder_id"]:r for r in candidates};found=collections.defaultdict(list);members=[]
 archive=verify_file(am["outputs"]["input_pdbs.tar.zst"])
 proc=subprocess.Popen([root/"env/metrics/bin/zstd","-dc",archive],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdout,mode="r|") as t:
  for member in t:
   if not member.isfile():continue
   members.append(dict(name=member.name,size=member.size))
   key=Path(member.name).stem
   if key in wanted and Path(member.name).suffix==".pdb":
    p=run.path/"work"/(key+".pdb");require(not p.exists(),"DUPLICATE_ARCHIVE_ID",key)
    with t.extractfile(member) as f:p.write_bytes(f.read())
    found[key].append(record_file(p))
 proc.stdout.close();rc=proc.wait();require(rc==0,"ZSTD_FAILURE",proc.stderr.read().decode())
 results=[]
 for e in candidates:
  recs=found[e["binder_id"]];row=dict(**e,archive_matches=recs,status="MISSING_INPUT_STRUCTURE",assay_construct_match="PENDING_PRIMARY_SOURCE")
  if len(recs)==1:
   cs,ctx=read_structure(verify_file(recs[0]));by={c["id"]:c for c in cs}
   bc=e["binder_chain"];tc=json.loads(e["target_chains"])
   exact=len(tc)==1 and bc in by and tc[0] in by and by[bc]["sequence"]==e["A_seq"] and by[tc[0]]["sequence"]==e["B_seq"]
   row.update(status="AUTHOR_INPUT_SEQUENCE_MATCH" if exact else "INPUT_SEQUENCE_MISMATCH",context=ctx,chains=[dict(id=c["id"],length=len(c["sequence"])) for c in cs])
  results.append(row)
 atomic_json(run.path/"outputs/controls.json",results);run.output("controls",run.path/"outputs/controls.json")
 atomic_json(run.path/"outputs/archive_inventory.json",members);run.output("archive_inventory",run.path/"outputs/archive_inventory.json")
 literature={}
 for key in ["rfd.xml","bindcraft.xml"]:
  doc=ET.parse(verify_file(am["outputs"][key])).getroot()
  text=[]
  for p in doc.iter("p"):
   s=" ".join("".join(p.itertext()).split())
   if any(w in s.lower() for w in ["mdm2","biolayer","biolayer interferometry","recombinant","supplementary data","supplementary information"]):text.append(s)
  media=[dict(tag=x.tag,attrs=x.attrib,text=" ".join("".join(x.itertext()).split())[:400]) for x in doc.iter() if x.tag in ["supplementary-material","media","ext-link"] and ("supp" in str(x.attrib).lower() or x.tag in ["supplementary-material","media"])]
  literature[key]=dict(paragraphs=text,media=media)
 atomic_json(run.path/"outputs/literature_extracts.json",literature);run.output("literature",run.path/"outputs/literature_extracts.json")
 schema={}
 for r in read_json(verify_file(mm["outputs"]["receipts"])):
  if r["status"]=="FETCHED" and r["path"].endswith(".csv"):
   with verify_file(r["artifact"]).open() as f:
    rd=csv.DictReader(f);rr=list(rd);columns=rd.fieldnames
   schema[r["path"]]=dict(n=len(rr),columns=columns,example=[{k:v for k,v in x.items() if any(z in k.lower() for z in ["target","bind","sequence","source","kd","name"])} for x in rr[:2]])
 atomic_json(run.path/"outputs/external_schema.json",schema);run.output("external_schema",run.path/"outputs/external_schema.json")
 print(run.finish("AUTHOR_INPUT_CONSTRUCTS_AUDITED","input_identity_not_assay_identity",
  dict(matched=sum(r["status"]=="AUTHOR_INPUT_SEQUENCE_MATCH" for r in results),total=len(results))),flush=True)
 print("STATUS",dict(collections.Counter(r["status"] for r in results)),flush=True)
 print("LITERATURE",json.dumps(literature),flush=True)
 print("SCHEMA",json.dumps(schema),flush=True)
except Exception as e:run.fail(e);raise

