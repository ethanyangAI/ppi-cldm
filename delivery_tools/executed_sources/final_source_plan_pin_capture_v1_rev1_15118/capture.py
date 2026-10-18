#!/usr/bin/env python3
"""Two finite operational pin routes. No source audit, child receipt IO or science."""
import argparse, hashlib, importlib.util, json, math, os, re, stat, subprocess, sys
from pathlib import Path, PurePosixPath

R = Path("/lustre/users/u21111210118/projects/test9")
S = R / "steps/24_benchmark_delivery"
P = S / "pending/final_source_plan_pin_capture_v1_rev1"
HISTORICAL_P = S / "pending/final_source_plan_pin_capture_v1"
HISTORICAL_BYTES = (218736, 1125, 18406)
D = Path(__file__).absolute().parent
FILES = ("capture.py", "capture_cpu.sbatch", "HANDOFF.md")
REQUEST = S / "submissions/final_source_pin_capture_from14925_v1/request.json"
PLAN = S / "pending/final_source_plan_from14706_14925_v1/final_source_plan.json"
JOB_NAME = "test9_final_source_plan_pin_capture_v1_rev1"
CORE = R / "env/core/bin/python"
CORE_REAL = R / "env/core/bin/python3.11"
CORE_BYTES = 25916456
CORE_SHA = "76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"
OPAQUE_INVENTORY = S / "handoffs/FINAL_SOURCE_PIN_READINESS_INVENTORY_14925_20261014_OPAQUE.txt"
ORIGINAL_INVENTORY = S / "handoffs/FINAL_SOURCE_PIN_READINESS_INVENTORY_14925_20261014.json"
CAPTURE_STATUS = "ACTUAL_FINITE_SOURCE_DOC_CONTROL_PINS_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE"
PLAN_STATUS = "ACTUAL_NEW_FINAL_SOURCE_PLAN_DESCRIPTOR_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE"
# Finite authority table from Root-authorized REV5. Never loaded from inventory at runtime.
FIXED_TARGETS = (
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012.md', 'DOC', 26185),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_1.md', 'DOC', 1840),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_10.md', 'DOC', 29220),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_2.md', 'DOC', 5239),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_3.md', 'DOC', 4611),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_4.md', 'DOC', 3095),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_5.md', 'DOC', 4611),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_6.md', 'DOC', 20258),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_7.md', 'DOC', 22778),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_8.md', 'DOC', 18275),
    ('/lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012_ERRATUM_9.md', 'DOC', 17386),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/COMMON13423_ROOT_RECEIPT_COST_INTERFACE_READINESS_STATIC_20261012.md', 'DOC', 18897),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/CONTINUATION_HISTORY_THROUGH_20261014T0845Z_605812B.md', 'DOC', 605812),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/FINAL_NINE_ROLE_LATE_SOURCE_COVERAGE_READINESS_20261012T151400Z.md', 'DOC', 4743),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/FINAL_NINE_ROLE_LATE_SOURCE_COVERAGE_READINESS_20261012T151400Z_REV1.md', 'DOC', 5156),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/FINAL_SOURCE_PIN_READINESS_INVENTORY_14925_20261014.json', 'CONTROL_METADATA', 1678331),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/FINAL_SOURCE_PIN_READINESS_INVENTORY_14925_20261014_OPAQUE.txt', 'DOC', 1678331),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_10_PROPOSED_ACTUAL_COST14576_COMMON_DRIVER14689_ROOT29814692_20261014.md', 'DOC', 27030),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_10_PROPOSED_ACTUAL_COST14576_COMMON_DRIVER14689_ROOT29814692_20261014_REV1.md', 'DOC', 28828),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_10_PROPOSED_ACTUAL_COST14576_COMMON_DRIVER14689_ROOT29814692_20261014_REV2.md', 'DOC', 29086),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_6_PROPOSED_FIX2_13377_20261012.md', 'DOC', 19960),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_7_FINAL_PROPOSED_DEFAULT13420_CAPTURE13433_20261012.md', 'DOC', 19922),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_7_FINAL_PROPOSED_DEFAULT13420_CAPTURE13433_20261012_rev1.md', 'DOC', 22462),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_7_PROPOSED_SCHEDULER13412_APPLY13420_20261012.md', 'DOC', 12969),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_8_PROPOSED_COMMON13460_JOURNAL0006_20261012.md', 'DOC', 17874),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_8_PROPOSED_COMMON13460_JOURNAL0006_20261012_rev1.md', 'DOC', 18032),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/OPERATOR_ERRATUM_9_PROPOSED_RESTORED_COMMON13460_VERIFIER13558_20261012.md', 'DOC', 17070),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/SCIENTIFIC_CAPABILITY_LITERATURE_AUDIT_REPORT14901_QA14925_20261014.md', 'DOC', 5774),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/default_workflow_materialized_integration_v3/HANDOFF.md', 'DOC', 3781),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/default_workflow_materialized_integration_v3/default_integration_cpu_v3.sbatch', 'SOURCE', 1970),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/default_workflow_materialized_integration_v3/integrate_default_workflow_v3.py', 'SOURCE', 50123),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/default_workflow_materialized_integration_v3/test_integrate_default_workflow_v3.py', 'SOURCE', 26928),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/HANDOFF.md', 'DOC', 4375),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/composer_bootstrap.py', 'SOURCE', 3648),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/composer_context_api.py', 'SOURCE', 2368),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/composer_contracts_cpu.sbatch', 'SOURCE', 1000),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/composer_cpu.sbatch', 'SOURCE', 941),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/final_delivery_composer.py', 'SOURCE', 43694),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/relative_archive_restore.py', 'SOURCE', 13146),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4/test_final_delivery_composer.py', 'SOURCE', 42747),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/HANDOFF.md', 'DOC', 6527),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/composer_bootstrap.py', 'SOURCE', 3660),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/composer_context_api.py', 'SOURCE', 2368),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/composer_contracts_cpu.sbatch', 'SOURCE', 1036),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/composer_cpu.sbatch', 'SOURCE', 965),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/final_delivery_composer.py', 'SOURCE', 43694),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/relative_archive_restore.py', 'SOURCE', 13146),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix1/test_final_delivery_composer.py', 'SOURCE', 44221),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/HANDOFF.md', 'DOC', 7006),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/composer_bootstrap.py', 'SOURCE', 3660),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/composer_context_api.py', 'SOURCE', 2368),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/composer_contracts_cpu.sbatch', 'SOURCE', 1036),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/composer_cpu.sbatch', 'SOURCE', 965),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/final_delivery_composer.py', 'SOURCE', 43694),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/relative_archive_restore.py', 'SOURCE', 13146),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v4_fixturefix2/test_final_delivery_composer.py', 'SOURCE', 45040),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/HANDOFF.md', 'DOC', 13917),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/composer_bootstrap.py', 'SOURCE', 4329),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/composer_context_api.py', 'SOURCE', 2368),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/composer_contracts_cpu.sbatch', 'SOURCE', 1048),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/composer_cpu.sbatch', 'SOURCE', 974),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/final_delivery_composer.py', 'SOURCE', 47023),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/github_export_context.py', 'SOURCE', 42073),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/relative_archive_restore.py', 'SOURCE', 14621),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/test_final_delivery_composer.py', 'SOURCE', 45040),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v5_exportcontext1/test_github_export_context.py', 'SOURCE', 27419),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/HANDOFF.md', 'DOC', 21929),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/composer_bootstrap.py', 'SOURCE', 4559),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/composer_context_api.py', 'SOURCE', 2368),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/composer_contracts_cpu.sbatch', 'SOURCE', 1045),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/composer_cpu.sbatch', 'SOURCE', 972),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/final_delivery_composer.py', 'SOURCE', 48390),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/github_export_context.py', 'SOURCE', 42088),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/relative_archive_restore.py', 'SOURCE', 17574),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/restored_index_scope.py', 'SOURCE', 27780),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/test_final_delivery_composer.py', 'SOURCE', 45040),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/test_github_export_context.py', 'SOURCE', 27421),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1/test_restored_index_scope.py', 'SOURCE', 32243),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/HANDOFF.md', 'DOC', 25479),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/composer_bootstrap.py', 'SOURCE', 4571),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/composer_context_api.py', 'SOURCE', 2368),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/composer_contracts_cpu.sbatch', 'SOURCE', 1069),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/composer_cpu.sbatch', 'SOURCE', 984),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/final_delivery_composer.py', 'SOURCE', 48390),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/github_export_context.py', 'SOURCE', 42100),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/relative_archive_restore.py', 'SOURCE', 17574),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/restored_index_scope.py', 'SOURCE', 34080),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/test_final_delivery_composer.py', 'SOURCE', 45040),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/test_github_export_context.py', 'SOURCE', 27433),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v6_restoreindex1_fixturefix1/test_restored_index_scope.py', 'SOURCE', 37997),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3/FINAL_SOURCE_CHECKLIST.md', 'DOC', 5104),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3/HANDOFF.md', 'DOC', 10537),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3/final_source_closure.py', 'SOURCE', 46366),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3/final_source_context_adapter.py', 'SOURCE', 6993),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3/final_source_cpu.sbatch', 'SOURCE', 1532),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3/test_final_source_closure.py', 'SOURCE', 31457),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/FINAL_SOURCE_CHECKLIST.md', 'DOC', 2383),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/HANDOFF.md', 'DOC', 3148),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/final_source_closure.py', 'SOURCE', 46366),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/final_source_context_adapter.py', 'SOURCE', 6993),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/final_source_cpu.sbatch', 'SOURCE', 1544),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/test_final_source_closure.py', 'SOURCE', 31753),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/formal_failed_atom_coverage_diagnostic_v1/diagnostic.py', 'SOURCE', 23765),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/formal_failed_atom_coverage_diagnostic_v1/diagnostic.sbatch', 'SOURCE', 1040),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/restored_root298_cost_verifier_v1/HANDOFF.md', 'DOC', 16258),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/restored_root298_cost_verifier_v1/checker.py', 'SOURCE', 39223),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/restored_root298_cost_verifier_v1/checker_cpu.sbatch', 'SOURCE', 1482),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/restored_root298_cost_verifier_v1/test_checker.py', 'SOURCE', 21586),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_query_probe_v1_rev1_14448/HANDOFF.md', 'DOC', 9616),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_query_probe_v1_rev1_14448/diagnostic.py', 'SOURCE', 26418),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_query_probe_v1_rev1_14448/diagnostic_cpu.sbatch', 'SOURCE', 1086),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_universe_diagnostic_v1_rev2_14178/HANDOFF.md', 'DOC', 3126),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_universe_diagnostic_v1_rev2_14178/diagnostic.py', 'SOURCE', 12510),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_universe_diagnostic_v1_rev2_14178/diagnostic_cpu.sbatch', 'SOURCE', 1060),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_native_catalog_capture_v1/capture.py', 'SOURCE', 2409),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_native_catalog_capture_v1/capture_cpu.sbatch', 'SOURCE', 924),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/common_root_receipt_metadata_amendment_13460/acceptance.json', 'CONTROL_METADATA', 17771),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/current_receipt_capture_13421/descriptor_capture.json', 'CONTROL_METADATA', 11740),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/default13420_receipt_capture_13433/descriptor_capture.json', 'CONTROL_METADATA', 7255),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/default_scheduler_dispatch_13420/scheduler_ready_before_unchanged_apply.json', 'CONTROL_METADATA', 20902),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_common_finish_ownerqueue14689_fullcost14576/owner_queue_driver_control/driver_execution_acceptance.json', 'CONTROL_METADATA', 79444),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_common_finish_ownerqueue14689_fullcost14576/owner_queue_driver_control/owner_queue.command.json', 'CONTROL_METADATA', 900),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_common_finish_ownerqueue14689_fullcost14576/owner_queue_driver_control/owner_queue.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_common_finish_ownerqueue14689_fullcost14576/owner_queue_driver_control/owner_queue.stdout', 'CONTROL_METADATA', 56),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_failed_atom_coverage_13410/diagnostic.json', 'CONTROL_METADATA', 64977),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_failed_atom_coverage_13410/evidence/0000_diagnostic.py', 'SOURCE', 23765),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_failed_atom_coverage_13410/evidence/0001_diagnostic.sbatch', 'SOURCE', 1040),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native_catalog_receipt_capture_13288/descriptor_capture.json', 'CONTROL_METADATA', 2941),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/report_request_descriptor_capture_14875/capture.json', 'CONTROL_METADATA', 9931),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_cost_time_query_probe_14513/diagnostic.json', 'CONTROL_METADATA', 63724),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_cost_universe_diagnostic_14448/diagnostic.json', 'CONTROL_METADATA', 34633),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_e2e_descriptor_capture_13318/descriptor_capture.json', 'CONTROL_METADATA', 4625),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common13460_actual_metadata_amendment_terminal_seal/receipt.json', 'CONTROL_METADATA', 10023),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common14706_actual_scientific_finish_terminal_metadata_seal_retry1/prepared_metadata.json', 'CONTROL_METADATA', 11703),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common14706_actual_scientific_finish_terminal_metadata_seal_retry1/receipt.json', 'CONTROL_METADATA', 26686),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common14706_actual_scientific_finish_terminal_metadata_seal_retry1/terminal.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common14706_actual_scientific_finish_terminal_metadata_seal_retry1/terminal.stdout.txt', 'CONTROL_METADATA', 115),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common14706_actual_scientific_finish_terminal_metadata_seal_retry1/unchanged_model_hardlink_metadata.json', 'CONTROL_METADATA', 505439),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_actual_terminal_metadata_seal/receipt.json', 'CONTROL_METADATA', 8123),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_actual_terminal_metadata_seal/terminal.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_actual_terminal_metadata_seal/terminal.stdout', 'CONTROL_METADATA', 113),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/query0.stdout', 'CONTROL_METADATA', 459),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/query1.stdout', 'CONTROL_METADATA', 1526),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/query2.stdout', 'CONTROL_METADATA', 550),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_driver_software14689_scheduler_metadata_20261014T053441Z/receipt.json', 'CONTROL_METADATA', 5326),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/query0.stdout', 'CONTROL_METADATA', 418),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/query2.stdout', 'CONTROL_METADATA', 825),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T053958Z/receipt.json', 'CONTROL_METADATA', 5453),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/query0.stdout', 'CONTROL_METADATA', 421),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/query2.stdout', 'CONTROL_METADATA', 1100),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T054442Z/receipt.json', 'CONTROL_METADATA', 5457),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/query0.stdout', 'CONTROL_METADATA', 421),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/query2.stdout', 'CONTROL_METADATA', 1100),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T055001Z/receipt.json', 'CONTROL_METADATA', 5457),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/query0.stdout', 'CONTROL_METADATA', 424),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/query2.stdout', 'CONTROL_METADATA', 1107),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T060242Z/receipt.json', 'CONTROL_METADATA', 5458),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/query0.stdout', 'CONTROL_METADATA', 424),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/query2.stdout', 'CONTROL_METADATA', 550),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T061405Z/receipt.json', 'CONTROL_METADATA', 5460),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/query0.stdout', 'CONTROL_METADATA', 424),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/query2.stdout', 'CONTROL_METADATA', 550),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062210Z/receipt.json', 'CONTROL_METADATA', 5625),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/query0.stdout', 'CONTROL_METADATA', 424),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/query1.stdout', 'CONTROL_METADATA', 1905),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/query2.stdout', 'CONTROL_METADATA', 550),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T062446Z/receipt.json', 'CONTROL_METADATA', 5632),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/query0.stdout', 'CONTROL_METADATA', 466),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/query1.stderr', 'CONTROL_METADATA', 48),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/query1.stdout', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/query2.stdout', 'CONTROL_METADATA', 275),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_ownerqueue_scientific_finish14706_scheduler_metadata_20261014T073653Z/receipt.json', 'CONTROL_METADATA', 6123),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_root_receipt_metadata_amendment_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 2920),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_root_receipt_metadata_amendment_v1_primary_claim/request.json', 'CONTROL_METADATA', 16136),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_root_receipt_metadata_amendment_v1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 383),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/common_root_receipt_metadata_amendment_v1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 493),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/consumer13319_13320_cpu_backfill_timelimits/receipt.json', 'CONTROL_METADATA', 7234),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/consumer13325_13326_software_cpu_timelimit1m/receipt.json', 'CONTROL_METADATA', 7582),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/consumer_v4_v3_v3_metadata_readonly_seal/receipt.json', 'CONTROL_METADATA', 9189),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/cost13277_common13269_actual_contract_logs_metadata_readonly_seal/receipt.json', 'CONTROL_METADATA', 2509),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/current_receipt_capture13421_actual_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 2950),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13408_actual_failure_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 7828),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13420_actual_CPU_envelope_90min/after.json', 'CONTROL_METADATA', 1902),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13420_actual_CPU_envelope_90min/before.json', 'CONTROL_METADATA', 1902),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13420_actual_CPU_envelope_90min/receipt.json', 'CONTROL_METADATA', 349),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13420_actual_CPU_envelope_90min/request.json', 'CONTROL_METADATA', 658),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13420_actual_CPU_envelope_90min/update.json', 'CONTROL_METADATA', 230),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13420_actual_success_metadata_terminal_seal_retry1/receipt.json', 'CONTROL_METADATA', 56318),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default13433_actual_descriptor_terminal_metadata_seal/receipt.json', 'CONTROL_METADATA', 3133),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_apply_scheduler_bootstrap_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 3097),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_apply_scheduler_bootstrap_v1_primary_claim/request.json', 'CONTROL_METADATA', 726),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_apply_scheduler_bootstrap_v1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 296),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_apply_scheduler_bootstrap_v1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 320),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_integration84_fixturefix1_retry_after13324/metadata_readonly_seal.json', 'CONTROL_METADATA', 1436),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_integration84_fixturefix1_retry_after13324/submit_receipt.json', 'CONTROL_METADATA', 1266),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_integration84_software_after13322_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 1013),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_apply_scheduler13412_retry1_primary_claim/request.json', 'CONTROL_METADATA', 1276),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_apply_scheduler13412_retry1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 490),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_apply_scheduler13412_retry1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 514),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_integration_actual_apply_primary_claim/request.json', 'CONTROL_METADATA', 1730),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_integration_actual_apply_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 784),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_integration_actual_apply_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_scheduler13412_actual_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 15229),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/exact_context_mapper_v4_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 596),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/failed13324_contract_log_metadata_readonly_seal/receipt.json', 'CONTROL_METADATA', 522),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v4_fixturefix1_retry_after13321/metadata_readonly_seal.json', 'CONTROL_METADATA', 2526),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v4_fixturefix1_retry_after13321/submit_receipt.json', 'CONTROL_METADATA', 751),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v4_fixturefix2_retry_after13323/metadata_readonly_seal.json', 'CONTROL_METADATA', 2533),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v4_fixturefix2_retry_after13323/submit_receipt.json', 'CONTROL_METADATA', 758),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v5_actual13328_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 2758),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_13368_actual_failure_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 7597),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_13368_cpu_backfill_timelimit/actual_update.json', 'CONTROL_METADATA', 190),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_13368_cpu_backfill_timelimit/after_scheduler.json', 'CONTROL_METADATA', 1675),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_13368_cpu_backfill_timelimit/before_scheduler.json', 'CONTROL_METADATA', 1679),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_13368_cpu_backfill_timelimit/receipt.json', 'CONTROL_METADATA', 4159),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_fixturefix1_13373_actual_metadata_terminal_seal_retry1/receipt.json', 'CONTROL_METADATA', 4632),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer_v6_fixturefix2_13377_actual_metadata_terminal_seal_retry1/receipt.json', 'CONTROL_METADATA', 4862),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_QA13282_from14901_primary_claim/in_progress.json', 'CONTROL_METADATA', 1018),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_QA13282_from14901_primary_claim/request.json', 'CONTROL_METADATA', 3646),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_QA13282_from14901_primary_claim/sbatch.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_QA13282_from14901_primary_claim/sbatch.stdout.txt', 'CONTROL_METADATA', 6),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_QA13282_from14901_primary_claim/submit.json', 'CONTROL_METADATA', 1186),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build13282_from14706_fullcost14576_primary_claim/in_progress.json', 'CONTROL_METADATA', 1049),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build13282_from14706_fullcost14576_primary_claim/request.json', 'CONTROL_METADATA', 4919),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build13282_from14706_fullcost14576_primary_claim/sbatch.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build13282_from14706_fullcost14576_primary_claim/sbatch.stdout.txt', 'CONTROL_METADATA', 6),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build13282_from14706_fullcost14576_primary_claim/submit.json', 'CONTROL_METADATA', 1222),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/query0.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/query0.stdout.txt', 'CONTROL_METADATA', 187),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/query1.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/query1.stdout.txt', 'CONTROL_METADATA', 1777),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/query2.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/query2.stdout.txt', 'CONTROL_METADATA', 73),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_build14901_scheduler_metadata_20261014T081325Z/receipt.json', 'CONTROL_METADATA', 7988),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/query0.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/query0.stdout.txt', 'CONTROL_METADATA', 186),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/query1.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/query1.stdout.txt', 'CONTROL_METADATA', 1757),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/query2.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/query2.stdout.txt', 'CONTROL_METADATA', 73),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_scientific_report_qa14925_scheduler_metadata_20261014T082352Z/receipt.json', 'CONTROL_METADATA', 7886),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_closure_v3_software_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 467),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_v3_fixturefix1_retry_after13320/metadata_readonly_seal.json', 'CONTROL_METADATA', 1918),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_v3_fixturefix1_retry_after13320/submit_receipt.json', 'CONTROL_METADATA', 756),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_atom13410_actual_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 38660),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish14600_actual_failed_typed_metadata_terminal_seal/terminal.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish14600_actual_failed_typed_metadata_terminal_seal/terminal.stdout', 'CONTROL_METADATA', 447),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish_from13422_fullcost14576_primary_claim/in_progress.json', 'CONTROL_METADATA', 1463),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish_from13422_fullcost14576_primary_claim/request.json', 'CONTROL_METADATA', 4272),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish_from13422_fullcost14576_primary_claim/submit.json', 'CONTROL_METADATA', 1702),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish_ownerqueue14689_fullcost14576_primary_claim/in_progress.json', 'CONTROL_METADATA', 1330),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish_ownerqueue14689_fullcost14576_primary_claim/request.json', 'CONTROL_METADATA', 6003),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_common_finish_ownerqueue14689_fullcost14576_primary_claim/submit.json', 'CONTROL_METADATA', 1440),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_failed_atom_coverage_diagnostic_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 1391),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_failed_atom_coverage_diagnostic_v1_primary_claim/request.json', 'CONTROL_METADATA', 1213),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_failed_atom_coverage_diagnostic_v1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 363),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/formal_failed_atom_coverage_diagnostic_v1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 454),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/human_report14901_QA14925_review_metadata/receipt.json', 'CONTROL_METADATA', 1513),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/ipsae_synthetic_loader_diagnostic_13372_actual_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 585675),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/operator_erratum10_actual14576_14689_14692_root_install_metadata/receipt.json', 'CONTROL_METADATA', 1393),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/operator_erratum6_actual13377_root_install_metadata/receipt.json', 'CONTROL_METADATA', 1329),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/operator_erratum7_actual13420_13433_root_install_metadata/receipt.json', 'CONTROL_METADATA', 1942),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/operator_erratum8_actual13460_journal0006_root_install_metadata/receipt.json', 'CONTROL_METADATA', 1885),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/operator_erratum9_actual13558_root_install_metadata/receipt.json', 'CONTROL_METADATA', 1134),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_QA14925_actual_terminal_metadata_seal/receipt.json', 'CONTROL_METADATA', 7208),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_QA14925_actual_terminal_metadata_seal/terminal.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_QA14925_actual_terminal_metadata_seal/terminal.stdout.txt', 'CONTROL_METADATA', 112),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_build14901_actual_terminal_metadata_seal/receipt.json', 'CONTROL_METADATA', 10354),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_build14901_actual_terminal_metadata_seal/terminal.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_build14901_actual_terminal_metadata_seal/terminal.stdout.txt', 'CONTROL_METADATA', 113),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_actual_terminal_metadata_seal/receipt.json', 'CONTROL_METADATA', 7129),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_actual_terminal_metadata_seal/terminal.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_actual_terminal_metadata_seal/terminal.stdout.txt', 'CONTROL_METADATA', 120),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/query0.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/query0.stdout.txt', 'CONTROL_METADATA', 194),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/query1.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/query1.stdout.txt', 'CONTROL_METADATA', 1680),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/query2.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/query2.stdout.txt', 'CONTROL_METADATA', 120),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_capture14875_scheduler_metadata_20261014T075859Z/receipt.json', 'CONTROL_METADATA', 8370),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_descriptor_capture_v1_primary_claim/in_progress.json', 'CONTROL_METADATA', 764),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_descriptor_capture_v1_primary_claim/request.json', 'CONTROL_METADATA', 4202),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_descriptor_capture_v1_primary_claim/sbatch.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_descriptor_capture_v1_primary_claim/sbatch.stdout.txt', 'CONTROL_METADATA', 6),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_descriptor_capture_v1_primary_claim/submit.json', 'CONTROL_METADATA', 904),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/report_request_descriptor_capture_v1_source_metadata_readonly_seal/receipt.json', 'CONTROL_METADATA', 3923),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_software_13558_actual_terminal_seal/receipt.json', 'CONTROL_METADATA', 8149),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_verifier_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 3272),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_verifier_v1_primary_claim/request.json', 'CONTROL_METADATA', 1379),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_verifier_v1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 469),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_verifier_v1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 790),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_actual_failed_parse_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 3070),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/query0.stdout', 'CONTROL_METADATA', 443),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/query1.stdout', 'CONTROL_METADATA', 1517),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/query2.stdout', 'CONTROL_METADATA', 1375),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14668_scheduler_metadata_20261014T051524Z/receipt.json', 'CONTROL_METADATA', 4763),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/query0.stdout', 'CONTROL_METADATA', 449),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/query1.stdout', 'CONTROL_METADATA', 1514),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/query2.stdout', 'CONTROL_METADATA', 550),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software14692_scheduler_metadata_20261014T053441Z/receipt.json', 'CONTROL_METADATA', 5267),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software_14692_actual_terminal_seal/receipt.json', 'CONTROL_METADATA', 8732),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software_14692_actual_terminal_seal/terminal.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_root298_cost_software_14692_actual_terminal_seal/terminal.stdout', 'CONTROL_METADATA', 105),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/query0.stdout', 'CONTROL_METADATA', 447),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/query1.stdout', 'CONTROL_METADATA', 2106),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/query2.stdout', 'CONTROL_METADATA', 5276),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_common_finish14600_scheduler_metadata_20261014T043111Z/receipt.json', 'CONTROL_METADATA', 4919),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_actual_metadata_terminal_seal_retry1/receipt.json', 'CONTROL_METADATA', 30298),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_actual_metadata_terminal_seal_retry1/terminal.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_actual_metadata_terminal_seal_retry1/terminal.stdout', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/0_stdout.txt', 'CONTROL_METADATA', 178),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/1_stdout.txt', 'CONTROL_METADATA', 1518),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/2_stdout.txt', 'CONTROL_METADATA', 2387),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe14513_scheduler_metadata_20261014T035130Z/receipt.json', 'CONTROL_METADATA', 8483),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe_from14448_rev1_primary_claim/request.json', 'CONTROL_METADATA', 2762),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe_from14448_rev1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 580),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_query_probe_from14448_rev1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 744),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_universe_diagnostic_from14178_rev2_primary_claim/request.json', 'CONTROL_METADATA', 2576),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_universe_diagnostic_from14178_rev2_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 604),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_time_universe_diagnostic_from14178_rev2_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 756),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_actual_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 11478),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_actual_metadata_terminal_seal/terminal_sacct.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_actual_metadata_terminal_seal/terminal_sacct.stdout', 'CONTROL_METADATA', 187),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/0_stdout.txt', 'CONTROL_METADATA', 187),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/1_stdout.txt', 'CONTROL_METADATA', 1541),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/2_stdout.txt', 'CONTROL_METADATA', 2240),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_cost_universe_diagnostic14448_scheduler_metadata_20261014T032135Z/receipt.json', 'CONTROL_METADATA', 8331),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_current_receipt_capture_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 1210),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_current_receipt_capture_v1_primary_claim/request.json', 'CONTROL_METADATA', 362),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_current_receipt_capture_v1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 232),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_current_receipt_capture_v1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 290),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_default13420_receipt_capture_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 1230),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_default13420_receipt_capture_v1_primary_claim/request.json', 'CONTROL_METADATA', 819),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_default13420_receipt_capture_v1_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 237),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_default13420_receipt_capture_v1_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 295),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T125602Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T125602Z/0_stdout.txt', 'CONTROL_METADATA', 1390),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T125602Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T125602Z/1_stdout.txt', 'CONTROL_METADATA', 1391),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T125602Z/receipt.json', 'CONTROL_METADATA', 4345),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T135609Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T135609Z/0_stdout.txt', 'CONTROL_METADATA', 1399),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T135609Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T135609Z/1_stdout.txt', 'CONTROL_METADATA', 1349),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T135609Z/receipt.json', 'CONTROL_METADATA', 4205),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/0_stdout.txt', 'CONTROL_METADATA', 1430),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/1_stdout.txt', 'CONTROL_METADATA', 1436),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/2_stdout.txt', 'CONTROL_METADATA', 1482),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/3_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/3_stdout.txt', 'CONTROL_METADATA', 1480),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/4_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/4_stdout.txt', 'CONTROL_METADATA', 1480),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/5_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/5_stdout.txt', 'CONTROL_METADATA', 1480),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261013T235557Z/receipt.json', 'CONTROL_METADATA', 10745),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T010530Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T010530Z/0_stdout.txt', 'CONTROL_METADATA', 1536),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T010530Z/receipt.json', 'CONTROL_METADATA', 2335),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/0_stdout.txt', 'CONTROL_METADATA', 1434),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/1_stdout.txt', 'CONTROL_METADATA', 1521),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/2_stdout.txt', 'CONTROL_METADATA', 1521),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/3_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/3_stdout.txt', 'CONTROL_METADATA', 1521),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/4_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/4_stdout.txt', 'CONTROL_METADATA', 1521),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/5_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/5_stdout.txt', 'CONTROL_METADATA', 1555),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/6_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/6_stdout.txt', 'CONTROL_METADATA', 1555),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/7_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/7_stdout.txt', 'CONTROL_METADATA', 1555),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_owned_queue_context_20261014T012845Z/receipt.json', 'CONTROL_METADATA', 14614),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/after.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/after.stdout.txt', 'CONTROL_METADATA', 2152),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/before.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/before.stdout.txt', 'CONTROL_METADATA', 2159),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/receipt.json', 'CONTROL_METADATA', 5283),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/request.json', 'CONTROL_METADATA', 904),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/update.stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_pending_CPU1_8G_10min_envelope_amendment/update.stdout.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/0_stdout.txt', 'CONTROL_METADATA', 100),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/1_stderr.txt', 'CONTROL_METADATA', 48),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/1_stdout.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/2_stdout.txt', 'CONTROL_METADATA', 1037),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_diagnostic_metadata_20261014T015834Z/receipt.json', 'CONTROL_METADATA', 2468),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/1_stdout.txt', 'CONTROL_METADATA', 2140),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T165128Z/receipt.json', 'CONTROL_METADATA', 3543),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/1_stdout.txt', 'CONTROL_METADATA', 2140),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T170550Z/receipt.json', 'CONTROL_METADATA', 3543),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/1_stdout.txt', 'CONTROL_METADATA', 2165),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T173504Z/receipt.json', 'CONTROL_METADATA', 3568),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T174558Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T180516Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T183510Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T190503Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T193532Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T200530Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T203536Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T210531Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T213540Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T220536Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T223535Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T230535Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261012T233541Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T000545Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T003534Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T010548Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/1_stdout.txt', 'CONTROL_METADATA', 2157),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T013618Z/receipt.json', 'CONTROL_METADATA', 3560),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T020541Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T023534Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T030612Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052011Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T052340Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T055338Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T062349Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T065359Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T072404Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T075441Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T082414Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T085430Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T094200Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T100323Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T102453Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T105439Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T112420Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T115428Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T122925Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/2_stdout.txt', 'CONTROL_METADATA', 441),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T125437Z/receipt.json', 'CONTROL_METADATA', 3862),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/2_stdout.txt', 'CONTROL_METADATA', 147),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T132442Z/receipt.json', 'CONTROL_METADATA', 3566),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T135432Z/receipt.json', 'CONTROL_METADATA', 3869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T142436Z/receipt.json', 'CONTROL_METADATA', 3869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T145436Z/receipt.json', 'CONTROL_METADATA', 3869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T152428Z/receipt.json', 'CONTROL_METADATA', 3869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T155456Z/receipt.json', 'CONTROL_METADATA', 3869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/1_stdout.txt', 'CONTROL_METADATA', 2163),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T162445Z/receipt.json', 'CONTROL_METADATA', 3869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T165429Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T172428Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T175443Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T182427Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T185434Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T192440Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T195424Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T202427Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T205423Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T212418Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T215418Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T222420Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T225418Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/2_stdout.txt', 'CONTROL_METADATA', 448),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T232437Z/receipt.json', 'CONTROL_METADATA', 3888),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/2_stdout.txt', 'CONTROL_METADATA', 1338),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261013T235427Z/receipt.json', 'CONTROL_METADATA', 4784),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/1_stdout.txt', 'CONTROL_METADATA', 2176),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/2_stdout.txt', 'CONTROL_METADATA', 597),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T010338Z/receipt.json', 'CONTROL_METADATA', 4032),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/1_stdout.txt', 'CONTROL_METADATA', 2182),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/2_stdout.txt', 'CONTROL_METADATA', 1638),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost13782_scheduler_metadata_20261014T012639Z/receipt.json', 'CONTROL_METADATA', 5086),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_actual_failed_typed_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 9834),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_actual_failed_typed_metadata_terminal_seal/terminal_sacct.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_actual_failed_typed_metadata_terminal_seal/terminal_sacct.stdout', 'CONTROL_METADATA', 171),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T021354Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T021354Z/0_stdout.txt', 'CONTROL_METADATA', 1398),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T021354Z/receipt.json', 'CONTROL_METADATA', 2181),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/0_stdout.txt', 'CONTROL_METADATA', 1460),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/1_stdout.txt', 'CONTROL_METADATA', 1434),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/2_stdout.txt', 'CONTROL_METADATA', 1584),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/3_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/3_stdout.txt', 'CONTROL_METADATA', 1584),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/4_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/4_stdout.txt', 'CONTROL_METADATA', 1584),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/5_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/5_stdout.txt', 'CONTROL_METADATA', 1584),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T022816Z/receipt.json', 'CONTROL_METADATA', 14388),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/0_stdout.txt', 'CONTROL_METADATA', 14134),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/1_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/2_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/3_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/3_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/4_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/4_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/5_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/5_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/6_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/6_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/7_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/7_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/8_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/8_stdout.txt', 'CONTROL_METADATA', 1578),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_owned_queue_context_20261014T025758Z/receipt.json', 'CONTROL_METADATA', 34421),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/1_stdout.txt', 'CONTROL_METADATA', 1890),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/2_stdout.txt', 'CONTROL_METADATA', 441),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T021005Z/receipt.json', 'CONTROL_METADATA', 3605),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/1_stdout.txt', 'CONTROL_METADATA', 1890),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/2_stdout.txt', 'CONTROL_METADATA', 1184),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T022710Z/receipt.json', 'CONTROL_METADATA', 7283),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/0_stdout.txt', 'CONTROL_METADATA', 75),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/1_stdout.txt', 'CONTROL_METADATA', 1896),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/2_stdout.txt', 'CONTROL_METADATA', 1643),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025641Z/receipt.json', 'CONTROL_METADATA', 7751),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/0_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/0_stdout.txt', 'CONTROL_METADATA', 97),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/1_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/1_stdout.txt', 'CONTROL_METADATA', 1945),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/2_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/2_stdout.txt', 'CONTROL_METADATA', 1644),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit14178_scheduler_metadata_20261014T025928Z/receipt.json', 'CONTROL_METADATA', 8311),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit_from13782_primary_claim/request.json', 'CONTROL_METADATA', 2607),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit_from13782_primary_claim/submission_in_progress.json', 'CONTROL_METADATA', 1330),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_audit_from13782_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 1650),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_seal_13782_actual_terminal_metadata_seal_retry1/receipt.json', 'CONTROL_METADATA', 6423),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_seal_13782_actual_terminal_metadata_seal_retry1/terminal_query_stderr.txt', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_seal_13782_actual_terminal_metadata_seal_retry1/terminal_query_stdout.txt', 'CONTROL_METADATA', 174),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/query0.stdout', 'CONTROL_METADATA', 446),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/query1.stdout', 'CONTROL_METADATA', 1955),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/query2.stdout', 'CONTROL_METADATA', 4716),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit14576_scheduler_metadata_20261014T041938Z/receipt.json', 'CONTROL_METADATA', 5189),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit_from13782_14565_primary_claim/in_progress.json', 'CONTROL_METADATA', 1367),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit_from13782_14565_primary_claim/request.json', 'CONTROL_METADATA', 5611),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_audit_from13782_14565_primary_claim/submit.json', 'CONTROL_METADATA', 1473),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_actual_metadata_terminal_seal/receipt.json', 'CONTROL_METADATA', 14649),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_actual_metadata_terminal_seal/terminal.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_actual_metadata_terminal_seal/terminal.stdout', 'CONTROL_METADATA', 446),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/query0.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/query0.stdout', 'CONTROL_METADATA', 446),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/query1.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/query1.stdout', 'CONTROL_METADATA', 1494),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/query2.stderr', 'CONTROL_METADATA', 0),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/query2.stdout', 'CONTROL_METADATA', 4437),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/receipt.json', 'CONTROL_METADATA', 5173),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_journal/0001_formal13260.json', 'CONTROL_METADATA', 435),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_journal/0002_e2e_design_13304.json', 'CONTROL_METADATA', 869),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_journal/0003_e2e_evaluate_13311.json', 'CONTROL_METADATA', 1158),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_journal/0004_controller_metadata_amendment_13315.json', 'CONTROL_METADATA', 1486),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_gpu_journal/0006_common_controller_metadata_amendment_13460.json', 'CONTROL_METADATA', 2123),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_native_catalog_capture_v1_primary_claim/metadata_readonly_seal.json', 'CONTROL_METADATA', 1307),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_native_catalog_capture_v1_primary_claim/submission_receipt.json', 'CONTROL_METADATA', 504),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_e2e_descriptor_capture_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 1326),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_e2e_descriptor_capture_retry_after13317_RO_fix/submit_receipt.json', 'CONTROL_METADATA', 1388),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_pin_inventory_opaque_history_copy_20261014/receipt.json', 'CONTROL_METADATA', 1210),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_plan_immutable_checkpoint_history_snapshot_20261014T090900Z/receipt.json', 'CONTROL_METADATA', 990),
    ('/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_v10_actual_cpu_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 5708),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/design13309_actual_metadata_readonly_seal/receipt.json', 'CONTROL_METADATA', 1575),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/e2e_design_cpu_after13304_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 3589),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/e2e_evaluate_after13309_primary_claim/dispatch_raw.json', 'CONTROL_METADATA', 61),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/e2e_evaluate_after13309_primary_claim/request.json', 'CONTROL_METADATA', 1167),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/e2e_evaluate_after13309_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 3626),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/e2e_final_cpu_after13311_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 1388),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/e2e_scheduling_formal_pending_hold_20261012/receipt.json', 'CONTROL_METADATA', 10057),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/final13312_actual_metadata_readonly_seal/receipt.json', 'CONTROL_METADATA', 1973),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/formal13260_release_after_e2e13311_terminal/receipt.json', 'CONTROL_METADATA', 4576),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/physical13294_e2e_design_primary_claim/formal_throttle_and_pose_metadata_seal.json', 'CONTROL_METADATA', 6954),
    ('/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/submissions/physical13294_e2e_design_primary_claim/submit_receipt.json', 'CONTROL_METADATA', 2755),
)

