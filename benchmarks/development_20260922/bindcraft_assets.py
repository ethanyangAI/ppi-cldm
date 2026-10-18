import tarfile,shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,atomic_json,require,verify_file
root=Path("/lustre/users/u21111210118/projects/test9");src=root/"assets/colabfold_parallel/weights.tar";rec=root/"assets/colabfold_parallel/receipt.json"
run=Run(root,"48_bindcraft_assets",[record_file(rec)])
expected=read_json(rec);require(record_file(src)["sha256"]==expected["sha256"],"ARCHIVE_CHECKSUM",str(src))
dest=root/"assets/bindcraft/params";dest.mkdir(parents=True,exist_ok=True);records=[]
with tarfile.open(src) as t:
 for m in t.getmembers():
  if not m.isfile() or not m.name.endswith(".npz"):continue
  name=Path(m.name).name
  if not ("_ptm." in name or "_multimer_v3." in name):continue
  p=dest/name
  if not p.exists():
   with t.extractfile(m) as f,p.open("wb") as out:shutil.copyfileobj(f,out)
  require(p.stat().st_size==m.size,"WEIGHT_SIZE",str(p));records.append(record_file(p))
require(len(records)==10,"WEIGHT_COUNT",str(len(records)))
atomic_json(run.path/"outputs/weights.json",dict(source=record_file(src),weights=records));run.output("weights",run.path/"outputs/weights.json")
print(run.finish("BINDCRAFT_WEIGHTS_PREPARED","model_assets_not_runtime_acceptance"),flush=True)
