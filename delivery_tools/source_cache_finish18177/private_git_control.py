# Root CPU control ONLY, after actual resumed-compatibility PASS.
# Insert in the existing qualified CPU transaction. No invocation has been performed here.
import os,re,json,hashlib,subprocess,stat
from pathlib import Path
R=Path('/lustre/users/u21111210118/projects/test9');REPO=R/'source'
CORE=R/'env/core/bin/python'
EXPORTER=R/'steps/24_benchmark_delivery/frozen/github_export_13086/github_source_export.py'
EXPORTER_SHA256='a824b6636c46d517ba91027074a182627fd164fb744c7782c9dec29a8e3ce1bd'
PUBLIC_PARENT='e2984a94674ffcb75b280680038df5e9f39d684d'
PRIVATE_BRANCH='delivery/private-ppi-blocker-20261018'
PRIVATE_MESSAGE='Complete matched PPI blocker benchmark source delivery'
C=ROOT_BIND_FINAL_PRIVATE_COMMIT_AND_EXPORT
# source_binding/current_compatibility_inputs are genuine outer-controller inputs, unchanged.
assert set(C)=={'source_binding','current_compatibility_inputs','approved_source_rows','bundle_path','export_dir'}
assert re.fullmatch(r'[0-9]+',os.environ.get('SLURM_JOB_ID',''))
assert not any(os.environ.get(k,'')for k in ['CUDA_VISIBLE_DEVICES','SLURM_JOB_GPUS','SLURM_STEP_GPUS'])
assert EXPORTER.stat().st_size==17447 and hashlib.sha256(EXPORTER.read_bytes()).hexdigest()==EXPORTER_SHA256

def git(*args):
 return subprocess.check_output(['git','-C',str(REPO),*args])
