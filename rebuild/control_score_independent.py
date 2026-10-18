"""Independent CPU-only audit of the 78-control AF2 prediction/scoring release.

No producer modules are imported. PDB fixed-column parsing, blocked NumPy
distances, explicit per-residue statistics and A3M parsing are implemented here.
"""
import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys
import traceback

import numpy as np

ROOT = Path("/lustre/users/u21111210118/projects/test9")
STEP = ROOT / "steps/17_control_calibration"
OUT = STEP / "independent_review"
AA = dict(zip(
    "ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split(),
    "ARNDCQEGHILKMFPSTWYV"))
EXPECTED_MODELS = {(m, s) for m in range(1, 6) for s in (1042, 1043, 1044)}
STAT_KEYS = (
    "global_iptm", "global_ptm", "target_plddt", "binder_plddt",
    "interface_plddt", "bidirectional_contact_PAE_A", "confidence_baseline")
VERIFIED = {}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def record(path):
    p = Path(path)
    return {"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size}


def verify(receipt):
    p = Path(receipt["path"])
    observed = VERIFIED.get(str(p))
    if observed is None:
        observed = record(p)
        VERIFIED[str(p)] = observed
    assert observed["sha256"] == receipt["sha256"], ("hash", str(p))
    if "bytes" in receipt:
        assert observed["bytes"] == receipt["bytes"], ("size", str(p))
    return p


def read(receipt):
    return json.loads(verify(receipt).read_text())


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as fh:
        json.dump(obj, fh, indent=2, allow_nan=False)
        fh.write("\n")


def compare(expected, actual, location="root"):
    """Fail closed for key, type, Boolean, null or numeric disagreement."""
    if expected is None or isinstance(expected, (str, bool)):
        assert type(expected) is type(actual) and expected == actual, (
            location, expected, actual)
    elif isinstance(expected, (int, float)):
        assert isinstance(actual, (int, float)) and not isinstance(actual, bool), (
            location, expected, actual)
        assert math.isfinite(expected) and math.isfinite(actual), location
        if isinstance(expected, int):
            assert expected == actual, (location, expected, actual)
        else:
            assert math.isclose(expected, actual, rel_tol=1e-10, abs_tol=1e-10), (
                location, expected, actual)
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(expected) == len(actual), location
        for i, (e, a) in enumerate(zip(expected, actual)):
            compare(e, a, f"{location}[{i}]")
    elif isinstance(expected, dict):
        assert isinstance(actual, dict) and set(expected) == set(actual), (
            location, set(expected), set(actual))
        for k in expected:
            compare(expected[k], actual[k], f"{location}.{k}")
    else:
        raise TypeError(type(expected))


def contacts(ax, ar, bx, br, cutoff=5.0):
    """Return unique residue pairs from blocked atom distance matrices."""
    ax = np.asarray(ax, dtype=float)
    bx = np.asarray(bx, dtype=float)
    ar = np.asarray(ar, dtype=int)
    br = np.asarray(br, dtype=int)
    pairs = set()
    for start in range(0, len(ax), 128):
        delta = ax[start:start + 128, None, :] - bx[None, :, :]
        i, j = np.nonzero(np.einsum("ijk,ijk->ij", delta, delta) <= cutoff ** 2)
        pairs.update(zip(ar[start + i].tolist(), br[j].tolist()))
    return sorted(pairs)


def confidence(iptm, binder, interface, pae):
    values = (iptm, binder, interface, pae)
    if any(v is None or not math.isfinite(v) for v in values):
        return None
    if any(v < 0 or v > 1 for v in values[:3]) or pae < 0:
        return None
    components = [iptm / 0.75, binder / 0.8, interface / 0.8]
    if pae != 0:
        components.append(8.0 / pae)
    return min(components)


def reduction(values, expected=15):
    valid = [float(v) for v in values if v is not None and math.isfinite(v)]
    full = len(values) == expected and len(valid) == expected
    return {
        "n_expected": expected, "n_valid": len(valid),
        "n_missing": expected - len(valid),
        "median": float(statistics.median(valid)) if full else None,
        "observed_only_median": float(statistics.median(valid)) if valid else None,
        "min": min(valid) if valid else None, "max": max(valid) if valid else None}


def interface_statistics(pairs, plddt, pae, n_target):
    if not pairs:
        return None, None, None, None
    forward = [float(pae[a, n_target + b]) for a, b in pairs]
    reverse = [float(pae[n_target + b, a]) for a, b in pairs]
    included = sorted({a for a, b in pairs} | {n_target + b for a, b in pairs})
    a_to_b, b_to_a = statistics.fmean(forward), statistics.fmean(reverse)
    both = statistics.fmean(forward + reverse)
    interface = statistics.fmean(float(plddt[i]) for i in included)
    return a_to_b, b_to_a, both, interface


def pdb_atoms(path, sequences):
    chain_data = collections.OrderedDict()
    model_tags = 0
    for line in Path(path).read_text().splitlines():
        if line.startswith("MODEL "):
            model_tags += 1
        if line.startswith("HETATM"):
            raise AssertionError("Unexpected HETATM in unrelaxed AF2 output")
        if not line.startswith("ATOM  "):
            continue
        assert line[16] == " " and line[26] == " ", "altloc/insertion not expected"
        cid = line[21]
        rkey = int(line[22:26])
        resname = line[17:20].strip()
        aname = line[12:16].strip()
        assert resname in AA, resname
        rs = chain_data.setdefault(cid, collections.OrderedDict())
        r = rs.setdefault(rkey, {"name": resname, "atoms": {}})
        assert r["name"] == resname and aname not in r["atoms"]
        xyz = [float(line[30:38]), float(line[38:46]), float(line[46:54])]
        assert all(math.isfinite(x) for x in xyz)
        element = line[76:78].strip()
        if not element:
            element = re.sub("[0-9]", "", aname)[0]
        r["atoms"][aname] = (xyz, element)
    assert model_tags <= 1 and list(chain_data) == ["A", "B"]
    arrays = []
    for chain, sequence in zip(chain_data.values(), sequences):
        assert len(chain) == len(sequence)
        assert "".join(AA[r["name"]] for r in chain.values()) == sequence
        coords, indices = [], []
        for i, residue in enumerate(chain.values()):
            assert "CA" in residue["atoms"]
            for xyz, element in residue["atoms"].values():
                if element not in ("H", "D"):
                    coords.append(xyz)
                    indices.append(i)
        # Biopython's accepted PDB coordinate representation is float32.
        # Cast independently parsed decimals to the same representation, then
        # calculate distances in float64 (as producer cKDTree does).
        arrays.append((np.asarray(coords, dtype=np.float32).astype(float), indices))
    return arrays


def score_one(model, condition):
    pdb = verify(model["pdb"])
    raw = read(model["scores"])
    match = re.search(r"_model_(\d+)_seed_(\d+)\.pdb$", pdb.name)
    assert match and tuple(map(int, match.groups())) == (model["model"], model["seed"])
    assert Path(model["scores"]["path"]).name == pdb.name.replace(
        "_unrelaxed_", "_scores_").replace(".pdb", ".json")
    target, binder = condition["target_sequence"], condition["sequence"]
    n_a, n_b = len(target), len(binder)
    assert model["chain_lengths"] == [n_a, n_b]
    assert model["pae_shape"] == [n_a + n_b, n_a + n_b]
    atoms = pdb_atoms(pdb, (target, binder))
    plddt = np.asarray(raw["plddt"], dtype=float) / 100.0
    pae = np.asarray(raw["pae"], dtype=float)
    assert plddt.shape == (n_a + n_b,) and pae.shape == (n_a + n_b, n_a + n_b)
    assert np.isfinite(plddt).all() and np.isfinite(pae).all()
    assert ((0 <= plddt) & (plddt <= 1)).all() and (pae >= 0).all()
    iptm, ptm = float(raw["iptm"]), float(raw["ptm"])
    assert all(math.isfinite(v) and 0 <= v <= 1 for v in (iptm, ptm))
    pairs = contacts(atoms[0][0], atoms[0][1], atoms[1][0], atoms[1][1])
    a_to_b, b_to_a, both, inter = interface_statistics(pairs, plddt, pae, n_a)
    bp = statistics.fmean(plddt[n_a:].tolist())
    tp = statistics.fmean(plddt[:n_a].tolist())
    baseline = confidence(iptm, bp, inter, both)
    return {
        "model": model["model"], "seed": model["seed"],
        "global_iptm": iptm, "global_ptm": ptm,
        "target_plddt": tp, "binder_plddt": bp, "interface_plddt": inter,
        "contact_PAE_A_to_B": a_to_b, "contact_PAE_B_to_A": b_to_a,
        "bidirectional_contact_PAE_A": both,
        "contact_residue_pair_count": len(pairs),
        "target_contact_residue_count": len({p[0] for p in pairs}),
        "binder_contact_residue_count": len({p[1] for p in pairs}),
        "confidence_baseline": baseline,
        "baseline_pass": None if baseline is None else baseline >= 1.0,
        "missing_reason": None if baseline is not None else
            "No cross-chain heavy-atom contact residue pairs at 5 A",
        "pdb": model["pdb"], "scores": model["scores"]}


def a3m_rows(path):
    lines = Path(path).read_text().splitlines()
    assert lines and lines[0].startswith("#")
    lengths, cardinality = lines[0][1:].split("\t")
    lengths = list(map(int, lengths.split(",")))
    cardinality = list(map(int, cardinality.split(",")))
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        if line.startswith(">"):
            rows.append([line[1:], ""])
        else:
            assert rows and not line.startswith("#")
            rows[-1][1] += line.strip()
    assert rows and all(sequence for header, sequence in rows)
    return lines[0], lengths, cardinality, rows


def split_alignment(raw, lengths):
    boundaries = np.cumsum(lengths)
    aligned_columns = 0
    parts = [""] * len(lengths)
    for c in raw:
        idx = int(np.searchsorted(boundaries, aligned_columns, side="right"))
        assert idx < len(lengths), "trailing insertion or excessive aligned columns"
        parts[idx] += c
        if not c.islower():
            aligned_columns += 1
    assert aligned_columns == sum(lengths)
    return parts


def alignment_feature(raw):
    residues, deletion = [], []
    inserted = 0
    for c in raw:
        if c.islower():
            inserted += 1
        else:
            residues.append(c)
            deletion.append(inserted)
            inserted = 0
    # AF2 discards insertion after the final aligned column.
    return "".join(residues), deletion


def a3m_features(path, target, binder):
    header, lengths, cardinality, rows = a3m_rows(path)
    assert lengths == [len(target), len(binder)] and cardinality == [1, 1]
    assert rows[0][1] == target + binder
    unpaired = [{"sequences": [], "deletion_matrix": []} for _ in range(2)]
    paired = [{"sequences": [], "deletion_matrix": []} for _ in range(2)]
    seen = set()
    for label, raw in rows:
        identity = (label, raw)
        if identity in seen:
            continue
        seen.add(identity)
        parts = split_alignment(raw, lengths)
        converted = [alignment_feature(part) for part in parts]
        present = [any(c != "-" for c in seq) for seq, deletion in converted]
        destination = paired if all(present) else unpaired
        for i in range(2):
            if present[i]:
                seq, deletion = converted[i]
                destination[i]["sequences"].append(seq)
                destination[i]["deletion_matrix"].append(deletion)
    return {"query": [target, binder], "cardinality": cardinality,
            "unpaired": unpaired, "paired": paired}


def fingerprint(obj):
    return hashlib.sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_msa(original, actual, semantic, target, binder):
    source, dest = verify(original), verify(actual)
    receipt = read(semantic)
    compare(original, receipt["input"], "msa input receipt")
    compare(actual, receipt["actual"], "msa actual receipt")
    assert receipt["status"] == "EXACT_CHAIN_QUERY_PAIRED_UNPAIRED_ORDER_AND_DELETION_MATRICES_VERIFIED"
    before = a3m_features(source, target, binder)
    after = a3m_features(dest, target, binder)
    compare(before, after, "independent MSA features")
    assert after["unpaired"][1]["sequences"] == [binder]
    assert after["paired"][0]["sequences"] == [target]
    assert after["paired"][1]["sequences"] == [binder]
    assert fingerprint(after) == receipt["features_sha256"]
    a, b = a3m_rows(source), a3m_rows(dest)
    assert a[0] == b[0]
    rows_a, rows_b = a[3], b[3]
    indices = collections.defaultdict(list)
    for i, (_, seq) in enumerate(rows_a):
        indices[seq].append(i)
    mapping, skipped, changed = [], [], []
    previous = -1
    for j, (header, seq) in enumerate(rows_b):
        choices = [i for i in indices[seq] if i > previous]
        assert choices, "actual MSA row is not ordered input row"
        i = choices[0]
        skipped.extend(range(previous + 1, i))
        mapping.append(i)
        if rows_a[i][0] != header:
            changed.append(j)
        previous = i
    skipped.extend(range(previous + 1, len(rows_a)))
    actual_seqs = {r[1] for r in rows_b}
    assert all(rows_a[i][1] in actual_seqs for i in skipped)
    compare(mapping, receipt["actual_row_to_input_row_0based"], "MSA ordered mapping")
    compare(skipped, receipt["removed_duplicate_input_rows_0based"], "MSA skipped rows")
    compare(changed, receipt["changed_header_actual_rows_0based"], "MSA headers")
    assert len(rows_a) == receipt["input_raw_row_count"]
    assert len(rows_b) == receipt["actual_raw_row_count"]
    regions = {}
    for label in ("unpaired", "paired"):
        regions[label] = [
            {"chain": i, "row_count": len(c["sequences"]),
             "ordered_sequences_sha256": fingerprint(c["sequences"]),
             "deletion_matrix_sha256": fingerprint(c["deletion_matrix"]),
             "deletion_total": sum(sum(r) for r in c["deletion_matrix"])}
            for i, c in enumerate(after[label])]
    compare(regions, receipt["regions"], "MSA per-chain region digests")
    return {"features_sha256": fingerprint(after), "actual_raw_rows": len(rows_b),
            "input_raw_rows": len(rows_a), "removed_duplicate_rows": len(skipped),
            "paired_query_only": True, "binder_single_sequence": True}


def verify_config(config):
    required = {
        "max_seq": 128, "max_extra_seq": 256, "num_recycles": 12,
        "num_models": 5, "num_seeds": 3, "num_relax": 0,
        "use_templates": False, "model_type": "alphafold2_multimer_v3",
        "random_seed": 1042, "recycle_early_stop_tolerance": 0.5}
    for k, v in required.items():
        compare(v, config[k], "effective_config." + k)


def tests():
    assert confidence(.9, .8, .8, 0) == 1
    assert confidence(.9, .8, .8, 8) == 1
    assert math.isclose(confidence(.3, .8, .8, 0), .4)
    assert confidence(.9, .8, None, 0) is None
    assert confidence(.9, .8, .8, float("nan")) is None
    assert confidence(.9, .8, .8, -1) is None
    assert reduction([1] * 14)["median"] is None
    assert reduction([0] * 15)["median"] == 0
    assert reduction([1] * 14 + [None])["n_missing"] == 1
    # Duplicate atom contacts must count each residue pair exactly once.
    a = [[0, 0, 0], [.1, 0, 0], [20, 0, 0]]
    b = [[1, 0, 0], [2, 0, 0]]
    assert contacts(a, [0, 0, 1], b, [0, 0]) == [(0, 0)]
    assert contacts([[0, 0, 0]], [0], [[20, 0, 0]], [0]) == []
    assert contacts([[0, 0, 0]], [0], [[5, 0, 0]], [0]) == [(0, 0)]
    # Directional PAE and unique-residue pLDDT must use distinct denominators.
    plddt = np.array([.2, .4, .6, .8])
    pae = np.zeros((4, 4))
    pae[0, 2], pae[0, 3], pae[2, 0], pae[3, 0] = 2, 4, 10, 12
    fwd, rev, mean, inter = interface_statistics([(0, 0), (0, 1)], plddt, pae, 2)
    assert (fwd, rev, mean) == (3, 11, 7)
    assert math.isclose(inter, (.2 + .6 + .8) / 3)
    assert interface_statistics([], plddt, pae, 2) == (None, None, None, None)
    assert alignment_feature("AaBCdd-") == ("ABC-", [0, 1, 0, 2])
    assert split_alignment("ABcc-CD", [3, 2]) == ["ABcc-", "CD"]
    for left, right in ((None, 0), (True, 1), (False, None), ({"a": 1}, {"a": 1, "b": 0})):
        rejected = False
        try:
            compare(left, right)
        except AssertionError:
            rejected = True
        assert rejected
    return {"status": "PASSED", "tests": [
        "zero interface yields null", "zero PAE is nonlimiting",
        "asymmetric PAE averages both directions", "duplicate contacts not weighted",
        "unique interface residue pLDDT denominator", "closed 5 A boundary",
        "incomplete identity median null", "numeric zero retained",
        "Boolean null number type distinction", "A3M lowercase deletion features"]}


def audit(array):
    test_result = tests()
    summary_p = STEP / "outputs" / f"score_summary_{array}.json"
    production = json.loads(summary_p.read_text())
    assert production["status"] == "ALL_78_CONTROLS_SCORED_WITH_EXPLICIT_MISSINGNESS"
    plan = read(production["plan"])
    assert record(STEP / "plan_v2.json") == production["plan"]
    original_plan = read(plan["previous_plan"])
    for field in ("conditions", "inference", "scoring", "counts"):
        compare(original_plan[field], plan[field], "unchanged scientific plan." + field)
    for code in plan["code"]:
        verify(code)
    identity_receipt = plan["control_identities"]
    identities = read(identity_receipt)["entries"]
    frozen = {e["id"]: e for e in identities}
    assert len(identities) == len(frozen) == 78
    conditions = {e["condition_id"]: e for e in plan["conditions"]}
    assert len(plan["conditions"]) == len(conditions) == 78 and set(conditions) == set(frozen)
    assert {e["new_slot"] for e in conditions.values()} == set(range(78))
    exact_targets = {}
    for cid, e in conditions.items():
        old = frozen[cid]
        for field in ("source_id", "target", "sequence", "target_sequence",
                      "sequence_sha256", "target_sequence_sha256"):
            compare(old[field], e[field], cid + ".frozen." + field)
        assert sha(e["sequence"]) == e["sequence_sha256"]
        assert sha(e["target_sequence"]) == e["target_sequence_sha256"]
        assert e["historical_binding_label"] == old["binary_binding_label"]
        item = exact_targets.setdefault(e["target_msa_key"], {
            "target": e["target"], "target_sequence_sha256": e["target_sequence_sha256"],
            "length": len(e["target_sequence"]), "identities": []})
        assert item["target_sequence_sha256"] == e["target_sequence_sha256"]
        item["identities"].append(cid)
    assert len(exact_targets) == 6 and len({r["target"] for r in exact_targets.values()}) == 5
    assert sorted(r["length"] for r in exact_targets.values() if r["target"] == "BBF-14") == [111, 112]
    assert len({e["sequence_sha256"] for e in conditions.values()}) == 78
    construct = read(plan["construct_preflight"])
    bbfseq = sorted({e["target_sequence"] for e in conditions.values() if e["target"] == "BBF-14"}, key=len)
    assert bbfseq[1] == "M" + bbfseq[0]
    assert construct["long_N_terminal_extra"] == "M" and construct["internal_difference"] is False
    release_p = STEP / "outputs/validation_release.json"
    release = json.loads(release_p.read_text())
    assert release["status"] == "V2_TECHNICAL_VALIDATION_RELEASED_AFTER_INITIAL_30_MODELS_NO_PROTOCOL_CHANGE"
    for f in ("inference_plan", "validation_plan", "validation_msa", "semantic_preflight"):
        verify(release[f])
    for item in release["source_snapshot"]:
        verify(item)
    compare(production["scoring"], plan["scoring"], "scoring contract")
    acceptance = read(production["acceptance"])
    assert acceptance["status"] == "ALL_1170_CONTROL_MODELS_VERIFIED"
    assert acceptance["model_count"] == 1170 and acceptance["errors"] == []
    compare(production["plan"], acceptance["plan"], "accepted plan")
    msa = read(acceptance["msa_acceptance"])
    compare(production["plan"], msa["plan"], "MSA plan")
    assert len(msa["targets"]) == 6 and set(msa["targets"]) == set(exact_targets)
    for key, t in msa["targets"].items():
        verify(t["input"])
        exact_targets[key]["msa_receipt"] = t["input"]
        exact_targets[key]["raw_sequence_count"] = t["raw_sequence_count"]
        exact_targets[key]["single_sequence"] = t["single_sequence"]
    msa_by_id = {e["condition_id"]: e for e in msa["conditions"]}
    assert len(msa_by_id) == 78 and set(msa_by_id) == set(conditions)
    production_entries = {e["id"]: e for e in production["entries"]}
    assert len(production_entries) == len(production["entries"]) == 78
    all_rows, entries, checks = [], [], []
    seen = set()
    for row in acceptance["accepted_conditions"]:
        e = row["condition"]
        cid = e["condition_id"]
        assert cid not in seen
        seen.add(cid)
        compare(conditions[cid], e, cid + ".accepted_condition")
        manifest = read(row["manifest"])
        compare(e, manifest["condition"], cid + ".manifest_condition")
        assert manifest["status"] == "PREDICTIONS_GENERATED_PENDING_CPU_ACCEPTANCE"
        for receipt in manifest["inputs"]:
            verify(receipt)
        cfg = read(row["config"])
        verify_config(cfg)
        compare(cfg, manifest["effective_config"], cid + ".recorded_effective_config")
        msa_check = verify_msa(msa_by_id[cid]["input"], row["actual_msa"],
                               row["msa_semantics"], e["target_sequence"], e["sequence"])
        ids = [(m["model"], m["seed"]) for m in row["models"]]
        assert len(ids) == 15 and set(ids) == EXPECTED_MODELS
        models = [score_one(m, e) for m in row["models"]]
        metrics = {key: reduction([model[key] for model in models]) for key in STAT_KEYS}
        result = {
            "id": cid, "source_id": e["source_id"], "target": e["target"],
            "historical_binding_label": e["historical_binding_label"],
            "target_sequence_sha256": e["target_sequence_sha256"],
            "sequence_sha256": e["sequence_sha256"],
            "model_count": len(models),
            "confidence_baseline_median": metrics["confidence_baseline"]["median"],
            "confidence_baseline_n_valid": metrics["confidence_baseline"]["n_valid"],
            "confidence_baseline_n_missing": metrics["confidence_baseline"]["n_missing"],
            "baseline_pass_count": sum(m["baseline_pass"] is True for m in models),
            "baseline_missing_count": sum(m["baseline_pass"] is None for m in models),
            "metrics": metrics, "models": models}
        compare(result, production_entries[cid], cid + ".all_scoring_fields")
        entries.append(result)
        all_rows.extend([{"id": cid, "target": e["target"], **model} for model in models])
        checks.append({"id": cid, "status": "ALL_FIELDS_AGREE",
                       "models": len(models), "msa": msa_check,
                       "confidence_n_valid": result["confidence_baseline_n_valid"],
                       "confidence_n_missing": result["confidence_baseline_n_missing"]})
        print("INDEPENDENTLY_VERIFIED", cid, len(models), flush=True)
    assert seen == set(conditions) and len(all_rows) == 1170
    model_file = read(production["model_scores"])
    assert model_file["status"] == "ALL_1170_TECHNICALLY_ACCEPTED_MODELS_SCORED"
    compare(production["acceptance"], model_file["acceptance"], "model-table acceptance")
    compare(all_rows, model_file["rows"], "all raw model table fields")
    counts = {
        "identities": len(entries), "models": len(all_rows),
        "complete_confidence_identities": sum(e["confidence_baseline_n_valid"] == 15 for e in entries),
        "missing_confidence_models": sum(e["confidence_baseline_n_missing"] for e in entries)}
    compare(counts, production["counts"], "global coverage")
    return {
        "status": "INDEPENDENTLY_VERIFIED_ALL_1170_CONTROL_MODELS_AND_ALL_SCORE_FIELDS",
        "job_id": os.environ.get("SLURM_JOB_ID"),
        "array_job_id": array,
        "source": record(Path(__file__)),
        "producer_summary": record(summary_p),
        "producer_acceptance": production["acceptance"],
        "producer_model_scores": production["model_scores"],
        "scientific_plan_v1": plan["previous_plan"],
        "validation_plan_v2": production["plan"],
        "validation_release": record(release_p),
        "construct_preflight": plan["construct_preflight"],
        "control_identities": identity_receipt,
        "verified_file_count": len(VERIFIED),
        "counts": counts, "exact_target_constructs": exact_targets,
        "sequence_identity_unit_count": 78, "target_names": 5,
        "exact_target_sequence_count": 6,
        "tests": test_result, "condition_checks": checks,
        "comparison": {"numeric_absolute_tolerance": 1e-10,
                       "numeric_relative_tolerance": 1e-10,
                       "bool_null_string_key_comparison": "exact",
                       "all_model_and_identity_score_fields": True},
        "implementation": "Independent fixed-column PDB parser; blocked NumPy atom distances; Python statistics reductions; independent A3M chain/order/insertion/deletion feature parser. No producer module imports.",
        "interpretation": "Technical agreement only. Binding qualification is separately frozen in step18. Missing interfaces/scores remain null; incomplete identities have null primary median. No blockade, affinity, calibrated probability or superiority claim."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["test", "audit", "preflight"])
    ap.add_argument("--array", default="11941")
    args = ap.parse_args()
    if args.mode == "test":
        print(json.dumps(tests(), indent=2))
        return
    run = OUT / ("run_" + os.environ.get("SLURM_JOB_ID", "manual"))
    run.mkdir(parents=True, exist_ok=False)
    try:
        if args.mode == "preflight":
            tests()
            plan = json.loads((STEP / "plan_v2.json").read_text())
            e = plan["conditions"][0]
            actual = STEP / "runs" / ("array_" + args.array) / "task_0/outputs/af2"
            mf = json.loads((actual.parents[1] / "manifest.json").read_text())
            verify_config(json.loads((actual / "config.json").read_text()))
            msa = json.loads((STEP / "inputs/msa_acceptance_v2.json").read_text())
            inp = msa["conditions"][0]["input"]
            src = verify(inp)
            before = a3m_features(src, e["target_sequence"], e["sequence"])
            after = a3m_features(actual / (e["condition_id"] + ".a3m"), e["target_sequence"], e["sequence"])
            compare(before, after, "preflight MSA")
            models = []
            for p in sorted(actual.glob("*_unrelaxed_rank_*.pdb")):
                match = re.search(r"_model_(\d+)_seed_(\d+)\.pdb$", p.name)
                model, seed = map(int, match.groups())
                sp = p.with_name(p.name.replace("_unrelaxed_", "_scores_").replace(".pdb", ".json"))
                lengths = [len(e["target_sequence"]), len(e["sequence"])]
                models.append(score_one({"model": model, "seed": seed,
                    "pdb": record(p), "scores": record(sp), "chain_lengths": lengths,
                    "pae_shape": [sum(lengths)] * 2}, e))
            assert len(models) == 15
            report = {"status": "INDEPENDENT_IMPLEMENTATION_PREFLIGHT_PASSED_15_MODELS",
                "tests": tests(), "models": 15, "condition_id": e["condition_id"],
                "feature_sha256": fingerprint(after), "source": record(Path(__file__)),
                "note": "Implementation preflight only; no production-score comparison until final release."}
        else:
            report = audit(args.array)
        write(run / "receipt.json", report)
        counts = report.get("counts", {})
        text = "# Controls 评分独立复核\n\n"
        text += "状态：" + report["status"] + "。\n\n"
        if counts:
            text += (f"独立逐文件核验 {counts['identities']} 个身份、{counts['models']} 个模型，"
                f"涵盖 6 个精确 target 构建（5 个 target 名称）。"
                f"可计算完整 15 模型主中位数的身份为 {counts['complete_confidence_identities']}；"
                f"缺失 confidence 的模型为 {counts['missing_confidence_models']}。\n\n")
            text += ("重新解析全部 PDB 与 raw score，独立重算 5 Å 重原子唯一残基接触对、"
                "双向 PAE、各 pLDDT、global ipTM 和冻结 baseline；逐字段核对模型、身份及全局汇总。"
                "数值容差 1e-10；布尔、空值、字符串和字段集合精确一致。\n\n"
                "A3M 查询/链顺序、paired/unpaired 行顺序、插入 deletion matrix、"
                "实际有效配置及输入/输出 SHA-256 均核验。BBF-14 的 111 aa 与 112 aa 构建保持分开。"
                "v2 属验证方法修正且晚于最早 30 模型，此时序以 validation_release.json 为准。\n\n"
                "零界面记为 null；零 PAE 不限制分数；每身份必须 15 个有效模型才能给主中位数。"
                "这是工程及计算一致性验收，实验 eligibility、结合或阻断证据另行判定。\n")
        else:
            text += "本次仅为实现预检；完整独立审阅尚须等待生产评分。\n"
        (run / "REPORT.md").write_text(text)
        write(run / "manifest.json", {"receipt": record(run / "receipt.json"),
            "report": record(run / "REPORT.md"), "source": record(Path(__file__))})
        if args.mode == "audit":
            write(OUT / "acceptance.json", {"status": report["status"],
                "receipt": record(run / "receipt.json"),
                "report": record(run / "REPORT.md"), "manifest": record(run / "manifest.json")})
        print(json.dumps({"status": report["status"], "receipt": record(run / "receipt.json"),
                          "counts": counts}, indent=2))
    except Exception as exc:
        write(run / "failure.json", {"status": "INDEPENDENT_REVIEW_FAILED",
            "error": repr(exc), "traceback": traceback.format_exc(),
            "source": record(Path(__file__))})
        raise


if __name__ == "__main__":
    main()

