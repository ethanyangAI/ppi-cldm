"""
AiZynthFinder retrosynthesis pipeline.
Run in aizyn conda env after models are downloaded.

Usage:
  # default: built-in example molecules
  python run_retrosynthesis.py

  # single SMILES
  python run_retrosynthesis.py --smiles "CCO" --name my_mol

  # top-N from a pipeline candidates CSV
  python run_retrosynthesis.py --csv results/MDM2_TP53_candidates.csv --top 5
"""
import sys
import argparse
import json
from pathlib import Path

DATA_DIR = Path.home() / "zjy" / "aizynth_data"
OUT_DIR = Path.home() / "zjy" / "ppi_gen_project" / "core" / "denovo" / "results" / "retrosynthesis"

# Top MDM2-TP53 candidates from de novo pipeline (vina=-9.5 and -8.9 kcal/mol)
_DEFAULT_MOLECULES = {
    "MDM2_TP53_001": "CCC(=O)N1CC(C)(CCC2C3CCCC(C)C32)C(=O)N(CC2CC(F)CC2F)CCC1=O",
    "MDM2_TP53_002": "O=C1C2CC(CC3CC(F)CC45CC4CCC35)N(CCCC3CCCCC13)C2",
}

REQUIRED_FILES = [
    "uspto_model.onnx",
    "uspto_templates.csv.gz",
    "zinc_stock.hdf5",
    "uspto_filter_model.onnx",
]


def check_data_files():
    missing = [f for f in REQUIRED_FILES if not (DATA_DIR / f).exists()]
    if missing:
        print(f"Missing model files: {missing}")
        sys.exit(1)
    print("All model files present.")


