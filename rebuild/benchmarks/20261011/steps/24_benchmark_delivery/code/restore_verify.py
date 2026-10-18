#!/usr/bin/env python3
"""Independent restore acceptance; only restored raw evidence is recomputed."""
import argparse,hashlib,json,os
from pathlib import Path
from delivery_core import cpu,rec,dump,read,verify
from restore_resolver import path_factory,audit_budget
from common_review_independent import audit_common
from target_statistics import target_statistics,POLICY
def run(package_path,restore_root,out):
    allocation=cpu();pkg=read(package_path);root=Path(restore_root);P=path_factory(pkg["authority_root"],root)
    hashes=read(root/"RESTORE_HASH_ACCEPTANCE.json")
    if hashes["status"]!="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING":
        raise ValueError("Hash-verified extraction required")
    if hashes["package"]!=rec(package_path):raise ValueError("Restore package receipt differs")
    config_path=P(pkg["config"]["path"]).physical()
    if rec(config_path)["sha256"]!=pkg["config"]["sha256"]:raise ValueError("Restored config bytes differ")
    config=read(config_path);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    if not out.is_relative_to(root):raise ValueError("Recomputed outputs must be inside restored tree")
    c=config["recomputation"]
    if c["statistics"]["aggregation_policy"]!=POLICY:raise ValueError("Predeclared aggregation differs")
    budget=audit_budget(c["generation"],pkg["authority_root"],root)
    dump(out/"budget_acceptance.json",budget)
    common=audit_common(c["common"],pkg["authority_root"],root,out/"common")
    plan=read(P(c["generation"]["plan"]).physical())
    stats=target_statistics(common,plan["protocol"],c["statistics"]["rf_method_id"],c["statistics"]["bindcraft_method_id"])
    dump(out/"target_statistics.json",stats)
    # Read the original report's machine summary from restored bytes and compare.
    from common_review_independent import compare
    expected=read(P(c["statistics"]["producer_summary"]).physical())
    compare(stats,expected,"frozen_target_statistics")
    acceptance={"schema":"benchmark-independent-restore.v1",
      "status":"INDEPENDENT_RESTORE_RAW_CONTENT_RECOMPUTATION_ACCEPTED",
      "phase_id":pkg["phase_id"],"allocation":allocation,"package":rec(package_path),
      "restore_root":str(root),"hash_acceptance":rec(root/"RESTORE_HASH_ACCEPTANCE.json"),
      "recomputed_budget":rec(out/"budget_acceptance.json"),"recomputed_common":rec(out/"common/acceptance.json"),
      "recomputed_statistics":rec(out/"target_statistics.json"),
      "source_receipts_resolved":"ORIGINAL_LOGICAL_PATHS_TO_RESTORED_BYTES",
      "frozen_plan_bytes_changed":False,"original_scientific_evidence_read":False,
      "same_lustre_filesystem":True,"offsite_backup":False,"offline_gpu_runtime_image":False,
      "conditional_inference_dependencies":pkg["conditional_inference_dependencies"],
      "scientific_scope":"COMPUTATIONAL_ONLY",
      "remaining_evidence_requirements":["experimental binding","functional PPI blockade","generalization beyond tested target matrix"]}
    dump(out/"acceptance.json",acceptance);return acceptance
def main():
    p=argparse.ArgumentParser()
    for key in ("package","restore-root","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args();print(run(a.package,a.restore_root,a.out)["status"])
if __name__=="__main__":main()

