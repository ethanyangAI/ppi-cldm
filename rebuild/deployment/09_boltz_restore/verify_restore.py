import hashlib,json,pickle,importlib.metadata as md
from pathlib import Path
import torch,numpy,rdkit
from rdkit import Chem
R=Path("/lustre/users/u21111210118/projects/test9");D=R/"assets/boltz";O=R/"steps/09_boltz_restore/outputs"
assert json.loads((O/"assets_receipt.json").read_text())["status"]=="BOLTZ_ASSETS_HASH_VERIFIED_NO_INFERENCE"
assert json.loads((O/"runtime_receipt.json").read_text())["status"]=="BOLTZ_RUNTIME_READY_NO_INFERENCE"
records=[]
for p in sorted((D/"mols").rglob("*")):
 if not p.is_file():continue
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 records.append(dict(relative_path=str(p.relative_to(D/"mols")),bytes=p.stat().st_size,sha256=h.hexdigest()))
assert len(records)>1000
tree=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(",",":")).encode()).hexdigest()
examples=[]
for name in ("ALA","GLY","HIS","MSE"):
 candidates=list((D/"mols").glob(name+".*"))
 assert len(candidates)==1,(name,[p.name for p in candidates])
 with candidates[0].open("rb") as f:mol=pickle.load(f)
 assert isinstance(mol,Chem.Mol),(name,type(mol))
 assert mol.GetNumAtoms()>0
 examples.append(dict(name=name,atoms=mol.GetNumAtoms(),conformers=mol.GetNumConformers()))
receipt=dict(status="BOLTZ_RESTORE_ACCEPTED_CPU_IMPORT_AND_ASSET_CHECKS_NO_INFERENCE",versions={n:md.version(n) for n in ("boltz","torch","numpy","rdkit")},cuda_runtime=torch.version.cuda,mols_files=len(records),mols_bytes=sum(x["bytes"] for x in records),mols_tree_sha256=tree,representative_molecules=examples,scientific_inference_performed=False)
(O/"mols_file_manifest.json").write_text(json.dumps(records,indent=2)+"\n")
(O/"boltz_restore_acceptance.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))