def need(value, message):
    if not value:
        raise ValueError(message)

def lexical(value):
    """Pure string/path-shape check; never access a receipt child's filesystem."""
    need(isinstance(value, str) and value.startswith("/"), "Absolute path string required")
    need(all(x not in ("", ".", "..") for x in value.split("/")[1:]), "Noncanonical path components")
    q = PurePosixPath(value)
    need(q.is_relative_to(PurePosixPath(str(R))), "Path outside exact logical authority")
    return Path(value)

def ancestry(p):
    p = lexical(str(p))
    for q in (p, *p.parents):
        if q == R.parent:
            break
        need(not q.is_symlink(), "Symbolic input/source/output ancestry rejected")
    return p

def file_metadata(p):
    p = ancestry(p)
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode) and not (s.st_mode & 0o222), "Readonly regular file required")
    return dict(path=str(p), bytes=s.st_size, inode=s.st_ino,
                mtime_ns=s.st_mtime_ns, mode=stat.S_IMODE(s.st_mode))

def read_ro(p):
    p = ancestry(p)
    before = file_metadata(p)
    data = p.read_bytes()
    need(file_metadata(p) == before and len(data) == before["bytes"], "File metadata changed during read")
    receipt = dict(path=str(p), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return receipt, data, before

def strict_json(data):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, "Duplicate JSON key")
            value[key] = item
        return value
    def constant(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    def number(value):
        parsed = float(value)
        need(math.isfinite(parsed), "Nonfinite JSON number")
        return parsed
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)

