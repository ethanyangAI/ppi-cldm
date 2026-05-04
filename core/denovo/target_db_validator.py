import os
import json

try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)


OPTIONAL_TARGET_FIELDS = [
    'description', 'box_size', 'pdbqt_path', 'pocket_center', 'structure_source', 'complex_method',
    'complex_status', 'modeled_complex', 'pocket_center_method', 'generation_mode',
    'parent_targets', 'notes', 'failure_reason', 'resolved_complex_pdb',
    'complex_confidence'
]

READY_COMPLEX_STATUSES = ['ready', 'modeled']
UNAVAILABLE_COMPLEX_STATUSES = ['unavailable']


def read_pdb_chains(pdb_path):
    chains = []
    seen = set()
    with open(pdb_path) as f:
        for line in f:
            if line.startswith('ATOM') and len(line) > 21:
                ch = line[21].strip()
                if ch and ch not in seen:
                    seen.add(ch)
                    chains.append(ch)
    return chains


def validate_target_entry(name, info):
    errors = []
    warnings = []
    normalized = {}

    if not isinstance(info, dict):
        return {'errors': ['target entry is not a dict'], 'warnings': [], 'normalized': None}

    complex_status = info.get('complex_status', 'ready')
    generation_mode = info.get('generation_mode', 'interface_conditioned')

    required_fields = ['disease', 'known_drugs']
    if complex_status in READY_COMPLEX_STATUSES:
        required_fields.extend(['pdb', 'pdb_path', 'chain_receptor', 'chain_ligand'])
    elif complex_status in UNAVAILABLE_COMPLEX_STATUSES:
        if generation_mode != 'degraded_no_interface':
            errors.append('unavailable complex requires generation_mode=degraded_no_interface')
    else:
        errors.append('invalid complex_status %s' % complex_status)

    for key in required_fields:
        value = info.get(key)
        if value is None or value == '':
            errors.append('missing %s' % key)
        else:
            normalized[key] = value

    for key in OPTIONAL_TARGET_FIELDS:
        if key in info:
            normalized[key] = info.get(key)

    normalized['complex_status'] = complex_status
    normalized['generation_mode'] = generation_mode

    if 'known_drugs' in normalized and not isinstance(normalized['known_drugs'], list):
        if isinstance(normalized['known_drugs'], string_types):
            normalized['known_drugs'] = [x.strip() for x in normalized['known_drugs'].split(',') if x.strip()]
            warnings.append('known_drugs normalized from string')
        else:
            errors.append('known_drugs must be a list')

    pdb_path = normalized.get('pdb_path')
    if pdb_path and not os.path.exists(pdb_path):
        errors.append('pdb_path does not exist: %s' % pdb_path)

    center = normalized.get('pocket_center')
    if center is not None:
        ok_center = isinstance(center, (list, tuple)) and len(center) == 3
        if not ok_center:
            errors.append('pocket_center must be a 3-item list')
    elif complex_status in READY_COMPLEX_STATUSES and generation_mode != 'degraded_no_interface':
        warnings.append('pocket_center missing; docking may be skipped')

    box_size = normalized.get('box_size')
    if box_size is not None:
        ok_box = isinstance(box_size, (list, tuple)) and len(box_size) == 3
        if not ok_box:
            errors.append('box_size must be a 3-item list')
        elif any(v <= 0 for v in box_size):
            errors.append('box_size values must be positive, got %s' % list(box_size))

    if pdb_path and os.path.exists(pdb_path) and complex_status in READY_COMPLEX_STATUSES:
        chains = read_pdb_chains(pdb_path)
        chain_r = normalized.get('chain_receptor')
        chain_l = normalized.get('chain_ligand')
        if chain_r and chain_r not in chains:
            errors.append('chain_receptor %s not found in %s' % (chain_r, chains))
        if chain_l and chain_l not in chains:
            errors.append('chain_ligand %s not found in %s' % (chain_l, chains))

    return {'errors': errors, 'warnings': warnings, 'normalized': normalized}


def validate_target_db(db):
    valid = {}
    invalid = {}
    for name, info in db.items():
        result = validate_target_entry(name, info)
        if result['errors']:
            invalid[name] = result
        else:
            valid[name] = result['normalized']
    return valid, invalid


def load_and_validate_target_db(db_path):
    with open(db_path) as f:
        db = json.load(f)
    return validate_target_db(db)
