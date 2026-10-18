"""A fixed upstream mirror of the existing evaluation interchain heavy-atom gate."""
from __future__ import annotations
import math
from .common import EvidenceError

POLICY = {
    "schema": "native_pose_physical_gate.v1",
    "atom_definition": "protein heavy atoms only, excluding H and D, from read_structure",
    "distance_scope": "minimum Euclidean distance between target A and native partner B",
    "reject_if_minimum_distance_less_than_angstrom": 1.5,
    "boundary": "strictly less than; exactly 1.5 Angstrom is not rejected by this gate",
    "derivation": "same fixed 1.5 Angstrom criterion already used by pipeline.evaluate",
    "not_a_clash_fraction_threshold": True,
    "does_not_establish_or_disprove_biological_interaction": True,
}

def physical_pose_reasons(contacts):
    value = contacts.get("minimum_distance")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise EvidenceError("INVALID_INTERFACE_DISTANCE", "Finite nonnegative interchain heavy-atom minimum distance is required")
    return ["SEVERE_TARGET_PARTNER_CLASH"] if value < 1.5 else []

def physical_pose_record(contacts):
    reasons = physical_pose_reasons(contacts)
    return {"policy": POLICY, "minimum_distance_angstrom": contacts["minimum_distance"],
            "status": "PHYSICAL_REJECT" if reasons else "PHYSICAL_GATE_PASS",
            "reasons": reasons}
