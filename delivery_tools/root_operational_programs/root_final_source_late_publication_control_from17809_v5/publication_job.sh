#!/bin/bash
set -euo pipefail
export PS1=${PS1-}
export CUDA_VISIBLE_DEVICES=''
export JAX_PLATFORMS=cpu
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/final_source_late_publication_v5_${SLURM_JOB_ID}
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'PY'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
# UNBOUND DISTINCT V5 OPERATIONAL SOURCE PROPOSAL: old fixed90 unchanged; one current-only Mapper-directory supplement and exactly four additional initial Source declarations require actual qualified controls.
SPEC = json.loads("{\"Common_original_metadata\":{\"bytes\":58825,\"ctime_ns\":1791695459000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115543165691265,\"mode\":33204,\"mtime_ns\":1791695459000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"uid\":6263900},\"conditional_core_metadata\":[{\"bytes\":10,\"ctime_ns\":1790940371000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115618512131424,\"mode\":41471,\"mtime_ns\":1790940371000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python\",\"uid\":6263900},{\"bytes\":25916456,\"ctime_ns\":1790940383000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115618512129393,\"mode\":33277,\"mtime_ns\":1790940364000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\",\"uid\":6263900}],\"existing_authority_controls\":[{\"native\":{\"bytes\":9390576,\"ctime_ns\":1792189199000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027394,\"mode\":33060,\"mtime_ns\":1792189199000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix7_software_execution_control_17811/execution_control.json\",\"uid\":6263900},\"receipt\":{\"bytes\":9390576,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix7_software_execution_control_17811/execution_control.json\",\"sha256\":\"28fac1f3564e0c5a6167faab9d2a4122366a1dbdd536b0d00d034c0426962cd3\"}},{\"native\":{\"bytes\":9625954,\"ctime_ns\":1792188530000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094795,\"mode\":33060,\"mtime_ns\":1792188530000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix7_source_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"receipt\":{\"bytes\":9625954,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix7_source_metadata_readonly_seal/receipt.json\",\"sha256\":\"952965766e101694d70bc71104c9ac07e127c98266b3451ddbf3cde1c5567aa5\"}},{\"native\":{\"bytes\":10871344,\"ctime_ns\":1792180384000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094681,\"mode\":33060,\"mtime_ns\":1792180384000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_stage17809_actual_terminal_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"receipt\":{\"bytes\":10871344,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_stage17809_actual_terminal_metadata_readonly_seal/receipt.json\",\"sha256\":\"f8cc21295c74bb65cd9c111984f7c56e5e1673d3387b34f5d9b527d0ab48f3d3\"}},{\"native\":{\"bytes\":32138,\"ctime_ns\":1792091207000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643493424923,\"mode\":33060,\"mtime_ns\":1792091207000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_wrapper_shell_byte_preservation_16998/capture.json\",\"uid\":6263900},\"receipt\":{\"bytes\":32138,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_wrapper_shell_byte_preservation_16998/capture.json\",\"sha256\":\"a665124984b928dbf7525d2d90059ed6dccccdaa2e80605ddc2f789ba4cf6325\"}},{\"native\":{\"bytes\":19249,\"ctime_ns\":1792174771000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006591,\"mode\":33060,\"mtime_ns\":1792174771000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/acceptance.json\",\"uid\":6263900},\"receipt\":{\"bytes\":19249,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/acceptance.json\",\"sha256\":\"55276b4b719d39de40fdb42a52d92d43d82d226b4496d78aab05301a849e92d2\"}},{\"native\":{\"bytes\":16062,\"ctime_ns\":1792174813000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006593,\"mode\":33060,\"mtime_ns\":1792174813000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/context_adapter_acceptance.json\",\"uid\":6263900},\"receipt\":{\"bytes\":16062,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/context_adapter_acceptance.json\",\"sha256\":\"ec6faaf0a6de0d00d3ae5c9c8f3f7b4f86ca3ee3a0334bb7eed1f4d2ea16ff0d\"}},{\"native\":{\"bytes\":1823791,\"ctime_ns\":1792174760000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006590,\"mode\":33060,\"mtime_ns\":1792174760000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_inclusion_final.json\",\"uid\":6263900},\"receipt\":{\"bytes\":1823791,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_inclusion_final.json\",\"sha256\":\"72282c88ae0483c5f42a1050e900eb2b015de246b589e414922d81ef4d35018d\"}},{\"native\":{\"bytes\":80706997,\"ctime_ns\":1792174754000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006589,\"mode\":33060,\"mtime_ns\":1792174754000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_receipt_closure_final.json\",\"uid\":6263900},\"receipt\":{\"bytes\":80706997,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_receipt_closure_final.json\",\"sha256\":\"0500dc61c631821eb8b8cc0746abada16409763e9a32aed25f634bd779de8456\"}},{\"native\":{\"bytes\":229750,\"ctime_ns\":1792179288000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980008252,\"mode\":33060,\"mtime_ns\":1792179288000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_stage_17809/acceptance.json\",\"uid\":6263900},\"receipt\":{\"bytes\":229750,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_stage_17809/acceptance.json\",\"sha256\":\"351c2b23b1681fc36023e043886e3e63e9625d457ac3c8cdbbeea9ae2dfc046d\"}}],\"failed_publisher_terminal_directory_metadata\":{\"bytes\":4096,\"ctime_ns\":1792202223000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094859,\"mode\":16749,\"mtime_ns\":1792202223000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_late_publication17812_actual_failed_terminal_metadata_readonly_seal\",\"uid\":6263900},\"failed_publisher_terminal_metadata\":{\"bytes\":9822126,\"ctime_ns\":1792202223000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094862,\"mode\":33060,\"mtime_ns\":1792202223000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_late_publication17812_actual_failed_terminal_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"human_readonly_directory\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_human_metadata_readonly_seal\",\"human_readonly_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_human_metadata_readonly_seal/receipt.json\",\"human_readonly_schema\":\"root-finite-late-source-publisher-v5-human-metadata-readonly-seal.v1\",\"human_static_PASS_field\":\"Root_and_two_whole_STATIC_PASS\",\"primary_claim_directory\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim\",\"primary_claim_files\":[\"publication_job.sh\",\"request.json\",\"in_progress.json\",\"submit.json\",\"sbatch.stdout\",\"sbatch.stderr\"],\"primary_raw_stderr_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim/sbatch.stderr\",\"primary_raw_stdout_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim/sbatch.stdout\",\"primary_request_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim/request.json\",\"primary_request_schema\":\"root-finite-late-source-publisher-primary-request.v1\",\"primary_submit_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim/submit.json\",\"primary_submit_schema\":\"root-finite-late-source-publisher-primary-submit.v1\",\"producer_metadata\":{\"acceptance\":{\"bytes\":19249,\"ctime_ns\":1792174771000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006591,\"mode\":33060,\"mtime_ns\":1792174771000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/acceptance.json\",\"uid\":6263900},\"context_adapter_acceptance\":{\"bytes\":16062,\"ctime_ns\":1792174813000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006593,\"mode\":33060,\"mtime_ns\":1792174813000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/context_adapter_acceptance.json\",\"uid\":6263900},\"source_closure\":{\"bytes\":80706997,\"ctime_ns\":1792174754000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006589,\"mode\":33060,\"mtime_ns\":1792174754000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_receipt_closure_final.json\",\"uid\":6263900},\"source_inclusion\":{\"bytes\":1823791,\"ctime_ns\":1792174760000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980006590,\"mode\":33060,\"mtime_ns\":1792174760000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_inclusion_final.json\",\"uid\":6263900}},\"producer_receipts\":{\"acceptance\":{\"bytes\":19249,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/acceptance.json\",\"sha256\":\"55276b4b719d39de40fdb42a52d92d43d82d226b4496d78aab05301a849e92d2\"},\"context_adapter_acceptance\":{\"bytes\":16062,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/context_adapter_acceptance.json\",\"sha256\":\"ec6faaf0a6de0d00d3ae5c9c8f3f7b4f86ca3ee3a0334bb7eed1f4d2ea16ff0d\"},\"source_closure\":{\"bytes\":80706997,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_receipt_closure_final.json\",\"sha256\":\"0500dc61c631821eb8b8cc0746abada16409763e9a32aed25f634bd779de8456\"},\"source_inclusion\":{\"bytes\":1823791,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_production_17808/source_inclusion_final.json\",\"sha256\":\"72282c88ae0483c5f42a1050e900eb2b015de246b589e414922d81ef4d35018d\"}},\"proof_namespace\":\"root_final_source_late_publication_v5_execution_control_\",\"protected_directory_children_delta\":{\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1\":[\"HANDOFF.md\",\"composer_bootstrap.py\",\"composer_context_api.py\",\"composer_contracts_cpu.sbatch\",\"composer_cpu.sbatch\",\"final_delivery_composer.py\",\"finite_source_delivery_context.py\",\"github_export_context.py\",\"qualified_source_semantics.py\",\"relative_archive_restore.py\",\"restored_index_scope.py\",\"test_final_delivery_composer.py\",\"test_finite_source_delivery_context.py\",\"test_github_export_context.py\",\"test_restored_index_scope.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1\":[\"HANDOFF.md\",\"composer_bootstrap.py\",\"composer_context_api.py\",\"composer_contracts_cpu.sbatch\",\"composer_cpu.sbatch\",\"final_delivery_composer.py\",\"finite_source_delivery_context.py\",\"github_export_context.py\",\"qualified_source_semantics.py\",\"relative_archive_restore.py\",\"restored_index_scope.py\",\"test_final_delivery_composer.py\",\"test_finite_source_delivery_context.py\",\"test_github_export_context.py\",\"test_restored_index_scope.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2\":[\"HANDOFF.md\",\"composer_bootstrap.py\",\"composer_context_api.py\",\"composer_contracts_cpu.sbatch\",\"composer_cpu.sbatch\",\"final_delivery_composer.py\",\"finite_source_delivery_context.py\",\"github_export_context.py\",\"qualified_source_semantics.py\",\"relative_archive_restore.py\",\"restored_index_scope.py\",\"test_final_delivery_composer.py\",\"test_finite_source_delivery_context.py\",\"test_github_export_context.py\",\"test_restored_index_scope.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4\":[\"HANDOFF.md\",\"composer_bootstrap.py\",\"composer_context_api.py\",\"composer_contracts_cpu.sbatch\",\"composer_cpu.sbatch\",\"final_delivery_composer.py\",\"finite_source_delivery_context.py\",\"github_export_context.py\",\"qualified_source_semantics.py\",\"relative_archive_restore.py\",\"restored_index_scope.py\",\"test_final_delivery_composer.py\",\"test_finite_source_delivery_context.py\",\"test_github_export_context.py\",\"test_restored_index_scope.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5\":[\"HANDOFF.md\",\"composer_bootstrap.py\",\"composer_context_api.py\",\"composer_contracts_cpu.sbatch\",\"composer_cpu.sbatch\",\"final_delivery_composer.py\",\"finite_source_delivery_context.py\",\"github_export_context.py\",\"qualified_source_semantics.py\",\"relative_archive_restore.py\",\"restored_index_scope.py\",\"test_final_delivery_composer.py\",\"test_finite_source_delivery_context.py\",\"test_github_export_context.py\",\"test_restored_index_scope.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v1\":[\"software_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v2\":[\"software_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v1\":[\"HANDOFF.md\",\"source_index_compatibility_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v2\":[\"HANDOFF.md\",\"source_index_compatibility_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v1\":[\"HANDOFF.md\",\"late_publication_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v2\":[\"HANDOFF.md\",\"late_publication_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v3\":[\"HANDOFF.md\",\"late_publication_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v4\":[\"HANDOFF.md\",\"late_publication_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v5\":[\"HANDOFF.md\",\"late_publication_control.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_late_publication17812_actual_failed_terminal_metadata_readonly_seal\":[\"fresh_sacct.stderr\",\"fresh_sacct.stdout\",\"receipt.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_index_compatibility_v2_human_metadata_readonly_seal\":[\"receipt.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim\":[\"in_progress.json\",\"publication_job.sh\",\"request.json\",\"sbatch.stderr\",\"sbatch.stdout\",\"submit.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812\":[\"attempt_001.stderr\",\"attempt_001.stdout\",\"current_scontrol.stderr\",\"current_scontrol.stdout\",\"readiness.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_human_metadata_readonly_seal\":[\"receipt.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_source_metadata_readonly_seal\":[\"receipt.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_unsubmitted_request_history_20261017_R13_physical_route_extras_v1\":[\"receipt.json\",\"unsubmitted_request.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_source_metadata_readonly_seal\":[\"receipt.json\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_publisher_v4_compat17811v2_pair_source_metadata_readonly_seal\":[\"receipt.json\"]},\"protected_metadata_delta\":[{\"bytes\":202500,\"ctime_ns\":1792199364000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094838,\"mode\":33060,\"mtime_ns\":1792198719000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_SOURCE_LATE_PUBLICATION_FROM17809_REV4_20261016.md\",\"uid\":6263900},{\"bytes\":161,\"ctime_ns\":1792202223000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027396,\"mode\":33060,\"mtime_ns\":1792201498000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_source_late_publication_v4_17812.err\",\"uid\":6263900},{\"bytes\":382,\"ctime_ns\":1792202223000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027395,\"mode\":33060,\"mtime_ns\":1792201085000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_source_late_publication_v4_17812.out\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094602,\"mode\":16893,\"mtime_ns\":1792176346000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094624,\"mode\":16893,\"mtime_ns\":1792177347000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094660,\"mode\":16893,\"mtime_ns\":1792179733000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094702,\"mode\":16893,\"mtime_ns\":1792182949000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094720,\"mode\":16893,\"mtime_ns\":1792184435000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792181846000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094700,\"mode\":16893,\"mtime_ns\":1792181846000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v1\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792182989000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094718,\"mode\":16893,\"mtime_ns\":1792182989000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v2\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792193962000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094819,\"mode\":16893,\"mtime_ns\":1792193962000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v1\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792195883000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094825,\"mode\":16749,\"mtime_ns\":1792195494000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v2\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792189197000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094806,\"mode\":16893,\"mtime_ns\":1792189197000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v1\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792191779000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094813,\"mode\":16893,\"mtime_ns\":1792191779000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v2\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792193201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094816,\"mode\":16893,\"mtime_ns\":1792193201000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v3\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792195883000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094822,\"mode\":16749,\"mtime_ns\":1792195072000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v4\",\"uid\":6263900},{\"bytes\":105063,\"ctime_ns\":1792195883000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094823,\"mode\":33060,\"mtime_ns\":1792195072000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v4/late_publication_control.py\",\"uid\":6263900},{\"bytes\":14106,\"ctime_ns\":1792204697000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094881,\"mode\":33060,\"mtime_ns\":1792204237000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v5/HANDOFF.md\",\"uid\":6263900},{\"bytes\":0,\"ctime_ns\":1792202223000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094861,\"mode\":33060,\"mtime_ns\":1792202223000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_late_publication17812_actual_failed_terminal_metadata_readonly_seal/fresh_sacct.stderr\",\"uid\":6263900},{\"bytes\":125,\"ctime_ns\":1792202223000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094860,\"mode\":33060,\"mtime_ns\":1792202223000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_late_publication17812_actual_failed_terminal_metadata_readonly_seal/fresh_sacct.stdout\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792197564000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094833,\"mode\":16749,\"mtime_ns\":1792197564000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_index_compatibility_v2_human_metadata_readonly_seal\",\"uid\":6263900},{\"bytes\":9640416,\"ctime_ns\":1792197564000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094834,\"mode\":33060,\"mtime_ns\":1792197564000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_index_compatibility_v2_human_metadata_readonly_seal/receipt.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792201054000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094837,\"mode\":16749,\"mtime_ns\":1792201054000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim\",\"uid\":6263900},{\"bytes\":2579,\"ctime_ns\":1792201054000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094846,\"mode\":33060,\"mtime_ns\":1792201054000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim/in_progress.json\",\"uid\":6263900},{\"bytes\":201853,\"ctime_ns\":1792199364000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094839,\"mode\":33060,\"mtime_ns\":1792198719000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim/publication_job.sh\",\"uid\":6263900},{\"bytes\":2899185,\"ctime_ns\":1792200753000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094844,\"mode\":33060,\"mtime_ns\":1792200753000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim/request.json\",\"uid\":6263900},{\"bytes\":0,\"ctime_ns\":1792201054000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094848,\"mode\":33060,\"mtime_ns\":1792201054000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim/sbatch.stderr\",\"uid\":6263900},{\"bytes\":6,\"ctime_ns\":1792201054000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094847,\"mode\":33060,\"mtime_ns\":1792201054000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim/sbatch.stdout\",\"uid\":6263900},{\"bytes\":1548,\"ctime_ns\":1792201054000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094849,\"mode\":33060,\"mtime_ns\":1792201054000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v4_primary_claim/submit.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792201085000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027397,\"mode\":16749,\"mtime_ns\":1792201085000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812\",\"uid\":6263900},{\"bytes\":0,\"ctime_ns\":1792201085000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027401,\"mode\":33060,\"mtime_ns\":1792201085000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812/attempt_001.stderr\",\"uid\":6263900},{\"bytes\":69,\"ctime_ns\":1792201085000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027400,\"mode\":33060,\"mtime_ns\":1792201085000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812/attempt_001.stdout\",\"uid\":6263900},{\"bytes\":0,\"ctime_ns\":1792201085000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027399,\"mode\":33060,\"mtime_ns\":1792201085000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812/current_scontrol.stderr\",\"uid\":6263900},{\"bytes\":1563,\"ctime_ns\":1792201085000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027398,\"mode\":33060,\"mtime_ns\":1792201085000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812/current_scontrol.stdout\",\"uid\":6263900},{\"bytes\":3442,\"ctime_ns\":1792201085000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027402,\"mode\":33060,\"mtime_ns\":1792201085000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_current_readiness_17812/readiness.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792199365000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094840,\"mode\":16749,\"mtime_ns\":1792199365000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_human_metadata_readonly_seal\",\"uid\":6263900},{\"bytes\":9682370,\"ctime_ns\":1792199365000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094841,\"mode\":33060,\"mtime_ns\":1792199365000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_human_metadata_readonly_seal/receipt.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792197863000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094835,\"mode\":16749,\"mtime_ns\":1792197863000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_source_metadata_readonly_seal\",\"uid\":6263900},{\"bytes\":9669985,\"ctime_ns\":1792197863000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094836,\"mode\":33060,\"mtime_ns\":1792197863000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_source_metadata_readonly_seal/receipt.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792200754000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094843,\"mode\":16749,\"mtime_ns\":1792200754000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_unsubmitted_request_history_20261017_R13_physical_route_extras_v1\",\"uid\":6263900},{\"bytes\":9751601,\"ctime_ns\":1792200754000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094845,\"mode\":33060,\"mtime_ns\":1792200754000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_unsubmitted_request_history_20261017_R13_physical_route_extras_v1/receipt.json\",\"uid\":6263900},{\"bytes\":3950747,\"ctime_ns\":1792200750000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094842,\"mode\":33060,\"mtime_ns\":1792199631000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v4_unsubmitted_request_history_20261017_R13_physical_route_extras_v1/unsubmitted_request.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792204706000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094882,\"mode\":16749,\"mtime_ns\":1792204705000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_source_metadata_readonly_seal\",\"uid\":6263900},{\"bytes\":19012061,\"ctime_ns\":1792204706000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094883,\"mode\":33060,\"mtime_ns\":1792204706000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_source_metadata_readonly_seal/receipt.json\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792195884000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094828,\"mode\":16749,\"mtime_ns\":1792195884000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_publisher_v4_compat17811v2_pair_source_metadata_readonly_seal\",\"uid\":6263900},{\"bytes\":9692207,\"ctime_ns\":1792195884000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094829,\"mode\":33060,\"mtime_ns\":1792195884000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_publisher_v4_compat17811v2_pair_source_metadata_readonly_seal/receipt.json\",\"uid\":6263900}],\"publication_namespace\":\"final_source_late_publication_v5_\",\"publisher_HANDOFF_metadata\":{\"bytes\":14106,\"ctime_ns\":1792204697000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094881,\"mode\":33060,\"mtime_ns\":1792204237000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v5/HANDOFF.md\",\"uid\":6263900},\"publisher_first_pin_Source_metadata_original\":[{\"bytes\":51661,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094603,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":45040,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094604,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":5889,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094605,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_bootstrap.py\",\"uid\":6263900},{\"bytes\":1006,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094606,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_cpu.sbatch\",\"uid\":6263900},{\"bytes\":1088,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094607,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_contracts_cpu.sbatch\",\"uid\":6263900},{\"bytes\":42750,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094608,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/HANDOFF.md\",\"uid\":6263900},{\"bytes\":2368,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094609,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_context_api.py\",\"uid\":6263900},{\"bytes\":19161,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094610,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/relative_archive_restore.py\",\"uid\":6263900},{\"bytes\":42116,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094611,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/github_export_context.py\",\"uid\":6263900},{\"bytes\":27438,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094612,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_github_export_context.py\",\"uid\":6263900},{\"bytes\":35746,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094613,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/restored_index_scope.py\",\"uid\":6263900},{\"bytes\":39158,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094614,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_restored_index_scope.py\",\"uid\":6263900},{\"bytes\":57864,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094615,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":35858,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094616,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":344832,\"ctime_ns\":1792176346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094617,\"mode\":33204,\"mtime_ns\":1792176346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/qualified_source_semantics.py\",\"uid\":6263900},{\"bytes\":51661,\"ctime_ns\":1792177346000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094625,\"mode\":33204,\"mtime_ns\":1792177346000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":45040,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094626,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":5889,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094627,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_bootstrap.py\",\"uid\":6263900},{\"bytes\":1006,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094628,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_cpu.sbatch\",\"uid\":6263900},{\"bytes\":1093,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094629,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_contracts_cpu.sbatch\",\"uid\":6263900},{\"bytes\":43574,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094630,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/HANDOFF.md\",\"uid\":6263900},{\"bytes\":2368,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094631,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_context_api.py\",\"uid\":6263900},{\"bytes\":19161,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094632,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/relative_archive_restore.py\",\"uid\":6263900},{\"bytes\":42116,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094633,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/github_export_context.py\",\"uid\":6263900},{\"bytes\":27438,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094634,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_github_export_context.py\",\"uid\":6263900},{\"bytes\":35746,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094635,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/restored_index_scope.py\",\"uid\":6263900},{\"bytes\":39158,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094636,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_restored_index_scope.py\",\"uid\":6263900},{\"bytes\":58897,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094637,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":37067,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094638,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":344832,\"ctime_ns\":1792177347000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094639,\"mode\":33204,\"mtime_ns\":1792177347000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/qualified_source_semantics.py\",\"uid\":6263900},{\"bytes\":51864,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094661,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":45040,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094662,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":5889,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094663,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_bootstrap.py\",\"uid\":6263900},{\"bytes\":1006,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094664,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_cpu.sbatch\",\"uid\":6263900},{\"bytes\":1093,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094665,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_contracts_cpu.sbatch\",\"uid\":6263900},{\"bytes\":50253,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094666,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/HANDOFF.md\",\"uid\":6263900},{\"bytes\":2368,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094667,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_context_api.py\",\"uid\":6263900},{\"bytes\":19161,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094668,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/relative_archive_restore.py\",\"uid\":6263900},{\"bytes\":42116,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094669,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/github_export_context.py\",\"uid\":6263900},{\"bytes\":27438,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094670,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_github_export_context.py\",\"uid\":6263900},{\"bytes\":35746,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094671,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/restored_index_scope.py\",\"uid\":6263900},{\"bytes\":39158,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094672,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_restored_index_scope.py\",\"uid\":6263900},{\"bytes\":72529,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094673,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":55266,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094674,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":344832,\"ctime_ns\":1792179733000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094675,\"mode\":33204,\"mtime_ns\":1792179733000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/qualified_source_semantics.py\",\"uid\":6263900},{\"bytes\":47762,\"ctime_ns\":1792181846000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094701,\"mode\":33204,\"mtime_ns\":1792181846000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v1/software_control.py\",\"uid\":6263900},{\"bytes\":56497,\"ctime_ns\":1792182989000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094719,\"mode\":33204,\"mtime_ns\":1792182989000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v2/software_control.py\",\"uid\":6263900},{\"bytes\":52113,\"ctime_ns\":1792182982000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094703,\"mode\":33204,\"mtime_ns\":1792182982000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":45040,\"ctime_ns\":1792182948000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094704,\"mode\":33204,\"mtime_ns\":1792182948000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":6942,\"ctime_ns\":1792182982000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094705,\"mode\":33204,\"mtime_ns\":1792182982000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_bootstrap.py\",\"uid\":6263900},{\"bytes\":1014,\"ctime_ns\":1792182982000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094706,\"mode\":33204,\"mtime_ns\":1792182982000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_cpu.sbatch\",\"uid\":6263900},{\"bytes\":1101,\"ctime_ns\":1792182982000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094707,\"mode\":33204,\"mtime_ns\":1792182982000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_contracts_cpu.sbatch\",\"uid\":6263900},{\"bytes\":60230,\"ctime_ns\":1792183074000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094708,\"mode\":33204,\"mtime_ns\":1792183074000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/HANDOFF.md\",\"uid\":6263900},{\"bytes\":2368,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094709,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_context_api.py\",\"uid\":6263900},{\"bytes\":19161,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094710,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/relative_archive_restore.py\",\"uid\":6263900},{\"bytes\":42116,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094711,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/github_export_context.py\",\"uid\":6263900},{\"bytes\":27438,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094712,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_github_export_context.py\",\"uid\":6263900},{\"bytes\":35746,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094713,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/restored_index_scope.py\",\"uid\":6263900},{\"bytes\":39158,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094714,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_restored_index_scope.py\",\"uid\":6263900},{\"bytes\":111217,\"ctime_ns\":1792183383000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094715,\"mode\":33204,\"mtime_ns\":1792183383000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":73512,\"ctime_ns\":1792183387000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094716,\"mode\":33204,\"mtime_ns\":1792183387000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":344832,\"ctime_ns\":1792182949000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094717,\"mode\":33204,\"mtime_ns\":1792182949000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/qualified_source_semantics.py\",\"uid\":6263900},{\"bytes\":52113,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094721,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":45040,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094722,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":6942,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094723,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_bootstrap.py\",\"uid\":6263900},{\"bytes\":1014,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094724,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_cpu.sbatch\",\"uid\":6263900},{\"bytes\":1101,\"ctime_ns\":1792184528000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094725,\"mode\":33204,\"mtime_ns\":1792184528000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_contracts_cpu.sbatch\",\"uid\":6263900},{\"bytes\":62766,\"ctime_ns\":1792184527000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094726,\"mode\":33204,\"mtime_ns\":1792184527000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/HANDOFF.md\",\"uid\":6263900},{\"bytes\":2368,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094727,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_context_api.py\",\"uid\":6263900},{\"bytes\":19161,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094728,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/relative_archive_restore.py\",\"uid\":6263900},{\"bytes\":42116,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094729,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/github_export_context.py\",\"uid\":6263900},{\"bytes\":27438,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094730,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_github_export_context.py\",\"uid\":6263900},{\"bytes\":35746,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094731,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/restored_index_scope.py\",\"uid\":6263900},{\"bytes\":39158,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094732,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_restored_index_scope.py\",\"uid\":6263900},{\"bytes\":113752,\"ctime_ns\":1792184524000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094733,\"mode\":33204,\"mtime_ns\":1792184524000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":77218,\"ctime_ns\":1792184526000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094734,\"mode\":33204,\"mtime_ns\":1792184526000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":344832,\"ctime_ns\":1792184435000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094735,\"mode\":33204,\"mtime_ns\":1792184435000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/qualified_source_semantics.py\",\"uid\":6263900},{\"bytes\":77266,\"ctime_ns\":1792189197000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094807,\"mode\":33204,\"mtime_ns\":1792189197000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v1/late_publication_control.py\",\"uid\":6263900},{\"bytes\":8148,\"ctime_ns\":1792189197000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094808,\"mode\":33204,\"mtime_ns\":1792189197000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v1/HANDOFF.md\",\"uid\":6263900},{\"bytes\":89429,\"ctime_ns\":1792191779000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094814,\"mode\":33204,\"mtime_ns\":1792191779000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v2/late_publication_control.py\",\"uid\":6263900},{\"bytes\":13145,\"ctime_ns\":1792191779000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094815,\"mode\":33204,\"mtime_ns\":1792191779000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v2/HANDOFF.md\",\"uid\":6263900},{\"bytes\":104385,\"ctime_ns\":1792193201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094817,\"mode\":33204,\"mtime_ns\":1792193201000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v3/late_publication_control.py\",\"uid\":6263900},{\"bytes\":12820,\"ctime_ns\":1792193201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094818,\"mode\":33204,\"mtime_ns\":1792193201000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v3/HANDOFF.md\",\"uid\":6263900},{\"bytes\":11985,\"ctime_ns\":1792195883000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094824,\"mode\":33060,\"mtime_ns\":1792195072000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v4/HANDOFF.md\",\"uid\":6263900},{\"bytes\":50361,\"ctime_ns\":1792193962000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094820,\"mode\":33204,\"mtime_ns\":1792193962000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v1/source_index_compatibility_control.py\",\"uid\":6263900},{\"bytes\":13736,\"ctime_ns\":1792193962000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094821,\"mode\":33204,\"mtime_ns\":1792193962000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v1/HANDOFF.md\",\"uid\":6263900},{\"bytes\":61120,\"ctime_ns\":1792195883000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094826,\"mode\":33060,\"mtime_ns\":1792195494000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v2/source_index_compatibility_control.py\",\"uid\":6263900},{\"bytes\":16019,\"ctime_ns\":1792195883000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094827,\"mode\":33060,\"mtime_ns\":1792195494000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v2/HANDOFF.md\",\"uid\":6263900},{\"bytes\":105262,\"ctime_ns\":1792197564000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094831,\"mode\":33060,\"mtime_ns\":1792196770000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_SOURCE_INDEX_COMPATIBILITY_FROM17811_REV2_20261016.md\",\"uid\":6263900},{\"bytes\":98984,\"ctime_ns\":1792197564000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094832,\"mode\":33060,\"mtime_ns\":1792196770000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_index_compatibility_from17811_v2_primary_claim/compatibility_job.sh\",\"uid\":6263900}],\"publisher_job_name\":\"test9_final_source_late_publication_v5\",\"publisher_source_readonly_directory_metadata\":{\"bytes\":4096,\"ctime_ns\":1792204706000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094882,\"mode\":16749,\"mtime_ns\":1792204705000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_source_metadata_readonly_seal\",\"uid\":6263900},\"publisher_source_readonly_metadata\":{\"bytes\":19012061,\"ctime_ns\":1792204706000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094883,\"mode\":33060,\"mtime_ns\":1792204706000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_v5_source_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"publisher_source_readonly_schema\":\"root-finite-late-source-publisher-v5-source-metadata-readonly-seal.v1\",\"readiness_namespace\":\"root_final_source_late_publication_v5_readiness_\",\"schema\":\"root-finite-late-source-publisher-binding.v5\",\"self_human_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_SOURCE_LATE_PUBLICATION_FROM17809_REV5_20261017.md\",\"self_primary_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim/publication_job.sh\",\"self_proposal_directory\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v5\",\"self_proposal_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v5/late_publication_control.py\",\"shell_header\":\"#!/bin/bash\\nset -euo pipefail\\nexport PS1=${PS1-}\\nexport CUDA_VISIBLE_DEVICES=''\\nexport JAX_PLATFORMS=cpu\\nexport PYTHONNOUSERSITE=1\\nexport PYTHONDONTWRITEBYTECODE=1\\nexport OPENBLAS_NUM_THREADS=1\\nexport OMP_NUM_THREADS=1\\nexport MKL_NUM_THREADS=1\\nunset PYTHONPATH\\nexport TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/final_source_late_publication_v5_${SLURM_JOB_ID}\\nexec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'PY'\\n\",\"software_contracts_metadata\":{\"bytes\":22143,\"ctime_ns\":1792189194000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027392,\"mode\":33060,\"mtime_ns\":1792189194000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_composer_operational_provenance_contracts_17811/contracts.json\",\"uid\":6263900},\"software_contracts_receipt\":{\"bytes\":22143,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_composer_operational_provenance_contracts_17811/contracts.json\",\"sha256\":\"78d970e2f7d39745c8f528af04e10559b90603d4d469d1435e86dd0e41f0c87f\"},\"software_expected_test_count\":215,\"source44_metadata\":[{\"bytes\":52113,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017839,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":45040,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017840,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_final_delivery_composer.py\",\"uid\":6263900},{\"bytes\":6942,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017841,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_bootstrap.py\",\"uid\":6263900},{\"bytes\":1014,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017842,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_cpu.sbatch\",\"uid\":6263900},{\"bytes\":1101,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017843,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_contracts_cpu.sbatch\",\"uid\":6263900},{\"bytes\":66353,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017844,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/HANDOFF.md\",\"uid\":6263900},{\"bytes\":2368,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017845,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_context_api.py\",\"uid\":6263900},{\"bytes\":19161,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017846,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/relative_archive_restore.py\",\"uid\":6263900},{\"bytes\":42116,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017847,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/github_export_context.py\",\"uid\":6263900},{\"bytes\":27438,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017848,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_github_export_context.py\",\"uid\":6263900},{\"bytes\":35746,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017849,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/restored_index_scope.py\",\"uid\":6263900},{\"bytes\":39158,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017850,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_restored_index_scope.py\",\"uid\":6263900},{\"bytes\":114244,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017851,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":83421,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017852,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_finite_source_delivery_context.py\",\"uid\":6263900},{\"bytes\":344832,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017853,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/qualified_source_semantics.py\",\"uid\":6263900},{\"bytes\":21656,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214860,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_core.py\",\"uid\":6263900},{\"bytes\":21981,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214861,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_core_v2.py\",\"uid\":6263900},{\"bytes\":8774,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214862,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_graph_v2.py\",\"uid\":6263900},{\"bytes\":5048,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214869,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/provenance_aliases_v2.py\",\"uid\":6263900},{\"bytes\":3163,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214865,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/historical_scope_v2.py\",\"uid\":6263900},{\"bytes\":20444,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214868,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/native_resource_closure_v2.py\",\"uid\":6263900},{\"bytes\":4979,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214872,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/restore_resolver_v2.py\",\"uid\":6263900},{\"bytes\":3526,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214874,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/restore_verify_v2.py\",\"uid\":6263900},{\"bytes\":18822,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214859,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/common_review_independent_v2.py\",\"uid\":6263900},{\"bytes\":8723,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214876,\"mode\":33060,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/target_statistics_v2.py\",\"uid\":6263900},{\"bytes\":11733,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214863,\"mode\":33133,\"mtime_ns\":1791726702000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/github_export_verify.py\",\"uid\":6263900},{\"bytes\":17447,\"ctime_ns\":1791696752000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668200926,\"mode\":33060,\"mtime_ns\":1791696752000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/github_export_13086/github_source_export.py\",\"uid\":6263900},{\"bytes\":37640,\"ctime_ns\":1791696918000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668201813,\"mode\":33060,\"mtime_ns\":1791696918000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_independent.py\",\"uid\":6263900},{\"bytes\":3592,\"ctime_ns\":1791698201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668203541,\"mode\":33060,\"mtime_ns\":1791695462000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/control_msa_check.py\",\"uid\":6263900},{\"bytes\":45140,\"ctime_ns\":1791698201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668203561,\"mode\":33060,\"mtime_ns\":1791695462000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/vendor/ipsae.py\",\"uid\":6263900},{\"bytes\":21560,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017855,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/exact_relative_bbf_context.py\",\"uid\":6263900},{\"bytes\":14616,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017856,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_exact_relative_bbf_context.py\",\"uid\":6263900},{\"bytes\":11280,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017857,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/context_mapper_audit_cpu.py\",\"uid\":6263900},{\"bytes\":1172,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017858,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/context_mapper_cpu.sbatch\",\"uid\":6263900},{\"bytes\":11487,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017859,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/context_consumer.py\",\"uid\":6263900},{\"bytes\":4174,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017860,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/HANDOFF.md\",\"uid\":6263900},{\"bytes\":16392,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017861,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/historical_annotation_context.py\",\"uid\":6263900},{\"bytes\":19936,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017862,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_historical_annotation_context.py\",\"uid\":6263900},{\"bytes\":8858,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017863,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/recovered_five_context.py\",\"uid\":6263900},{\"bytes\":9440,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017864,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_recovered_five_context.py\",\"uid\":6263900},{\"bytes\":19215,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017865,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/archive_member_context.py\",\"uid\":6263900},{\"bytes\":16014,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017866,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_archive_member_context.py\",\"uid\":6263900},{\"bytes\":78635,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017867,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/finite_source_context.py\",\"uid\":6263900},{\"bytes\":35289,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017868,\"mode\":33060,\"mtime_ns\":1792189128000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_finite_source_context.py\",\"uid\":6263900}],\"source44_receipts\":[{\"bytes\":52113,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/final_delivery_composer.py\",\"sha256\":\"87f38c6c4b4ff9386c7b05f4dcc332b0cfa49660fd1f56d5ec504ffdc0e6f1a9\"},{\"bytes\":45040,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_final_delivery_composer.py\",\"sha256\":\"d80819d21470a7df787aa1803c81b43b2eaff7eb4d8d784af0a5f5281a0d3797\"},{\"bytes\":6942,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_bootstrap.py\",\"sha256\":\"7568acf87264631b157759caf13725d0da6e1151379664bdb3fc0b600e43d7a9\"},{\"bytes\":1014,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_cpu.sbatch\",\"sha256\":\"1b064d02270379b96a0abe8f80dc8075c1c83aa3252153b2b34af9213c03ae94\"},{\"bytes\":1101,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_contracts_cpu.sbatch\",\"sha256\":\"9442c11da57a1480210dc6fb9776096ea660a48dec6fcd9b9df2234d06a727b6\"},{\"bytes\":66353,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/HANDOFF.md\",\"sha256\":\"0553f7d3ea72364191c10f2208567be26320d998cae958ce6c8cfe3822eeffd9\"},{\"bytes\":2368,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/composer_context_api.py\",\"sha256\":\"65ba810594e545190fe57c0478675e252e9eea9d611a626288ea0fd262a2e7f0\"},{\"bytes\":19161,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/relative_archive_restore.py\",\"sha256\":\"0bcd456fd4a879f85b8654916f0eae5288ff02c33c1a72caee4240901280a7b3\"},{\"bytes\":42116,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/github_export_context.py\",\"sha256\":\"40d37654626910d2456e38f051bc2aaba6aebcabc79e4ff54348a359aa4a538f\"},{\"bytes\":27438,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_github_export_context.py\",\"sha256\":\"172cc5112e271ee012a9f429dd3bb597b19df56a9f773c20943cd811de83f587\"},{\"bytes\":35746,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/restored_index_scope.py\",\"sha256\":\"17b229ae2db5b5b607223c5c9aa960a4b6546c7939019bc09ccc352d79a76252\"},{\"bytes\":39158,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_restored_index_scope.py\",\"sha256\":\"9c27db250676ac50d9f2bc94fbb6372107d6a86918e6414791311b53515c749b\"},{\"bytes\":114244,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/finite_source_delivery_context.py\",\"sha256\":\"ad61059a3e7b2dbecb4f02e02b1c72b67f8ef51109efaf913fb3db3fbb79c4b1\"},{\"bytes\":83421,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/test_finite_source_delivery_context.py\",\"sha256\":\"73431f7bae4fbd8dbdf5dc8d98faa63cc3baacc259b9635b963dd4f82cda5d33\"},{\"bytes\":344832,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code/qualified_source_semantics.py\",\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},{\"bytes\":21656,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_core.py\",\"sha256\":\"5e1e1f3f2e8a5f2c5771508b7e9433139ee36d58d5b2cc6514bf97333973ca4c\"},{\"bytes\":21981,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_core_v2.py\",\"sha256\":\"eb46c9adf772433e06851f2328f47bd5b2b11a101288d97cce9424cea718eb06\"},{\"bytes\":8774,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_graph_v2.py\",\"sha256\":\"e14b12e01c8e2b9a70ecb30d70d2194bbe89147c01eb02dd305be4075276f98d\"},{\"bytes\":5048,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/provenance_aliases_v2.py\",\"sha256\":\"1de9f0ba13cf8774f6de0fbe4410fd41b8dacf5e9e6d5f1f969b9842f1d8bd01\"},{\"bytes\":3163,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/historical_scope_v2.py\",\"sha256\":\"b8070b30e4633cc6e7d92ffc678fb921a325e96e51aa852bf7fd8b748213c735\"},{\"bytes\":20444,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/native_resource_closure_v2.py\",\"sha256\":\"33a1a8103efbf5d467e9e8360b9bac2f04624e1f1a5929caaa3cc282c6a66c48\"},{\"bytes\":4979,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/restore_resolver_v2.py\",\"sha256\":\"1618974ee343570adf82ad70ac56a0fcfe0a1eac8274476e81ef05691190689c\"},{\"bytes\":3526,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/restore_verify_v2.py\",\"sha256\":\"f052c3bb2f75f6cbd6c7d923df2fb40274cd7a088c62e5386627400d5059e0bf\"},{\"bytes\":18822,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/common_review_independent_v2.py\",\"sha256\":\"e42fc17a996e0fddf5c9d9f0cda6fbee4487ae0577f69b4c1ed3c17ee1a96919\"},{\"bytes\":8723,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/target_statistics_v2.py\",\"sha256\":\"cdad0d2dfb2005c2704178a641c48b40a5268b464cab9587d72ddcdc89f4bf73\"},{\"bytes\":11733,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code/github_export_verify.py\",\"sha256\":\"157c9311f0b40dfbdd9114511741e32b5894f57fa8f02b68a66c3eb2da0978bd\"},{\"bytes\":17447,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/github_export_13086/github_source_export.py\",\"sha256\":\"a824b6636c46d517ba91027074a182627fd164fb744c7782c9dec29a8e3ce1bd\"},{\"bytes\":37640,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_independent.py\",\"sha256\":\"5128ce9776371dd88a48bac7c95fbe0a6e2c8496253394d0ea657799768aaa54\"},{\"bytes\":3592,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/control_msa_check.py\",\"sha256\":\"c4a53008639c3e4e4e28d5653487e4cb858e60f81f54752b8c00dae8ac11f205\"},{\"bytes\":45140,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/vendor/ipsae.py\",\"sha256\":\"10cf9b08c68c91e06cb28526cf2026f47a3980c9048fd3226d13e3304eaf1c27\"},{\"bytes\":21560,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/exact_relative_bbf_context.py\",\"sha256\":\"018732d96d1ad430d4af3cd0d18b46a58e6c62dd6d39f3b1ce7b00d16a0eb194\"},{\"bytes\":14616,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_exact_relative_bbf_context.py\",\"sha256\":\"ef34477b2775f2eba03048e8d7b917029afbb5f0b9ed0be764b9d28114c39bdb\"},{\"bytes\":11280,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/context_mapper_audit_cpu.py\",\"sha256\":\"b3b38eab09c2b27dfd20457d2a631141eb3cd2e37bd93179d53d559ba4a95d22\"},{\"bytes\":1172,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/context_mapper_cpu.sbatch\",\"sha256\":\"d85f025a592ad3634bc4488cc0fe903dcc5e60cab33a1db2db2848d458cf3414\"},{\"bytes\":11487,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/context_consumer.py\",\"sha256\":\"c02b91f01b4b026a3d080376e2f5e6ef6694a917e1e468249e6016d0a95b483d\"},{\"bytes\":4174,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/HANDOFF.md\",\"sha256\":\"286c54250171b11027b5d8f2ca06bbbecb629a2c23c452541a176b67af20f2d0\"},{\"bytes\":16392,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/historical_annotation_context.py\",\"sha256\":\"69a0a33af7cf24a1d50edf993257d0ac072f61b1eb089ef50d19e5c09f4df1c6\"},{\"bytes\":19936,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_historical_annotation_context.py\",\"sha256\":\"97286be74f481dfeb2b77fb2d83dce70e124e87dad998dbc4140e16cd73018dd\"},{\"bytes\":8858,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/recovered_five_context.py\",\"sha256\":\"99b4efcedbae9c70f2d5fce856f02218a5807e25fd6785dd9df17277e49cd1e6\"},{\"bytes\":9440,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_recovered_five_context.py\",\"sha256\":\"358d577a4c7b12e7980c290a9391fdafacefc69ca82c411c60beb567a54cdf35\"},{\"bytes\":19215,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/archive_member_context.py\",\"sha256\":\"fc468c0e9e882569a303ec52aa0a3d6ece0809249fc1ee118eb491ee3f356254\"},{\"bytes\":16014,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_archive_member_context.py\",\"sha256\":\"0f2a1010d81ff2f35bc1c98b10b8eed6e97c97f8ecf8d075ca64b8035073ff38\"},{\"bytes\":78635,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/finite_source_context.py\",\"sha256\":\"6a7fc2a8008b7bdc39b73ac0585b7a96a2b4c8153db47983f3014c70df5e4cc0\"},{\"bytes\":35289,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4/test_finite_source_context.py\",\"sha256\":\"98e6d84e086314ff71d82176c21335e50d03f9c514c83b2da955a048366f96b7\"}],\"source_directory_children\":{\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source\":[\"PAIRED_BUDGET_API.md\",\"paired_budget_benchmark.py\",\"paired_budget_independent.py\",\"snapshot_manifest.json\",\"test_paired_budget_benchmark.py\"],\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code\":[\"__pycache__\",\"benchmark_common_review.py\",\"benchmark_common_review_v2.py\",\"control_msa_check.py\",\"runtime_entries\",\"screening_transfer.py\",\"src\",\"vendor\"],\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/vendor\":[\"ipsae.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code\":[\"HANDOFF.md\",\"composer_bootstrap.py\",\"composer_context_api.py\",\"composer_contracts_cpu.sbatch\",\"composer_cpu.sbatch\",\"final_delivery_composer.py\",\"finite_source_delivery_context.py\",\"github_export_context.py\",\"qualified_source_semantics.py\",\"relative_archive_restore.py\",\"restored_index_scope.py\",\"test_final_delivery_composer.py\",\"test_finite_source_delivery_context.py\",\"test_github_export_context.py\",\"test_restored_index_scope.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4\":[\"HANDOFF.md\",\"archive_member_context.py\",\"context_consumer.py\",\"context_mapper_audit_cpu.py\",\"context_mapper_cpu.sbatch\",\"exact_relative_bbf_context.py\",\"finite_source_context.py\",\"historical_annotation_context.py\",\"recovered_five_context.py\",\"test_archive_member_context.py\",\"test_exact_relative_bbf_context.py\",\"test_finite_source_context.py\",\"test_historical_annotation_context.py\",\"test_recovered_five_context.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/github_export_13086\":[\"README_GITHUB_SOURCE_DELIVERY.md\",\"github_export_contracts.sbatch\",\"github_export_verify.py\",\"github_source_export.py\",\"manifest.json\",\"test_github_source_export.py\"],\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code\":[\"common_review_independent.py\",\"common_review_independent_v2.py\",\"delivery_core.py\",\"delivery_core_v2.py\",\"delivery_graph_v2.py\",\"github_export_verify.py\",\"github_source_export.py\",\"historical_scope_v2.py\",\"history_policy_contracts.sbatch\",\"native74_edge_seal_v2.py\",\"native_full74_collection_v2.py\",\"native_resource_closure_v2.py\",\"provenance_aliases_v2.py\",\"receipt_chain_diagnostic_v2.py\",\"restore_resolver.py\",\"restore_resolver_v2.py\",\"restore_verify.py\",\"restore_verify_v2.py\",\"target_statistics.py\",\"target_statistics_v2.py\",\"test_delivery.py\",\"test_delivery_v2.py\",\"test_github_source_export.py\",\"test_historical_scope_v2.py\",\"test_native_resource_closure_v2.py\"]},\"source_directory_metadata\":[{\"bytes\":4096,\"ctime_ns\":1791696918000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668201811,\"mode\":16749,\"mtime_ns\":1791696918000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1791698201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668203538,\"mode\":16893,\"mtime_ns\":1791698201000000000,\"nlink\":6,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1791698201000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668203560,\"mode\":16893,\"mtime_ns\":1791698201000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/vendor\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017838,\"mode\":16749,\"mtime_ns\":1792189128000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/code\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1792189128000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980017854,\"mode\":16749,\"mtime_ns\":1792189128000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v7_operational_source_provenance_17811/context_mapper_v4\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1791696752000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668200925,\"mode\":16893,\"mtime_ns\":1791696752000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/github_export_13086\",\"uid\":6263900},{\"bytes\":4096,\"ctime_ns\":1791726702000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115639668214857,\"mode\":16749,\"mtime_ns\":1791726702000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/history_policy_13223/code\",\"uid\":6263900}],\"source_readonly_directory_metadata\":{\"bytes\":4096,\"ctime_ns\":1792188530000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094794,\"mode\":16749,\"mtime_ns\":1792188530000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix7_source_metadata_readonly_seal\",\"uid\":6263900},\"source_readonly_metadata\":{\"bytes\":9625954,\"ctime_ns\":1792188530000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094795,\"mode\":33060,\"mtime_ns\":1792188530000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix7_source_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"source_readonly_schema\":\"root-final-composer-v7-fix7-source-metadata-readonly-seal.v1\",\"source_software_metadata\":{\"bytes\":31212,\"ctime_ns\":1792189194000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980027393,\"mode\":33060,\"mtime_ns\":1792189194000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_composer_operational_provenance_contracts_17811/acceptance.json\",\"uid\":6263900},\"source_software_receipt\":{\"bytes\":31212,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_composer_operational_provenance_contracts_17811/acceptance.json\",\"sha256\":\"92d2c167cb969a3573b1ec99ae09cc4e32458aa501a431ccc0cd8958c1aafe6b\"},\"source_software_status\":\"FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE\",\"source_software_terminal_PASS_field\":\"Root_and_two_whole_content_PASS\",\"source_software_terminal_directory_metadata\":{\"bytes\":4096,\"ctime_ns\":1792189810000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094809,\"mode\":16749,\"mtime_ns\":1792189810000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer17811_actual_terminal_metadata_readonly_seal\",\"uid\":6263900},\"source_software_terminal_metadata\":{\"bytes\":9919151,\"ctime_ns\":1792189810000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094812,\"mode\":33060,\"mtime_ns\":1792189810000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_composer17811_actual_terminal_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"source_software_terminal_schema\":\"root-final-composer-v7-17811-terminal-metadata-readonly-seal.v1\",\"stage_acceptance_metadata\":{\"bytes\":229750,\"ctime_ns\":1792179288000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643980008252,\"mode\":33060,\"mtime_ns\":1792179288000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_stage_17809/acceptance.json\",\"uid\":6263900},\"stage_acceptance_receipt\":{\"bytes\":229750,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_stage_17809/acceptance.json\",\"sha256\":\"351c2b23b1681fc36023e043886e3e63e9625d457ac3c8cdbbeea9ae2dfc046d\"},\"stage_terminal_directory_metadata\":{\"bytes\":4096,\"ctime_ns\":1792180384000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094678,\"mode\":16749,\"mtime_ns\":1792180384000000000,\"nlink\":2,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_stage17809_actual_terminal_metadata_readonly_seal\",\"uid\":6263900},\"stage_terminal_metadata\":{\"bytes\":10871344,\"ctime_ns\":1792180384000000000,\"dev\":1119461688,\"gid\":6263900,\"inode\":144115643443094681,\"mode\":33060,\"mtime_ns\":1792180384000000000,\"nlink\":1,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_stage17809_actual_terminal_metadata_readonly_seal/receipt.json\",\"uid\":6263900},\"submit_argv\":[\"sbatch\",\"--parsable\",\"--account=u21111210118\",\"--qos=normal\",\"--job-name=test9_final_source_late_publication_v5\",\"--cpus-per-task=1\",\"--ntasks=1\",\"--nodes=1\",\"--mem=16G\",\"--time=00:30:00\",\"--partition=organ\",\"--chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery\",\"--output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_source_late_publication_v5_%j.out\",\"--error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_source_late_publication_v5_%j.err\",\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_late_publication_from17809_v5_primary_claim/publication_job.sh\"],\"tmp_namespace\":\"final_source_late_publication_v5_\"}")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
# These four existing operational parents are metadata/name-only snapshots.
def initial_md(p):
    x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
