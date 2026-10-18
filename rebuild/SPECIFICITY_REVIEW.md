# Specificity review reconstruction

The frozen primary plan uses complete declared experimental entity sequences for KEAP1, KLHL3 and KLHL12. It includes 180 new primary AF2 models and 45 predeclared observed-native sensitivity models. The original 45 observed-core KEAP1 candidates are a separate comparison arm, never part of the declared primary denominator.

Runtime entry: `specificity_review.py worker <slot>` runs only under a one-GPU Slurm array; `specificity_review.py validate <array_id>` runs on CPU. `specificity_prepare.py` prepares frozen input sequences and CPU MSA queries. `specificity_analyze.py` computes full/mapped geometry and separate directional PAE on CPU. `specificity_scoring_check.py` verifies native self-comparison, directional PAE and internal-gap projection with explicitly synthetic tests.

Actual authority is `/lustre/users/u21111210118/projects/test9/steps/15_specificity_review/plan.json`, SHA256 `93dadac25bcf8899b4ecfcd332326b1b8845f8045f4ffc9ef4ac9bb1a2b65fe4`. Original inputs, query MSA hashes, full outputs, condition membership and all denominators remain in the step. Known experimental coordinates are comparison references, never inference input. Native references may overlap training; these are diagnostic calculations, not a blind benchmark or experimental specificity/blockade proof.

AF2 JSON global ipTM is retained under that name; it is not relabeled as Boltz's minimum directional pair ipTM. Native control adequacy and confidence rules are frozen in the plan and unchanged after prediction.