def tres(value):
    fields = {}
    for token in value.split(","):
        need("=" in token, "Malformed allocated TRES")
        key, val = token.split("=", 1)
        need(key and val and key not in fields, "Duplicate/empty allocated TRES")
        fields[key] = val
    need(fields.get("cpu") == "1", "Actual allocated CPU1 required")
    for key, val in fields.items():
        if key == "gpu" or key.startswith(("gres/gpu", "gres:gpu")):
            need(re.fullmatch(r"(?:gpu|gres/gpu|gres:gpu)(?::[A-Za-z0-9_.-]+)?", key) and
                 val.isdigit() and int(val) == 0, "GPU allocation or malformed GPU namespace")
    return fields

def cpu():
    jid = os.environ.get("SLURM_JOB_ID", "")
    need(jid.isdigit() and int(jid) > 0, "Actual named CPU allocation required before hashing")
    for key, val in {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu",
                     "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
                     "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                     "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}.items():
        need(os.environ.get(key) == val, "Pure CPU import/thread isolation differs")
    need("PYTHONPATH" not in os.environ, "Injected PYTHONPATH")
    argv = ["scontrol", "show", "job", jid, "-o"]
    proc = subprocess.run(argv, capture_output=True, text=True)
    need(proc.returncode == 0, "Current own allocation query failed")
    rows = [line for line in proc.stdout.splitlines()
            if re.search(r"\bJobId=" + re.escape(jid) + r"(?:\s|$)", line)]
    need(len(rows) == 1, "Unique actual numeric current allocation")
    fields = {}
    for key, val in re.findall(r"(\w+)=(\S*)", rows[0]):
        need(key not in fields, "Duplicate scheduler field")
        fields[key] = val
    need(fields.get("JobState") == "RUNNING" and fields.get("JobName") == JOB_NAME and
         fields.get("UserId", "").startswith("u21111210118(") and
         fields.get("Account") == "u21111210118" and fields.get("Partition") == "organ" and
         fields.get("NumCPUs") == "1" and fields.get("NumTasks") == "1",
         "Actual named owner/account/organ CPU1 required")
    reps = [tres(fields[key]) for key in ("TRES", "AllocTRES") if key in fields]
    need(reps and all(row == reps[0] for row in reps), "Missing/inconsistent actual allocated TRES")
    return dict(job_id=jid, allocated_CPUs=1, allocated_GPUs=0, query_argv=argv,
                returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)

