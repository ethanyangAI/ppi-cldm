"""Executed by the actual backend Python; no imports of model/GPU libraries."""
import hashlib
import importlib.metadata as metadata
import json
import sys
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def probe():
    packages=[];files={}
    model_packages={'boltz','rfdiffusion','se3-transformer','e3nn','dgl','dllogger'}
    for dist in metadata.distributions():
        name=dist.metadata.get('Name','').lower().replace('_','-')
        packages.append({'name':name,'version':dist.version})
        if name in model_packages:
            for entry in dist.files or []:
                path=Path(dist.locate_file(entry)).resolve()
                if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc':
                    files[str(path)]={'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}
    exe=Path(sys.executable).resolve()
    return {'python':sys.version,'executable':{'path':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size},
            'packages':sorted(packages,key=lambda x:(x['name'],x['version'])),
            'model_distribution_files':[files[k] for k in sorted(files)]}

if __name__=='__main__':print(json.dumps(probe(),sort_keys=True))
