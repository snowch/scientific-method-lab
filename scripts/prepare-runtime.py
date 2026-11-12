# Copyright © 2026 Christopher Snow
"""Vendor only pinned Pyodide packages and their dependency closure, checking hashes."""
import concurrent.futures, hashlib, json, shutil, urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
engine=root/'node_modules/pyodide'
lock=json.loads((engine/'pyodide-lock.json').read_text())
packages=lock['packages']
needed=set()
def visit(name):
    if name in needed: return
    needed.add(name)
    for dependency in packages[name]['depends']: visit(dependency)
for package in ['numpy','scipy','pandas','matplotlib']: visit(package)
cache=root/'.cache/packages'; cache.mkdir(parents=True,exist_ok=True)
base='https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'
def get(name):
    meta=packages[name]; path=cache/meta['file_name']
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=meta['sha256']:
        with urllib.request.urlopen(base+meta['file_name'],timeout=120) as response:
            body=response.read()
        if hashlib.sha256(body).hexdigest()!=meta['sha256']: raise ValueError('Hash mismatch: '+name)
        path.write_bytes(body)
    return {'name':name,'version':meta['version'],'file':meta['file_name'],'sha256':meta['sha256'],'source':base+meta['file_name']}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    manifest=list(pool.map(get,sorted(needed)))
dest=root/'dist/engine'; dest.mkdir(parents=True,exist_ok=True)
for file in engine.iterdir():
    if file.is_file() and file.name not in ['package.json','README.md']:
        shutil.copyfile(file,dest/file.name)
for item in manifest: shutil.copyfile(cache/item['file'],dest/item['file'])
(root/'dist/runtime-manifest.json').write_text(json.dumps({'pyodide':'0.27.7','packages':manifest},indent=2)+'\n')
print('Self-hosted pinned runtime:', ', '.join(f'{p["name"]} {p["version"]}' for p in manifest))