def stable_runtime_metadata(s):
    # Atime is an access observation, not an immutable byte identity.
    return dict(dev=s.st_dev, inode=s.st_ino, fullmode=s.st_mode, nlink=s.st_nlink,
                uid=s.st_uid, gid=s.st_gid, bytes=s.st_size, mtime_ns=s.st_mtime_ns,
                ctime_ns=s.st_ctime_ns,
                kind="regular" if stat.S_ISREG(s.st_mode) else
                     "symlink" if stat.S_ISLNK(s.st_mode) else "unsupported")

def runtime_core():
    link_before = CORE.lstat()
    need(stat.S_ISLNK(link_before.st_mode) and os.readlink(CORE) == "python3.11" and
         CORE.resolve() == CORE_REAL and Path(sys.executable).resolve() == CORE_REAL,
         "Exact conditional core interpreter/link required")
    ancestry(CORE_REAL)
    before = CORE_REAL.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_size == CORE_BYTES,
         "Conditional binary shape differs")
    digest = hashlib.sha256(CORE_REAL.read_bytes()).hexdigest()
    after = CORE_REAL.lstat()
    link_after = CORE.lstat()
    stable_before = stable_runtime_metadata(before)
    stable_after = stable_runtime_metadata(after)
    link_stable_before = stable_runtime_metadata(link_before)
    link_stable_after = stable_runtime_metadata(link_after)
    diagnostic = dict(schema="conditional-core-runtime-access-observation.v1",
        actual_current_CPU_job_id=os.environ.get("SLURM_JOB_ID"),
        scope="STDERR_ONLY_CONDITIONAL_RUNTIME_METADATA_NOT_ARCHIVE_SOURCE",
        binary_atime_ns_before=before.st_atime_ns, binary_atime_ns_after=after.st_atime_ns,
        link_atime_ns_before=link_before.st_atime_ns, link_atime_ns_after=link_after.st_atime_ns,
        rawstat_equal=(before == after), stable_equal=(stable_before == stable_after),
        link_stable_equal=(link_stable_before == link_stable_after),
        digest_exact=(digest == CORE_SHA), observed_sha256_as_scalar=digest,
        before_stable=stable_before, after_stable=stable_after,
        link_before_stable=link_stable_before, link_after_stable=link_stable_after,
        atime_used_in_runtime_identity_or_guard=False,
        old15063_specific_cause_proven=False)
    sys.stderr.write(json.dumps(diagnostic, ensure_ascii=False, allow_nan=False) + "\n")
    sys.stderr.flush()
    need(digest == CORE_SHA, "Conditional core exact SHA differs")
    need(stable_before == stable_after and link_stable_before == link_stable_after and
         stat.S_ISREG(after.st_mode) and os.readlink(CORE) == "python3.11" and
         CORE.resolve() == CORE_REAL, "Conditional core stable metadata or link differs")
    return dict(scope="CONDITIONAL_INSTALLED_CPU_RUNTIME_NOT_ARCHIVE_SOURCE",
        logical_interpreter=str(CORE), resolved_interpreter=str(CORE_REAL),
        link_target="python3.11", link_inode=link_after.st_ino,
        link_mtime_ns=link_after.st_mtime_ns, binary_inode=after.st_ino,
        binary_mtime_ns=after.st_mtime_ns, binary_mode=stat.S_IMODE(after.st_mode),
        bytes_as_scalar=after.st_size, sha256_as_scalar=digest,
        binary_stable_metadata=stable_after, link_stable_metadata=link_stable_after,
        included_in_package=False)

