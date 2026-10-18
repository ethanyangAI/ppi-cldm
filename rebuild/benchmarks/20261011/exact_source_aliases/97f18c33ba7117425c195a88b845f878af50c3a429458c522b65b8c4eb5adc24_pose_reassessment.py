#!/usr/bin/env python3
"""Audit accepted NEW AF2 ensembles; geometric diagnostics, never binding validation."""
import argparse, copy, datetime, hashlib, json, os, platform, shutil, sys, time
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform, cdist
from Bio.PDB import PDBParser, PDBIO, ShrakeRupley
from Bio.SeqUtils import seq1

def receipt(path):
    path = Path(path)
    b = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}

def verify(item):
    got = receipt(item["path"])
    for key in ("sha256", "bytes"):
        if got[key] != item[key]:
            raise ValueError(f"Receipt mismatch {key}: {item['path']}")
    return got

def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)

def rmsd(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 3 or len(a) < 3:
        raise ValueError("Full, equal coordinate correspondence with >=3 atoms required")
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("Nonfinite coordinates")
    return float(np.sqrt(np.mean(np.sum((a-b)**2, axis=1))))

def fit(moving, reference):
    moving, reference = np.asarray(moving, dtype=float), np.asarray(reference, dtype=float)
    rmsd(moving, reference)
    cm, cr = moving.mean(axis=0), reference.mean(axis=0)
    u, _, vt = np.linalg.svd((moving-cm).T @ (reference-cr))
    if np.linalg.det(u @ vt) < 0:
        u[:, -1] *= -1
    rotation = u @ vt
    if not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-10):
        raise ValueError("Invalid rigid rotation")
    return rotation, cm, cr

def aligned(moving, fit_moving, fit_reference):
    r, cm, cr = fit(fit_moving, fit_reference)
    return (np.asarray(moving, dtype=float)-cm) @ r + cr

def fold_rmsd(a, b):
    return rmsd(aligned(a, a, b), b)

def pose_rmsd(target_a, binder_a, target_b, binder_b):
    return rmsd(aligned(binder_a, target_a, target_b), binder_b)

def validate_sequence(observed, expected):
    if observed != expected:
        raise ValueError(f"Exact full sequence mismatch: observed length {len(observed)}, expected {len(expected)}")

def read_model(model_record, expected_sequences):
    verify(model_record["pdb"]); verify(model_record["scores"])
    structure = PDBParser(QUIET=True).get_structure("model", model_record["pdb"]["path"])
    models = list(structure.get_models())
    if len(models) != 1:
        raise ValueError("Exactly one PDB MODEL required")
    chains = list(models[0].get_chains())
    if len(chains) != len(expected_sequences):
        raise ValueError("Unexpected chain count")
    coords, maps = [], []
    for chain, expected in zip(chains, expected_sequences):
        residues = list(chain.get_residues())
        if any(r.id[0] != " " for r in residues):
            raise ValueError("Unexpected nonstandard/hetero residues")
        observed = "".join(seq1(r.resname) for r in residues)
        validate_sequence(observed, expected)
        if any("CA" not in r for r in residues):
            raise ValueError("Missing CA in full sequence correspondence")
        if len({r.id for r in residues}) != len(residues):
            raise ValueError("Duplicate residue identity")
        ca = np.asarray([r["CA"].coord for r in residues], dtype=float)
        if not np.isfinite(ca).all():
            raise ValueError("Nonfinite CA coordinates")
        coords.append(ca)
        maps.append([{"sequence_position": i+1, "chain": chain.id, "residue_number": r.id[1],
                      "insertion_code": r.id[2].strip(), "amino_acid": expected[i]}
                     for i, r in enumerate(residues)])
    score = json.loads(Path(model_record["scores"]["path"]).read_text())
    n = sum(map(len, expected_sequences))
    plddt, pae = np.asarray(score["plddt"], float), np.asarray(score["pae"], float)
    if plddt.shape != (n,) or pae.shape != (n,n):
        raise ValueError("Confidence dimensions differ from full sequence")
    if not (np.isfinite(plddt).all() and np.isfinite(pae).all()):
        raise ValueError("Nonfinite confidence")
    if not np.all((plddt >= 0) & (plddt <= 100)) or np.any(pae < 0):
        raise ValueError("Confidence outside allowed domain")
    model, seed = int(model_record["model"]), int(model_record["seed"])
    return {"id": f"model_{model}_seed_{seed}", "model": model, "seed": seed,
            "coords": coords, "residue_maps": maps, "plddt": plddt, "pae": pae,
            "score": score, "structure": structure, "chains": chains,
            "pdb": model_record["pdb"], "scores": model_record["scores"]}

