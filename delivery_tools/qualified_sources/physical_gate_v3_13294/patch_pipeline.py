"""Exact, fail-closed patch for a separate snapshot; never edits the active repository."""
from pathlib import Path

def patch(source):
    anchor="from .backends import boltz_predict, confidence_metrics, confidence_reasons, rfd_mpnn\n"
    if source.count(anchor)!=1:raise RuntimeError("Unexpected pipeline import source")
    source = source.replace(anchor,
        "from .backends import boltz_predict, confidence_metrics, confidence_reasons, rfd_mpnn\n"
        "from .pose_physical_gate import POLICY, physical_pose_reasons, physical_pose_record\n", 1)
    old = '''                reasons=confidence_reasons(metrics,config.get("gates",{}))
                rows.append({"model":i,"metrics":metrics,"reasons":reasons,"interface":pair["interface"]})
'''
    new = '''                confidence_gate_reasons=confidence_reasons(metrics,config.get("gates",{}))
                physical_gate=physical_pose_record(pair["interface"])
                reasons=confidence_gate_reasons+physical_gate["reasons"]
                rows.append({"model":i,"metrics":metrics,"reasons":reasons,"interface":pair["interface"],
                             "confidence_gate_reasons":confidence_gate_reasons,"physical_gate":physical_gate})
'''
    if source.count(old) != 1: raise RuntimeError("Unexpected native prediction gate source")
    source = source.replace(old, new)
    old = 'put(run,"ensemble",{"models":rows,"convergent_model_indices":support,"iptm_is_probability":False})'
    new = '''put(run,"ensemble",{"models":rows,"convergent_model_indices":support,"iptm_is_probability":False,
                            "pose_physical_policy":POLICY,
                            "eligible_model_indices":[x[0] for x in passing],
                            "selection_rule":"unchanged maximum compatible neighborhood after target alignment; first representative wins ties",
                            "minimum_support":max(2,int(np.ceil(len(models)*.6))),
                            "support_denominator":"all requested models, including physical rejects",
                            "alternate_compatible_neighborhoods_are_not_complete_linkage_clusters":True})'''
    if source.count(old) != 1: raise RuntimeError("Unexpected ensemble write source")
    source = source.replace(old, new)
    old = '''                        "observed_target_sequence":a["sequence"],"observed_partner_sequence":b["sequence"]})
        return run.finish("POSE_ACCEPTED","computational_interaction_hypothesis")'''
    new = '''                        "observed_target_sequence":a["sequence"],"observed_partner_sequence":b["sequence"],
                        "physical_gate":physical_pose_record(pair["interface"]),
                        "ensemble_support_model_indices":support})
        return run.finish("POSE_ACCEPTED","computational_interaction_hypothesis")'''
    if source.count(old) != 1: raise RuntimeError("Unexpected accepted prediction pose source")
    source = source.replace(old, new)
    old = '''    return config,pose,native

def design(root,upstream):'''
    new = '''    require([c["id"] for c in chains]==["A","B"] and not context,
            "NATIVE_POSE_CHAIN_OR_CONTEXT_INVALID","Native coordinates must contain only normalized target A and partner B")
    actual_interface=interface(chains[0],chains[1],config.get("gates",{}).get("contact_cutoff",5))
    physical_gate=physical_pose_record(actual_interface)
    require(not physical_gate["reasons"],"SEVERE_NATIVE_POSE_CLASH",
            "Actual native target/partner coordinates fail the existing <1.5 Angstrom heavy-atom criterion")
    pose={**pose,"design_entry_physical_gate":physical_gate}
    return config,pose,native

def design(root,upstream):'''
    if source.count(old) != 1: raise RuntimeError("Unexpected design contract source")
    return source.replace(old, new)