def source_rows(directory):
    directory = ancestry(directory)
    need(directory.is_dir() and not (directory.stat().st_mode & 0o222) and
         {p.name for p in directory.iterdir()} == set(FILES), "Exact readonly OWN3 source universe")
    values = [text_ro(directory / name) for name in FILES]
    return [r for r, b, m in values], [m for r, b, m in values]

def historical_rows():
    # EXACT old failed OWN3, hash-only SOURCE data; never compile/import/copy/execute it.
    receipts, metadata = source_rows(HISTORICAL_P)
    need(tuple(r["bytes"] for r in receipts) == HISTORICAL_BYTES,
         "Old failed OWN3 literal byte sizes changed")
    return receipts, metadata

def metadata_shape(row):
    need(type(row) is dict and set(row) == {"path", "kind", "bytes", "inode", "mtime_ns", "mode"},
         "Exact declared target metadata required")
    for key in ("bytes", "inode", "mtime_ns", "mode"):
        need(type(row[key]) is int, "Target metadata must contain Python integers, never bool/float")
    need(row["bytes"] >= 0 and row["inode"] > 0 and row["mtime_ns"] >= 0 and
         row["mode"] == 0o444, "Exact positive identity and readonly target mode required")
    lexical(row["path"])
    need(type(row["kind"]) is str, "Literal target kind")