def matrices(models):
    n = len(models)
    pose, fold, target = [np.zeros((n,n)) for _ in range(3)]
    for i in range(n):
        for j in range(i+1,n):
            ta, ba = models[i]["coords"]; tb, bb = models[j]["coords"]
            pose[i,j] = pose[j,i] = pose_rmsd(ta,ba,tb,bb)
            fold[i,j] = fold[j,i] = fold_rmsd(ba,bb)
            target[i,j] = target[j,i] = fold_rmsd(ta,tb)
    return pose, fold, target

def clusters(matrix, ids, cutoff):
    if len(ids) != len(set(ids)) or ids != sorted(ids):
        raise ValueError("Stable, unique, sorted model identifiers required")
    m = np.asarray(matrix, float)
    if m.shape != (len(ids), len(ids)) or not np.isfinite(m).all():
        raise ValueError("Invalid distance matrix")
    if not np.allclose(m,m.T,atol=1e-10) or not np.allclose(np.diag(m),0):
        raise ValueError("Distance matrix must be symmetric with zero diagonal")
    labels = fcluster(linkage(squareform(m, checks=True), method="complete"),
                      t=cutoff, criterion="distance") if len(ids) > 1 else np.ones(1,int)
    groups = sorted(([i for i,x in enumerate(labels) if x == label]
                     for label in set(labels)), key=lambda g: tuple(ids[i] for i in g))
    major = max(map(len,groups))
    out = []
    for number, members in enumerate(groups, 1):
        means = m[np.ix_(members,members)].mean(axis=1)
        minimum = float(means.min())
        ties = [members[k] for k,v in enumerate(means) if abs(v-minimum) <= 1e-10]
        medoid = min(ties, key=lambda i: ids[i])
        diameter = float(m[np.ix_(members,members)].max())
        if diameter > cutoff + 1e-8:
            raise ValueError("Complete-link cluster exceeds cutoff")
        out.append({"cluster_id": f"C{number:02d}", "members": [ids[i] for i in members],
                    "size": len(members), "fraction_of_15": len(members)/len(ids),
                    "is_co_major": len(members) == major, "diameter_A": diameter,
                    "medoid": ids[medoid], "medoid_mean_intracluster_pose_rmsd_A": minimum,
                    "medoid_tie_candidates": sorted(ids[i] for i in ties)})
    return out

def interface_geometry(model):
    ca, cb = model["chains"]
    aa = [a for a in ca.get_atoms() if a.element not in ("H","D")]
    ab = [a for a in cb.get_atoms() if a.element not in ("H","D")]
    d = cdist(np.asarray([a.coord for a in aa]), np.asarray([a.coord for a in ab]))
    hits = np.argwhere(d <= 5.0)
    ra = sorted({int(i) for i in hits[:,0]}) if len(hits) else []
    rb = sorted({int(i) for i in hits[:,1]}) if len(hits) else []
    residue_a = sorted({a.parent.id for a in (aa[i] for i in ra)})
    residue_b = sorted({a.parent.id for a in (ab[i] for i in rb)})
    complex_copy = copy.deepcopy(model["structure"])
    sr = ShrakeRupley(probe_radius=1.4, n_points=100)
    sr.compute(complex_copy, level="S")
    isolated_area = 0.0
    for chain in (ca,cb):
        chain_copy = copy.deepcopy(chain); sr.compute(chain_copy,level="C")
        isolated_area += chain_copy.sasa
    area = float(isolated_area-complex_copy.sasa)
    if area < -1e-6:
        raise ValueError("Negative buried surface area beyond numerical tolerance")
    area = max(0.0,area)
    return {"heavy_atom_contacts_within_5A": int(len(hits)),
            "target_contact_residues": len(residue_a), "binder_contact_residues": len(residue_b),
            "minimum_heavy_atom_distance_A": float(d.min()),
            "heavy_atom_pairs_below_2A": int((d<2.0).sum()),
            "geometric_dSASA_A2": area,
            "dSASA_definition": "SASA(target)+SASA(binder)-SASA(complex); no half-factor",
            "sasa_parameters": {"algorithm":"Bio.PDB.ShrakeRupley","probe_radius_A":1.4,"n_points":100},
            "energy_per_area": None,
            "energy_per_area_status": "NOT_ESTIMABLE_NO_ENERGY_BACKEND" if area>0 else "NOT_ESTIMABLE_ZERO_AREA",
            "evidence_scope":"Unrelaxed static geometry; not binding or blockade validation"}