def build_config():
    import yaml
    config = {
        "expansion": {
            "uspto": {
                "type": "TemplateBasedExpansionStrategy",
                "model": str(DATA_DIR / "uspto_model.onnx"),
                "template": str(DATA_DIR / "uspto_templates.csv.gz"),
                "cutoff_cumulative": 0.995,
                "cutoff_number": 50,
                "use_rdchiral": True,
            },
        },
        "filter": {
            "uspto": {
                "type": "QuickKerasFilter",
                "model": str(DATA_DIR / "uspto_filter_model.onnx"),
            }
        },
        "stock": {
            "zinc": {
                "type": "InMemoryInchiKeyQuery",
                "path": str(DATA_DIR / "zinc_stock.hdf5"),
            }
        },
        "search": {
            "algorithm": "mcts",
            "time_limit": 120,
            "iteration_limit": 1500,
            "max_transforms": 6,
            "return_first": False,
        },
    }
    cfg_path = DATA_DIR / "aizynthfinder_config.yml"
    with open(cfg_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    return cfg_path


def extract_route_steps(node, depth=0):
    """Recursively extract steps from a ReactionTree dict node."""
    steps = []
    node_type = node.get("type", "")
    smiles = node.get("smiles", "")
    in_stock = node.get("in_stock", False)

    if node_type == "reaction":
        steps.append({
            "depth": depth,
            "type": "reaction",
            "smiles": smiles,
        })
    elif node_type == "mol" and depth > 0:
        steps.append({
            "depth": depth,
            "type": "mol",
            "smiles": smiles,
            "in_stock": in_stock,
        })

    for child in node.get("children", []):
        steps.extend(extract_route_steps(child, depth + 1))
    return steps


def run_retrosynthesis(name, smiles, config_path):
    from aizynthfinder.aizynthfinder import AiZynthFinder

    print(f"\n{'='*60}")
    print(f"Molecule: {name}")
    print(f"SMILES:   {smiles}")
    print(f"{'='*60}")

    finder = AiZynthFinder(configfile=str(config_path))
    finder.expansion_policy.select(finder.expansion_policy.items)
    finder.filter_policy.select(finder.filter_policy.items)
    finder.stock.select(finder.stock.items)
    finder.target_smiles = smiles
    finder.tree_search()
    finder.build_routes()
    stats = finder.extract_statistics()

    n_routes = stats.get("number_of_routes", 0)
    is_solved = stats.get("is_solved", False)
    print(f"\nSearch complete.")
    print(f"  Routes found:  {n_routes}")
    print(f"  Solved:        {is_solved}")

    result = {
        "molecule": name,
        "smiles": smiles,
        "is_solved": bool(is_solved),
        "num_routes": n_routes,
        "routes": [],
    }

    reaction_trees = finder.routes.reaction_trees
    scores_list = finder.routes.scores  # list of score dicts per route

    for i, rt in enumerate(reaction_trees[:5]):
        score = None
        if scores_list and i < len(scores_list):
            score_dict = scores_list[i]
            if isinstance(score_dict, dict):
                score = list(score_dict.values())[0] if score_dict else None
            else:
                score = float(score_dict)

        route_info = {
            "rank": i + 1,
            "score": round(float(score), 4) if score is not None else None,
            "is_solved": bool(rt.is_solved),
            "steps": [],
        }

        try:
            tree_dict = rt.to_dict()
            route_info["steps"] = extract_route_steps(tree_dict)
        except Exception as e:
            route_info["parse_error"] = str(e)

        result["routes"].append(route_info)

        solved_tag = "SOLVED" if rt.is_solved else "partial"
        score_str = f"{score:.3f}" if score is not None else "N/A"
        print(f"\n  Route {i+1} [{solved_tag}, score={score_str}]:")
        for step in route_info["steps"]:
            indent = "    " + "  " * step["depth"]
            tag = ""
            if step["type"] == "mol":
                tag = " [IN STOCK]" if step.get("in_stock") else " [needs synthesis]"
            print(f"{indent}{step['smiles']}{tag}")

    return result


def load_molecules_from_csv(csv_path, top_n=None, smiles_col='smiles'):
    import csv
    molecules = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if top_n:
        rows = rows[:top_n]
    for i, row in enumerate(rows):
        smi = row.get(smiles_col, '').strip()
        if smi:
            name = row.get('name', f'mol{i+1}')
            molecules[name] = smi
    return molecules


def main():
    parser = argparse.ArgumentParser(description='AiZynthFinder retrosynthesis pipeline')
    parser.add_argument('--smiles', type=str, default=None, help='Single SMILES string')
    parser.add_argument('--name',   type=str, default='mol', help='Name for single SMILES mode')
    parser.add_argument('--csv',    type=str, default=None,  help='Candidates CSV file path')
    parser.add_argument('--top',    type=int, default=None,  help='Top-N from CSV (default: all)')
    parser.add_argument('--out',    type=str, default=None,  help='Output JSON path')
    parser.add_argument('--time_limit', type=int, default=120, help='Search time limit per mol (s)')
    args = parser.parse_args()

    if args.smiles:
        molecules = {args.name: args.smiles}
    elif args.csv:
        molecules = load_molecules_from_csv(args.csv, top_n=args.top)
        if not molecules:
            print(f"No valid SMILES found in {args.csv}")
            sys.exit(1)
    else:
        molecules = _DEFAULT_MOLECULES

    check_data_files()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    config_path = build_config()
    print(f"Config written to: {config_path}")
    print(f"Molecules to analyze: {len(molecules)}")

    all_results = {}
    for name, smiles in molecules.items():
        try:
            result = run_retrosynthesis(name, smiles, config_path)
            all_results[name] = result
        except Exception as e:
            import traceback
            print(f"ERROR for {name}: {e}")
            traceback.print_exc()
            all_results[name] = {"molecule": name, "smiles": smiles, "error": str(e)}

    out_path = Path(args.out) if args.out else OUT_DIR / "retrosynthesis_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n\nResults saved to: {out_path}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, res in all_results.items():
        if "error" in res:
            print(f"{name}: ERROR - {res['error']}")
        else:
            solved = "SOLVED" if res.get("is_solved") else "not solved"
            print(f"{name}: {solved}, {res.get('num_routes', 0)} routes")


if __name__ == "__main__":
    main()
