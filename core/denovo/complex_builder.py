import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import urllib.parse
import urllib.request


COLABFOLD_BIN = '/home/huangym/zjy/localcolabfold/colabfold-conda/bin/colabfold_batch'
COMMON_BACKENDS = [
    ('env', 'PPI_COMPLEX_DOCKING_CMD'),
    ('colabfold', COLABFOLD_BIN),
    ('ppi_complex_dock', None),
    ('build_ppi_complex', None),
    ('hdock_wrapper.py', None),
]

AA3_TO1 = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
    'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
    'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
    'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
    'MSE': 'M'
}


def safe_name(text):
    return re.sub(r'[^A-Za-z0-9._-]+', '_', text or 'target').strip('_') or 'target'


def search_single_protein_pdb(protein_name, rows=5):
    query = {
        'query': {
            'type': 'terminal',
            'service': 'full_text',
            'parameters': {'value': protein_name},
        },
        'return_type': 'entry',
        'request_options': {
            'paginate': {'start': 0, 'rows': rows},
            'sort': [{'sort_by': 'score', 'direction': 'desc'}],
        },
    }
    url = 'https://search.rcsb.org/rcsbsearch/v2/query?json=' + urllib.parse.quote(json.dumps(query))
    with urllib.request.urlopen(url, timeout=20) as response:
        body = response.read()
    if not body:
        return None
    data = json.loads(body.decode('utf-8'))
    hits = data.get('result_set', [])
    if not hits:
        return None
    return hits[0].get('identifier')


def lookup_uniprot_accession(protein_name, organism_id='9606'):
    query = '(gene_exact:{0} OR protein_name:{0}) AND organism_id:{1}'.format(protein_name, organism_id)
    params = {
        'query': query,
        'fields': 'accession,reviewed,protein_name,gene_names,organism_name',
        'format': 'json',
        'size': '3',
    }
    url = 'https://rest.uniprot.org/uniprotkb/search?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as response:
        body = response.read()
    if not body:
        return None
    data = json.loads(body.decode('utf-8'))
    results = data.get('results', [])
    if not results:
        return None
    return results[0].get('primaryAccession')


def download_alphafold_structure(uniprot_accession, out_path):
    url = 'https://alphafold.ebi.ac.uk/files/AF-{0}-F1-model_v4.pdb'.format(uniprot_accession)
    with urllib.request.urlopen(url, timeout=60) as response:
        body = response.read()
    if not body:
        return False
    with open(out_path, 'wb') as f:
        f.write(body)
    return os.path.exists(out_path) and os.path.getsize(out_path) > 0


def download_uniprot_fasta(uniprot_accession, out_path):
    url = 'https://rest.uniprot.org/uniprotkb/{0}.fasta'.format(uniprot_accession)
    with urllib.request.urlopen(url, timeout=60) as response:
        body = response.read()
    if not body:
        return False
    with open(out_path, 'wb') as f:
        f.write(body)
    return os.path.exists(out_path) and os.path.getsize(out_path) > 0