def saved_metadata_shape(row):
    need(type(row) is dict and set(row) == {"path", "bytes", "inode", "mtime_ns", "mode"},
         "Exact saved metadata keys")
    for key in ("bytes", "inode", "mtime_ns", "mode"):
        need(type(row[key]) is int, "Exact integer saved metadata")
    need(row["bytes"] >= 0 and row["inode"] > 0 and row["mtime_ns"] >= 0 and
         row["mode"] == 0o444, "Saved readonly metadata identity")
    lexical(row["path"])

def receipt_shape(row):
    need(type(row) is dict and set(row) == {"path", "bytes", "sha256"}, "Exact full tuple required")
    need(type(row["bytes"]) is int and row["bytes"] >= 0 and
         type(row["sha256"]) is str and re.fullmatch("[0-9a-f]{64}", row["sha256"]),
         "Exact bytes/SHA tuple required")
    lexical(row["path"])

def text_ro(p):
    p = ancestry(p)
    before = file_metadata(p)
    data = p.read_bytes()
    need(file_metadata(p) == before and len(data) == before["bytes"], "Text metadata drift during read")
    need(b"\x00" not in data, "Binary payload is outside text capture")
    data.decode("utf-8", "strict")
    receipt = dict(path=str(p), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return receipt, data, before

def target_policy(path, kind):
    expected = {p: (k, n) for p, k, n in FIXED_TARGETS}
    need(len(expected) == len(FIXED_TARGETS) and FIXED_TARGETS,
         "Finite explicit target whitelist required")
    need(path in expected and expected[path][0] == kind, "Target not in exact literal path/kind whitelist")
    suffix = Path(path).suffix
    need((kind == "SOURCE" and suffix in (".py", ".sbatch", ".sh")) or
         (kind == "DOC" and (suffix == ".md" or
                             (Path(path) == OPAQUE_INVENTORY and suffix == ".txt"))) or
         (kind == "CONTROL_METADATA" and suffix in (".json", ".txt", ".stdout", ".stderr")),
         "Only declared source/doc/control text; no model, binary, archive or scientific RAW")
    need(Path(path) not in (REQUEST, PLAN) and not Path(path).is_relative_to(P),
         "Request/new plan/OWN3 are separate exact scopes")

def request_shape(obj):
    need(type(obj) is dict and set(obj) == {"schema", "metadata_scope", "targets"},
         "Exact finite capture-request keys")
    need(obj["schema"] == "final-source-plan-pin-capture-request.v1" and
         obj["metadata_scope"] == "EXPLICIT_SOURCE_DOC_CONTROL_METADATA_ONLY",
         "Fixed nonscientific metadata request")
    rows = obj["targets"]
    need(type(rows) is list and len(rows) == len(FIXED_TARGETS) and rows,
         "Whole finite whitelist must appear exactly once")
    for row, (path, kind, size) in zip(rows, FIXED_TARGETS):
        metadata_shape(row)
        need((row["path"], row["kind"], row["bytes"]) == (path, kind, size), "Literal target order/identity/size mismatch")
        target_policy(path, kind)
    return rows

def verify_targets(rows, saved=None):
    results = []
    for row in rows:
        target_policy(row["path"], row["kind"])
        receipt, data, meta = text_ro(Path(row["path"]))
        need(meta == {k: row[k] for k in ("path", "bytes", "inode", "mtime_ns", "mode")},
             "Declared target metadata drift")
        if Path(row["path"]) == ORIGINAL_INVENTORY:
            results.append(dict(kind=row["kind"], metadata=meta,
                historical_original_json_identity=dict(
                    classification="RAW_HISTORY_JSON_BYTE_IDENTITY_NOT_OPERATIVE_SEED",
                    logical_path=receipt["path"], bytes_as_scalar=receipt["bytes"],
                    sha256_as_scalar=receipt["sha256"])))
        else:
            results.append(dict(kind=row["kind"], receipt=receipt, metadata=meta))
    if saved is not None:
        need(results == saved, "Finite target bytes/metadata drift")
    return results

def opaque_history_identity(targets):
    # Two exact text paths only. Do not parse original JSON or its receipt-like children.
    original, original_data, original_meta = text_ro(ORIGINAL_INVENTORY)
    opaque, opaque_data, opaque_meta = text_ro(OPAQUE_INVENTORY)
    need(original_data == opaque_data and original["bytes"] == opaque["bytes"] and
         original["sha256"] == opaque["sha256"], "Exact original/opaque raw bytes differ")
    table = {row["metadata"]["path"]: row for row in targets}
    need(table[str(ORIGINAL_INVENTORY)]["metadata"] == original_meta and
         table[str(OPAQUE_INVENTORY)]["metadata"] == opaque_meta and
         table[str(OPAQUE_INVENTORY)]["receipt"] == opaque and
         table[str(ORIGINAL_INVENTORY)]["historical_original_json_identity"] ==
            dict(classification="RAW_HISTORY_JSON_BYTE_IDENTITY_NOT_OPERATIVE_SEED",
                 logical_path=original["path"], bytes_as_scalar=original["bytes"],
                 sha256_as_scalar=original["sha256"]), "Observed opaque pair identity/metadata drift")
    return dict(original_identity=table[str(ORIGINAL_INVENTORY)]["historical_original_json_identity"],
        opaque_text_receipt=opaque, exact_raw_bytes_equal=True, sha256_and_size_equal=True,
        original_metadata=original_meta, opaque_metadata=opaque_meta,
        original_JSON_parsed=False, original_JSON_is_operative_seed=False,
        new_parent_permission_granted=False)

def snapshot_name(jid):
    need(type(jid) is str and re.fullmatch("[1-9][0-9]*", jid), "Numeric original CPU identity")
    return S / "frozen" / ("final_source_plan_pin_capture_v1_rev1_" + jid) / "code"

def owned_output(mode, jid):
    need(mode in ("capture", "plan") and re.fullmatch("[1-9][0-9]*", jid), "Finite output namespace")
    prefix = "final_source_plan_pin_capture_" if mode == "capture" else "final_source_plan_descriptor_"
    p = ancestry(S / "runs" / (prefix + jid))
    need(not p.exists(), "Unique absent owned output required")
    p.mkdir(exist_ok=False)
    return p

def write_ro(out, name, obj):
    allowed = {"source_snapshot.json", "capture.json", "plan_descriptor.json"}
    need(name in allowed and out.parent == S / "runs" and out.is_dir(),
         "Exact owned output file capability")
    p = ancestry(out / name)
    with p.open("xb") as stream:
        stream.write((json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o444)
    return read_ro(p)[0]

def flags():
    return dict(metadata_only=True, source_audit_or_stage_performed=False,
                scientific_acceptance=False, cost_or_scores_recomputed=False,
                receipt_children_opened_hashed_or_statted=False, new_GPU_submission=False,
                Git_changed=False, ACTIVE_changed=False, original_input_mutated=False)

def capture(args, allocation, original, before, frozen, frozen_before, runtime, syntax, history, history_before):
    need(D == snapshot_name(allocation["job_id"]) and Path(__file__).absolute() == D / "capture.py",
         "Actual executing sealed OWN3 required")
    need(Path(args.request) == REQUEST and str(args.request) == str(REQUEST),
         "Only the exact root request is allowed")
    rr, data, request_before = text_ro(REQUEST)
    obj = strict_json(data)
    rows = request_shape(obj)
    targets = verify_targets(rows)
    opaque_proof = opaque_history_identity(targets)
    out = owned_output("capture", allocation["job_id"])
    snapshot_obj = dict(schema="final-source-plan-pin-source-snapshot.v1",
        original_executing_sources=original, frozen_source_files=frozen,
        original_metadata_before=before, frozen_metadata_before=frozen_before,
        compile_owned_Python=True, bash_syntax=syntax, allocation=allocation,
        historical_failed_v1_sources=history, historical_metadata_before=history_before,
        historical_sources_hash_only_no_import_compile_or_execution=True)
    snapshot = write_ro(out, "source_snapshot.json", snapshot_obj)
    need(source_rows(P) == (original, before) and source_rows(D) == (frozen, frozen_before),
         "Whole OWN3 source drift before capture")
    need(all((x["bytes"], x["sha256"]) == (y["bytes"], y["sha256"])
             for x, y in zip(original, frozen)), "Original/frozen OWN3 byte mismatch")
    verify_targets(rows, targets)
    need(opaque_history_identity(targets) == opaque_proof, "Opaque original history pre/post drift")
    rr2, data2, rm2 = text_ro(REQUEST)
    need((rr2, data2, rm2) == (rr, data, request_before), "Exact request drift")
    history_after, history_meta = historical_rows()
    need((history_after, history_meta) == (history, history_before), "Old failed OWN3 pre/post drift")
    need(runtime_core() == runtime, "Conditional core runtime drift")
    result = dict(schema="final-source-plan-pin-capture.v1", status=CAPTURE_STATUS,
        actual_CPU_job_id=allocation["job_id"], allocation=allocation, request=rr,
        owned_source_count=3, owned_executable_source_count=2,
        exact_target_count=len(targets), fixed_literal_target_whitelist=list(FIXED_TARGETS),
        targets=targets, opaque_history_byte_identity=opaque_proof,
        original_and_opaque_history_bytes_and_metadata_prepost_PASS=True,
        request_metadata_before=request_before, request_metadata_after=rm2,
        original_executing_sources=original, source_files=frozen, source_snapshot=snapshot,
        historical_failed_v1_sources=history, historical_metadata_before=history_before,
        historical_metadata_after=history_meta, historical_source_prepost_PASS=True,
        historical_sources_hash_only_no_import_compile_or_execution=True,
        original_metadata_before=before, original_metadata_after=before,
        frozen_metadata_before=frozen_before, frozen_metadata_after=frozen_before,
        original_and_frozen_sources_byte_identical=True, whole3_source_prepost_PASS=True,
        request_and_target_bytes_and_metadata_prepost_PASS=True, compiled_owned_Python=True,
        bash_syntax_PASS=True, conditional_core_runtime=runtime,
        conditional_runtime_prepost_PASS=True, **flags())
    own = write_ro(out, "capture.json", result)
    verify_targets(rows, targets)
    need(opaque_history_identity(targets) == opaque_proof, "Opaque original history drift after output")
    need(text_ro(REQUEST) == (rr, data, request_before), "Request drift after output")
    need(source_rows(P) == (original, before) and source_rows(D) == (frozen, frozen_before),
         "OWN3 drift after output")
    need(historical_rows() == (history, history_before), "Old failed OWN3 drift after output")
    need(runtime_core() == runtime and read_ro(Path(snapshot["path"]))[0] == snapshot and
         read_ro(Path(own["path"]))[0] == own, "Runtime/owned output drift")
    print(json.dumps(dict(status=CAPTURE_STATUS, capture=own, request=rr,
                         source_files=frozen, source_snapshot=snapshot, targets=targets,
                         historical_failed_v1_sources=history,
                         original_inventory_RAW_descriptor=dict(
                             path=opaque_proof["original_identity"]["logical_path"],
                             bytes=opaque_proof["original_identity"]["bytes_as_scalar"],
                             sha256=opaque_proof["original_identity"]["sha256_as_scalar"])), ensure_ascii=False))

def phase1_terminal(capture, c, snapshot, frozen, frozen_meta):
    # Exact saved Root terminal control; never query the historical producer.
    jid = c["actual_CPU_job_id"]
    path = S / "submissions" / ("final_source_plan_pin_capture_" + jid +
                               "_actual_terminal_metadata_seal") / "receipt.json"
    receipt, data, metadata = text_ro(path)
    seal = strict_json(data)
    need(seal["schema"] == "final-source-plan-pin-capture-actual-terminal-metadata-only.v1" and
         seal["status"] == "ACTUAL_FINITE_PIN_CAPTURE_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE" and
         seal["metadata_only"] is True and seal["actual_job_id"] == jid,
         "Exact actual phase1 terminal seal contract")
    need(seal["actual_capture_CPU_stdout_descriptor"] == capture and
         seal["source_snapshot"] == snapshot and seal["request"] == c["request"] and
         seal["source_files"] == frozen and seal["source_metadata"] == frozen_meta and
         seal["request_metadata"] == c["request_metadata_after"] and
         seal["all_current_source_and_request_metadata_exactint_readback_PASS"] is True,
         "Actual stdout capture/source/snapshot/request terminal binding")
    need(type(seal["source_metadata"]) is list and len(seal["source_metadata"]) == 3,
         "Complete saved terminal source metadata")
    for row in seal["source_metadata"]:
        saved_metadata_shape(row)
    saved_metadata_shape(seal["request_metadata"])
    need(seal["owned_CPU_GPU0_basis"] == c["allocation"], "Actual CPU1/GPU0 phase1 guard basis")
    t = seal["actual_terminal"]
    expected_argv = ["sacct", "-X", "-n", "-P", "-j", jid,
        "--format=JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES"]
    need(t["argv"] == expected_argv and type(t["returncode"]) is int and t["returncode"] == 0 and
         t["stderr"] == "" and t["environment"]["TZ"] == "UTC" and
         t["environment"]["SLURM_TIME_FORMAT"] == "standard", "Saved independent terminal query exact")
    need(type(t["stdout"]) is str and t["stdout"].endswith("\n") and
         len(t["stdout"].splitlines()) == 1, "Single saved terminal allocation row")
    fields = t["stdout"].splitlines()[0].split("|")
    need(len(fields) == 9 and fields[:7] == [jid, JOB_NAME, "u21111210118", "u21111210118",
         "organ", "COMPLETED", "0:0"] and re.fullmatch("[0-9]+", fields[7]),
         "Actual phase1 COMPLETE0:0/named-owner-account-organ terminal")
    tres(fields[8])  # Independent CPU1/GPU namespace validation; GPU0 also bound above.
    return receipt, metadata

def qualified_capture(args):
    need(re.fullmatch("[0-9a-f]{64}", args.capture_sha256), "Actual capture own SHA required")
    cp = lexical(args.capture)
    match = re.fullmatch(re.escape(str(S / "runs")) +
                         r"/final_source_plan_pin_capture_([1-9][0-9]*)/capture\.json", str(cp))
    need(match is not None, "Exact actual phase1 capture namespace")
    cr, data, cm = text_ro(cp)
    need(cr["sha256"] == args.capture_sha256, "Actual phase1 capture byte identity")
    c = strict_json(data)
    need(c["schema"] == "final-source-plan-pin-capture.v1" and c["status"] == CAPTURE_STATUS and
         c["actual_CPU_job_id"] == match.group(1) and D == snapshot_name(match.group(1)),
         "Execute the phase1-qualified sealed source only")
    need(c["allocation"]["job_id"] == c["actual_CPU_job_id"] and
         type(c["allocation"]["allocated_CPUs"]) is int and c["allocation"]["allocated_CPUs"] == 1 and
         type(c["allocation"]["allocated_GPUs"]) is int and c["allocation"]["allocated_GPUs"] == 0,
         "Saved phase1 CPU-only allocation")
    for k in ("original_and_frozen_sources_byte_identical", "whole3_source_prepost_PASS",
              "request_and_target_bytes_and_metadata_prepost_PASS", "compiled_owned_Python",
              "bash_syntax_PASS", "conditional_runtime_prepost_PASS"):
        need(c[k] is True, "Phase1 qualification flag: " + k)
    need(c["metadata_only"] is True and c["scientific_acceptance"] is False and
         c["source_audit_or_stage_performed"] is False and c["receipt_children_opened_hashed_or_statted"] is False,
         "Saved finite metadata-only route")
    need(c["owned_source_count"] == 3 and type(c["owned_source_count"]) is int and
         c["fixed_literal_target_whitelist"] == [list(x) for x in FIXED_TARGETS],
         "Saved whole OWN3/finite target universe")
    need(type(c["exact_target_count"]) is int and c["exact_target_count"] == len(FIXED_TARGETS) and
         type(c["targets"]) is list and len(c["targets"]) == len(FIXED_TARGETS),
         "Saved whole finite target denominator")
    for target, (path, kind, size) in zip(c["targets"], FIXED_TARGETS):
        need(type(target) is dict and target["kind"] == kind, "Saved target kind")
        metadata_shape(dict(target["metadata"], kind=kind))
        if Path(path) == ORIGINAL_INVENTORY:
            need(set(target) == {"kind", "metadata", "historical_original_json_identity"},
                 "Original history is scalar-only, never an operative JSON receipt")
            identity = target["historical_original_json_identity"]
            need(type(identity) is dict and set(identity) ==
                 {"classification", "logical_path", "bytes_as_scalar", "sha256_as_scalar"} and
                 identity["classification"] == "RAW_HISTORY_JSON_BYTE_IDENTITY_NOT_OPERATIVE_SEED",
                 "Exact typed original history identity")
            receipt_shape(dict(path=identity["logical_path"], bytes=identity["bytes_as_scalar"],
                               sha256=identity["sha256_as_scalar"]))
            need(identity["logical_path"] == path and identity["bytes_as_scalar"] == size,
                 "Saved original historical byte identity")
        else:
            need(set(target) == {"kind", "receipt", "metadata"}, "Saved target observation shape")
            receipt_shape(target["receipt"])
            need(target["receipt"]["path"] == path and target["receipt"]["bytes"] == size,
                 "Saved receipt literal identity/bytes")
        need(target["metadata"]["path"] == path and target["metadata"]["bytes"] == size,
             "Saved target literal metadata/bytes")
    proof = c["opaque_history_byte_identity"]
    observed = {t["metadata"]["path"]: t for t in c["targets"]}
    need(c["original_and_opaque_history_bytes_and_metadata_prepost_PASS"] is True and
         proof["original_identity"] == observed[str(ORIGINAL_INVENTORY)]["historical_original_json_identity"] and
         proof["opaque_text_receipt"] == observed[str(OPAQUE_INVENTORY)]["receipt"] and
         proof["original_metadata"] == observed[str(ORIGINAL_INVENTORY)]["metadata"] and
         proof["opaque_metadata"] == observed[str(OPAQUE_INVENTORY)]["metadata"] and
         proof["original_identity"]["bytes_as_scalar"] == proof["opaque_text_receipt"]["bytes"] and
         proof["original_identity"]["sha256_as_scalar"] == proof["opaque_text_receipt"]["sha256"] and
         proof["exact_raw_bytes_equal"] is True and proof["sha256_and_size_equal"] is True and
         proof["original_JSON_parsed"] is False and proof["original_JSON_is_operative_seed"] is False and
         proof["new_parent_permission_granted"] is False,
         "Actual saved raw original/opaque history qualification")
    receipt_shape(c["request"])
    need(c["request"]["path"] == str(REQUEST) and
         c["request_metadata_before"] == c["request_metadata_after"],
         "Saved exact request metadata binding")
    for key in ("original_metadata_before", "original_metadata_after",
                "frozen_metadata_before", "frozen_metadata_after"):
        need(type(c[key]) is list and len(c[key]) == 3, "Saved complete OWN3 metadata")
        for row in c[key]:
            saved_metadata_shape(row)
    saved_metadata_shape(c["request_metadata_before"])
    saved_metadata_shape(c["request_metadata_after"])
    frozen, frozen_meta = source_rows(D)
    need(frozen == c["source_files"] and frozen_meta == c["frozen_metadata_after"],
         "Actual executing OWN3 differs from qualified phase1")
    need(c["original_metadata_before"] == c["original_metadata_after"] and
         c["frozen_metadata_before"] == c["frozen_metadata_after"] and
         len(c["original_executing_sources"]) == 3 and
         all((x["bytes"], x["sha256"]) == (y["bytes"], y["sha256"])
             for x, y in zip(c["original_executing_sources"], frozen)),
         "Original/frozen source identities are not closed")
    sr = c["source_snapshot"]; receipt_shape(sr)
    need(Path(sr["path"]) == cp.parent / "source_snapshot.json", "Exact phase1 source snapshot")
    actual_sr, source_data, sm = text_ro(Path(sr["path"]))
    need(actual_sr == sr, "Phase1 snapshot byte identity")
    snapshot = strict_json(source_data)
    need(snapshot["schema"] == "final-source-plan-pin-source-snapshot.v1" and
         snapshot["frozen_source_files"] == frozen and
         snapshot["original_executing_sources"] == c["original_executing_sources"] and
         snapshot["allocation"] == c["allocation"] and snapshot["compile_owned_Python"] is True and
         type(snapshot["bash_syntax"]["returncode"]) is int and snapshot["bash_syntax"]["returncode"] == 0 and
         snapshot["bash_syntax"]["argv"] == ["bash", "-n", str(D / "capture_cpu.sbatch")] and
         snapshot["bash_syntax"]["stdout"] == "" and snapshot["bash_syntax"]["stderr"] == "" and
         snapshot["original_metadata_before"] == c["original_metadata_before"] and
         snapshot["frozen_metadata_before"] == frozen_meta,
         "Whole source qualification snapshot mismatch")
    need(c["historical_source_prepost_PASS"] is True and
         c["historical_sources_hash_only_no_import_compile_or_execution"] is True and
         c["historical_metadata_before"] == c["historical_metadata_after"] and
         type(c["historical_failed_v1_sources"]) is list and len(c["historical_failed_v1_sources"]) == 3 and
         type(c["historical_metadata_before"]) is list and len(c["historical_metadata_before"]) == 3 and
         type(c["historical_metadata_after"]) is list and len(c["historical_metadata_after"]) == 3 and
         snapshot["historical_failed_v1_sources"] == c["historical_failed_v1_sources"] and
         snapshot["historical_metadata_before"] == c["historical_metadata_before"] and
         snapshot["historical_sources_hash_only_no_import_compile_or_execution"] is True,
         "Saved old failed OWN3 hash-only qualification")
    for receipt, meta, name, size in zip(c["historical_failed_v1_sources"],
            c["historical_metadata_after"], FILES, HISTORICAL_BYTES):
        receipt_shape(receipt); saved_metadata_shape(meta)
        need(receipt["path"] == str(HISTORICAL_P / name) and receipt["bytes"] == size and
             meta["path"] == receipt["path"] and meta["bytes"] == size,
             "Finite old failed OWN3 source identity")
    tr, tm = phase1_terminal(cr, c, sr, frozen, frozen_meta)
    return cr, c, cm, sr, sm, frozen, frozen_meta, tr, tm

def plan(args, allocation):
    need(Path(__file__).absolute() == D / "capture.py" and D != P,
         "Phase2 may only execute qualified frozen entry; no pending bootstrap/copy")
    cr, c, cm, sr, sm, frozen, frozen_meta, tr, tm = qualified_capture(args)
    runtime = runtime_core()
    need(runtime == c["conditional_core_runtime"], "Qualified core runtime changed")
    need(args.plan == str(PLAN), "Only exact new plan control path")
    pr, pdata, pm = text_ro(PLAN)
    pobj = strict_json(pdata)
    need(type(pobj) is dict and type(pobj.get("schema")) is str and pobj["schema"],
         "Readonly new JSON plan control; correctness remains future actual source audit")
    out = owned_output("plan", allocation["job_id"])
    result = dict(schema="final-source-plan-own-descriptor.v1", status=PLAN_STATUS,
        actual_CPU_job_id=allocation["job_id"], allocation=allocation,
        phase1_capture=cr, phase1_source_snapshot=sr, phase1_terminal_seal=tr, plan=pr,
        owned_source_count=3, owned_executable_source_count=2,
        plan_schema_scalar=pobj["schema"], plan_metadata_before=pm, plan_metadata_after=pm,
        source_files=frozen, frozen_metadata_before=frozen_meta, frozen_metadata_after=frozen_meta,
        same_phase1_frozen_source_executed=True, qualified_phase1_compile_and_bash_preserved=True,
        phase1_saved_CPU_job_id=c["actual_CPU_job_id"],
        conditional_core_runtime=runtime, conditional_runtime_prepost_PASS=True,
        source_and_plan_and_controls_prepost_PASS=True,
        phase2_receipt_must_not_be_own_plan_prerequisite=True, **flags())
    need(source_rows(D) == (frozen, frozen_meta) and text_ro(PLAN) == (pr, pdata, pm),
         "Phase2 source/plan drift before output")
    need(text_ro(Path(cr["path"]))[0::2] == (cr, cm) and
         text_ro(Path(sr["path"]))[0::2] == (sr, sm) and
         text_ro(Path(tr["path"]))[0::2] == (tr, tm) and runtime_core() == runtime,
         "Phase1 control/runtime drift before output")
    own = write_ro(out, "plan_descriptor.json", result)
    need(source_rows(D) == (frozen, frozen_meta) and text_ro(PLAN) == (pr, pdata, pm),
         "Phase2 source/plan drift after output")
    need(text_ro(Path(cr["path"]))[0::2] == (cr, cm) and
         text_ro(Path(sr["path"]))[0::2] == (sr, sm) and
         text_ro(Path(tr["path"]))[0::2] == (tr, tm) and runtime_core() == runtime and
         read_ro(Path(own["path"]))[0] == own, "Control/runtime/output drift after output")
    print(json.dumps(dict(status=PLAN_STATUS, plan=pr, plan_descriptor=own,
                         phase1_capture=cr, phase1_terminal_seal=tr, source_files=frozen), ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    pc = sub.add_parser("capture"); pc.add_argument("--request", required=True)
    pp = sub.add_parser("plan"); pp.add_argument("--plan", required=True)
    pp.add_argument("--capture", required=True); pp.add_argument("--capture-sha256", required=True)
    args = parser.parse_args()
    allocation = cpu()  # Before hashing, project imports, runtime hashing, compile or output creation.
    if args.mode == "plan":
        plan(args, allocation)
        return
    need(D == P and Path(__file__).absolute() == P / "capture.py", "Exact reviewed original OWN3")
    need(args.request == str(REQUEST), "Only exact capture request")
    runtime = runtime_core()
    original, original_before = source_rows(P)
    history, history_before = historical_rows()
    fd = ancestry(snapshot_name(allocation["job_id"]))
    need(not fd.parent.exists() and not fd.exists(), "Unique absent frozen OWN3 namespace")
    fd.parent.mkdir(exist_ok=False); fd.mkdir(exist_ok=False)
    for name, expected in zip(FILES, original):
        r, data, meta = read_ro(P / name)
        need(r == expected and meta == original_before[FILES.index(name)], "Original copy drift")
        with (fd / name).open("xb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno()); os.fchmod(stream.fileno(), 0o444)
    fd.chmod(0o555); fd.parent.chmod(0o555)
    frozen, frozen_before = source_rows(fd)
    need(all((x["bytes"], x["sha256"]) == (y["bytes"], y["sha256"])
             for x,y in zip(original,frozen)), "Whole OWN3 frozen bytes differ")
    for row in frozen:
        if Path(row["path"]).suffix == ".py":
            compile(read_ro(Path(row["path"]))[1], row["path"], "exec", dont_inherit=True)
    proc = subprocess.run(["bash", "-n", str(fd / "capture_cpu.sbatch")], capture_output=True, text=True)
    need(proc.returncode == 0, "Owned launcher Bash syntax")
    syntax = dict(argv=proc.args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    spec = importlib.util.spec_from_file_location("sealed_final_source_pin_" + allocation["job_id"], fd / "capture.py")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    need(Path(module.__file__).absolute() == fd / "capture.py", "Actual frozen module execution identity")
    module.capture(args, allocation, original, original_before, frozen, frozen_before, runtime, syntax, history, history_before)

if __name__ == "__main__":
    main()
