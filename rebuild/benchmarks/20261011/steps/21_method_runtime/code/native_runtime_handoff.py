#!/usr/bin/env python3
"""CPU-only native runtime handoff; does not promote any formal scientific result."""
import hashlib,json,os,random,subprocess
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
job=os.environ["SLURM_JOB_ID"]
out=S/"runs"/("native_runtime_handoff_"+job)/"outputs";out.mkdir(parents=True,exist_ok=False)
def rec(path):
 p=Path(path);return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def check(x):
 actual=rec(x["path"]);assert actual==x,(actual,x);return Path(x["path"])
def write(name,value):
 p=out/name;p.write_text(json.dumps(value,indent=2)+"\n");return rec(p)
scheduler=subprocess.check_output(["scontrol","show","job",job,"-o"],text=True)
assert "JobState=RUNNING" in scheduler and not any(t.startswith("gres/gpu=") and int(t.split("=")[1])>0 for t in scheduler.split("TRES=",1)[1].split()[0].split(","))
assert not os.environ.get("CUDA_VISIBLE_DEVICES")
rf_receipt={"path":str(S/"runs/actual_native_v8_13213/outputs/rf/acceptance.json"),"bytes":47799,"sha256":"615c2d52aba64c3fae9f82bb56944823ecb94cefe73004c3d5972f8ad0b74e97"}
bc_receipt={"path":str(S/"runs/supplemental_actual_current_13247/outputs/acceptance.json"),"bytes":7942,"sha256":"c5bccf4f4a12ac9cc0e37521fbde24a67a5207610de4e66e4b18dafe6d20d6e4"}
rf=json.loads(check(rf_receipt).read_text());bc=json.loads(check(bc_receipt).read_text())
required={"rf_diffusion":["rf_diffusion_backbone","original_proteinmpnn","native_af2_ptm1"],"bindcraft":["native_bindcraft_trajectory","soluble_proteinmpnn","native_af2_ptm1_and_2","native_filters"]}
checks=[]
for method,data,receipt in [("rf_diffusion",rf,rf_receipt),("bindcraft",bc,bc_receipt)]:
 assert data["method_id"]==method and data["status"]=="NATIVE_GPU_METHOD_WORKFLOW_CONTENT_ACCEPTED_ENGINEERING_ONLY" and data["actual_assigned_gpu_count"]==1 and data["scientific_scope"]=="ENGINEERING_ONLY"
 assert set(data["native_stage_status"])==set(required[method]) and all(v=="PASS" for v in data["native_stage_status"].values())
 assert set(data["stage_evidence"])==set(required[method])
 for key in ["plan","runtime_source","orchestrator_source","config_receipt","target_manifest","run_receipt"]:check(data[key])
 for key,x in data["stage_evidence"].items():check(x)
 checks.append({"method_id":method,"acceptance":receipt,"native_stage_status":data["native_stage_status"],"coverage_mode":data.get("coverage_mode","native_main_workflow"),"verified_direct_gate_receipts":6+len(required[method])})
assert rf["plan"]==bc["plan"] and rf["runtime_source"]==bc["runtime_source"] and rf["orchestrator_source"]==bc["orchestrator_source"] and rf["target_manifest"]==bc["target_manifest"]
assert bc["main_workflow_full_native_chain_completed"] is False and bc["main_workflow_sequence_count"]==0 and bc["supplemental_sequence_count"]==20 and bc["supplemental_formal_eligible_sequences"]==0
assert bc["coverage_mode"]=="main_rejected_trajectory_plus_separate_supplemental_stage_coverage"
rng=json.loads(check(bc["supplemental_deterministic_rng"]).read_text());events=json.loads(json.dumps(rng))
original_event_lines=[json.loads(x) for x in check(rng["events"]).read_text().splitlines()]
root_seed=rng["root_seed"];assert root_seed==791205
np_stream=np.random.default_rng(root_seed)
numpy_rows=[]
for actual in rng["numpy_entropy_events"]:
 expected=int(np_stream.integers(0,2**31-1))
 assert expected==actual["seed"],(expected,actual)
 numpy_rows.append({"actual":actual["seed"],"independently_replayed":expected})
python_stream=random.Random(root_seed);python_rows=[]
for actual in rng["actual_python_randint_returns"]:
 expected=python_stream.randint(actual["lower"],actual["upper"])
 assert expected==actual["value"]
 python_rows.append({"actual":actual["value"],"independently_replayed":expected,"lower":actual["lower"],"upper":actual["upper"]})