operational_parent_before={}
operational_parent_names={}
for parent in (S/"submissions",S/"runs",S/"tmp",S/"frozen"):
    before=initial_md(parent)
    if not stat.S_ISDIR(before["mode"]) or parent.is_symlink():raise SystemExit("Existing nonlink operational parent required")
    names=sorted(os.listdir(parent))
    if initial_md(parent)!=before:raise SystemExit("Operational parent changed during initial names read")
    operational_parent_before[str(parent)]=before
    operational_parent_names[str(parent)]=names
D = S / "submissions" / (SPEC["readiness_namespace"] + jid)
if D.exists() or D.is_symlink():
    raise SystemExit("Exclusive absent current readiness namespace required")
D.mkdir(mode=0o755, exist_ok=False)
readiness_directory_creation=initial_md(D)
readiness_native_original=[]
def native_metadata(p):
    p=Path(p);x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
def persist(name, data):
    p = D / name
    with p.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno()); os.fchmod(stream.fileno(), 0o444); os.fsync(stream.fileno())
    st = p.lstat()
    readiness_native_original.append(native_metadata(p))
    return {"path": str(p), "bytes": st.st_size, "inode": st.st_ino, "mtime_ns": st.st_mtime_ns, "mode": stat.S_IMODE(st.st_mode)}