def receipt(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return dict(path=str(path),bytes=path.stat().st_size,sha256=h.hexdigest())
def core_state():
 def native(p,follow):
  s=os.stat(str(p),follow_symlinks=follow)
  return dict(path=str(p),mode=s.st_mode,uid=s.st_uid,gid=s.st_gid,bytes=s.st_size,dev=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
 return dict(logical=native(CORE,False),resolved=native(CORE.resolve(strict=True),True))
# The outer controller supplies existing Core/source authority; this is exact pre/post preservation.
core_before=core_state()
assert core_before['resolved']['path']==str(R/'env/core/bin/python3.11')and core_before['resolved']['bytes']==25916456
assert receipt(CORE.resolve(strict=True))['sha256']=='76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a'
head=git('rev-parse','HEAD').decode().strip()
assert re.fullmatch('[0-9a-f]{40}',head)
assert git('rev-parse','--show-toplevel').decode().strip()==str(REPO)
assert git('rev-parse','--is-shallow-repository').decode().strip()=='false'
assert not git('replace','-l').strip()
git('check-ref-format','--branch',PRIVATE_BRANCH)
assert subprocess.run(['git','-C',str(REPO),'show-ref','--verify','--quiet','refs/heads/'+PRIVATE_BRANCH]).returncode==1
old_public_refs=git('for-each-ref','--format=%(refname) %(objectname)','refs/heads/master','refs/heads/main')
rows=C['approved_source_rows'];required={r['repository_relative']for r in rows}
assert required and len(required)==len(rows)
# ALL qualified final rows, including existing2254 staged/modified/untracked and real resume rows.
allowed=required
for path in allowed:
 assert path and not path.startswith('/') and all(v not in ('','.','..','.git')for v in path.split('/'))
for row in rows:
 dest=REPO/row['repository_relative'];assert dest.is_file()and not dest.is_symlink()
 actual=receipt(dest)
 assert (actual['bytes'],actual['sha256'])==(row['source']['bytes'],row['source']['sha256'])
changed=set(git('diff','--no-renames','--name-only','-z','HEAD','--').decode().split('\0'))-{''}
staged=set(git('diff','--cached','--no-renames','--name-only','-z').decode().split('\0'))-{''}
untracked=set(git('ls-files','--others','--exclude-standard','-z').decode().split('\0'))-{''}
assert (changed|staged|untracked)<=allowed,('Unrelated changes must not be committed',sorted((changed|staged|untracked)-allowed))
bundle=Path(C['bundle_path']);export=Path(C['export_dir'])
assert bundle.is_absolute()and export.is_absolute()and R in bundle.parents and R in export.parents
assert REPO not in bundle.parents and REPO not in export.parents and not bundle.exists()and not export.exists()
# New branch from actual CPU HEAD preserves every parent and existing baseline entry.
git('checkout','-b',PRIVATE_BRANCH)
git('add','-f','--',*sorted(required))
assert set(git('diff','--cached','--no-renames','--name-only','-z').decode().split('\0'))-{''}<=allowed
if git('diff','--cached','--name-only','-z'):
 git('-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false','commit','-m',PRIVATE_MESSAGE)
private=git('rev-parse','HEAD').decode().strip()
if private!=head:assert git('show','-s','--format=%P',private).decode().strip()==head
assert set(git('diff','--no-renames','--name-only','-z',head,private,'--').decode().split('\0'))-{''}<=allowed
for row in rows:
 data=git('cat-file','blob',private+':'+row['repository_relative'])
 assert len(data)==row['source']['bytes']and hashlib.sha256(data).hexdigest()==row['source']['sha256']
assert not git('status','--porcelain=v1','-z','--untracked-files=all')
assert git('for-each-ref','--format=%(refname) %(objectname)','refs/heads/master','refs/heads/main')==old_public_refs
# All refs, no exclusions/prerequisites; bundle remains outside the public Source tree.
git('bundle','create',str(bundle),'--all')
verified=subprocess.run(['git','-C',str(REPO),'bundle','verify',str(bundle)],capture_output=True,check=True)
heads=git('bundle','list-heads',str(bundle)).decode()
assert private in {line.split()[0]for line in heads.splitlines()}
bfd=os.open(str(bundle),os.O_RDONLY|os.O_NOFOLLOW)
try:
 before=os.fstat(bfd);assert stat.S_ISREG(before.st_mode)and before.st_nlink==1
 os.fchmod(bfd,0o444);os.fsync(bfd)
 after=os.fstat(bfd);assert (after.st_dev,after.st_ino,after.st_size)==(before.st_dev,before.st_ino,before.st_size)and stat.S_IMODE(after.st_mode)==0o444
 assert os.stat(str(bundle),follow_symlinks=False)==after
finally:os.close(bfd)
pfd=os.open(str(bundle.parent),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(pfd)
finally:os.close(pfd)
assert core_state()==core_before
argv=[str(CORE),'-B',str(EXPORTER),'--repo',str(REPO),'--baseline',PUBLIC_PARENT,'--expected-head',private,'--output-dir',str(export),'--repository','ethanyangAI/ppi-cldm']
exported=subprocess.run(argv,capture_output=True,check=True)
core_after=core_state();assert core_after==core_before
assert receipt(CORE.resolve(strict=True))['sha256']=='76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a'
assert git('rev-parse','HEAD').decode().strip()==private and not git('status','--porcelain=v1','-z','--untracked-files=all')
print(json.dumps(dict(source_binding=C['source_binding'],current_compatibility_inputs=C['current_compatibility_inputs'],private_parent=head,private_commit=private,private_branch=PRIVATE_BRANCH,committed_required_source_rows=len(rows),final_tree=git('rev-parse',private+'^{tree}').decode().strip(),source_bundle=receipt(bundle),bundle_verify_stdout=verified.stdout.decode(),bundle_verify_stderr=verified.stderr.decode(),bundle_heads=heads,Core_logical_and_resolved_before=core_before,Core_logical_and_resolved_after=core_after,exporter_argv=argv,exporter_stdout=exported.stdout.decode(),exporter_stderr=exported.stderr.decode(),export_manifest=receipt(export/'export_manifest.json'),public_parent=PUBLIC_PARENT,public_commit_not_created=True,private_history_not_pushed=True)))
# Root LIVE re-verifies public master after private export, then publishes only this exact tree.