def run_colabfold_monomer_prediction(protein_name, fasta_path, output_dir, timeout=86400):
    os.makedirs(output_dir, exist_ok=True)
    command = [
        COLABFOLD_BIN,
        '--num-models', '1',
        '--num-recycle', '3',
        '--model-type', 'alphafold2_ptm',
        fasta_path,
        output_dir,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        notes = 'monomer prediction timed out after %ss' % timeout
        if exc.stderr:
            _b = exc.stderr if isinstance(exc.stderr, bytes) else exc.stderr.encode()
            notes = _b.decode('utf-8', errors='replace').strip() or notes
        elif exc.stdout:
            _b = exc.stdout if isinstance(exc.stdout, bytes) else exc.stdout.encode()
            notes = _b.decode('utf-8', errors='replace').strip() or notes
        return {
            'ok': False,
            'reason': 'monomer_prediction_timeout',
            'notes': notes,
        }

    if result.returncode != 0:
        return {
            'ok': False,
            'reason': 'monomer_prediction_failed',
            'notes': result.stderr.strip() or result.stdout.strip() or protein_name,
        }

    chosen_pdb, score_json = pick_colabfold_model(output_dir)
    if not chosen_pdb:
        return {
            'ok': False,
            'reason': 'monomer_prediction_output_missing',
            'notes': output_dir,
        }

    return {
        'ok': True,
        'pdb_path': chosen_pdb,
        'notes': chosen_pdb,
        'confidence': parse_colabfold_confidence(score_json),
    }


def detect_complex_backend(provider='auto'):
    if provider in ('none', 'manual'):
        return {'provider': provider, 'ok': False, 'reason': 'provider_disabled'}

    env_template = os.environ.get('PPI_COMPLEX_DOCKING_CMD')
    if env_template and provider in ('auto', 'dock'):
        return {
            'provider': 'env',
            'ok': True,
            'command_template': env_template,
            'complex_method': 'protein_docking',
        }

    if provider in ('auto', 'dock', 'colabfold') and os.path.exists(COLABFOLD_BIN):
        return {
            'provider': 'colabfold',
            'ok': True,
            'path': COLABFOLD_BIN,
            'complex_method': 'alphafold_multimer',
        }

    for name, _ in COMMON_BACKENDS[2:]:
        path = shutil.which(name)
        if path and provider in ('auto', 'dock'):
            return {
                'provider': name,
                'ok': True,
                'path': path,
                'complex_method': 'protein_docking',
            }

    return {
        'provider': provider,
        'ok': False,
        'reason': 'no_supported_complex_builder_found',
    }


def resolve_structure_input(label, protein_name, cache_dir, provided_pdb=None, fetch_pdb_func=None):
    if provided_pdb:
        if os.path.exists(provided_pdb):
            return {
                'ok': True,
                'pdb_path': provided_pdb,
                'pdb_id': None,
                'source': 'provided',
            }
        return {
            'ok': False,
            'reason': '%s_pdb_not_found' % label,
            'notes': 'missing file: %s' % provided_pdb,
        }

    pdb_id = None
    rcsb_error = None
    try:
        pdb_id = search_single_protein_pdb(protein_name)
    except Exception as exc:
        rcsb_error = str(exc)

    if pdb_id and fetch_pdb_func is not None:
        out_path = os.path.join(cache_dir, '%s_%s.pdb' % (safe_name(protein_name), pdb_id.lower()))
        if not os.path.exists(out_path):
            fetch_pdb_func(pdb_id, out_path)
        if os.path.exists(out_path):
            return {
                'ok': True,
                'pdb_path': out_path,
                'pdb_id': pdb_id,
                'source': 'rcsb_search',
                'reason': None,
            }

    try:
        accession = lookup_uniprot_accession(protein_name)
    except Exception as exc:
        return {
            'ok': False,
            'reason': '%s_structure_search_failed' % label,
            'notes': rcsb_error or str(exc),
        }

    if not accession:
        return {
            'ok': False,
            'reason': '%s_structure_not_found' % label,
            'notes': rcsb_error or protein_name,
        }

    af_path = os.path.join(cache_dir, '%s_%s_afdb.pdb' % (safe_name(protein_name), accession.lower()))
    af_error = None
    try:
        if not os.path.exists(af_path):
            ok = download_alphafold_structure(accession, af_path)
        else:
            ok = True
    except Exception as exc:
        ok = False
        af_error = str(exc)

    if ok and os.path.exists(af_path):
        return {
            'ok': True,
            'pdb_path': af_path,
            'pdb_id': accession,
            'source': 'alphafold_db',
            'reason': None,
        }

    if not os.path.exists(COLABFOLD_BIN):
        return {
            'ok': False,
            'reason': '%s_alphafold_download_failed' % label,
            'notes': af_error or 'alphafold_db_unavailable',
        }

    fasta_path = os.path.join(cache_dir, '%s_%s.fasta' % (safe_name(protein_name), accession.lower()))
    try:
        if not os.path.exists(fasta_path):
            fasta_ok = download_uniprot_fasta(accession, fasta_path)
        else:
            fasta_ok = True
    except Exception as exc:
        return {
            'ok': False,
            'reason': '%s_sequence_download_failed' % label,
            'notes': str(exc),
        }

    if not fasta_ok or not os.path.exists(fasta_path):
        return {
            'ok': False,
            'reason': '%s_sequence_download_failed' % label,
            'notes': accession,
        }

    monomer_dir = os.path.join(cache_dir, '%s_%s_monomer_cf' % (safe_name(protein_name), accession.lower()))
    predicted = run_colabfold_monomer_prediction(protein_name, fasta_path, monomer_dir)
    if not predicted.get('ok'):
        return {
            'ok': False,
            'reason': predicted.get('reason') or '%s_monomer_prediction_failed' % label,
            'notes': predicted.get('notes') or af_error or accession,
        }

    predicted_out = os.path.join(cache_dir, '%s_%s_monomer_cf.pdb' % (safe_name(protein_name), accession.lower()))
    shutil.copyfile(predicted['pdb_path'], predicted_out)
    return {
        'ok': True,
        'pdb_path': predicted_out,
        'pdb_id': accession,
        'source': 'colabfold_monomer',
        'reason': None,
    }


def format_shell_command(template, values):
    safe_values = dict((key, shlex.quote(str(value))) for key, value in values.items())
    return template.format(**safe_values)


def extract_primary_sequence_from_pdb(pdb_path):
    chains = {}
    seen = set()
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith('ATOM'):
                continue
            if line[12:16].strip() != 'CA':
                continue
            chain = line[21].strip() or 'A'
            resname = line[17:20].strip().upper()
            aa = AA3_TO1.get(resname)
            if aa is None:
                continue
            resid = (chain, line[22:26].strip(), line[26].strip())
            if resid in seen:
                continue
            seen.add(resid)
            chains.setdefault(chain, []).append(aa)
    if not chains:
        return None
    best_chain = sorted(chains.items(), key=lambda item: len(item[1]), reverse=True)[0]
    return ''.join(best_chain[1])


def pick_colabfold_model(output_dir):
    pdbs = sorted(glob.glob(os.path.join(output_dir, '*.pdb')))
    if not pdbs:
        return None, None

    preferred = []
    preferred.extend([p for p in pdbs if 'relaxed_rank_001' in os.path.basename(p)])
    preferred.extend([p for p in pdbs if 'unrelaxed_rank_001' in os.path.basename(p)])
    preferred.extend(pdbs)
    chosen = preferred[0]

    json_path = None
    base = os.path.basename(chosen)
    if '_relaxed_' in base:
        candidate = os.path.join(output_dir, base.replace('_relaxed_', '_scores_').rsplit('.pdb', 1)[0] + '.json')
        if os.path.exists(candidate):
            json_path = candidate
    if json_path is None and '_unrelaxed_' in base:
        candidate = os.path.join(output_dir, base.replace('_unrelaxed_', '_scores_').rsplit('.pdb', 1)[0] + '.json')
        if os.path.exists(candidate):
            json_path = candidate
    return chosen, json_path


def parse_colabfold_confidence(json_path):
    if not json_path or not os.path.exists(json_path):
        return None
    try:
        data = json.load(open(json_path))
    except Exception:
        return None
    for key in ['iptm', 'ptm', 'ranking_confidence']:
        if key in data:
            return data.get(key)
    return None


def run_colabfold_builder(backend, receptor_pdb, ligand_pdb, output_pdb, work_dir, timeout=21600):
    receptor_seq = extract_primary_sequence_from_pdb(receptor_pdb)
    ligand_seq = extract_primary_sequence_from_pdb(ligand_pdb)
    if not receptor_seq or not ligand_seq:
        return {
            'ok': False,
            'reason': 'sequence_extraction_failed',
            'notes': 'failed to extract sequences from receptor/ligand pdb',
        }

    os.makedirs(work_dir, exist_ok=True)
    base = safe_name(os.path.splitext(os.path.basename(output_pdb))[0])
    input_fasta = os.path.join(work_dir, '%s.fasta' % base)
    output_dir = os.path.join(work_dir, '%s_colabfold' % base)

    with open(input_fasta, 'w') as f:
        f.write('>%s\n%s:%s\n' % (base, receptor_seq, ligand_seq))

    command = [
        backend['path'],
        '--num-models', '1',
        '--num-recycle', '3',
        input_fasta,
        output_dir,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        notes = result.stderr.strip() or result.stdout.strip() or 'colabfold_failed'
        return {
            'ok': False,
            'reason': 'complex_builder_command_failed',
            'notes': notes,
        }

    chosen_pdb, score_json = pick_colabfold_model(output_dir)
    if not chosen_pdb:
        return {
            'ok': False,
            'reason': 'complex_builder_output_missing',
            'notes': output_dir,
        }

    shutil.copyfile(chosen_pdb, output_pdb)
    return {
        'ok': True,
        'complex_pdb': output_pdb,
        'notes': chosen_pdb,
        'complex_confidence': parse_colabfold_confidence(score_json),
    }


def run_complex_builder(backend, receptor_pdb, ligand_pdb, output_pdb, work_dir):
    if not backend.get('ok'):
        return {
            'ok': False,
            'reason': backend.get('reason') or 'complex_builder_unavailable',
            'notes': backend.get('provider'),
        }

    os.makedirs(work_dir, exist_ok=True)

    if backend['provider'] == 'colabfold':
        return run_colabfold_builder(backend, receptor_pdb, ligand_pdb, output_pdb, work_dir, timeout=21600)

    if backend['provider'] == 'env':
        command = format_shell_command(backend['command_template'], {
            'receptor_pdb': receptor_pdb,
            'ligand_pdb': ligand_pdb,
            'output_pdb': output_pdb,
            'work_dir': work_dir,
        })
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=3600)
    else:
        command = [
            backend['path'],
            '--receptor', receptor_pdb,
            '--ligand', ligand_pdb,
            '--out', output_pdb,
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=3600)

    if result.returncode != 0:
        notes = result.stderr.strip() or result.stdout.strip() or backend['provider']
        return {
            'ok': False,
            'reason': 'complex_builder_command_failed',
            'notes': notes,
        }

    if not os.path.exists(output_pdb):
        return {
            'ok': False,
            'reason': 'complex_builder_output_missing',
            'notes': output_pdb,
        }

    return {
        'ok': True,
        'complex_pdb': output_pdb,
        'notes': result.stdout.strip() or backend['provider'],
    }


def build_modeled_complex(name, protein1, protein2, cache_dir, provider='auto', modeled_complex_pdb=None,
                          receptor_pdb=None, ligand_pdb=None, fetch_pdb_func=None):
    if modeled_complex_pdb:
        if os.path.exists(modeled_complex_pdb):
            return {
                'ok': True,
                'complex_pdb': modeled_complex_pdb,
                'complex_method': 'manual_model',
                'structure_source': 'manual',
                'complex_status': 'modeled',
                'modeled_complex': True,
                'notes': 'modeled complex provided by user',
            }
        return {
            'ok': False,
            'failure_reason': 'modeled_complex_pdb_not_found',
            'notes': modeled_complex_pdb,
        }

    receptor = resolve_structure_input('receptor', protein1, cache_dir, receptor_pdb, fetch_pdb_func)
    if not receptor.get('ok'):
        return {
            'ok': False,
            'failure_reason': receptor.get('reason') or 'receptor_structure_unavailable',
            'notes': receptor.get('notes'),
        }

    ligand = resolve_structure_input('ligand', protein2, cache_dir, ligand_pdb, fetch_pdb_func)
    if not ligand.get('ok'):
        return {
            'ok': False,
            'failure_reason': ligand.get('reason') or 'ligand_structure_unavailable',
            'notes': ligand.get('notes'),
        }

    backend = detect_complex_backend(provider)
    output_pdb = os.path.join(cache_dir, '%s_modeled_complex.pdb' % safe_name(name))
    built = run_complex_builder(backend, receptor['pdb_path'], ligand['pdb_path'], output_pdb, cache_dir)
    if not built.get('ok'):
        return {
            'ok': False,
            'failure_reason': built.get('reason') or 'complex_builder_failed',
            'notes': built.get('notes'),
            'receptor_pdb': receptor['pdb_path'],
            'ligand_pdb': ligand['pdb_path'],
        }

    return {
        'ok': True,
        'complex_pdb': built['complex_pdb'],
        'complex_method': backend.get('complex_method', 'protein_docking'),
        'complex_status': 'modeled',
        'structure_source': 'modeled',
        'modeled_complex': True,
        'notes': built.get('notes'),
        'complex_confidence': built.get('complex_confidence'),
        'receptor_pdb': receptor['pdb_path'],
        'ligand_pdb': ligand['pdb_path'],
    }
