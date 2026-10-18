#!/bin/bash
#SBATCH --job-name=ppi_github_export_contract
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/github_contract_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/github_contract_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export CUDA_VISIBLE_DEVICES=""
export JAX_PLATFORMS=cpu
export OPENBLAS_NUM_THREADS=1
R=/lustre/users/u21111210118/projects/test9
RUN="$R/steps/24_benchmark_delivery/runs/github_contract_${SLURM_JOB_ID}"
mkdir -p "$RUN" "$RUN/tmp"
export TMPDIR="$RUN/tmp"
"$R/env/core/bin/python" "$R/steps/24_benchmark_delivery/code/test_github_source_export.py" > "$RUN/tests.log" 2>&1
"$R/env/core/bin/python" - "$RUN" <<'PY'
import hashlib, json, os, pathlib, sys
code = pathlib.Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code")
sys.path.insert(0, str(code))
import github_source_export as e
run = pathlib.Path(sys.argv[1])
files = ["github_source_export.py", "github_export_verify.py", "test_github_source_export.py", "README_GITHUB_SOURCE_DELIVERY.md", "github_export_contracts.sbatch"]
receipts = [{"path":str(code/f), "bytes":(code/f).stat().st_size, "sha256":hashlib.sha256((code/f).read_bytes()).hexdigest()} for f in files]
allocation = e.require_cpu_slurm()
repo = pathlib.Path("/lustre/users/u21111210118/projects/test9/source")
head = e.resolve_commit(repo, "HEAD")
leaves = e.entries(repo, head)
tree = e.build_trees(leaves)[""]["sha"]
issues = []
for path, item in leaves.items():
    if item["type"] == "blob":
        raw = e.git(repo, "cat-file", "blob", item["sha"])
        reason = e.forbidden(path, raw, item["mode"])
        if reason:
            issues.append({"path":path,"reason":reason})
receipt = {"schema":"github_export_contract_receipt.v1","status":"PASS","tests":22,"allocation":allocation,"files":receipts,"existing_committed_source_readonly_audit":{"head":head,"tree_sha":tree,"tracked_file_count":len(leaves),"publication_exclusion_issues":issues,"note":"The checkout is still under active integration; this is not a final-source export or acceptance."}}
(run/"receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
print(json.dumps({"status":"PASS","tests":22,"job_id":os.environ["SLURM_JOB_ID"],"committed_source_files":len(leaves),"publication_exclusion_issue_count":len(issues)}))
PY

