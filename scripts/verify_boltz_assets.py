from pathlib import Path
import hashlib,json,sys,tarfile,uuid,shutil
ROOT=Path("/lustre/users/u21111210118/projects/test9")
dest=ROOT/"assets/boltz"
expected={
"mols.tar":(1855662080,"39e076d96dbec6b4e86982bbda16f3a53a2a60c9bdc17828d88f6f9a0c7d1fd7"),
"boltz2_conf.ckpt":(2286561469,"090e82ac8c92f5e943fa1b39e7410a44027bea7243c0bbb3caa67a77fc1428e1"),
"boltz2_aff.ckpt":(2062139170,"dcc5cd3722b1c9eaa34267e4ae32f55cbbf1963f4c19319381ccfa30fdd2ca9e")}
for name in (sys.argv[1:] or expected):
 p=dest/name;size,sha=expected[name]
 assert p.stat().st_size==size,(name,"size mismatch")
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 assert h.hexdigest()==sha,(name,"SHA256 mismatch")
 receipt={"url":f"https://huggingface.co/boltz-community/boltz-2/resolve/6fdef46d763fee7fbb83ca5501ccceff43b85607/{name}",
          "sha256":sha,"bytes":size,"verified_against":"official Hugging Face X-Linked-ETag SHA256"}
 p.with_suffix(p.suffix+".receipt.json").write_text(json.dumps(receipt,indent=2))
 print("VERIFIED",name,sha,flush=True)
 if name=="mols.tar" and not (dest/"mols").exists():
  staging=dest/("extract_"+uuid.uuid4().hex);staging.mkdir()
  with tarfile.open(p) as tar:
   members=tar.getmembers()
   for m in members:
    q=(staging/m.name).resolve()
    if not q.is_relative_to(staging.resolve()) or m.issym() or m.islnk():raise RuntimeError("unsafe archive")
   print("EXTRACT",len(members),"members",flush=True)
   tar.extractall(staging)
  (staging/"mols").rename(dest/"mols");shutil.rmtree(staging)
  print("MOLS_READY",flush=True)

