#!/usr/bin/env python3
"""Publish one accepted evidence phase after complete independent restore."""
import argparse,datetime,json,os,re,subprocess,tempfile
from pathlib import Path
from evidence_delivery import record,verify_record,slurm,read,validate_plan

BASE_HASH="70c12ec40a5474d8876fd6da020709106169d0e2fcba39af6f7b1fc8f928a939"
def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=path.name+".",suffix=".partial",dir=path.parent)
    try:
        with os.fdopen(fd,"w") as f:
            json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n");f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if Path(name).exists():Path(name).unlink()
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--delivery-acceptance",required=True);a=p.parse_args()
    job=slurm();root=Path(a.root).absolute()
    delivery_path=Path(a.delivery_acceptance);delivery=read(delivery_path)
    assert delivery["status"]=="EVIDENCE_DELIVERY_INDEPENDENTLY_RESTORED_AND_VERIFIED"
    assert delivery["source_tests"]["status"]=="PASSED"
    verify_record(delivery["source_tests"]["log"],root)
    coretest=re.search(r"(\d+) passed",Path(delivery["source_tests"]["log"]["path"]).read_text())
    assert coretest and int(coretest.group(1))>=131
    package=read(verify_record(delivery["packaging_receipt"],root))
    for part in package["parts"]:verify_record(part["archive"],root)
    verify_record(package["source_bundle"],root)
    plan=read(verify_record(package["plan"],root));assert plan["source_commit"]==delivery["source_commit"]
    assert package["status"]=="PACKAGED_AWAITING_INDEPENDENT_RESTORE"
    assert package["source_commit"]==delivery["source_commit"]
    assert delivery["restored_files"]==plan["packed_file_count"]
    assert delivery["restored_source_files"]==len(plan["source_files"])
    validate_plan(plan)
    source=root/"source";head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=source,text=True).strip()
    assert head==delivery["source_commit"]
    assert not subprocess.check_output(["git","status","--porcelain"],cwd=source,text=True).strip()
    gates={v["role"]:v for v in plan["terminal_gates"]}
    required={"qualification_rfd60","qualification_rfd60_independent","qualification_bindcraft18",
      "qualification_bindcraft18_independent","specificity_review","evidence_axes","evidence_axes_independent",
      "controls_technical","controls_scoring","calibration"}
    assert required.issubset(gates)
    for value in gates.values():verify_record(value["file"],root)
    base=root/"00_admin/reconstruction_20261002.json";base_rec=record(base);assert base_rec["sha256"]==BASE_HASH
    report=root/plan["config"]["report"];report_rec=record(report)
    report_rows=[r for r in plan["artifact_closure"]["files"] if r["path"]==str(report)]
    assert len(report_rows)==1 and report_rows[0]["sha256"]==report_rec["sha256"]
    report_text=report.read_text()
    assert "DRAFT_WAITING" not in report_text and "[待写入" not in report_text
    phase_path=root/"00_admin/evidence_repair_20261004.json"
    active_path=root/"00_admin/ACTIVE.json"
    output=root/"00_admin/evidence_repair_publication_20261004.json"
    old_active=read(active_path) if active_path.exists() else None
    if old_active is not None: assert old_active.get("project_id")=="test9"
    if output.exists():
        published=read(output)
        assert published["status"]=="EVIDENCE_REPAIR_PUBLICATION_VERIFIED"
        assert published["delivery"]==record(delivery_path) and published["report"]==report_rec
        for key in ("active_registry","phase_registry","delivery","report"):verify_record(published[key],root)
        assert read(published["phase_registry"]["path"])["source_commit"]==head
        print(json.dumps(dict(publication=record(output),status=published["status"],idempotent_reuse=True),indent=2))
        return
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    phase=dict(project_id="test9",phase_id="PPI-EVIDENCE-REPAIR-20261004",version="2.0.1",
      status="EVIDENCE_REPAIR_AND_QUALIFIED_CALIBRATION_ACCEPTED_COMPUTATIONAL_ONLY",
      published_utc=now,publication_job=job,authority="u21111210118@192.168.81.6:22560:"+str(root),
      source_commit=head,reconstruction_parent=base_rec,report=report_rec,
      modules={k:v["file"] for k,v in gates.items()},terminal_gate_assertions=plan["terminal_gates"],
      delivery=record(delivery_path),source_core_tests=int(coretest.group(1)),
      bounds=dict(experimental_binding_or_blockade_of_candidates="NOT_VALIDATED",
        general_blockade_benchmark_labels=0,workflow_superiority="NOT_ESTABLISHED",
        old_design_backbones="NOT_RECOVERED",old_MD="NOT_RECOVERED",new_MD="NOT_PERFORMED",
        backup_scope="SAME_FILESYSTEM_VERIFIED_RESTORE_NOT_OFFSITE",
        interpretation="Author-conditioned binding screens and computational diagnostics; not prospective efficacy"),
      script=record(__file__))
    if phase_path.exists():
        previous=read(phase_path)
        for key in ("project_id","phase_id","version","status","source_commit","reconstruction_parent","report","modules","delivery","script"):
            assert previous[key]==phase[key], "Existing phase conflicts: "+key
        phase=previous;now=phase["published_utc"]
    else:atomic(phase_path,phase)
    phase_rec=record(phase_path)
    if old_active is not None and old_active.get("current_phase")!=phase_rec:
        archive=root/"00_admin/history"/("ACTIVE_before_evidence_repair_"+job+".json")
        archive.parent.mkdir(parents=True,exist_ok=True)
        if archive.exists():assert read(archive)==old_active
        else:atomic(archive,old_active)
    active=dict(project_id="test9",updated_utc=now,authority=phase["authority"],
      phase_id=phase["phase_id"],current_phase=phase_rec,reconstruction=base_rec,
      status=phase["status"],human_report=report_rec)
    atomic(active_path,active)
    receipt=dict(status="EVIDENCE_REPAIR_PUBLICATION_VERIFIED",job_id=job,created_utc=now,
      active_registry=record(active_path),phase_registry=phase_rec,delivery=record(delivery_path),report=report_rec,
      old_reconstruction_registry_unchanged=record(base)==base_rec)
    assert read(active_path)["current_phase"]==phase_rec and receipt["old_reconstruction_registry_unchanged"]
    atomic(output,receipt)
    print(json.dumps(dict(publication=record(output),source_commit=head,status=receipt["status"]),indent=2))
if __name__=="__main__":main()

