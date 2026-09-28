"""Content-based P3 runtime provenance; same-host verification, not attestation."""
import hashlib,json,os,platform,re,subprocess,sys,sysconfig
from pathlib import Path

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def loaded_native_paths():
    # Linux production host. Anonymous mappings/vDSO are covered by platform
    # metadata only; this is not a kernel, hardware, or container attestation.
    result=set()
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields=line.split(None,5)
        if len(fields)==6 and fields[5].startswith('/'):
            path=Path(fields[5])
            if path.is_file() and ('.so' in path.name or str(path.resolve())==str(Path(sys.executable).resolve())):result.add(str(path.resolve()))
    return result

def file_manifest(paths):
    return {str(Path(p).absolute()):{'resolved':str(Path(p).resolve()),'sha256':digest(p),'bytes':Path(p).stat().st_size} for p in sorted(set(map(str,paths)))}

def verify_files(files):
    if not files:raise ValueError('empty dependency inventory')
    for name,row in files.items():
        p=Path(name)
        if str(p.resolve())!=row['resolved'] or digest(p)!=row['sha256']:raise ValueError('dependency changed: '+name)

def capture_manifest(kernel_path):
    # Manifest capture needs NumPy/SciPy package roots and versions.
    # Keep these imports local so verification-only supervisor processes
    # do not permanently map the scientific runtime before RLIMIT_AS.
    import numpy as np
    import scipy
    paths={str(Path(sys.executable).absolute()),str(Path(sys.executable).resolve()),str(Path(kernel_path).absolute())}
    roots=[Path(sysconfig.get_path('stdlib')),Path(np.__file__).parent,Path(scipy.__file__).parent]
    roots += [p.parent/(p.name+'.libs') for p in roots[1:]]
    for root in roots:
        if not root.exists():continue
        for p in root.rglob('*'):
            if any(x in ('__pycache__','site-packages','dist-packages') for x in p.relative_to(root).parts):continue
            if p.is_file() and (p.suffix in ('.py','.json','.cfg','.ini') or '.so' in p.name):paths.add(str(p.absolute()))
    paths.update(loaded_native_paths())
    # Resolve native dependencies of all inventoried extension/shared objects,
    # not only those loaded by this particular deterministic preflight.
    inspection_dirs=sorted({str(Path(p).parent) for p in paths if '.so' in Path(p).name})
    inspection_env={**os.environ,'LD_LIBRARY_PATH':':'.join(inspection_dirs)}
    for name in list(paths):
        if '.so' not in Path(name).name:continue
        result=subprocess.run(['ldd',name],capture_output=True,text=True,env=inspection_env)
        if result.returncode:raise ValueError('cannot resolve native dependencies: '+name)
        if 'not found' in result.stdout:raise ValueError('missing native dependency: '+name)
        for line in result.stdout.splitlines():
            match=re.search(r'(?:=>\s+)?(/[^\s]+)',line)
            if match:paths.add(match.group(1))
    return {'schema':'cpc-shor-p3-dependencies/1','python_executable':str(Path(sys.executable).absolute()),
        'python_build':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,
        'loader_environment':{k:os.environ.get(k,'') for k in ('LD_LIBRARY_PATH','LD_PRELOAD')},
        'files':file_manifest(paths),
        'coverage':'interpreter, stdlib source/extensions, NumPy/SciPy source/extensions/bundled libs, recursively linked system libraries, kernel and currently mapped native libraries',
        'native_inspection':'ldd uses inventoried package/private native directories to resolve transitive bundled libraries when inspecting an individual child .so; production loader environment is separately recorded and checked',
        'limitations':'same-host content identities, not hermetic build reproduction or security attestation; kernel/hardware/scheduler/compiler reproducibility not established; source C and produced kernel are sealed separately'}

def verify_manifest(path,expected_sha256):
    if digest(path)!=expected_sha256:raise ValueError('dependency manifest identity mismatch')
    m=json.loads(Path(path).read_text())
    if m.get('schema')!='cpc-shor-p3-dependencies/1':raise ValueError('dependency schema')
    if m['python_executable']!=str(Path(sys.executable).absolute()) or m['python_build']!=sys.version:raise ValueError('interpreter identity mismatch')
    if m['loader_environment']!={k:os.environ.get(k,'') for k in ('LD_LIBRARY_PATH','LD_PRELOAD')}:raise ValueError('native loader configuration changed')
    verify_files(m['files'])
    resolved={row['resolved'] for row in m['files'].values()}
    if not loaded_native_paths()<=resolved:raise ValueError('unsealed native mapping')
    return m