def tres(text):
    values = {}
    gpu_keys = []
    gpu_bases = ("gpu", "gres/gpu", "gres:gpu")
    for item in text.split(","):
        if item.count("=") != 1:
            raise ValueError("Malformed allocated TRES")
        key, value = item.split("=", 1)
        if not key or not value or key in values:
            raise ValueError("Empty or duplicate allocated TRES key")
        gpu_base = next((base for base in gpu_bases if key == base or key.startswith(base + ":")), None)
        if gpu_base is not None:
            if key != gpu_base and not re.fullmatch("[A-Za-z0-9_.-]+", key[len(gpu_base) + 1:]):
                raise ValueError("Malformed typed GPU key")
            gpu_keys.append(key)
        elif "gpu" in key.lower():
            raise ValueError("Unrecognized GPU allocation namespace")
        values[key] = value
    if "cpu" not in values or not re.fullmatch("[0-9]+", values["cpu"]) or int(values["cpu"]) != 1:
        raise ValueError("Actual CPU1 required")
    if "node" in values and (not re.fullmatch("[0-9]+", values["node"]) or int(values["node"]) != 1):
        raise ValueError("Actual allocated Node1 required when present")
    gpu_values = [values[key] for key in gpu_keys]
    if any(not re.fullmatch("[0-9]+", value) for value in gpu_values) or any(int(value) != 0 for value in gpu_values):
        raise ValueError("Actual current GPU0 required")
    return values
query_env = dict(os.environ, TZ="UTC", SLURM_TIME_FORMAT="standard")
commands = []
operation_deadline = time.monotonic() + 60
def query(argv, prefix):
    timeout = max(0.001, min(5, operation_deadline - time.monotonic()))
    timeout_observed = False
    try:
        r = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=query_env, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        class IncompleteQuery:
            returncode = None
            stdout = e.stdout or b""
            stderr = e.stderr or b""
        r = IncompleteQuery()
        timeout_observed = True
    a = {"argv": argv, "returncode": r.returncode,
         "raw_stdout": persist(prefix + ".stdout", r.stdout),
         "raw_stderr": persist(prefix + ".stderr", r.stderr),
         "timeout_seconds": timeout, "timeout_observed": timeout_observed,
         "query_completed": not timeout_observed}
    commands.append(a)
    return r, a
control_argv = ["scontrol", "show", "job", jid, "-o"]
ctl, ctl_saved = query(control_argv, "current_scontrol")
try:
    if ctl.returncode != 0 or ctl.stderr:
        raise ValueError("Actual current scontrol rc0/empty stderr required")
    fields = {}
    for token in ctl.stdout.decode("utf-8").split():
        if "=" in token:
            key, value = token.split("=", 1)
            if key in fields:
                raise ValueError("Duplicate scontrol field")
            fields[key] = value
    required = {"JobId": jid, "JobName": SPEC["publisher_job_name"], "Account": "u21111210118", "QOS": "normal", "WorkDir": str(S), "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumNodes": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-finite-late-source-publisher-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_FINITE_LATE_SOURCE_PUBLISHER_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "publisher_entered": False}
    persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555); raise
argv = ["sacct", "-X", "-j", jid, "--noheader", "--parsable2", "--format=JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64"]
attempts = []; selected = None; deadline = operation_deadline
for number in range(1, 31):
    if time.monotonic() >= deadline:
        break
    r, observation = query(argv, "attempt_%03d" % number)
    try:
        if r.returncode != 0 or r.stderr:
            raise ValueError("Actual current sacct rc0/empty stderr required")
        rows = [line.split("|") for line in r.stdout.decode("utf-8").splitlines() if line.split("|", 1)[0] == jid]
        if len(rows) != 1 or len(rows[0]) != 6 or rows[0][1] != "RUNNING" or rows[0][3:] != ["u21111210118", "u21111210118", "organ"]:
            raise ValueError("Unique actual current six-column RUNNING owner/account/organ row required")
        values = tres(rows[0][2])
        observation.update({"accepted_current_readiness": True, "actual_row": rows[0], "parsed_tres": values})
        selected = number
    except Exception as e:
        observation.update({"accepted_current_readiness": False, "reason_type": type(e).__name__, "reason": str(e)})
    attempts.append(observation)
    if selected is not None or time.monotonic() >= deadline or number == 30:
        break
    time.sleep(min(2, max(0, deadline - time.monotonic())))
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_FINITE_LATE_SOURCE_PUBLISHER_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_FINITE_LATE_SOURCE_PUBLISHER_NOT_EXECUTED"
obj = {"schema": "root-current-owned-finite-late-source-publisher-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres,
       "all_present_scontrol_TRES_fields_CPU1_GPU0": current_tres_fields, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "current_strict_CPU_readiness_authenticated_no_additional_library_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "publisher_entered": False,
       "additional_pin_or_source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
readiness_directory_original=native_metadata(D)
readiness_names_original={Path(x["path"]).name for x in readiness_native_original}
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "publisher_next_not_acceptance": True}), flush=True)


# RAM Source proposal, never executed by Source preparation.
import hashlib, importlib.util
R=S.parent.parent
CORE_LOGICAL=R/"env/core/bin/python";CORE_REAL=R/"env/core/bin/python3.11"
CORE_BYTES=25916456;CORE_SHA="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"
COMMON=R/"source/rebuild/benchmark_common_review.py"
COMMON_FP=(58825,"ad8edf0ac5250e587709c26e61957101072ea4343f83514271634b3bf7c36b5b")
SPEC_KEYS={"schema","publisher_job_name","readiness_namespace","publication_namespace","tmp_namespace","proof_namespace",
 "source_software_receipt","source_software_metadata","source_software_status","software_expected_test_count","software_contracts_receipt","software_contracts_metadata","source_software_terminal_metadata","source_software_terminal_directory_metadata","source_software_terminal_schema","source_software_terminal_PASS_field",
 "source_readonly_metadata","source_readonly_directory_metadata","source_readonly_schema",
 "producer_receipts","producer_metadata","stage_acceptance_receipt","stage_acceptance_metadata",
 "stage_terminal_metadata","stage_terminal_directory_metadata","source44_receipts","source44_metadata",
 "source_directory_metadata","source_directory_children","conditional_core_metadata","Common_original_metadata",
 "protected_metadata_delta","protected_directory_children_delta","existing_authority_controls",
 "publisher_source_readonly_metadata","publisher_source_readonly_directory_metadata","publisher_source_readonly_schema","publisher_first_pin_Source_metadata_original",
 "primary_claim_directory","primary_claim_files","primary_request_path","primary_submit_path",
 "primary_raw_stdout_path","primary_raw_stderr_path","self_human_path","self_primary_path","self_proposal_path",
 "self_proposal_directory","human_readonly_path","human_readonly_directory","human_readonly_schema",
 "primary_request_schema","primary_submit_schema","human_static_PASS_field","shell_header","submit_argv",
 "failed_publisher_terminal_metadata","failed_publisher_terminal_directory_metadata","publisher_HANDOFF_metadata"}