assert len(rng["actual_mpnn_constructor"])==1 and rng["actual_mpnn_constructor"][0]["seed"]==python_rows[0]["actual"]==1781849165
assert numpy_rows[0]["actual"]==1925930840 and numpy_rows[0]["actual"]!=python_rows[0]["actual"]
seed_event=next(x for x in original_event_lines if x["stage"]=="python_rng_seeded_before_official_constructors")
assert seed_event["completed_at_epoch"]<rng["actual_python_randint_returns"][0]["completed_at_epoch"]<rng["actual_mpnn_constructor"][0]["completed_at_epoch"]
for x in rng["official_python_key_sources"]:check(x)
rng_proof=write("independent_numpy_python_rng_replay.json",{"status":"CURRENT_ACTUAL_SUPPLEMENTAL_NUMPY_PCG64_AND_PYTHON_MT19937_STREAMS_INDEPENDENTLY_REPLAYED_CPU_ONLY","root_seed":root_seed,"python_stream":python_rows,"numpy_default_rng_bit_generator":type(np_stream.bit_generator).__name__,"numpy_entropy_stream":numpy_rows,"source_receipt":bc["supplemental_source"],"events":rng["events"],"actual_mpnn_constructor":rng["actual_mpnn_constructor"],"interpretation":"Two different recorded RNG streams; reproduces their original draws without touching any GPU/model state","additional_model_draws":0,"cpu_job":job,"numpy_version":np.__version__})
history_path=S/"runs/supplemental_actual_current_13247/outputs/old_supplemental_rng_history_disposition.json"
history=json.loads(history_path.read_text());check(history["historical_cpu_content_audit"]);check(history["historical_source"]);check(history["rng_limitation_proof"]);check(history["current_actual_acceptance"])
base_path=S/"runs/actual_bc_v8_identity_13220/outputs/acceptance.json"
base=json.loads(base_path.read_text());assert base["status"]=="NATIVE_GPU_METHOD_WORKFLOW_STAGE_COVERAGE_INCOMPLETE_ENGINEERING_ONLY"
for x in [bc["supplemental_source"],bc["supplemental_config"],bc["supplemental_cost"],bc["supplemental_audit"],bc["supplemental_launcher_receipt"],bc["collector_source"]]:check(x)
cost=json.loads(Path(bc["supplemental_cost"]["path"]).read_text());accounting_line=next(x for x in cost["sacct"].splitlines() if x.startswith("13246|"))
assert "|COMPLETED|" in accounting_line and "|359|" in accounting_line and "cpu=2,gres/gpu=1" in accounting_line
check(cost["actual_allocation"]);check(cost["actual_worker"]);check(cost["launcher_budget"])
confidence=S/"runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py"
confidence_rec=rec(confidence);assert confidence_rec["bytes"]==16372 and confidence_rec["sha256"]=="eca561182d06eca52bde005b45f02dd261d57b916d70ea5e34e99e86a79830b5"
envs=[rec(R/"steps/22_matched_benchmark/settings/pilot_v8/source/rfd_env.sh"),rec(R/"steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh")]
report=out/"NATIVE_RUNTIME_ENGINEERING_HANDOFF.md"
report.write_text("""# Native method runtime and engineering handoff

Both native computational methods have actual GPU technical stage evidence with exact source/config/query/structure/confidence receipts. This is an engineering handoff, not a scientific benchmark result or experimental PPI-blockade validation.

| Method | Actual main engineering run | Covered native stages | Explicit limit |
|---|---|---|---|
| RFdiffusion + original ProteinMPNN | 13175_0 / raw job 13181, 202 GPU-seconds | 1 actual backbone; 8 original MPNN sequences; 8 native AF2 PTM1 predictions; raw PAE/pLDDT/PDB/query/model/seed/filter and incremental-ledger closure | Engineering input only; no claim of superior blocker quality |
| BindCraft | 13175_1, 389 GPU-seconds; actual official trajectory scientific rejection | Actual default trajectory and rejection; downstream official soluble MPNN20, PTM1/2, binder-only PTM1/2 and default-filter APIs additionally covered by separately billed deterministic supplemental job13246 (359 GPU-seconds) | Main trajectory did not run downstream MPNN/AF2; supplemental sequences are excluded from every formal pool/ranking |

The current method acceptances are RF CPU13213 and BC CPU13247. The BC coverage mode is explicitly main_rejected_trajectory_plus_separate_supplemental_stage_coverage. Both supplemental PTM models were actually rejected by unchanged native basic filters; this is a successful API/feature/confidence audit, not a native scientific positive. The fixed supplemental literal PDB carries C12 while the original hard-sequence event carries M12, matching official soft-aatype PDB versus hard-sequence export semantics. Both identities and source evidence remain archived.

The earlier supplemental13234 produced real API content at 381 GPU-seconds but omitted Python RNG initialization for official Key(None). It remains ENGINEERING_HISTORY_ONLY, with original bytes and cost retained. Corrected13246 seeded Python before constructors and preserved actual original random.randint returns and MPNN Key seed. Independent CPU replay confirms Python seed791205 -> actual MPNN key1781849165, and a separate NumPy PCG64 seed791205 -> entropy fallback1925930840. No seed search, output-based pose selection, filter relaxation, extra native prediction, or formal-eligible supplement is introduced.

The frozen production runtime remains pilot_v8, with pinned private environments, original scientific parameters, persistent task sessions, strict scheduler-owned GPU UUID masking, and hard whole-process-group budget cutoff. All generation, internal prediction, observation/fsync overhead, startup and failed scientific trajectories count toward their task deadline. Completed MPNN FASTA writes are emitted incrementally; native screening updates are a separate ledger.

RF native AF2 uses model_1_ptm, single MSA, 3 recycles, target-only templates and full designed-complex initial guess; literal query/chain/CB/template arrays were CPU intercepted on the actual eight sequences. Fixed paper-aligned criteria are binder pLDDT >=0.8, mean both cross-PAE blocks <=10 Angstrom, target-aligned binder CA RMSD <=1 Angstrom, ranked by lower native cross PAE. BindCraft retains its official soluble20/default settings and native PTM1/2/default filters; its native rounded-average ipTM ranking is method-specific. Native acceptance rates are not a shared scientific comparison endpoint.

For every formal attempt, run the immutable CPU confidence collector:
python <collector> --attempt-dir <absolute_attempt> --target-manifest <absolute_manifest> --config <immutable_method_config> --config-sha256 <config_SHA> --runtime-source <immutable_pilot_v8_source> --output-dir <new_CPU_output>
The collector receipt and exact paths are in manifest.json. It audits all raw/native updates, including rejected/NA/partial evidence; the independent budget/formal contract supplies cutoff eligibility and independent full-array ranking verification.

The remaining parent-owned work is independent supplemental allocation/resource/RNG accounting acceptance, the combined engineering gate, and the frozen matched-budget scientific benchmark with common blinded re-review and final benchmark report. No formal scientific task has been submitted by this runtime subagent. No new managed credential or shared-environment installation is required.
""")
manifest=write("manifest.json",{"schema":"native-runtime-engineering-handoff.v1","status":"NATIVE_RUNTIME_AND_ACTUAL_GPU_METHOD_CONTENT_ACCEPTED_ENGINEERING_ONLY_PARENT_INDEPENDENT_ACCOUNTING_REQUIRED","scientific_scope":"ENGINEERING_ONLY","runtime_source":rf["runtime_source"],"orchestrator_source":rf["orchestrator_source"],"engineering_plan":rf["plan"],"target_manifest":rf["target_manifest"],"environments":envs,"method_acceptances":checks,"confidence_collector":confidence_rec,"independent_actual_rng_replay":rng_proof,"superseded_supplemental_history":rec(history_path),"report":rec(report),"scope_limits":{"formal_benchmark_results":False,"experimental_blockade":False,"superiority_claim":False,"supplemental_formal_eligible_sequences":0},"known_separately_costed_gpu_seconds":{"main_rf":202,"main_bindcraft":389,"old_supplemental_history":381,"corrected_supplemental":359},"prior_failed_engineering_cost":"Retained in parent independent accounting; not estimated by this handoff","collector_source":rec(Path(__file__).resolve()),"cpu_job":job,"scheduler_record":scheduler})
acceptance=write("acceptance.json",{"status":"NATIVE_RUNTIME_ENGINEERING_HANDOFF_CONTENT_AND_SEPARATE_RNG_REPLAY_CPU_PASS","manifest":manifest,"report":rec(report),"independent_actual_rng_replay":rng_proof,"method_acceptances":[rf_receipt,bc_receipt],"formal_ready_claim":False,"parent_independent_accounting_required":True,"cpu_job":job})
authority={"schema":"private_native_runtime_authority.v1","scope":"Actual GPU native engineering content accepted; formal scientific and independent accounting gate remains parent-owned","acceptance":acceptance,"runtime_source":rf["runtime_source"],"confidence_collector":confidence_rec}
ptr=S/"NATIVE_RUNTIME_CURRENT.json";assert not ptr.exists();ptr.write_text(json.dumps(authority,indent=2)+"\n")
for p in out.iterdir():
 if p.is_file():p.chmod(0o444)
out.chmod(0o555)
print(json.dumps({"status":"PASS","acceptance":acceptance,"manifest":manifest,"report":rec(report),"authority":rec(ptr)},indent=2))