def normalized_medoid(model, path, target_sequence, binder_sequence):
    structure=copy.deepcopy(model["structure"])
    copied_model=next(structure.get_models())
    chains=list(copied_model.get_chains())
    for chain in chains:copied_model.detach_child(chain.id)
    for chain,new_id in zip(chains,("A","B")):
        chain.id=new_id;copied_model.add(chain)
    path.parent.mkdir(parents=True,exist_ok=True)
    writer=PDBIO();writer.set_structure(structure);writer.save(str(path))
    reread=next(PDBParser(QUIET=True).get_structure("readback",path).get_models())
    if [c.id for c in reread]!=["A","B"]:raise ValueError("Normalized chains differ")
    atom_rmsds=[]
    for chain,original,sequence in zip(reread,model["chains"],(target_sequence,binder_sequence)):
        validate_sequence("".join(seq1(r.resname) for r in chain),sequence)
        atoms=list(chain.get_atoms());original_atoms=list(original.get_atoms())
        if len(atoms)!=len(original_atoms) or [a.name for a in atoms]!=[a.name for a in original_atoms]:
            raise ValueError("Normalization altered atom correspondence")
        atom_rmsds.append(rmsd(np.array([a.coord for a in atoms]),np.array([a.coord for a in original_atoms])))
    if max(atom_rmsds)>0.002:raise ValueError("Normalization altered coordinates")
    return receipt(path),{"chains":{"A":"target","B":"binder"},"all_atom_rmsd_from_original_A":atom_rmsds}

def confidence(model, target_length):
    score, plddt, pae = model["score"], model["plddt"], model["pae"]
    data = {"ptm":float(score["ptm"]), "mean_plddt":float(plddt.mean()),
            "binder_mean_plddt":float(plddt[target_length:].mean()),
            "ipsae":None,"ipsae_status":"NOT_COMPUTED"}
    if target_length:
        data.update(iptm=float(score["iptm"]),
                    target_mean_plddt=float(plddt[:target_length].mean()),
                    mean_pae_target_rows_binder_columns_A=float(pae[:target_length,target_length:].mean()),
                    mean_pae_binder_rows_target_columns_A=float(pae[target_length:,:target_length].mean()))
    return data

def self_tests():
    rng = np.random.default_rng(87)
    target = rng.normal(size=(31,3))*9
    binder = rng.normal(size=(13,3))*2 + [12,3,0]
    q, _ = np.linalg.qr(rng.normal(size=(3,3)))
    if np.linalg.det(q)<0: q[:,0] *= -1
    moved_t, moved_b = target@q+[52,-12,3], binder@q+[52,-12,3]
    assert pose_rmsd(target,binder,moved_t,moved_b)<1e-10
    assert fold_rmsd(binder,moved_b)<1e-10
    translated = binder+[4,0,0]
    assert abs(pose_rmsd(target,binder,target,translated)-4)<1e-10
    assert fold_rmsd(binder,translated)<1e-10
    ids=["a","b","c","d"]
    m=np.array([[0,1,5,6],[1,0,4,5],[5,4,0,1],[6,5,1,0]],float)
    c=clusters(m,ids,2)
    assert [x["members"] for x in c]==[["a","b"],["c","d"]]
    assert all(x["is_co_major"] for x in c)
    assert [x["medoid"] for x in c]==["a","c"]
    # Single-link would incorrectly chain all three; complete-link must not.
    c2=clusters(np.array([[0,1,2.5],[1,0,1],[2.5,1,0]],float),["a","b","c"],1.5)
    assert sorted(x["size"] for x in c2)==[1,2]
    rejected=False
    try: validate_sequence("ADE","ACE")
    except ValueError: rejected=True
    assert rejected
    rejected=False
    try: rmsd(np.zeros((4,3)),np.zeros((3,3)))
    except ValueError: rejected=True
    assert rejected
    return {"status":"PASSED","tests":["global_rigid_transform_invariance",
      "binder_translation_distinguishes_pose_from_intrinsic_fold",
      "all_co_major_clusters_and_stable_medoid_ties",
      "complete_link_rejects_single_link_chaining","sequence_mismatch_rejected",
      "missing_coordinate_correspondence_rejected"]}

