import os
import json
import time


def build_run_id(target_name):
    return '%s_%s' % (target_name, time.strftime('%Y%m%d_%H%M%S'))


def build_output_paths(results_dir, target_name, run_id):
    base = os.path.join(results_dir, '%s_%s' % (target_name, run_id))
    latest = os.path.join(results_dir, '%s_candidates.csv' % target_name)
    return {
        'run_csv': base + '_candidates.csv',
        'run_manifest': base + '_manifest.json',
        'latest_csv': latest,
        'latest_manifest': os.path.join(results_dir, '%s_manifest.latest.json' % target_name),
    }


def _safe(v):
    if isinstance(v, bytes):
        return v.decode('utf-8', errors='replace')
    if isinstance(v, dict):
        return {k: _safe(vv) for k, vv in v.items()}
    if isinstance(v, list):
        return [_safe(x) for x in v]
    try:
        import numpy as np
        if isinstance(v, np.integer):
            return int(v)
        if isinstance(v, np.floating):
            return float(v)
    except ImportError:
        pass
    return v

def write_manifest(path, payload):
    with open(path, 'w') as f:
        json.dump(_safe(payload), f, indent=2, ensure_ascii=False, sort_keys=True)


def summarize_results(results):
    total = len(results)
    docked = [r for r in results if r.get('vina_score') not in (None, '', 'None')]
    undocked = total - len(docked)
    vina_scores = [float(r['vina_score']) for r in docked]
    pains_flagged = sum(1 for r in results if r.get('pains_flag') not in (None, '', 'None'))
    screened = [r for r in results if r.get('selectivity') is not None]

    summary = {
        'result_count': total,
        'docked_count': len(docked),
        'undocked_count': undocked,
        'pains_flagged': pains_flagged,
        'pains_clean': total - pains_flagged,
        'counter_screened': len(screened),
    }
    if vina_scores:
        summary['vina_best'] = round(min(vina_scores), 3)
        summary['vina_mean'] = round(sum(vina_scores) / len(vina_scores), 3)
    if screened:
        sel_vals = [float(r['selectivity']) for r in screened if r['selectivity'] is not None]
        if sel_vals:
            summary['selectivity_best'] = round(min(sel_vals), 3)
            summary['selectivity_mean'] = round(sum(sel_vals) / len(sel_vals), 3)
    return summary