def need(v,m):
 if not v:raise ValueError(m)
need(type(SPEC)is dict and set(SPEC)==SPEC_KEYS and SPEC["schema"]=="root-finite-late-source-publisher-binding.v5","Actual prior-input publisher SPEC")
for k in("publisher_job_name","readiness_namespace","publication_namespace","tmp_namespace","proof_namespace"):
 need(type(SPEC[k])is str and re.fullmatch("[A-Za-z0-9_]{5,120}",SPEC[k]),"Literal reviewed publisher profile")
need(sys.flags.isolated==0 and sys.flags.no_user_site==1 and sys.flags.dont_write_bytecode==1,"CORE -B, no -I, original isolation")
need(Path(sys.executable)in(CORE_LOGICAL,CORE_REAL),"Only unchanged conditional Core runtime")
MD_KEYS={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
def md_shape(v):
 need(type(v)is dict and set(v)==MD_KEYS and type(v["path"])is str and Path(v["path"]).is_absolute(),"Full native record")
 need(all(type(v[k])is int and v[k]>=0 for k in MD_KEYS-{"path"}),"Exact integer native fields")
 return v
def rid(r):
 need(type(r)is dict and set(r)=={"path","bytes","sha256"},"Whole tuple")
 need(type(r["path"])is str and Path(r["path"]).is_absolute()and ".."not in Path(r["path"]).parts,"Absolute literal tuple")
 need(type(r["bytes"])is int and r["bytes"]>=0 and type(r["sha256"])is str and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Actual CPU bytes/SHA")
 return r["path"],r["bytes"],r["sha256"]
def subset(r):return {k:r[k]for k in("path","bytes","sha256")}
def fp(r):rid(subset(r));return r["bytes"],r["sha256"]
def ordinary(p):
 p=Path(p);need(p.is_absolute()and(p==R or R in p.parents)and ".."not in p.parts,"Internal literal authority")
 for q in[p]+list(p.parents):
  if q==R.parent:break
  need(not stat.S_ISLNK(q.lstat().st_mode),"Ordinary nonlink ancestry")
 return p
ORIGINAL={};CREATED={};EVENTS={};PAYLOAD={};WORKER=set();TARGET_PINS={};AFFECTED={};NEW_TARGETS={};NEW_DIRS={}
def enroll(records):
 for v in records:
  md_shape(v);k=v["path"]
  need(k not in CREATED,"Original collides with created output")
  if k in ORIGINAL:need(ORIGINAL[k]==v,"Conflicting ORIGINAL native")
  else:ORIGINAL[k]=dict(v)
def created(v):
 md_shape(v);k=v["path"];need(k not in ORIGINAL,"Created output collides with original")
 if k in CREATED:need(CREATED[k]==v,"Creation baseline cannot refresh")
 else:CREATED[k]=dict(v)
def expected_md(p):
 k=str(p);need(k in ORIGINAL or k in CREATED,"Enroll native before FIRST payload IO")
 return EVENTS.get(k,ORIGINAL[k]if k in ORIGINAL else CREATED[k])
def matches(p):
 v=expected_md(p);need(native_metadata(Path(p))==v,"Original/creation/event native changed");return v
def allow(records,purpose):
 for v in records:
  k=v["path"];need(k!=str(COMMON)and k not in WORKER,"No Common/worker payload permission")
  need(type(purpose)is str and re.fullmatch("[A-Z0-9_]+",purpose),"Closed payload purpose")
  PAYLOAD.setdefault(k,set()).add(purpose)
def pairs(items):
 out={}
 for k,v in items:need(k not in out,"Duplicate JSON key");out[k]=v
 return out
def number(s):
 v=float(s);need(v==v and abs(v)!=float("inf"),"Nonfinite/overflow number");return v
def strict(raw):
 return json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,parse_float=number,parse_constant=lambda x:(_ for _ in()).throw(ValueError("Nonfinite JSON")))
def read_own(p,limit):
 p=ordinary(p);need(str(p)in PAYLOAD,"Explicit own payload purpose")
 v=matches(p);need(stat.S_ISREG(v["mode"])and v["nlink"]==1 and v["bytes"]<=limit,"Bounded regular singlelink input")
 fd=os.open(str(p),os.O_RDONLY|os.O_NOFOLLOW)
 try:
  st=os.fstat(fd);need(st.st_ino==v["inode"]and st.st_dev==v["dev"]and st.st_mode==v["mode"],"Exact original fd")
  with os.fdopen(fd,"rb",closefd=False)as stream:raw=stream.read(limit+1)
 finally:os.close(fd)
 need(len(raw)==v["bytes"]and native_metadata(p)==v,"Own payload/native changed")
 return raw
def hash_own(p):
 p=ordinary(p);need(str(p)in PAYLOAD,"Explicit source/control/evidence purpose")
 v=matches(p);need(stat.S_ISREG(v["mode"])and v["nlink"]==1,"Regular singlelink full stream")
 fd=os.open(str(p),os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256();size=0
 try:
  st=os.fstat(fd);need(st.st_ino==v["inode"]and st.st_dev==v["dev"]and st.st_mode==v["mode"],"Exact fullhash fd")
  with os.fdopen(fd,"rb",closefd=False)as stream:
   for block in iter(lambda:stream.read(1024*1024),b""):h.update(block);size+=len(block)
 finally:os.close(fd)
 need(size==v["bytes"]and native_metadata(p)==v,"Full stream original drift")
 return dict(path=str(p),bytes=size,sha256=h.hexdigest())
def checked_control(record,receipt,limit=20*1024*1024):
 md_shape(record);rid(receipt);need(record["path"]==receipt["path"]and record["bytes"]==receipt["bytes"],"Existing control tuple/native")
 ordinary(record["path"]);need(stat.S_ISREG(record["mode"])and record["nlink"]==1 and(not(record["mode"]&0o222)or receipt in list(getattr(globals().get("g"),"_WORKER_PARENTS",()))),"Readonly control or exact declared raw-parent native policy")
 enroll([record]);allow([record],"EXPLICIT_CONTROL_OWN_BYTES")
 need(hash_own(record["path"])==receipt,"Actual existing control full tuple")
 return strict(read_own(record["path"],limit))
def initial_metadata_control(record,limit=20*1024*1024):
 md_shape(record);ordinary(record["path"]);need(stat.S_ISREG(record["mode"])and record["nlink"]==1 and not(record["mode"]&0o222),"Existing readonly metadata control")
 enroll([record]);allow([record],"EXPLICIT_CONTROL_OWN_BYTES")
 return strict(read_own(record["path"],limit))
def directory(record):
 md_shape(record);ordinary(record["path"]);need(stat.S_ISDIR(record["mode"])and native_metadata(Path(record["path"]))==record,"Exact existing directory")
 enroll([record])

phase="before_bound_primary"
try:
    CLAIM=Path(SPEC["primary_claim_directory"]);names=SPEC["primary_claim_files"]
    need(CLAIM.parent==S/"submissions"and type(names)is list and len(names)==len(set(names))==6 and all(type(n)is str and Path(n).name==n and n not in(".","..","")for n in names),"Closed primary sixfile namespace")
    claim_rows=None;claim_md=None;claim_wait=[];deadline=time.monotonic()+60
    for attempt in range(1,31):
     observation=dict(attempt=attempt,complete_readonly=False)
     try:
      if CLAIM.is_symlink():raise ValueError("Primary symlink")
      if CLAIM.exists():
       before=native_metadata(CLAIM);actual_names=sorted(os.listdir(CLAIM))
       need(set(actual_names)<=set(names),"Unexpected primary member")
       if set(actual_names)==set(names)and stat.S_ISDIR(before["mode"])and stat.S_IMODE(before["mode"])==0o555:
        rows=[native_metadata(CLAIM/n)for n in names]
        need(all(stat.S_ISREG(v["mode"])and stat.S_IMODE(v["mode"])==0o444 and v["nlink"]==1 for v in rows),"Primary exact444 files")
        need(native_metadata(CLAIM)==before and[native_metadata(CLAIM/n)for n in names]==rows,"Original complete claim stable")
        claim_rows=rows;claim_md=before;observation["complete_readonly"]=True
     except FileNotFoundError:observation["temporarily_incomplete"]=True
     claim_wait.append(observation)
     if claim_rows is not None or attempt==30 or time.monotonic()>=deadline:break
     time.sleep(min(2,max(0,deadline-time.monotonic())))
    need(claim_rows is not None,"Bounded readonly primary wait exhausted")
    directory(claim_md);enroll(claim_rows);allow(claim_rows,"ROOT_PRIMARY_OWN_BYTES")
    for k in("primary_request_path","primary_submit_path","primary_raw_stdout_path","primary_raw_stderr_path","self_primary_path"):
     need(Path(SPEC[k]).parent==CLAIM and Path(SPEC[k]).name in names,"Same primary literal file")
    REQUEST=strict(read_own(SPEC["primary_request_path"],4*1024*1024))
    REQUEST_KEYS={"schema","status","Human_after","human_readonly_receipt_metadata","human_readonly_directory_metadata",
     "primary_script_metadata","source_proposal_metadata_after","source_candidates","candidate_authority_controls",
     "i_source_route_choices","source_control_receipts","source_control_metadata","self_source_destinations"}
    need(type(REQUEST)is dict and set(REQUEST)==REQUEST_KEYS and REQUEST["schema"]==SPEC["primary_request_schema"]
     and REQUEST["status"]=="ACTUAL_SEALED_FINITE_PUBLISHER_INPUTS_NOT_SUBMISSION_OR_PUBLICATION","Closed postHRO request/no ownMD-SHA-JID")
    BINDING={"human":REQUEST["Human_after"],"hro":REQUEST["human_readonly_receipt_metadata"],"hroD":REQUEST["human_readonly_directory_metadata"],
     "script":REQUEST["primary_script_metadata"]}
    need(type(REQUEST["source_proposal_metadata_after"])is list and len(REQUEST["source_proposal_metadata_after"])==2,"Actual proposal file/D")
    BINDING["proposal"],BINDING["proposalD"]=REQUEST["source_proposal_metadata_after"]
    for k,pathkey in(("human","self_human_path"),("hro","human_readonly_path"),("hroD","human_readonly_directory"),("script","self_primary_path"),("proposal","self_proposal_path"),("proposalD","self_proposal_directory")):
     md_shape(BINDING[k]);need(BINDING[k]["path"]==SPEC[pathkey],"Actual planned self path afterHRO")
    for k in("hroD","proposalD"):directory(BINDING[k])
    for k in("human","hro","script","proposal"):
     v=BINDING[k];ordinary(v["path"]);need(stat.S_ISREG(v["mode"])and v["nlink"]==1 and stat.S_IMODE(v["mode"])==0o444,"Actual sealed self file")
    enroll([BINDING[k]for k in("human","hro","script","proposal")]);allow([BINDING[k]for k in("human","hro","script","proposal")],"ROOT_SELF_OWN_BYTES")
    SUBMIT=strict(read_own(SPEC["primary_submit_path"],2*1024*1024))
    SUBMIT_KEYS={"schema","status","primary_request_path","primary_script_path","argv","returncode","raw_stdout","raw_stderr","submitted_job_id","started_at_UTC","ended_at_UTC","timeout_seconds"}
    need(type(SUBMIT)is dict and set(SUBMIT)==SUBMIT_KEYS and SUBMIT["schema"]==SPEC["primary_submit_schema"]
     and SUBMIT["status"]=="ACTUAL_UNIQUE_SCRIPTFILE_SBATCH_SUBMITTED_NOT_PUBLICATION","Closed separate submit receipt")
    need(SUBMIT["primary_request_path"]==SPEC["primary_request_path"]and SUBMIT["primary_script_path"]==SPEC["self_primary_path"]
     and SUBMIT["argv"]==SPEC["submit_argv"]and SUBMIT["returncode"]==0 and SUBMIT["submitted_job_id"]==jid
     and SUBMIT["raw_stdout"]==jid+"\n"and SUBMIT["raw_stderr"]=="","Actual current unique numeric scriptfile submit")
    need(type(SPEC["submit_argv"])is list and SPEC["submit_argv"][0]=="sbatch"and SPEC["submit_argv"][-1]==SPEC["self_primary_path"]
     and all(type(x)is str and "--wrap"not in x for x in SPEC["submit_argv"]),"No wrap Source creation")
    need(read_own(SPEC["primary_raw_stdout_path"],4096)==(jid+"\n").encode()and read_own(SPEC["primary_raw_stderr_path"],4096)==b"","Saved submit raw facts")
    # ST47 is authenticated and reconstructed before any Human/Source payload read; no embedded17k table.
    directory(SPEC["source_software_terminal_directory_metadata"])
    ST=initial_metadata_control(SPEC["source_software_terminal_metadata"])
    need(set(ST)==set(["schema","status","captured_at_UTC","metadata_only","actual_job_id","Root_and_two_whole_content_PASS","whole_content_evidence","actual_terminal","actual_HRO_metadata","actual_HRO_directory_metadata","protected_metadata_before","protected_metadata_unchanged","protected_directory_children","conditional_CORE_metadata_original","Common_original_metadata_only_original","worker_exact_metadata_only_routes","job_owned_metadata_before","job_owned_metadata_after","job_owned_directory_children","exact_permission_events","actual_software_acceptance","actual_Root_execution_control","actual_contracts","actual_contract_log","actual_Source_groups_original","actual_Source_groups_frozen","actual_Output32_metadata_original","actual_readiness_metadata","actual_readiness_summary","actual_software_stdout_final_descriptor","actual_suite_summary","actual_fixture_SOURCE_BYTE_CPU_tuples","actual_fixture_SOURCE_PROVENANCE_control_CPU_tuples","actual_fixture_DATA_CPU_tuples","actual_fixed_control_own_CPU_tuples","historical_software_jobtime_shared_parent_events","terminal_seal_created_parent_event","actual_fresh_allocation","Source_or_INDEX_compatibility_accepted","production_science_accepted","Git_changed","published","ACTIVE_changed","full_final_delivery_accepted","no_replay_or_resubmit","own_control_LATE_not_own_Source_Plan_or_package_prerequisite","source_payload_hashes_or_import_compile_tests_on_login"]) and len(ST)==47
     and ST["schema"]==SPEC["source_software_terminal_schema"]=="root-final-composer-v7-17811-terminal-metadata-readonly-seal.v1"
     and ST["status"]=="ACTUAL_SOFTWARE215_AND_ROOT_EXECUTION_CONTROL_FULL_CONTENT_AND_TERMINAL_METADATA_ACCEPTED_NOT_SOURCE_INDEX_SCIENCE_OR_DELIVERY"
     and ST["actual_job_id"]=="17811"and ST[SPEC["source_software_terminal_PASS_field"]]is True
     and ST["Root_and_two_whole_content_PASS"]is True and ST["protected_metadata_unchanged"]is True,"Actual qualified ST47")
    need(ST["actual_software_acceptance"]==SPEC["source_software_receipt"]and ST["actual_contracts"]==SPEC["software_contracts_receipt"]
     and SPEC["software_expected_test_count"]==215,"ST47 exact accepted software/contract lineage")
    need(ST["actual_suite_summary"]==dict(tests_run=215,OK=215,failures=0,errors=0,skipped=0,operational_tests=21,compile_PASS=True,Bash_PASS=True),"Actual215/zero failure-error-skip")
    terminal=ST["actual_terminal"]
    need(type(terminal)is dict and terminal["returncode"]==0 and terminal["raw_stderr"]==""
     and type(terminal["row"])is list and len(terminal["row"])==9
     and terminal["row"][:6]==["17811","test9_final_composer_worker_identity_contracts_v7","COMPLETED","0:0","87","1"]
     and terminal["raw_stdout"]=="|".join(terminal["row"])+"\n"and terminal["row"][6]=="billing=1,cpu=1,node=1","Authenticated actual software terminal row")
    need(all(ST[k]is False for k in("Source_or_INDEX_compatibility_accepted","production_science_accepted","Git_changed","published","ACTIVE_changed","full_final_delivery_accepted","source_payload_hashes_or_import_compile_tests_on_login")),"Software-only ST47 status")
    need(type(ST["protected_metadata_before"])is list and len(ST["protected_metadata_before"])==17679
     and type(ST["job_owned_metadata_after"])is list and len(ST["job_owned_metadata_after"])==51,"Finite original ST47 tables")
    protected_rows=list(ST["protected_metadata_before"])+list(ST["job_owned_metadata_after"])+[terminal["raw_stdout_metadata"],terminal["raw_stderr_metadata"],SPEC["source_software_terminal_metadata"],SPEC["source_software_terminal_directory_metadata"]]
    need(len(protected_rows)==17734 and len({v["path"]for v in protected_rows})==17734,"Exact17734 reconstructed original records")
    enroll(protected_rows);enroll(SPEC["conditional_core_metadata"]+[SPEC["Common_original_metadata"]])
    need(ST["conditional_CORE_metadata_original"]==SPEC["conditional_core_metadata"]and ST["Common_original_metadata_only_original"]==SPEC["Common_original_metadata"],"ST47 original Core/Common lineage")
    WORKER=set(ST["worker_exact_metadata_only_routes"]);need(len(WORKER)==68 and WORKER<=set(ORIGINAL),"Exact prior worker metadata-only routes")
    # A separately qualified failed-job control supplies one CURRENT directory
    # observation. It never retroactively changes the ST47 17734-row authority.
    phase="authenticate_fixed_saved_name_only_directory_observation"
    failed_tro_md=SPEC["failed_publisher_terminal_metadata"]
    failed_tro_D=SPEC["failed_publisher_terminal_directory_metadata"]
    md_shape(failed_tro_md);md_shape(failed_tro_D)
    need(failed_tro_md["path"]==str(S/"submissions/final_source_late_publication17812_actual_failed_terminal_metadata_readonly_seal/receipt.json")
     and Path(failed_tro_md["path"]).parent.parent==S/"submissions"
     and failed_tro_D["path"]==str(Path(failed_tro_md["path"]).parent),
     "One literal bound failed17812 own-control file/directory")
    ordinary(failed_tro_md["path"])
    need(stat.S_ISREG(failed_tro_md["mode"])and stat.S_IMODE(failed_tro_md["mode"])==0o444
     and failed_tro_md["nlink"]==1 and 0<failed_tro_md["bytes"]<=20*1024*1024
     and stat.S_IMODE(failed_tro_D["mode"])==0o555,"Qualified readonly failed17812 own metadata only")
    directory(failed_tro_D);enroll([failed_tro_md]);allow([failed_tro_md],"FIXED_FAILED_PUBLISHER_TERMINAL_OWN_BYTES")
    failed_tro_pin=hash_own(failed_tro_md["path"])
    FAILED_TRO=strict(read_own(failed_tro_md["path"],20*1024*1024))
    need(hash_own(failed_tro_md["path"])==failed_tro_pin,"Failed17812 own whole bytes before/end initial parse")
    need(type(FAILED_TRO)is dict
     and FAILED_TRO["schema"]=="root-finite-late-source-publisher-actual-failed-terminal-metadata-readonly-seal.v1"
     and FAILED_TRO["status"]=="ACTUAL_FAILED_TERMINAL_METADATA_READBACK_PRESERVED_NO_PUBLICATION_OR_SOURCE_ACCEPTANCE"
     and FAILED_TRO["actual_job_id"]=="17812","Exact qualified failed17812 metadata control, never publication")
    mapper_parent=str(S/"pending/exact_context_mapper_v4")
    mapper_names=["HANDOFF.md","archive_member_context.py","context_consumer.py","context_mapper_audit_cpu.py",
     "context_mapper_cpu.sbatch","exact_relative_bbf_context.py","finite_source_context.py","historical_annotation_context.py",
     "recovered_five_context.py","test_archive_member_context.py","test_exact_relative_bbf_context.py",
     "test_finite_source_context.py","test_historical_annotation_context.py","test_recovered_five_context.py"]
    mapper_current=dict(path=mapper_parent,bytes=4096,inode=144115543165692550,
     mtime_ns=1791745915000000000,ctime_ns=1791746829000000000,mode=16749,
     dev=1119461688,nlink=2,uid=6263900,gid=6263900)
    old_v4_hro=dict(path=str(S/"submissions/root_final_source_late_publication_v4_human_metadata_readonly_seal/receipt.json"),
     bytes=9682370,inode=144115643443094841,mtime_ns=1792199365000000000,ctime_ns=1792199365000000000,
     mode=33060,dev=1119461688,nlink=1,uid=6263900,gid=6263900)
    mapper_observation=FAILED_TRO["saved_name_only_directory_new_metadata_observation"]
    need(type(mapper_observation)is dict and set(mapper_observation)=={
     "directory_metadata","directory_children_original","children_metadata_authority","children_metadata_existing_original","scope"},
     "Closed single current Mapper-directory observation")
    need(mapper_observation["scope"]=="CURRENT_METADATA_ONLY_NOT_RETROACTIVE_ST_OR_SOURCE_READER_PERMISSION"
     and mapper_observation["directory_metadata"]==mapper_current
     and mapper_observation["directory_children_original"]==mapper_names
     and mapper_observation["children_metadata_authority"]==old_v4_hro,
     "Exact current-only P Native and already-saved14 names; no generic directory fallback")
    need(mapper_parent not in ORIGINAL and ST["protected_directory_children"][mapper_parent]==mapper_names,
     "P was name-only in ST47 and must never be represented as a retrospective native row")
    mapper_children=mapper_observation["children_metadata_existing_original"]
    need(type(mapper_children)is list and len(mapper_children)==14
     and [v["path"]for v in mapper_children]==[str(Path(mapper_parent)/name)for name in mapper_names],
     "Exact original fourteen Mapper child Native records")
    for v in mapper_children:
     md_shape(v);need(v["path"]in ORIGINAL and ORIGINAL[v["path"]]==v
      and stat.S_ISREG(v["mode"])and v["nlink"]==1,"Child Native already belongs to unchanged ST17734; never refresh it")
    directory(mapper_current)
    need(sorted(os.listdir(mapper_parent))==mapper_names,"Exact fixed fourteen-child metadata universe")
    mapper_observation_authenticated=True
    failed_self_paths=[str(S/"handoffs/ROOT_FIXED_FINAL_SOURCE_LATE_PUBLICATION_FROM17809_REV4_20261016.md"),
     str(S/"submissions/root_final_source_late_publication_from17809_v4_primary_claim/publication_job.sh"),
     str(S/"pending/root_final_source_late_publication_control_from17809_v4/late_publication_control.py")]
    failed_self_kinds=["DOCUMENT","CONFIGURATION_OR_LAUNCHER","IMPLEMENTATION"]
    failed_self_tags=["human","script","proposal"]
    failed_self_folder="delivery_tools/root_operational_programs/root_final_source_late_publication_control_from17809_v4/"
    failed_self_destinations=dict(
     human=dict(kind="DOCUMENT",roles=["final_delivery_tools"],repository_relative=failed_self_folder+"ROOT_FIXED_FINAL_SOURCE_LATE_PUBLICATION_FROM17809_REV4_20261016.md"),
     script=dict(kind="CONFIGURATION_OR_LAUNCHER",roles=["final_delivery_tools"],repository_relative=failed_self_folder+"publication_job.sh"),
     proposal=dict(kind="IMPLEMENTATION",roles=["final_delivery_tools"],repository_relative=failed_self_folder+"late_publication_control.py"))
    failed_self_records=FAILED_TRO["failed_publisher_self_source_metadata_original"]
    need(type(failed_self_records)is list and len(failed_self_records)==3
     and [v["path"]for v in failed_self_records]==failed_self_paths
     and FAILED_TRO["failed_publisher_self_source_destinations_declared"]==failed_self_destinations
     and FAILED_TRO["failed_self_Source_CPU_tuples_captured"]is False,
     "Exactly three failed V4 selfSources: original Native and declared roles/destinations, no invented CPU pins")
    for v in failed_self_records:
     md_shape(v);ordinary(v["path"]);need(stat.S_ISREG(v["mode"])and stat.S_IMODE(v["mode"])==0o444
      and v["nlink"]==1,"Original three V4 selfSource Native records remain readonly singlelink")
    failed_tro_authenticated=True
    protected_children={}
    for source in(ST["protected_directory_children"],ST["job_owned_directory_children"],{SPEC["source_software_terminal_directory_metadata"]["path"]:["fresh_sacct.stderr","fresh_sacct.stdout","receipt.json"]}):
     need(type(source)is dict,"Closed saved directory-name table")
     for path,children in source.items():
      need(path not in protected_children and path in ORIGINAL and stat.S_ISDIR(ORIGINAL[path]["mode"])
       and type(children)is list and len(children)==len(set(children))and all(type(x)is str and Path(x).name==x and x not in("","..",".")for x in children),"Exact unique saved directory children")
      protected_children[path]=list(children)
    need(len(ST["protected_directory_children"])==340 and len(ST["job_owned_directory_children"])==7 and len(protected_children)==348,"Exact348 saved universes")
    need(type(SPEC["protected_metadata_delta"])is list and len(SPEC["protected_metadata_delta"])<=64,"Small literal new-path metadata delta")
    for v in SPEC["protected_metadata_delta"]:md_shape(v);need(v["path"]not in ORIGINAL,"Delta cannot shadow17734 originals")
    enroll(SPEC["protected_metadata_delta"])
    need(type(SPEC["protected_directory_children_delta"])is dict and len(SPEC["protected_directory_children_delta"])<=24,"Small finite operational custody directory delta (at most24; never Reader17 authority)")
    for path,children in SPEC["protected_directory_children_delta"].items():
     need(path not in protected_children and path in ORIGINAL and stat.S_ISDIR(ORIGINAL[path]["mode"])
      and type(children)is list and len(children)==len(set(children))and all(type(x)is str and Path(x).name==x and x not in("","..",".")for x in children),"New directory delta never shadows saved universe")
     protected_children[path]=list(children)
    for p,v in ORIGINAL.items():
     if p not in WORKER and p not in(str(CORE_LOGICAL),str(CORE_REAL)):ordinary(p)
     need(native_metadata(Path(p))==v,"Reconstructed ORIGINAL full native before payload")
    for p,children in protected_children.items():need(sorted(os.listdir(p))==sorted(children),"Reconstructed ORIGINAL directory universe")
    for p,v in operational_parent_before.items():
     need(p not in ORIGINAL or ORIGINAL[p]==v,"Operational parent original authority must agree before event")
    enroll(list(operational_parent_before.values()))
    # New publisher SourceRO is separate; Q below remains the accepted software SourceRO35.
    PUBLISHER_Q=initial_metadata_control(SPEC["publisher_source_readonly_metadata"])
    directory(SPEC["publisher_source_readonly_directory_metadata"])
    need(PUBLISHER_Q["schema"]==SPEC["publisher_source_readonly_schema"]=="root-finite-late-source-publisher-v5-source-metadata-readonly-seal.v1"
     and PUBLISHER_Q["Root_and_two_whole_STATIC_PASS"]is True and PUBLISHER_Q["protected_metadata_unchanged"]is True,"Actual separately reviewed publisher SourceRO")
    first_pin_records=SPEC["publisher_first_pin_Source_metadata_original"]
    first_pin_paths=["/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_bootstrap.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_contracts_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/composer_context_api.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/relative_archive_restore.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/test_finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1/qualified_source_semantics.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_bootstrap.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_contracts_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/composer_context_api.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/relative_archive_restore.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/test_finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix1/qualified_source_semantics.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_bootstrap.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_contracts_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/composer_context_api.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/relative_archive_restore.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/test_finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix2/qualified_source_semantics.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v1/software_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix3_software_control_from17809_v2/software_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_bootstrap.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_contracts_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/composer_context_api.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/relative_archive_restore.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/test_finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix4/qualified_source_semantics.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_final_delivery_composer.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_bootstrap.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_contracts_cpu.sbatch","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/composer_context_api.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/relative_archive_restore.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_github_export_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_restored_index_scope.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/test_finite_source_delivery_context.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix5/qualified_source_semantics.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v1/late_publication_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v1/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v2/late_publication_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v2/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v3/late_publication_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v3/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_late_publication_control_from17809_v4/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v1/source_index_compatibility_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v1/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v2/source_index_compatibility_control.py","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_source_index_compatibility_control_from17811_v2/HANDOFF.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_SOURCE_INDEX_COMPATIBILITY_FROM17811_REV2_20261016.md","/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_source_index_compatibility_from17811_v2_primary_claim/compatibility_job.sh"]
    need(type(first_pin_records)is list and len(first_pin_records)==90 and len(set(first_pin_paths))==90
     and [v["path"]for v in first_pin_records]==first_pin_paths
     and PUBLISHER_Q["source_first_pin_authority_metadata_original"]==first_pin_records,"Closed90 exact ordered Source records")
    for index,v in enumerate(first_pin_records):
     md_shape(v);ordinary(v["path"]);need(stat.S_ISREG(v["mode"])and v["nlink"]==1
      and stat.S_IMODE(v["mode"])in((0o444,)if index in {83,86,87,88,89}else(0o444,0o664)),"Exact historical modes preserved; only actual sealed V4 HANDOFF and compatV2 four require444")
    enroll(first_pin_records)
    publisher_handoff_md=SPEC["publisher_HANDOFF_metadata"]
    md_shape(publisher_handoff_md);ordinary(publisher_handoff_md["path"])
    need(publisher_handoff_md["path"]==str(Path(SPEC["self_proposal_directory"])/"HANDOFF.md")
     and stat.S_ISREG(publisher_handoff_md["mode"])and publisher_handoff_md["nlink"]==1
     and stat.S_IMODE(publisher_handoff_md["mode"])==0o444
     and PUBLISHER_Q["publisher_HANDOFF_metadata_after"]==publisher_handoff_md,
     "Exactly one current V5 HANDOFF native from qualified SourceRO; old90 remain unchanged")
    need(publisher_handoff_md["path"]in ORIGINAL and ORIGINAL[publisher_handoff_md["path"]]==publisher_handoff_md,
     "Current V5 HANDOFF is enrolled exactly by the explicit new-path metadata delta, never refreshed")
    human=read_own(BINDING["human"]["path"],2*1024*1024).decode("utf-8");fence=chr(96)*3
    need(human.count(fence+"python\n")==1 and human.count("\n"+fence+"\n")==1,"Exact opening and closing Human fences")
    body=human.split(fence+"python\n",1)[1].split("\n"+fence+"\n",1)[0]+"\n"
    need(read_own(BINDING["script"]["path"],2*1024*1024)==SPEC["shell_header"].encode()+body.encode()+b"PY\n","Exact reviewed Human scriptfile body")
    enroll(readiness_native_original+[readiness_directory_original]);allow(readiness_native_original,"ROOT_CURRENT_READINESS_OWN_BYTES")
    # All protected originals were reconstructed and enrolled before the Human payload read.
    need(SPEC["Common_original_metadata"]["path"]==str(COMMON),"Common metadata only")
    def core_check():
     d={v["path"]:v for v in SPEC["conditional_core_metadata"]}
     need(set(d)=={str(CORE_LOGICAL),str(CORE_REAL)},"Exact Core2 scope")
     need(stat.S_ISLNK(d[str(CORE_LOGICAL)]["mode"])and d[str(CORE_LOGICAL)]["bytes"]==10 and d[str(CORE_LOGICAL)]["nlink"]==1,"Exact Core logical")
     need(stat.S_ISREG(d[str(CORE_REAL)]["mode"])and d[str(CORE_REAL)]["bytes"]==CORE_BYTES and d[str(CORE_REAL)]["nlink"]==1,"Exact Core real")
     need(native_metadata(CORE_LOGICAL)==d[str(CORE_LOGICAL)]and native_metadata(CORE_REAL)==d[str(CORE_REAL)]and os.readlink(CORE_LOGICAL)=="python3.11","Original Core2 metadata/link")
     h=hashlib.sha256();size=0
     with CORE_REAL.open("rb")as stream:
      for block in iter(lambda:stream.read(1024*1024),b""):h.update(block);size+=len(block)
     need(size==CORE_BYTES and h.hexdigest()==CORE_SHA,"Exact fixed Core bytes")
     need(native_metadata(CORE_LOGICAL)==d[str(CORE_LOGICAL)]and native_metadata(CORE_REAL)==d[str(CORE_REAL)],"Core drift")
    core_check()
    T=initial_metadata_control(SPEC["stage_terminal_metadata"]);directory(SPEC["stage_terminal_directory_metadata"])
    need(T["schema"]=="root-plan-v13-stage17809-terminal-metadata-readonly-seal.v1"and len(T)==42 and T["actual_job_id"]=="17809"and T["Root_and_two_whole_content_PASS"]is True,"Actual accepted Stage")
    WORKER=set(T["worker_exact_metadata_only_routes"]);need(len(WORKER)==68 and WORKER<=set(ORIGINAL),"Closed prior worker metadata routes")
    need(T["conditional_CORE_metadata_original"]==SPEC["conditional_core_metadata"]and T["Common_original_metadata_only_original"]==SPEC["Common_original_metadata"],"Existing Core/Common lineage")
    Q=initial_metadata_control(SPEC["source_readonly_metadata"]);directory(SPEC["source_readonly_directory_metadata"])
    need(Q["schema"]==SPEC["source_readonly_schema"]and Q["Root_and_two_whole_STATIC_PASS"]is True and Q["protected_metadata_unchanged"]is True,"Actual qualified stopped F SourceRO")
    SWA=checked_control(SPEC["source_software_metadata"],SPEC["source_software_receipt"])
    need(SWA["schema"]=="final-composer-software.v7"and SWA["scientific_scope"]=="SOFTWARE_FIXTURES_ONLY"
     and SWA["status"]==SPEC["source_software_status"]and SWA["production_science_accepted"]is False and SWA["archive_or_restore_complete"]is False and SWA["ACTIVE_changed"]is False,"Qualified actual F software only")
    CT=checked_control(SPEC["software_contracts_metadata"],SPEC["software_contracts_receipt"])
    need(SWA["contracts"]==SPEC["software_contracts_receipt"]and CT["status"]=="PASS"and CT["tests_run"]==SPEC["software_expected_test_count"]and CT["failures"]==CT["errors"]==0 and CT["tested_source"]==SWA["source"],"Externally qualified actual software contracts")
    need(ST["actual_Source_groups_frozen"]==SWA["source"]and ST["actual_contracts"]==SWA["contracts"],"Full ST47 frozen Source44/contract provenance")
    need(type(ST["actual_Source_groups_original"])is dict and set(ST["actual_Source_groups_original"])==set(SWA["source"])
     and all(type(ST["actual_Source_groups_original"][k])is list and len(ST["actual_Source_groups_original"][k])==len(SWA["source"][k])for k in SWA["source"]),"Separate complete original Source44 provenance retained")
    for group in SWA["source"]:
     for original,frozen in zip(ST["actual_Source_groups_original"][group],ST["actual_Source_groups_frozen"][group]):
      rid(original);rid(frozen);need(fp(original)==fp(frozen)and original["path"]in ORIGINAL
       and ORIGINAL[original["path"]]["bytes"]==original["bytes"],"Original and frozen complete Source identities preserve the same FP")
    H=initial_metadata_control(BINDING["hro"])
    need(H["schema"]==SPEC["human_readonly_schema"]and H[SPEC["human_static_PASS_field"]]is True and H["Human_after"]==BINDING["human"]
     and H["source_proposal_metadata_after"]==[BINDING["proposal"],BINDING["proposalD"]]
     and H["publisher_first_pin_Source_metadata_original"]==first_pin_records
      and H["publisher_HANDOFF_metadata_after"]==publisher_handoff_md,"Actual selfHRO, unchanged90 and separate currentHANDOFF binding")
    code_records=SPEC["source44_metadata"];code_receipts=SPEC["source44_receipts"]
    need(len(code_records)==len(code_receipts)==44 and len({v["path"]for v in code_records})==44,"Exact qualified Source44")
    for v,r in zip(code_records,code_receipts):
     md_shape(v);rid(r);ordinary(v["path"])
     need(stat.S_ISREG(v["mode"])and v["nlink"]==1 and not(v["mode"]&0o222)and v["path"]==r["path"],"Readonly Code44")
    enroll(code_records);allow(code_records,"QUALIFIED_CODE44_BYTES")
    for v,r in zip(code_records,code_receipts):need(hash_own(v["path"])==r,"Qualified Code44 BEFORE first project import")
    need([r for values in SWA["source"].values()for r in values]==code_receipts,"Code44 exact actual software snapshot")
    for v in SPEC["source_directory_metadata"]:directory(v)
    for path,names in SPEC["source_directory_children"].items():need(sorted(os.listdir(path))==sorted(names),"Qualified source directory universe")
    core_check()
    control_pins=[];pre_pins={}
    for v in list(BINDING.values())+claim_rows+readiness_native_original+[SPEC["stage_terminal_metadata"],SPEC["source_readonly_metadata"],SPEC["publisher_source_readonly_metadata"],SPEC["source_software_metadata"],SPEC["source_software_terminal_metadata"],SPEC["software_contracts_metadata"],failed_tro_md,publisher_handoff_md]:
     if stat.S_ISREG(v["mode"]):
      if v["path"]not in PAYLOAD:allow([v],"EXPLICIT_CONTROL_OWN_BYTES")
      pre_pins[v["path"]]=hash_own(v["path"]);control_pins.append(pre_pins[v["path"]])
    need(pre_pins[failed_tro_md["path"]]==failed_tro_pin,"Same CPU failedTRO pin cannot change before project imports")
    OWN=Path(code_records[0]["path"]).parent
    need([Path(v["path"]).name for v in code_records[:15]]==
     ["final_delivery_composer.py","test_final_delivery_composer.py","composer_bootstrap.py","composer_cpu.sbatch","composer_contracts_cpu.sbatch","HANDOFF.md","composer_context_api.py","relative_archive_restore.py","github_export_context.py","test_github_export_context.py","restored_index_scope.py","test_restored_index_scope.py","finite_source_delivery_context.py","test_finite_source_delivery_context.py","qualified_source_semantics.py"],"Actual OWN15 order")
    # Only this already authenticated actual module is loaded. No tests/bootstrap/audit/stage.
    f_spec=importlib.util.spec_from_file_location("root_qualified_finite_publisher_context",OWN/"finite_source_delivery_context.py")
    f=importlib.util.module_from_spec(f_spec);sys.modules[f_spec.name]=f;f_spec.loader.exec_module(f)
    semantic_receipt=code_receipts[14]
    g=f._load_semantics_bytes(read_own(semantic_receipt["path"],1024*1024),semantic_receipt)
    need(f.SCHEMA=="finite-final-source-delivery-context.v3"and f.SEMANTICS_FP==fp(semantic_receipt),"Exact stopped qualified pure interface")
    need(SWA["software_fixture_inputs"]==Q["software_fixture_DATA_receipts"]and SWA["software_fixture_input_native_before"]==SWA["software_fixture_input_native_after"]==Q["software_fixture_DATA_metadata_original"],"Qualified four DATA provenance")
    need(SWA["software_operational_source_provenance_byte_fixture_metadata"]==Q["software_fixture_SOURCE_BYTE_metadata_original"],"Qualified six nonexecuted Source byte provenance")
    
    producer=SPEC["producer_receipts"];producer_md=SPEC["producer_metadata"]
    need(set(producer)==set(producer_md)==f.PRODUCER_KEYS,"Exact A/CA/I/C descriptors")
    for k in producer:
     checked_control(producer_md[k],producer[k],f.MAX_SOURCE_CLOSURE if k=="source_closure"else f.MAX_CONTROL)
    stage=checked_control(SPEC["stage_acceptance_metadata"],SPEC["stage_acceptance_receipt"])
    I=strict(read_own(producer["source_inclusion"]["path"],4*1024*1024))
    need(I["schema"]=="benchmark-source-inclusion.v3"and I["status"]=="SOURCE_INCLUSION_AUDIT_PASS"and I["applied"]is False and not I["issues"],"Immutable accepted Source I")
    need(stage["status"]=="EXACT_AUDITED_FROZEN_SOURCE_SET_INSTALLED_NOT_GIT_STAGED"and stage["source_inclusion"]==producer["source_inclusion"]and stage["entry_n"]==len(I["files"]),"Actual selected stage")
    need(I["runner_source_snapshot"]and any(Path(r["path"]).name=="final_source_closure.py"and fp(r)==f.SEMANTICS_FP for r in I["runner_source_snapshot"]),"I selected same qualified Source semantics")
    # Every introduced control is literal/own-byte only, not recursive receipt discovery.
    control_objects={};control_receipts={}
    def admit_control(row):
     need(type(row)is dict and set(row)=={"receipt","native"},"Closed explicit Source control")
     r=row["receipt"];v=row["native"]
     obj=checked_control(v,r,f.MAX_SOURCE_CLOSURE if r==producer["source_closure"]else f.MAX_CONTROL)
     control_objects[rid(r)]=obj;control_receipts[rid(r)]=r
     return obj
    for row in SPEC["existing_authority_controls"]+REQUEST["source_control_metadata"]:
     admit_control(row)
    need(REQUEST["source_control_receipts"]==[x["receipt"]for x in REQUEST["source_control_metadata"]],"Exact separate Source control tuple list")
    # The request's candidate authority ledger is independently actual-control authenticated.
    authorities={}
    for row in REQUEST["candidate_authority_controls"]:
     need(type(row)is dict and set(row)=={"receipt","native"},"Closed candidate authority control")
     obj=admit_control(row);authorities[rid(row["receipt"])]=obj
    def select_field(obj,field):
     need(type(field)is list and all(type(x)is str for x in field),"Exact field path")
     for x in field:obj=obj[int(x)]if isinstance(obj,list)else obj[x]
     return obj
    need(type(REQUEST["source_candidates"])is list and REQUEST["source_candidates"],"Finite actual source declarations")
    candidate_declarations=list(REQUEST["source_candidates"])
    initial_self_paths={BINDING[tag]["path"]for tag in("human","script","proposal")}
    need(not any(d.get("literal_path")in initial_self_paths for d in candidate_declarations if type(d)is dict),"Initial roster excludes own Human/script/proposal before append")
    candidate_authorities={};used_first_pin=set();used_failed_self=set();used_publisher_HANDOFF=False
    need(len(candidate_declarations)==692,"Exactly derived old688 +fixedoldV4three +currentHANDOFF initial Source declarations")
    DECL_REQUIRED={"literal_path","original_native","kind","roles","public_destinations","selected_destination","authority","logical_receipts"}
    decl_paths=set()
    for d in candidate_declarations:
     need(type(d)is dict and DECL_REQUIRED<=set(d)<=DECL_REQUIRED|{"known_CPU_tuple"},"Closed declared candidate, no future tuple")
     md_shape(d["original_native"]);need(d["literal_path"]==d["original_native"]["path"]and d["literal_path"]not in decl_paths,"Literal unique path")
     decl_paths.add(d["literal_path"]);ordinary(d["literal_path"])
     need(stat.S_ISREG(d["original_native"]["mode"])and d["original_native"]["nlink"]==1,"Declared actual Source regular/singlelink; old mode preserved")
     need(d["kind"]in("IMPLEMENTATION","TEST","DOCUMENT","CONFIGURATION_OR_LAUNCHER")and type(d["roles"])is list and d["roles"]and all(type(x)is str for x in d["roles"]),"Original Source kind/roles")
     need(type(d["public_destinations"])is list and d["public_destinations"]and len(set(d["public_destinations"]))==len(d["public_destinations"])and d["selected_destination"]in d["public_destinations"],"All destinations +one explicit chosen destination")
     need(type(d["logical_receipts"])is list and not d["logical_receipts"],"Late declaration introduces only its actual original path identity")
     authority=d["authority"];need(type(authority)is dict,"Explicit candidate authority")
     if set(authority)=={"post_HRO_authority","field"}:
      if authority["post_HRO_authority"]=="publisher_first_pin_Source":
       need(type(authority["field"])is list and len(authority["field"])==2
        and authority["field"][0]=="publisher_first_pin_Source_metadata_original"
        and authority["field"][1]in {str(i)for i in range(90)},"Only canonical closed90 postHRO Source authority")
       index=int(authority["field"][1]);expected=first_pin_records[index]
       need(d["literal_path"]==first_pin_paths[index]and d["original_native"]==expected
        and select_field(H,authority["field"])==expected and "known_CPU_tuple"not in d,"Exact first-pin Source path/native, no invented tuple")
       used_first_pin.add(index);candidate_authorities[d["literal_path"]]={"control":pre_pins[BINDING["hro"]["path"]],"field":list(authority["field"])}
      else:
       hand_dest="delivery_tools/root_operational_programs/"+Path(SPEC["self_proposal_directory"]).name+"/HANDOFF.md"
       need(authority["post_HRO_authority"]=="publisher_HANDOFF_Metadata"
        and authority["field"]==["publisher_HANDOFF_metadata_after"]
        and d["literal_path"]==publisher_handoff_md["path"]and d["original_native"]==publisher_handoff_md
        and select_field(H,authority["field"])==publisher_handoff_md
        and d["kind"]=="DOCUMENT"and d["roles"]==["final_delivery_tools"]
        and d["public_destinations"]==[hand_dest]and d["selected_destination"]==hand_dest
        and "known_CPU_tuple"not in d,"Only exact current V5 HANDOFF Doc, currentHRO Native authority")
       used_publisher_HANDOFF=True;candidate_authorities[d["literal_path"]]={"control":pre_pins[BINDING["hro"]["path"]],"field":["publisher_HANDOFF_metadata_after"]}
     elif set(authority)=={"post_failed_terminal_authority","field"}:
      need(authority["post_failed_terminal_authority"]=="fixed_v4_self_sources"
       and type(authority["field"])is list and len(authority["field"])==2
       and authority["field"][0]=="failed_publisher_self_source_metadata_original"
       and authority["field"][1]in {"0","1","2"},"Only canonical fixed oldV4 three-source metadata authority")
      index=int(authority["field"][1]);expected=failed_self_records[index]
      destination=failed_self_destinations[failed_self_tags[index]]["repository_relative"]
      need(d["literal_path"]==failed_self_paths[index]and d["original_native"]==expected
       and d["kind"]==failed_self_kinds[index]and d["roles"]==["final_delivery_tools"]
       and d["public_destinations"]==[destination]and d["selected_destination"]==destination
       and "known_CPU_tuple"not in d,"Old V4 selfSources preserve full Native/kind/roles/declared destination; first CPU bytes only")
      used_failed_self.add(index);candidate_authorities[d["literal_path"]]={"control":failed_tro_pin,"field":list(authority["field"])}
     else:
      need(set(authority)=={"control","field"}and d["literal_path"]not in first_pin_paths
       and d["literal_path"]not in failed_self_paths and d["literal_path"]!=publisher_handoff_md["path"],
       "Existing qualified authority only outside all closed extra Source variants")
      need(rid(authority["control"])in authorities and select_field(authorities[rid(authority["control"])],authority["field"])==d["original_native"],"Candidate actual native proved by fixed qualified authority")
     if "known_CPU_tuple"in d:rid(d["known_CPU_tuple"]);need(d["known_CPU_tuple"]["path"]==d["literal_path"],"Known actual tuple path")
    need(used_first_pin==set(range(90))and used_failed_self==set(range(3))and used_publisher_HANDOFF is True,
     "All unchanged90, fixedoldV4three and currentHANDOFF Source obligations retained")
    enroll([d["original_native"]for d in candidate_declarations]);allow([d["original_native"]for d in candidate_declarations],"FINITE_PUBLIC_SOURCE_ORIGINAL_BYTES")
    cache_table,cache_dirs,cache_members=f.operational_stage_table(T)
    need(len(cache_dirs)==14 and len(cache_members)==13060,"Exact actual Stage cache13060/14")
    enroll(cache_dirs+cache_members)
    for v in cache_members:ordinary(v["path"])
    allow(cache_members,"FIXED_CACHE_EVIDENCE_OWN_BYTES")
    for root,v in zip(f.CACHE_ROOTS,cache_dirs):
     need(native_metadata(Path(root))==v and sorted(os.listdir(root))==sorted(Path(x["path"]).name for x in cache_members if str(Path(x["path"]).parent)==root),"Fixed direct cache universe only")
    raw_six=[cache_table[path]for path in f.WRAPPER_ORIGINAL_PATHS]
    enroll(raw_six);allow(raw_six,"FIXED_SIX_NONEXECUTED_OPERATIONAL_SOURCE_BYTES")
    for v in raw_six:need(stat.S_ISREG(v["mode"])and v["nlink"]==1 and stat.S_IMODE(v["mode"])==0o444,"Six actual fixed readonly sources")
    need(type(REQUEST["self_source_destinations"])is dict and set(REQUEST["self_source_destinations"])=={"human","script","proposal"},"Exact own publisher Source declarations")
    for tag in ("human","script","proposal"):
     v=BINDING[tag];d=REQUEST["self_source_destinations"][tag]
     need(type(d)is dict and set(d)=={"kind","roles","repository_relative"}and d["kind"]==g.kind(v["path"]),"Actual own Source kind")
     candidate_declarations.append(dict(literal_path=v["path"],original_native=v,kind=d["kind"],roles=d["roles"],public_destinations=[d["repository_relative"]],selected_destination=d["repository_relative"],authority={"postHRO_primary_binding":tag},logical_receipts=[],known_CPU_tuple=pre_pins[v["path"]]))
     enroll([v]);allow([v],"FINITE_PUBLIC_SOURCE_ORIGINAL_BYTES")
    txt_md=ORIGINAL.get(f.SOURCE_TEXT_ORIGIN)
    need(txt_md is not None and txt_md["bytes"]==f.SOURCE_TEXT_BYTES,"Exact fixed original TXT already in protected metadata")
    allow([txt_md],"SOLE_NONOPERATIVE_TEXT_BRIDGE_BYTES")
    for row in I["files"]:
     r=subset(row["source"]);rid(r);need(r["path"]in ORIGINAL,"All I physical inputs bound by actual current original native")
     allow([ORIGINAL[r["path"]]],"IMMUTABLE_I_PHYSICAL_SOURCE_BYTES")
    # Two distinct purposes may refer to the same path; only explicit equivalent Source/evidence
    # purposes are merged, never Common or worker payload grants.
    CAP=control_objects.get(rid(next(r for r in control_receipts.values()if r["path"]==f.LEGACY_CAPTURE_PATH)))
    need(CAP is not None,"Existing actual legacy CAP own object")
    PUB=S/"runs"/(SPEC["publication_namespace"]+jid)
    OP=S/"submissions"/(f.OPERATIONAL_ROOT_PREFIX+jid)
    PD=S/"submissions"/(SPEC["proof_namespace"]+jid)
    TMP=S/"tmp"/(SPEC["tmp_namespace"]+jid)
    for p in(PUB,OP,PD,TMP):need(not p.exists()and not p.is_symlink(),"Exclusive absent publication roots")
    expected_names={};phase="before_output";installed=[];copy_receipts=[];target_before={}
    def new_dir(p,mode=0o775):
     p=Path(p);need(p.parent.is_dir()and not p.exists()and not p.is_symlink(),"Exact missing owned directory")
     p.mkdir(mode=mode);v=native_metadata(p);created(v);NEW_DIRS[str(p)]=v;expected_names[str(p)]=set()
     if str(p.parent)in expected_names:expected_names[str(p.parent)].add(p.name)
     return p
    for p in(PUB,OP,PD,TMP):new_dir(p)
    operational_allowed_children={str(S/"submissions"):{D.name,OP.name,PD.name},str(S/"runs"):{PUB.name},str(S/"tmp"):{TMP.name},str(S/"frozen"):set()}
    operational_parent_events=[]
    for path,before in operational_parent_before.items():
     permitted=operational_allowed_children[path];old=operational_parent_names[path];p=Path(path)
     need(not(set(old)&permitted),"Operational children must be newly absent exact namespaces")
     children=sorted(os.listdir(p));after=native_metadata(p)
     need(children==sorted(set(old)|permitted)and all(after[k]==before[k]for k in("inode","dev","uid","gid","mode")),"Only declared operational child additions, no old permission/identity change")
     need(after["nlink"]==before["nlink"]+len(permitted),"Operational parent nlink equals exact new directory count")
     if not permitted:need(after==before,"Frozen parent full original native/name universe unchanged")
     need(path not in EVENTS,"Operational parent event cannot be recaptured");EVENTS[path]=after
     need(native_metadata(p)==after,"Operational parent stable after name read")
     operational_parent_events.append(dict(path=path,before=before,after=after,names_before=list(old),declared_added_children=sorted(permitted),names_after=children,permission_unchanged=True))
    SRC=new_dir(PUB/"source_text_bytes");BRIDGE_D=new_dir(PUB/"source_bridge");CONTROL_D=new_dir(PUB/"control_bytes")
    SHELL=new_dir(OP/"operational_shell_sources");EVIDENCE=new_dir(OP/"operational_evidence")
    os.environ["TMPDIR"]=str(TMP)
    LATE_COPY=new_dir(PUB/"late_source_copies")
    PARTIAL_PATHS=[]
    def mark_file(p,v,purpose):
     created(v);allow([v],purpose);expected_names[str(p.parent)].add(p.name)
    def durable(p):
     before=matches(p);fd=os.open(str(p),os.O_RDONLY|os.O_NOFOLLOW)
     try:
      st=os.fstat(fd);need(st.st_ino==before["inode"]and st.st_dev==before["dev"]and st.st_mode==before["mode"],"Durable exact fd")
      os.fsync(fd)
     finally:os.close(fd)
     need(native_metadata(Path(p))==before,"Durable own native unchanged")
    def copy_own(source,destination,purpose,text_source=False):
     source=ordinary(source);before=matches(source);need(str(source)in PAYLOAD,"Explicit source/copy purpose")
     destination=ordinary(destination.parent)/destination.name
     need(not destination.exists()and not destination.is_symlink(),"Exclusive own copy target")
     sfd=os.open(str(source),os.O_RDONLY|os.O_NOFOLLOW)
     PARTIAL_PATHS.append(str(destination));expected_names[str(destination.parent)].add(destination.name)
     dfd=os.open(str(destination),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o664)
     h=hashlib.sha256();size=0
     try:
      st=os.fstat(sfd);need(st.st_ino==before["inode"]and st.st_dev==before["dev"]and st.st_mode==before["mode"]and st.st_nlink==1,"Original input fd")
      with os.fdopen(sfd,"rb",closefd=False)as inp,os.fdopen(dfd,"wb",closefd=False)as out:
       for block in iter(lambda:inp.read(1024*1024),b""):out.write(block);h.update(block);size+=len(block)
       out.flush();os.fsync(dfd)
      os.fchmod(dfd,0o444);os.fsync(dfd)
     finally:os.close(sfd);os.close(dfd)
     need(size==before["bytes"]and native_metadata(source)==before,"Original source/copy drift")
     v=native_metadata(destination);need(stat.S_ISREG(v["mode"])and v["nlink"]==1 and stat.S_IMODE(v["mode"])==0o444,"Own readonly singlelink copy")
     mark_file(destination,v,purpose)
     result=dict(path=str(destination),bytes=size,sha256=h.hexdigest())
     need(hash_own(destination)==result,"FIRST enrolled full own copy readback")
     if text_source:
      raw=read_own(destination,max(size,1));text=raw.decode("utf-8","strict")
      need(not SECRET_RE.search(text)and "-----BEGIN "+"OPENSSH PRIVATE KEY-----"not in text,"Same selected-public-source secret policy")
     copy_receipts.append(result);return result,v
    SECRET_RE=re.compile(r"(?im)(?:password|access_token|secret_key|api_key|private_key)\s*[:=]\s*[\"']?(?!None\b|null\b|os\.|env\b|\$\{|<|YOUR_|getenv\b)[A-Za-z0-9+/=_-]{12,}")
    def dump_own(path,obj,limit=20*1024*1024):
     raw=(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")
     need(len(raw)<=limit,"Declared own JSON byte bound BEFORE write")
     fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o664)
     try:
      with os.fdopen(fd,"wb",closefd=False)as out:out.write(raw);out.flush();os.fsync(fd)
      os.fchmod(fd,0o444);os.fsync(fd)
     finally:os.close(fd)
     v=native_metadata(path);mark_file(path,v,"NEW_PROOF_OR_MANIFEST_OWN_BYTES")
     need(read_own(path,limit)==raw and strict(read_own(path,limit))==obj,"Durable complete own object readback")
     return hash_own(path)
    def seal_owned_directory(p):
     p=Path(p);before=CREATED[str(p)]
     need(sorted(os.listdir(p))==sorted(expected_names[str(p)]),"Exact declared created directory universe")
     fd=os.open(str(p),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
     try:os.fchmod(fd,0o555);os.fsync(fd)
     finally:os.close(fd)
     after=native_metadata(p)
     need(all(after[k]==before[k]for k in("inode","dev","uid","gid"))and stat.S_IMODE(after["mode"])==0o555,"Declared own directory creation/fill/seal event")
     need(str(p)not in EVENTS,"No final directory event refresh");EVENTS[str(p)]=after
     return after
    
    # Runtime workload: each definition is inert until the owned CPU executes this body.
    all_input_pins=dict(pre_pins)
    for r in list(control_receipts.values())+list(producer.values())+[SPEC["stage_acceptance_receipt"]]:
     need(r["path"]not in all_input_pins or all_input_pins[r["path"]]==r,"Closed control pin conflict");all_input_pins[r["path"]]=r
    payloads={};late_rows=[];transport_rows=[];public_rows=list(I["files"])
    source_first_pins=[];operational_caches=[];operational_new=[];operational_legacy=[]
    def remember(r):
     k=rid(r);p=r["path"]
     need(p not in all_input_pins or all_input_pins[p]==r,"One original path cannot change full bytes")
     all_input_pins[p]=dict(r);return r
    def actual_original(v,expected=None,purpose=None):
     enroll([v])
     if purpose:allow([v],purpose)
     r=hash_own(v["path"])
     if expected is not None:need(r==expected,"Known actual full tuple differs")
     return remember(r)
    def destination(s):
     need(type(s)is str and s and not s.startswith("/")and "\\"not in s and "\0"not in s,"Safe literal public destination")
     p=Path(s);need(p.as_posix()==s and all(x not in("","..",".",".git",".ssh")for x in p.parts),"Exact public destination")
     need(not any(x in p.parts for x in("env","site-packages","weights","params","assets")),"No runtime/science target")
     return R/"source"/p
    def late_row(original,physical,dest,kind,roles,logical=()):
     rid(original);rid(physical);destination(dest)
     need(fp(original)==fp(physical)and type(roles)is list and roles and len(roles)==len(set(roles)),"Complete late identity/role tuple")
     g.eligible_public(original,dest);need(g.kind(original["path"])==kind,"Original Source kind retained")
     need(all(fp(r)==fp(original)for r in logical),"Every logical identity retains complete FP")
     row=dict(logical_receipt=original,physical_receipt=physical,repository_relative=dest,kind=kind,roles=list(roles))
     if logical:row["logical_receipts"]=list(logical)
     late_rows.append(row);return row
    phase="finite_source_first_actual_pins"
    # All existing I physical instances are authenticated independently. No filename-derived SHA.
    i_physical={}
    for row in I["files"]:
     r=subset(row["source"]);k=rid(r)
     if k not in i_physical:
      actual_original(ORIGINAL[r["path"]],r)
      i_physical[k]=r
    for n,d in enumerate(candidate_declarations):
     original=actual_original(d["original_native"],d.get("known_CPU_tuple"))
     need(original["path"]!=f.SOURCE_TEXT_ORIGIN and original["path"]not in f.WRAPPER_ORIGINAL_PATHS,"TXT/raw wrapper is not Source")
     for dest in d["public_destinations"]:g.eligible_public(original,dest)
     need(g.kind(original["path"])==d["kind"],"Original candidate extension/kind")
     suffix=Path(original["path"]).suffix
     copyD=new_dir(LATE_COPY/("%04d"%n))
     physical,copy_md=copy_own(original["path"],copyD/Path(original["path"]).name,"PUBLIC_SOURCE_OWN_COPY_BYTES",True)
     need(fp(physical)==fp(original),"Candidate full bytecopy")
     source_first_pins.append(dict(original=original,original_native=d["original_native"],physical=physical,physical_native=copy_md,
      public_destinations=d["public_destinations"],selected_destination=d["selected_destination"],authority=candidate_authorities.get(d["literal_path"],d["authority"])))
     for dest in d["public_destinations"]:
      late_row(original,physical,dest,d["kind"],d["roles"],d["logical_receipts"])
    # The four new .sh Source identities are actual newly created files. Originals stay nonoperative evidence.
    phase="six_wrapper_and_all_cache_evidence"
    raw_known={r["path"]:r for r in SWA["software_operational_source_provenance_byte_fixture_receipts"]}
    need(set(raw_known)==set(f.WRAPPER_ORIGINAL_PATHS),"Actual qualified raw-six full tuples")
    for n,fixed in enumerate(f.WRAPPER_NEW_FOUR):
     v=cache_table[fixed[0]];original=actual_original(v,raw_known[fixed[0]],"FIXED_SIX_NONEXECUTED_OPERATIONAL_SOURCE_BYTES")
     need(original["bytes"]==fixed[1],"Fixed new raw wrapper actual size")
     evidence,em=copy_own(original["path"],EVIDENCE/("wrapper_new_%02d.OPAQUE.txt"%n),"NONOPERATIVE_EVIDENCE_OWN_BYTES")
     eligible,sm=copy_own(original["path"],SHELL/(fixed[2]+".sh"),"NEW_ELIGIBLE_SHELL_SOURCE_BYTES",True)
     need(fp(original)==fp(evidence)==fp(eligible),"Actual new shell/evidence full FP")
     operational_new.append(dict(original_text=original,original_metadata=v,evidence_copy=evidence,evidence_metadata=em,
      eligible_source=eligible,eligible_source_metadata=sm,repository_relative=fixed[3]))
     late_row(eligible,eligible,fixed[3],"CONFIGURATION_OR_LAUNCHER",["final_delivery_tools"])
    for n,fixed in enumerate(f.WRAPPER_LEGACY_TWO,4):
     v=cache_table[fixed[0]];expected=dict(path=fixed[0],bytes=fixed[1],sha256=fixed[2])
     original=actual_original(v,expected,"FIXED_SIX_NONEXECUTED_OPERATIONAL_SOURCE_BYTES")
     preserved=dict(path=fixed[3],bytes=fixed[1],sha256=fixed[2]);need(preserved["path"]in ORIGINAL,"Legacy shell original native member")
     allow([ORIGINAL[preserved["path"]]],"IMMUTABLE_I_PHYSICAL_SOURCE_BYTES");actual_original(ORIGINAL[preserved["path"]],preserved)
     evidence,em=copy_own(original["path"],EVIDENCE/("wrapper_legacy_%02d.OPAQUE.txt"%(n-4)),"NONOPERATIVE_EVIDENCE_OWN_BYTES")
     operational_legacy.append(dict(original_text=original,original_metadata=v,evidence_copy=evidence,evidence_metadata=em,
      eligible_source=preserved,eligible_source_metadata=ORIGINAL[preserved["path"]],repository_relative=fixed[4]))
    for n,v in enumerate(cache_members):
     original=actual_original(v,purpose="FIXED_CACHE_EVIDENCE_OWN_BYTES")
     evidence,em=copy_own(original["path"],EVIDENCE/("cache_%05d.OPAQUE.txt"%n),"NONOPERATIVE_EVIDENCE_OWN_BYTES")
     need(fp(original)==fp(evidence),"Every cache physical instance actually byte-identical")
     operational_caches.append(dict(original_receipt=original,original_metadata=v,evidence_copy=evidence,evidence_metadata=em))
    need(len(operational_caches)==13060 and len({x["evidence_copy"]["path"]for x in operational_caches})==13060,"No cache identity collapse")
    # The sole fixed TXT bridge; neither original nor .py copy is imported, compiled or executed.
    phase="sole_nonoperative_text_bridge"
    text_original=actual_original(txt_md,purpose="SOLE_NONOPERATIVE_TEXT_BRIDGE_BYTES")
    py_r,py_md=copy_own(text_original["path"],SRC/f.SOURCE_TEXT_PY,"SOLE_ELIGIBLE_PY_SOURCE_COPY_BYTES",True)
    late_row(py_r,py_r,f.SOURCE_TEXT_DEST,"IMPLEMENTATION",["final_delivery_tools","RECURSIVE_OPERATIVE_SOURCE"])
    allocation=dict(job_id=jid,allocated_CPUs=1,allocated_gpus=0,current_owner_account_partition=attempts[selected-1]["actual_row"][3:],
     current_scontrol_record=ctl.stdout.decode("utf-8"),current_sacct_record=attempts[selected-1]["actual_row"])
    f._operational_cpu(allocation)
    # Proofs are durably written before the manifest, with no own-future hash prerequisite.
    for v in raw_six+cache_members+[txt_md]:need(hash_own(v["path"])==all_input_pins[v["path"]],"Operational originals pre/end full bytes")
    operational=dict(schema=f.OPERATIONAL_SCHEMA,status=f.OPERATIONAL_STATUS,
     source_inclusion=producer["source_inclusion"],stage_acceptance=SPEC["stage_acceptance_receipt"],
     stage_terminal_metadata=pre_pins[SPEC["stage_terminal_metadata"]["path"]],
     legacy_capture=control_receipts[rid(next(r for r in control_receipts.values()if r["path"]==f.LEGACY_CAPTURE_PATH))],
     publisher_output_root=str(OP),allocation=allocation,new_four=operational_new,legacy_two=dict(capture=next(r for r in control_receipts.values()if r["path"]==f.LEGACY_CAPTURE_PATH),entries=operational_legacy),cache_history=dict(directories=cache_dirs,members=operational_caches),
     original_bytes_and_native_pre_end_afteroutput_PASS=True,original_or_copied_programs_executed=False,
     original_text_promoted_to_Source=False,cache_Source_IDs_invented=False,generic_reader_permission_changed=False,
     scientific_or_restore_acceptance=False,ACTIVE_changed=False)
    need(set(operational)==f.OPERATIONAL_KEYS,"Source-defined operational proof exact keys")
    # Parent directories used as historical evidence retain their exact original native, no chmod.
    for v in cache_dirs+raw_six+[txt_md]:need(native_metadata(Path(v["path"]))==v,"Operational original metadata before proof")
    op_r=dump_own(OP/"operational_source_provenance.json",operational,f.MAX_OPERATIONAL_PROOF)
    # Bridge proof is its own fixed submissions child, outside the exact three-child OP root.
    bridgeD=new_dir(PD/"source_text_bridge")
    bridge_base=dict(schema=f.BRIDGE_SCHEMA,role=f.BRIDGE_ROLE,original_text=text_original,
     original_metadata_before=txt_md,original_metadata_after=txt_md,eligible_copy=py_r,eligible_copy_metadata=py_md,repository_relative=f.SOURCE_TEXT_DEST)
    bridge_proof=dict(bridge_base,source_inclusion=producer["source_inclusion"],stage_acceptance=SPEC["stage_acceptance_receipt"],
     publisher_output_root=str(PUB),allocation=allocation,original_or_copied_text_executed=False,
     original_text_promoted_to_Source=False,generic_reader_permission_changed=False)
    need(set(bridge_proof)==f.BRIDGE_PROOF_KEYS,"Source-defined bridge proof exact keys")
    bridge_r=dump_own(bridgeD/"byte_identity_proof.json",bridge_proof)
    bridge=dict(bridge_base,byte_identity_proof=bridge_r)
    f.source_text_bridge_shape(bridge,bridge_proof,read_own(py_r["path"],f.SOURCE_TEXT_BYTES),producer["source_inclusion"],SPEC["stage_acceptance_receipt"],g)
    manifest=dict(schema="finite-late-source-publication.v2",
     status="EXACT_FINITE_LATE_SOURCE_TREE_BYTES_CPU_VERIFIED_NOT_SCIENTIFIC_ACCEPTANCE",
     source_inclusion=producer["source_inclusion"],stage_acceptance=SPEC["stage_acceptance_receipt"],
     files=late_rows,source_text_provenance_bridges=[bridge],raw_JSON_rewritten=False,
     source_inclusion_rewritten=False,Source_IDs_invented=False,filename_SHA_inferred=False)
    # All source destinations are installed before this truthful publication status is written.
    public_rows.extend(dict(original_source=r["logical_receipt"],source=r["physical_receipt"],
     repository_relative=r["repository_relative"],kind=r["kind"],roles=r["roles"],logical_receipts=r.get("logical_receipts",[]))for r in late_rows)
    identities,by_fp,dests=f.identity_multimap(public_rows)
    need(all(k[0]!=f.SOURCE_TEXT_ORIGIN for k in identities),"Original TXT not Source")
    # Root selects each I identity's route by complete identity+actual row, never first/lexical/FP lookup.
    i_keys=f.identity_multimap(I["files"])[0]
    selected_routes={}
    for choice in REQUEST["i_source_route_choices"]:
     need(type(choice)is dict and set(choice)=={"original","selected_physical","repository_relative"},"Closed explicit I route")
     k=rid(choice["original"]);need(k in i_keys and k not in selected_routes,"I route identity unique")
     need(any(subset(x["source"])==choice["selected_physical"]and x["repository_relative"]==choice["repository_relative"]for x in i_keys[k]),"I explicit selected full candidate")
     selected_routes[k]=choice
    need(set(selected_routes)==set(i_keys),"Every I original/logical/physical identity explicitly selected")
    for d,pair in zip(candidate_declarations,source_first_pins):
     original=pair["original"];physical=pair["physical"];dest=d["selected_destination"]
     k=rid(original);route=dict(original=original,selected_physical=physical,repository_relative=dest)
     if k in selected_routes:need(selected_routes[k]==route,"Duplicate identity requires exact compatible explicit route")
     else:selected_routes[k]=route
    for r in late_rows:
     # New .sh/.py identities and actual physical copies have one explicit compatible route,
     # which is stored even when several same-FP copies/destinations exist.
     for logical in [r["logical_receipt"]]+r.get("logical_receipts",[])+[r["physical_receipt"]]:
      k=rid(logical)
      if k not in identities or k in selected_routes:continue
      candidates=identities[k]
      if logical==r["physical_receipt"]:
       candidates=[x for x in candidates if subset(x["source"])==logical]
       own_dests={x["repository_relative"]for x in candidates}
       # Physical self-route destination uses its parent's explicit selected declaration.
       declared=[x["selected_destination"]for x in candidate_declarations if any(p["physical"]==logical and p["original"]["path"]==x["literal_path"]for p in source_first_pins)]
       if declared:dest=declared[0];need(len(set(declared))==1,"Physical copy explicit destination conflict")
       else:need(len(own_dests)==1,"New physical source with multiple dests needs explicit declaration");dest=next(iter(own_dests))
       need(any(x["repository_relative"]==dest for x in candidates),"Physical destination explicitly authenticated")
       selected_routes[k]=dict(original=logical,selected_physical=logical,repository_relative=dest)
      else:
       need(len(candidates)==1,"Unselected logical candidate ambiguity")
       x=candidates[0];selected_routes[k]=dict(original=logical,selected_physical=subset(x["source"]),repository_relative=x["repository_relative"])
    routes=list(selected_routes.values())
    f._source_route_table(public_rows,routes)
    
    # Exact finite installed-target plan. No recursive directory walk, Source child discovery or Git.
    phase="finite_target_install"
    TARGETS={};parent_plans={};target_before={};target_after={};target_receipts={};created_targets=[]
    for row in public_rows:
     path=destination(row["repository_relative"]);r=subset(row["source"])
     if str(path)in TARGETS:need(fp(TARGETS[str(path)])==fp(r),"Two Source destinations have different complete bytes")
     else:TARGETS[str(path)]=r
    def current_target(path,expected):
     path=Path(path);v=expected_md(path)
     need(stat.S_ISREG(v["mode"])and v["nlink"]==1,"Installed Source regular/singlelink")
     if path==COMMON:
      need(path==R/"source/rebuild/benchmark_common_review.py"and fp(expected)==COMMON_FP
       and any(row["repository_relative"]=="rebuild/benchmark_common_review.py"and fp(row["source"])==COMMON_FP for row in I["files"])
       and v==SPEC["Common_original_metadata"],"Only exact installed-I Common SOURCE readback")
     else:
      ordinary(path);need(not conditional_target(path),"No conditional-runtime target Source")
     before=matches(path);fd=os.open(str(path),os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256();size=0
     try:
      st=os.fstat(fd);need(st.st_ino==before["inode"]and st.st_dev==before["dev"]and st.st_mode==before["mode"]and st.st_nlink==1,"Installed target original fd")
      with os.fdopen(fd,"rb",closefd=False)as stream:
       for block in iter(lambda:stream.read(1024*1024),b""):h.update(block);size+=len(block)
     finally:os.close(fd)
     need(size==before["bytes"]and native_metadata(path)==before,"Installed target native changed during read")
     result=dict(path=str(path),bytes=size,sha256=h.hexdigest())
     need(fp(result)==fp(expected),"Installed Source full bytes differ")
     return result
    def conditional_target(path):return any(x in Path(path).parts for x in("env","site-packages","weights","params","assets"))
    # Parent records are captured before the first target payload/write, then only declared additions are permitted.
    all_parent_paths=set()
    for target in TARGETS:
     p=Path(target).parent
     while True:
      need(p==R/"source"or(R/"source")in p.parents,"Exact installed parent authority")
      all_parent_paths.add(str(p))
      if p==R/"source":break
      p=p.parent
    for p in sorted(all_parent_paths,key=lambda x:(len(Path(x).parts),x)):
     q=Path(p)
     if q.exists()or q.is_symlink():
      ordinary(q);v=native_metadata(q);need(stat.S_ISDIR(v["mode"]),"Existing finite target parent directory")
      if p in ORIGINAL:need(ORIGINAL[p]==v,"Existing target parent differs from protected original")
      else:enroll([v])
      names_before=sorted(os.listdir(q))
      parent_plans[p]=dict(before=v,names_before=names_before,added_children=set(),created=False)
     else:parent_plans[p]=dict(before=None,names_before=[],added_children=set(),created=True)
    for p,plan in parent_plans.items():
     if plan["created"]:parent_plans[str(Path(p).parent)]["added_children"].add(Path(p).name)
    for p,r in TARGETS.items():
     q=Path(p)
     if q.exists()or q.is_symlink():
      ordinary(q);v=native_metadata(q);need(stat.S_ISREG(v["mode"])and v["nlink"]==1,"Existing target no link/hardlink")
      if p in ORIGINAL:need(ORIGINAL[p]==v,"Existing target matches original Stage/HRO native")
      else:enroll([v])
      target_before[p]=v;target_receipts[p]=current_target(q,r)
     else:parent_plans[str(q.parent)]["added_children"].add(q.name)
    for p,plan in parent_plans.items():
     if not plan["created"]:
      need(sorted(os.listdir(p))==plan["names_before"],"Target parent changed before first install")
      need(native_metadata(Path(p))==plan["before"],"Original target parent drift before install")
      if plan["added_children"]:need(plan["before"]["mode"]&0o200,"Existing target parent cannot add children without forbidden permission change")
    for p in sorted(all_parent_paths,key=lambda x:(len(Path(x).parts),x)):
     plan=parent_plans[p]
     if plan["created"]:
      q=Path(p);need(q.parent.is_dir()and not q.exists()and not q.is_symlink(),"Missing finite parent remains absent")
      q.mkdir(mode=0o775);v=native_metadata(q);created(v);NEW_DIRS[p]=v
    def install_source(path,r):
     q=Path(path);source=ordinary(r["path"]);before=matches(source)
     need(str(source)in PAYLOAD and fp(hash_own(source))==fp(r),"Only authenticated physical Source copy")
     need(not q.exists()and not q.is_symlink(),"Exclusive missing Source destination")
     ordinary(q.parent)
     sfd=os.open(str(source),os.O_RDONLY|os.O_NOFOLLOW);dfd=os.open(str(q),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o664)
     PARTIAL_PATHS.append(str(q))
     h=hashlib.sha256();size=0
     try:
      st=os.fstat(sfd);need(st.st_ino==before["inode"]and st.st_dev==before["dev"]and st.st_mode==before["mode"],"Installed input original fd")
      with os.fdopen(sfd,"rb",closefd=False)as inp,os.fdopen(dfd,"wb",closefd=False)as out:
       for block in iter(lambda:inp.read(1024*1024),b""):out.write(block);h.update(block);size+=len(block)
       out.flush();os.fsync(dfd)
     finally:os.close(sfd);os.close(dfd)
     # No chmod: retain actual newly installed mode as produced under the approved CPU environment.
     need((size,h.hexdigest())==fp(r)and native_metadata(source)==before,"Actual installed Source bytes/input native")
     v=native_metadata(q);need(stat.S_ISREG(v["mode"])and v["nlink"]==1,"Actual installed Source normal file")
     created(v);NEW_TARGETS[str(q)]=v;TARGET_PINS[str(q)]=r
     got=current_target(q,r);created_targets.append(str(q));return v,got
    for p,r in TARGETS.items():
     if p not in target_before:
      v,got=install_source(p,r);target_after[p]=v;target_receipts[p]=got
     else:target_after[p]=target_before[p]
    # Explicit parent addition events are fixed once; they are not new original baselines.
    parent_events=[]
    for p,plan in parent_plans.items():
     q=Path(p);after=native_metadata(q);expected_children=sorted(set(plan["names_before"])|plan["added_children"])
     need(sorted(os.listdir(q))==expected_children,"Exact declared children added, no other parent mutation")
     if plan["created"]:
      original=CREATED[p]
      need(all(after[k]==original[k]for k in("inode","dev","uid","gid","mode")),"New parent creation properties")
     else:
      original=plan["before"]
      need(all(after[k]==original[k]for k in("inode","dev","uid","gid","mode")),"Existing parent permissions/identity unchanged")
      new_dir_n=sum(str(q/name)in parent_plans and parent_plans[str(q/name)]["created"]for name in plan["added_children"])
      need(after["nlink"]==original["nlink"]+new_dir_n,"Directory hard-link count equals only created subdirectories")
      if not plan["added_children"]:need(after==original,"Unaffected parent keeps entire original native")
     need(p not in EVENTS,"No repeated parent event/baseline refresh")
     EVENTS[p]=after
     parent_events.append(dict(path=p,before=original,after=after,names_before=plan["names_before"],
      declared_added_children=sorted(plan["added_children"]),names_after=expected_children,created=plan["created"],permission_unchanged=True))
    def protected_children_after_install(path,original_children):
     if path not in parent_plans:return list(original_children)
     plan=parent_plans[path];q=Path(path)
     need((q==R/"source"or R/"source"in q.parents)and not plan["created"]
      and path in ORIGINAL and plan["before"]==ORIGINAL[path]
      and sorted(plan["names_before"])==sorted(original_children),"Affected saved Source directory must retain exact original native/name baseline")
     return sorted(set(original_children)|plan["added_children"])
    for p,r in TARGETS.items():
     need(current_target(p,r)==target_receipts[p]and native_metadata(Path(p))==target_after[p],"All installed destinations afteroutput")
    for p,v in target_before.items():need(native_metadata(Path(p))==v,"Original existing targets full native unchanged")
    f.late_publication_shape(manifest,producer["source_inclusion"],SPEC["stage_acceptance_receipt"],g)
    # This installation proof records real events, not Git staging or public publication.
    install_obj=dict(schema="root-finite-source-installation-readback.v1",
     status="ALL_EXPLICIT_I_AND_LATE_DESTINATIONS_FULL_BYTES_READ_BACK_NOT_GIT_STAGED",
     source_inclusion=producer["source_inclusion"],stage_acceptance=SPEC["stage_acceptance_receipt"],allocation=allocation,
     existing_target_metadata_original=list(target_before.values()),all_target_metadata_after=list(target_after.values()),
     all_target_CPU_receipts=list(target_receipts.values()),created_files=created_targets,parent_child_addition_events=parent_events,
     existing_targets_overwritten=False,installed_permissions_changed=False,Git_changed=False,published=False,ACTIVE_changed=False)
    install_r=dump_own(PD/"installation_readback.json",install_obj)
    phase="manifest_after_all_proofs_and_installed_targets"
    manifest_r=dump_own(PUB/"late_source_manifest.json",manifest)
    # Explicit physical-TXT transports; original JSON remains unchanged and never gets an extra physical archive entry.
    required_controls={}
    def require_control(r):
     rid(r);k=rid(r)
     if k in required_controls:need(required_controls[k]==r,"Conflicting semantic control identity")
     else:required_controls[k]=r
    for r in producer.values():require_control(r)
    A=strict(read_own(producer["acceptance"]["path"],f.MAX_CONTROL))
    for r in f._proof_receipts(A):require_control(r)
    proofs=[]
    for pk,ik in f.PAIRS:
     r=A[pk];need(r["path"]in ORIGINAL,"Proof native saved before first read")
     v=ORIGINAL[r["path"]];allow([v],"SOURCE_PRESERVATION_CONTROL_OWN_BYTES")
     need(hash_own(r["path"])==r,"Existing preservation control full CPU pin");remember(r)
     proof=strict(read_own(r["path"],f.MAX_CONTROL));proofs.append(proof)
     require_control(A[ik])
    for r in list(g._catalog_msa_controls())+[g._WORKER_BASE,g._WORKER_CLOSURE]+[r for p in proofs[2:]for r in p["authority_receipts"]]:
     require_control(r)
    for r in REQUEST["source_control_receipts"]+[SPEC["stage_acceptance_receipt"],manifest_r,bridge_r,op_r,
     operational["stage_terminal_metadata"],operational["legacy_capture"]]:
     require_control(r)
    additional_controls=list(REQUEST["source_control_receipts"])
    # Only this closed derived receipt list adds payload purposes; documentary children are not followed.
    derived=f._derived_receipts(A,I,proofs,g)
    semantic_targets={rid(r):r for r in required_controls.values()}
    for r in derived+list(i_physical.values())+[x["physical_receipt"]for x in late_rows]+[x["evidence_copy"]for x in operational_caches+operational_new+operational_legacy]+[py_r,semantic_receipt]:
     semantic_targets[rid(r)]=r
    for r in semantic_targets.values():
     p=r["path"];need(p in ORIGINAL or p in CREATED,"Native enrollment BEFORE first semantic payload read")
     allow([expected_md(p)],"CLOSED_CURRENT_OR_INDEX_PREFLIGHT_OWN_BYTES")
     if p in ORIGINAL:actual_original(ORIGINAL[p],r)
     else:need(hash_own(p)==r,"Created semantic tuple")
     limit=f.MAX_SOURCE_CLOSURE if r==producer["source_closure"]else f.MAX_OPERATIONAL_PROOF if r==op_r else f.MAX_CONTROL
     payloads[rid(r)]=read_own(p,limit)
    for r in required_controls.values():
     need(Path(r["path"]).suffix==".json","Only explicit own JSON semantic control")
    # JSON Source copies need their exact physical TXT transport too.
    for r in list(semantic_targets.values()):
     if rid(r)in required_controls or Path(r["path"]).suffix==".json"and rid(r)in {rid(subset(x["source"]))for x in public_rows}:
      name="%05d_%s.OPAQUE.txt"%(len(transport_rows),Path(r["path"]).stem)
      tr,tmd=copy_own(r["path"],CONTROL_D/name,"FINITE_JSON_PHYSICAL_TXT_TRANSPORT")
      role="FINITE_SOURCE_CONTROL_BYTES"if rid(r)in required_controls else"FINITE_SOURCE_JSON_BYTES"
      transport_rows.append(dict(original=r,archived=tr,status="READONLY_BYTE_IDENTICAL_ALIAS",role=role))
      payloads[rid(tr)]=read_own(tr["path"],max(tr["bytes"],1))
    binding=dict(schema=f.SCHEMA,root_owned=True,producer=producer,semantics_source=semantic_receipt,
     stage_acceptance=SPEC["stage_acceptance_receipt"],late_source_publication=manifest_r,
     transport_aliases=transport_rows,additional_control_receipts=additional_controls,source_routes=routes,operational_source_provenance=op_r)
    f._binding_shape(binding)
    phase="current_and_pure_INDEX_shape_preflight_only"
    projection=f.SavedProjection(binding,payloads);projection.validate()
    # No fake package/constructor or live historical child IO. A separate actual SOURCE-only package/StrictIndex CPU is mandatory.
    for row in projection.selected_source_aliases()+projection.aliases():
     projection.check_source_text_alias(row)
     selected_route=projection.project_source_alias(row)
     if selected_route is not None:need(rid(selected_route["archived"])in semantic_targets or rid(selected_route["archived"])in payloads,"Selected route actual candidate retained")
    index_plan_rows={rid(r):r for r in projection.terminal_source_receipts()+projection.semantic_control_receipts()}
    for row in transport_rows:index_plan_rows[rid(row["archived"])]=row["archived"]
    for r in index_plan_rows.values():
     need(rid(r)in payloads or r["path"]in PAYLOAD,"Every planned INDEX physical row has actual bytes")
     need(r["path"]not in f.WRAPPER_ORIGINAL_PATHS and r["path"]!=f.SOURCE_TEXT_ORIGIN,"No original rawTXT INDEX entry")
    index_alias_plan={}
    for row in projection.selected_source_aliases()+projection.aliases():
     if projection.operational_alias(row):selected_row=row
     else:
      selected_row=projection.project_source_alias(row)or row
      selected_row=dict(selected_row,archived=projection._transport_target(selected_row["archived"]))
     key=rid(selected_row["original"]);target=rid(selected_row["archived"])
     need(target in index_plan_rows,"Planned alias physical row absent")
     need(key not in index_alias_plan or index_alias_plan[key]==target,"Explicit selected alias cannot be undone by order/repetition")
     index_alias_plan[key]=target
    need(len({rid(x["evidence_copy"])for x in operational_caches})==13060
     and all(rid(x["evidence_copy"])in index_plan_rows for x in operational_caches),"All13060 evidence copies have separate physical plan rows")
    for r in required_controls.values():need(rid(r)not in index_plan_rows,"Semantic JSON original forbidden as separate physical archive entry")
    preflight=dict(schema="root-finite-source-current-and-index-shape-preflight.v1",
     status="ACTUAL_CURRENT_FULL_BYTES_AND_PURE_INDEX_SHAPES_ONLY_NOT_ACTUAL_INDEX_PACKAGE_OR_RESTORE",
     source_context=binding,finite_projection=projection.proof(),
     physical_row_n=len(index_plan_rows),exact_alias_row_n=len(index_alias_plan),
     physical_copy_and_alias_closure_derived_from_complete_projection=True,
     actual_Source_only_StrictIndex_compatibility_CPU_required=True,actual_package_or_restore_accepted=False,
     original_worker_payload_read=False,original_TXT_executed=False,Git_changed=False,published=False,ACTIVE_changed=False)
    preflight_r=dump_own(PD/"current_index_shape_preflight.json",preflight)
    # Final original/created own bytes, Source/Core and semantic replay precede the native-only true-last sweep.
    def verify_inputs():
     core_check()
     need(hash_own(failed_tro_md["path"])==failed_tro_pin
      and strict(read_own(failed_tro_md["path"],20*1024*1024))==FAILED_TRO,"Qualified failedTRO whole own bytes/JSON unchanged before/end/afteroutput")
     need(native_metadata(Path(mapper_parent))==mapper_current and sorted(os.listdir(mapper_parent))==mapper_names,
      "Current-only P original saved metadata/names unchanged; never a new payload reader")

     for path,r in all_input_pins.items():need(hash_own(path)==r,"All original Source/control/evidence complete bytes changed")
     for r in copy_receipts+[op_r,bridge_r,install_r,manifest_r,preflight_r]:
      need(hash_own(r["path"])==r,"All own copies/proofs/manifest full bytes")
     for p,r in TARGETS.items():need(current_target(p,r)==target_receipts[p],"All installed targets exact full bytes")
     need(strict(read_own(op_r["path"],f.MAX_OPERATIONAL_PROOF))==operational,"Complete operational proof readback")
     need(strict(read_own(bridge_r["path"],f.MAX_CONTROL))==bridge_proof,"Complete bridge proof readback")
     need(strict(read_own(manifest_r["path"],f.MAX_CONTROL))==manifest,"Complete manifest readback")
     need(strict(read_own(install_r["path"],f.MAX_CONTROL))==install_obj,"Complete install proof readback")
     need(strict(read_own(preflight_r["path"],f.MAX_CONTROL))==preflight,"Complete shape preflight readback")
     repeated=f.SavedProjection(binding,payloads);repeated.validate()
     need(f.exact(repeated.proof(),projection.proof()),"Repeated complete Source pure semantic projection")
     for path,names in SPEC["source_directory_children"].items():need(sorted(os.listdir(path))==sorted(names),"Original code directory universe")
     for root in f.CACHE_ROOTS:need(sorted(os.listdir(root))==sorted(Path(v["path"]).name for v in cache_members if str(Path(v["path"]).parent)==root),"Original closed cache universe")
     need(strict(read_own(SPEC["primary_request_path"],4*1024*1024))==REQUEST,"Immutable whole primary request remains unchanged")
     for p,children in protected_children.items():need(sorted(os.listdir(p))==sorted(protected_children_after_install(p,children)),"Saved protected universe plus only exact installed-parent additions")
     core_check()
    def final_native_only(complete=True):
     # Name checks precede the final native-only union; no payload/hash/JSON/readlink/resolve or fresh baseline.
     for event in operational_parent_events:need(sorted(os.listdir(event["path"]))==event["names_after"],"TRUE_LAST operational parent exact declared additions")
     for p,children in protected_children.items():need(sorted(os.listdir(p))==sorted(protected_children_after_install(p,children)),"TRUE_LAST exact saved baseline plus finite installed-parent additions")
     for p,plan in parent_plans.items():need(sorted(os.listdir(p))==sorted(set(plan["names_before"])|plan["added_children"]),"TRUE_LAST exact parent addition universe")
     for p,names in expected_names.items():need(sorted(os.listdir(p))==sorted(names),"TRUE_LAST own directory exact universe")
     need(sorted(os.listdir(D))==sorted(readiness_names_original),"TRUE_LAST readiness universe")
     for p,v in ORIGINAL.items():
      if p not in WORKER and p not in(str(CORE_LOGICAL),str(CORE_REAL)):ordinary(p)
      need(native_metadata(Path(p))==EVENTS.get(p,v),"TRUE_LAST original/explicit parent-event native")
     for p,v in CREATED.items():
      if not complete and stat.S_ISDIR(v["mode"])and p not in EVENTS:
       current=native_metadata(Path(p));need(all(current[k]==v[k]for k in("inode","dev","uid","gid","mode")),"Open created directory identity")
      else:need(native_metadata(Path(p))==EVENTS.get(p,v),"TRUE_LAST created/file or sealed/fill directory event")
     for p,v in target_before.items():need(native_metadata(Path(p))==v,"TRUE_LAST unchanged existing target")
     need(native_metadata(D)==readiness_directory_original,"TRUE_LAST readiness original directory")
     for v in readiness_native_original:need(native_metadata(Path(v["path"]))==v,"TRUE_LAST readiness raw original")
    phase="final_input_readbacks"
    verify_inputs()
    # All leaf copy directories are sealed before Root proof; PD is sealed only after its final proof.
    for p in sorted(expected_names,key=lambda x:len(Path(x).parts),reverse=True):
     if p!=str(PD):seal_owned_directory(p)
    final_native_only(complete=False)
    root_obj=dict(schema="root-finite-late-source-publisher-execution-control.v1",
     status="EXPLICIT_SOURCE_AND_NONOPERATIVE_EVIDENCE_INSTALLED_CURRENT_PURE_SHAPES_READ_BACK_NOT_GIT_OR_PACKAGE",
     allocation=allocation,actual_job_id=jid,source_software=SPEC["source_software_receipt"],source_context=binding,
     source_first_actual_CPU_pins=source_first_pins,all_original_input_CPU_pins=list(all_input_pins.values()),
     operational_proof=op_r,source_text_bridge_proof=bridge_r,installation_readback=install_r,late_source_manifest=manifest_r,
     current_index_shape_preflight=preflight_r,created_file_CPU_pins=list(copy_receipts),parent_child_addition_events=parent_events,
     reconstructed_prior_original_metadata_count=17734,reconstructed_prior_directory_universe_count=348,
      saved_name_only_directory_current_supplement=dict(authority=failed_tro_pin,
       field=["saved_name_only_directory_new_metadata_observation"],observation=mapper_observation,
       newly_observed_directory_n=1,old_ST_native_rows_rewritten=False,Source_reader_permission_changed=False),
      failed_v4_self_Source_authority=dict(authority=failed_tro_pin,
       field=["failed_publisher_self_source_metadata_original"],original_metadata=failed_self_records,
       declared_destinations=failed_self_destinations,prior_CPU_pins_invented=False),

     prior_software_terminal_CPU_pin=pre_pins[SPEC["source_software_terminal_metadata"]["path"]],
     operational_shared_parent_addition_events=operational_parent_events,
     self_control_CPU_pins=control_pins,readiness=dict(path=str(D/"readiness.json"),native=next(x for x in readiness_native_original if Path(x["path"]).name=="readiness.json")),
     failed_source_histories_retained=True,raw_JSON_rewritten=False,Source_IDs_invented=False,
     original_or_copied_programs_executed=False,generic_reader_permission_changed=False,
     actual_Source_only_StrictIndex_CPU_still_required=True,archive_or_restore_accepted=False,
     production_science_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False)
    root_r=dump_own(PD/"execution_control.json",root_obj)
    need(strict(read_own(root_r["path"],f.MAX_CONTROL))==root_obj,"Whole Root proof persisted/read back")
    seal_owned_directory(PD)
    verify_inputs()
    need(hash_own(root_r["path"])==root_r,"Root full proof after final Source/Core/current projection")
    core_check()
    final_native_only()
    print(json.dumps(dict(schema="root-finite-late-source-publisher-final-CPU-descriptor.v1",
     status="ACTUAL_CURRENT_SOURCE_PUBLICATION_AND_NONOPERATIVE_EVIDENCE_ONLY_PENDING_INDEPENDENT_TERMINAL_READBACK",
     actual_job_id=jid,allocation=allocation,execution_control=root_r,execution_control_directory=EVENTS[str(PD)],
     operational_provenance=op_r,late_source_manifest=manifest_r,installation_readback=install_r,
     true_last_original_native_union_PASS=True,actual_Source_only_StrictIndex_CPU_still_required=True,
     Git_changed=False,published=False,archive_or_restore_accepted=False,ACTIVE_changed=False)),flush=True)
    

except BaseException as original_error:
    # Failure is preserved; no qualification descriptor, fallback Source read, overwrite or automatic replay.
    failure_guards=[]
    for label,guard in (
        ("original_native",lambda:all(native_metadata(Path(p))==EVENTS.get(p,v)for p,v in ORIGINAL.items())),
        ("created_native",lambda:all(native_metadata(Path(p))==EVENTS.get(p,v)for p,v in CREATED.items())),
        ("Core_original_native",lambda:all(native_metadata(Path(v["path"]))==v for v in SPEC["conditional_core_metadata"])),
        ("Common_original_native",lambda:native_metadata(COMMON)==SPEC["Common_original_metadata"])):
        try:
            result=guard();failure_guards.append(dict(check=label,PASS=result is True))
        except BaseException as guard_error:
            failure_guards.append(dict(check=label,PASS=False,error_type=type(guard_error).__name__,error=str(guard_error)))
    partial=[]
    for path in globals().get("PARTIAL_PATHS",[]):
        try:
            value=native_metadata(Path(path));partial.append(value)
        except FileNotFoundError:
            partial.append(dict(path=path,absent=True))
        except BaseException as observation_error:
            partial.append(dict(path=path,error_type=type(observation_error).__name__,error=str(observation_error)))
    failed_authority_detail={"own_CPU_pin_available":False,"observation_authenticated":False,
     "reason":"FIXED_FAILED_CONTROL_NOT_AUTHENTICATED_AT_FAILURE"}
    if "failed_tro_pin"in globals():
     failed_authority_detail={"own_CPU_pin_available":True,"own_CPU_tuple":failed_tro_pin,
      "observation_authenticated":globals().get("mapper_observation_authenticated",False)is True,
      "control_authenticated":globals().get("failed_tro_authenticated",False)is True}
    failed_observation_detail={"available":False,"reason":"FIXED_CURRENT_METADATA_OBSERVATION_NOT_AUTHENTICATED_AT_FAILURE"}
    if globals().get("mapper_observation_authenticated",False)is True:
     failed_observation_detail={"available":True,"observation":mapper_observation}
    failure=dict(schema="root-finite-late-source-publisher-typed-failure.v1",
        status="ACTUAL_PARTIAL_FINITE_PUBLISHER_FAILURE_PRESERVED_NOT_ACCEPTED",
        actual_job_id=jid,phase=globals().get("phase","before_bound_inputs"),
        error_type=type(original_error).__name__,error=str(original_error),
        native_guard_outcomes=failure_guards,partial_created_metadata=partial,
        failed_prior_terminal_authority=failed_authority_detail,
        saved_name_only_directory_current_observation=failed_observation_detail,
        installed_paths=globals().get("created_targets",[]),
        original_inputs_or_public_targets_overwritten=False,
        no_automatic_replay=True,Source_or_INDEX_compatibility_accepted=False,
        production_science_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False)
    try:
        # A typed stderr record exists even before PUB/PD or dump_own are defined.
        # It is failure evidence only; no namespace is created and the original exception is re-raised.
        print(json.dumps(failure,sort_keys=True,allow_nan=False),file=sys.stderr,flush=True)
    except BaseException as typed_stderr_error:
        try:
            print(json.dumps(dict(status="PUBLISHER_TYPED_STDERR_PRESERVATION_ERROR_NOT_QUALIFICATION",
             original_error_type=type(original_error).__name__,preservation_error_type=type(typed_stderr_error).__name__)),
             file=sys.stderr,flush=True)
        except BaseException:
            pass
    try:
        # Only a still-writable exact new own PD is usable; never chmod an already sealed directory.
        if "PD"in globals()and Path(PD).is_dir()and str(PD)in CREATED and native_metadata(PD)["mode"]&0o200:
            failure_r=dump_own(Path(PD)/"failure.json",failure)
            need(strict(read_own(failure_r["path"],20*1024*1024))==failure,"Complete typed failure readback")
            if str(PD)not in EVENTS:seal_owned_directory(PD)
    except BaseException as preservation_error:
        print(json.dumps(dict(status="PUBLISHER_FAILURE_PRESERVATION_ERROR_NOT_QUALIFICATION",
            actual_job_id=jid,original_error_type=type(original_error).__name__,
            preservation_error_type=type(preservation_error).__name__,preservation_error=str(preservation_error))),file=sys.stderr,flush=True)
    raise
PY