def analyze(config, run, manifest):
    plan_path, acceptance_path = Path(config["plan"]["path"]), Path(config["acceptance_path"])
    verify(config["plan"])
    plan, acceptance = json.loads(plan_path.read_text()), json.loads(acceptance_path.read_text())
    if acceptance["status"]!="ALL_90_AF2_MODELS_VERIFIED" or acceptance.get("errors"):
        raise ValueError("AF2 CPU acceptance incomplete")
    verify(acceptance["plan"])
    if acceptance["plan"] != receipt(plan_path):
        raise ValueError("Acceptance belongs to a different frozen plan")
    if acceptance["coordinate_provenance"]!="NEW_PREDICTIONS_NOT_RESTORED_OLD_COORDINATES":
        raise ValueError("Unexpected coordinate provenance")
    expected_ids={(m,s) for m in plan["protocol"]["model_order"] for s in plan["protocol"]["seeds"]}
    if len(expected_ids)!=15 or len(acceptance["accepted_entries"])!=6:
        raise ValueError("Expected all3 candidates x 15complex +15monomer")
    entries={(e["id"],e["mode"]):e for e in plan["entries"]}
    accepted={(e["id"],e["mode"]):e for e in acceptance["accepted_entries"]}
    if set(entries)!=set(accepted): raise ValueError("Plan/acceptance entry mismatch")
    manifest["inputs"] += [receipt(plan_path),receipt(acceptance_path)]
    tests = self_tests()
    atomic_json(run/"qc/self_tests.json",tests)
    result={"status":"NEW_AF2_POSE_AND_FOLD_DIAGNOSTICS_COMPLETE",
            "coordinate_provenance":acceptance["coordinate_provenance"],"config":config,
            "candidates":[],"limitations":[
             "These are new AF2 predictions, not restored historical coordinates.",
             "No original RFdiffusion backbone remains: designed-backbone RMSD is not estimable.",
             "AF2 ensemble members and seeds are correlated predictions, not independent experiments.",
             "No binding, blockade, off-target selectivity, thermodynamics or workflow superiority is established.",
             "Monomer support is a geometric/plDDT diagnostic conditional on this AF2 protocol.",
             "ipSAE, Rosetta energies and MD are not computed in this module."]}
    medoid_export={"status":"NORMALIZED_MAIN_THRESHOLD_MEDOIDS","cutoff_A":config["main_cutoff_A"],
                   "coordinate_provenance":acceptance["coordinate_provenance"],"entries":[]}
    for candidate in sorted({e["id"] for e in plan["entries"]}):
        ensembles={}
        for mode in ("complex","monomer"):
            entry,acc=entries[(candidate,mode)],accepted[(candidate,mode)]
            verify(acc["run_manifest"]); manifest["inputs"].append(acc["run_manifest"])
            records=acc["models"]
            if {(int(x["model"]),int(x["seed"])) for x in records}!=expected_ids or len(records)!=15:
                raise ValueError("Missing/duplicate model-seed identity")
            seqs=[entry["target_sequence"],entry["sequence"]] if mode=="complex" else [entry["sequence"]]
            models=sorted([read_model(x,seqs) for x in records],key=lambda x:x["id"])
            for x in models: manifest["inputs"] += [x["pdb"],x["scores"]]
            ensembles[mode]=models
        models,monomers=ensembles["complex"],ensembles["monomer"]
        ids=[x["id"] for x in models]; by_id={x["id"]:x for x in models}
        pose,fold,target=matrices(models)
        cdata={"candidate":candidate,"complex_denominator":15,"monomer_denominator":15,
               "binder_sequence":entries[(candidate,"complex")]["sequence"],
               "target_sequence":entries[(candidate,"complex")]["target_sequence"],
               "matrix_model_order":ids,"target_aligned_binder_pose_rmsd_A":pose.tolist(),
               "binder_intrinsic_fold_rmsd_A":fold.tolist(),
               "target_intrinsic_fold_rmsd_A":target.tolist(),"models":[],
               "clusters_by_cutoff_A":{},"designed_backbone_rmsd_A":None,
               "designed_backbone_rmsd_status":"NOT_ESTIMABLE_ORIGINAL_BACKBONE_MISSING"}
        main_medoids=set()
        for cutoff in config["cluster_cutoffs_A"]:
            grouped=clusters(pose,ids,cutoff)
            for g in grouped:
                medoid=by_id[g["medoid"]]
                comparisons=[]
                for monomer in monomers:
                    distance=fold_rmsd(monomer["coords"][0],medoid["coords"][1])
                    plddt=float(monomer["plddt"].mean())
                    comparisons.append({"monomer":monomer["id"],"binder_intrinsic_rmsd_to_medoid_A":distance,
                                        "monomer_mean_plddt":plddt,
                                        "supports_medoid":plddt>=80.0 and distance<=2.0})
                g["monomer_comparisons"]=comparisons
                g["monomer_support_n"]=sum(x["supports_medoid"] for x in comparisons)
                g["monomer_support_denominator"]=15
                g["monomer_support_fraction"]=g["monomer_support_n"]/15
                if cutoff==config["main_cutoff_A"]:main_medoids.add(g["medoid"])
            cdata["clusters_by_cutoff_A"][str(cutoff)]=grouped
        all_medoids={g["medoid"] for gs in cdata["clusters_by_cutoff_A"].values() for g in gs}
        for model in models:
            data={"id":model["id"],"model":model["model"],"seed":model["seed"],
                  "pdb":model["pdb"],"scores":model["scores"],
                  "chain_residue_mapping":model["residue_maps"],
                  "confidence":confidence(model,len(model["coords"][0]))}
            if model["id"] in all_medoids:data["medoid_interface_geometry"]=interface_geometry(model)
            cdata["models"].append(data)
        cdata["monomer_models"]=[{"id":m["id"],"model":m["model"],"seed":m["seed"],
                                   "pdb":m["pdb"],"scores":m["scores"],
                                   "confidence":confidence(m,0),
                                   "chain_residue_mapping":m["residue_maps"]} for m in monomers]
        ref="model_1_seed_1042"
        groups=cdata["clusters_by_cutoff_A"][str(config["main_cutoff_A"])]
        ref_group=next(g for g in groups if ref in g["members"])
        cdata["fixed_reference_identity_diagnostic"]={
          "model":ref,"coordinate_basis":"NEW_RUN_MODEL_WITH_SAME_MODEL_SEED_IDENTITY_NOT_OLD_COORDINATES",
          "main_cluster":ref_group["cluster_id"],"main_cluster_size":ref_group["size"],
          "main_cluster_is_co_major":ref_group["is_co_major"],
          "mean_pose_rmsd_to_other_14_A":float(pose[ids.index(ref)].sum()/14),
          "interpretation":"Locates the newly reconstructed model1/seed1042; does not recover historical outlier coordinates."}
        cdata["co_major_cluster_ids"]=[g["cluster_id"] for g in groups if g["is_co_major"]]
        for g in groups:
            model=by_id[g["medoid"]]
            normalized,qc=normalized_medoid(model,run/"outputs/medoids"/candidate/(g["cluster_id"]+"_"+g["medoid"]+".pdb"),
                cdata["target_sequence"],cdata["binder_sequence"])
            data=next(x for x in cdata["models"] if x["id"]==g["medoid"])
            medoid_export["entries"].append({"candidate":candidate,"cluster_id":g["cluster_id"],
                "cluster_size":g["size"],"is_co_major":g["is_co_major"],"medoid_id":g["medoid"],
                "normalized_pdb":normalized,"original_pdb":model["pdb"],"normalization_qc":qc,
                "target_sequence":cdata["target_sequence"],"binder_sequence":cdata["binder_sequence"],
                "confidence":data["confidence"],"interface_geometry":data["medoid_interface_geometry"],
                "monomer_support_n":g["monomer_support_n"],"monomer_support_denominator":15})
        result["candidates"].append(cdata)
        print("CANDIDATE_COMPLETE",candidate,[(g["cluster_id"],g["size"],g["monomer_support_n"]) for g in groups],flush=True)
    medoid_path=run/"outputs/primary_medoids.json";atomic_json(medoid_path,medoid_export)
    result["normalized_main_threshold_medoid_export"]=receipt(medoid_path)
    path=run/"outputs/pose_reassessment.json";atomic_json(path,result)
    lines=["# New AF2 ensemble pose reassessment","",
           "All 90 models passed exact full-sequence, CA correspondence and hash verification. These are newly generated predictions; lost historical coordinates were not restored.","",
           "Complete-link clustering uses target-aligned binder CA pose RMSD. Main threshold is 2 Å; 1 and 3 Å are sensitivity analyses. Binder intrinsic fold RMSD is reported separately. Medoids are actual models minimizing mean intracluster pose RMSD; identifier order breaks exact numerical ties.","",
           "| Candidate | 2 Å clusters (size) | Co-major clusters | Monomer support per co-major medoid | New model1/seed1042 cluster |",
           "|---|---|---|---|---|"]
    for c in result["candidates"]:
        groups=c["clusters_by_cutoff_A"][str(config["main_cutoff_A"])]
        sizes=", ".join(f'{g["cluster_id"]}: {g["size"]}/15' for g in groups)
        major=", ".join(g["cluster_id"] for g in groups if g["is_co_major"])
        support=", ".join(f'{g["cluster_id"]} ({g["medoid"]}): {g["monomer_support_n"]}/15' for g in groups if g["is_co_major"])
        ref=c["fixed_reference_identity_diagnostic"]
        lines.append(f'| {c["candidate"]} | {sizes} | {major} | {support} | {ref["main_cluster"]} ({ref["main_cluster_size"]}/15) |')
    lines += ["","Monomer support requires mean monomer pLDDT ≥80 and full-binder intrinsic CA RMSD ≤2 Å against each medoid separately. All cluster medoids, including minor clusters and threshold sensitivities, retain their complete 15-model comparison table in the JSON.","",
              "Static heavy-atom contacts, close contacts and geometric buried surface area are supplied for every unique medoid. No interaction-energy backend is used. Energy/area remains null; zero area is explicitly not estimable.","",
              "No original designed-backbone RMSD can be calculated. This analysis does not establish experimental binding, PPI blockade, off-target selectivity, molecular-dynamics stability, or benchmark superiority.","",
              "Machine-readable result: "+str(path),"Acceptance evidence: "+str(acceptance_path)]
    report=run/"outputs/REPORT.md";report.write_text("\n".join(lines)+"\n")
    manifest["outputs"]={"results":receipt(path),"report":receipt(report),"self_tests":receipt(run/"qc/self_tests.json")}
    manifest["outputs"]["primary_medoids"]=receipt(medoid_path)
    for i,entry in enumerate(medoid_export["entries"]):manifest["outputs"]["normalized_medoid_"+str(i)]=entry["normalized_pdb"]
    manifest.update(status=result["status"],finished=time.time(),candidate_count=3,complex_count=45,monomer_count=45)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",required=True)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if not os.environ.get("SLURM_JOB_ID"):raise RuntimeError("Run computation through Slurm")
    config_path=Path(args.config);config=json.loads(config_path.read_text())
    step=Path(config["step_directory"])
    rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+os.environ["SLURM_JOB_ID"]
    if args.self_test:rid+="_selftest"
    run=step/"runs"/rid
    for d in ("outputs","qc"):(run/d).mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,run/"qc/pose_reassessment.py")
    shutil.copy2(config_path,run/"qc/config.json")
    manifest={"status":"RUNNING","started":time.time(),"job_id":os.environ["SLURM_JOB_ID"],
              "run_id":rid,"inputs":[receipt(config_path),receipt(Path(__file__).resolve())],
              "python":sys.version,"platform":platform.platform(),
              "coordinate_provenance":"NEW_PREDICTIONS_NOT_RESTORED_OLD_COORDINATES"}
    atomic_json(run/"manifest.json",manifest)
    try:
        if args.self_test:
            path=run/"outputs/self_tests.json";atomic_json(path,self_tests())
            manifest.update(status="SELF_TESTS_PASSED",finished=time.time(),outputs={"tests":receipt(path)})
        else:analyze(config,run,manifest)
        atomic_json(run/"manifest.json",manifest)
        print("COMPLETE",run/"manifest.json",flush=True)
    except BaseException as e:
        manifest.update(status="FAILED",finished=time.time(),error=repr(e))
        atomic_json(run/"manifest.json",manifest)
        raise

if __name__=="__main__":main()
