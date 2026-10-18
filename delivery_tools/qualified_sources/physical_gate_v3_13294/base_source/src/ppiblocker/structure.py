from __future__ import annotations
import itertools
from pathlib import Path
import numpy as np
from Bio import Align
from Bio.PDB import PDBParser, MMCIFParser
from Bio.SeqUtils import seq1
from scipy.spatial import cKDTree
from .common import EvidenceError, require

def read_structure(path):
    path = Path(path)
    parser = MMCIFParser(QUIET=True, auth_chains=False) if path.suffix.lower() in (".cif", ".mmcif", ".bin") else PDBParser(QUIET=True)
    try:
        model = next(parser.get_structure("pose", str(path)).get_models())
    except Exception as e:
        raise EvidenceError("STRUCTURE_PARSE_FAILED", str(e)) from e
    chains = []
    context = []
    for chain in model:
        residues, coords, atoms = [], [], []
        for residue in chain:
            letter = seq1(residue.resname, custom_map={"MSE": "M"})
            if letter == "X" or "CA" not in residue:
                if residue.resname not in ("HOH", "WAT"):
                    context.append({"chain": chain.id, "resname": residue.resname, "resid": str(residue.id)})
                continue
            heavy = [a for a in residue.get_atoms() if a.element not in ("H", "D")]
            require(all(np.isfinite(a.coord).all() for a in heavy), "NONFINITE_COORDINATES", chain.id)
            residues.append({"name": residue.resname, "letter": letter, "number": residue.id[1],
                             "icode": residue.id[2].strip(), "bfactor": float(residue["CA"].bfactor), "ca": np.asarray(residue["CA"].coord, float)})
            coords.append(np.array([a.coord for a in heavy], dtype=float))
            atoms.append([(a.name, a.element, np.asarray(a.coord, float)) for a in heavy])
        if residues:
            chains.append({"id": str(chain.id), "sequence": "".join(r["letter"] for r in residues),
                           "residues": residues, "heavy": coords, "atoms": atoms})
    require(len(chains) >= 2, "NOT_A_COMPLEX", "At least two protein chains are required")
    return chains, context

def match_chain(chain, protein, min_identity=.95, min_coverage=.8):
    aligner = Align.PairwiseAligner(mode="local", match_score=2, mismatch_score=-3,
                                   open_gap_score=-5, extend_gap_score=-.5)
    alignments = aligner.align(protein["sequence"], chain["sequence"])
    alignment = next(iter(alignments), None)
    if alignment is None:
        return {"chain": chain["id"], "identity": 0., "coverage": 0., "accepted": False, "residue_mapping": []}
    pairs = [(int(a), int(b)) for a,b in alignment.indices.T if a >= 0 and b >= 0]
    identical = [(a,b) for a,b in pairs if protein["sequence"][a] == chain["sequence"][b]]
    identity = len(identical) / max(len(pairs), 1)
    coverage = len({a for a,b in pairs}) / len(protein["sequence"])
    observed_coverage = len({b for a,b in pairs}) / len(chain["sequence"])
    return {"chain": chain["id"], "identity": identity, "coverage": coverage, "observed_coverage": observed_coverage,
            "accepted": identity >= min_identity and coverage >= min_coverage and observed_coverage >= .9,
            "residue_mapping": [{"construct_position": a+1,
                                 "canonical_position": a+protein["canonical_start"],
                                 "observed_index": b+1, "author_residue": chain["residues"][b]["number"],
                                 "insertion_code": chain["residues"][b]["icode"]} for a,b in pairs]}

def interface(a, b, cutoff=5.0):
    require(a["id"] != b["id"], "SAME_CHAIN", "Target and partner must be distinct physical chains")
    xa, xb = np.concatenate(a["heavy"]), np.concatenate(b["heavy"])
    ia = np.repeat(np.arange(len(a["heavy"])), [len(x) for x in a["heavy"]])
    ib = np.repeat(np.arange(len(b["heavy"])), [len(x) for x in b["heavy"]])
    neighbors = cKDTree(xa).query_ball_tree(cKDTree(xb), cutoff)
    pairs = sorted({(int(ia[i]), int(ib[j])) for i, js in enumerate(neighbors) for j in js})
    return {"cutoff_angstrom": cutoff, "residue_pairs": [[i+1,j+1] for i,j in pairs],
            "target_residues": sorted({i+1 for i,j in pairs}),
            "partner_residues": sorted({j+1 for i,j in pairs}),
            "atom_contact_count": sum(map(len,neighbors)),
            "minimum_distance": float(cKDTree(xb).query(xa,k=1)[0].min())}

def choose_pair(chains, proteins, gates, requested=None, validator=None, exact_construct=False):
    matches = [[match_chain(c,p,gates.get("min_identity",.95),gates.get("min_coverage",.8)) for c in chains] for p in proteins]
    candidates = []
    mismatched_constructs = []
    for i,j in itertools.permutations(range(len(chains)),2):
        if requested and [chains[i]["id"],chains[j]["id"]] != list(requested):
            continue
        if not (matches[0][i]["accepted"] and matches[1][j]["accepted"]):
            continue
        if exact_construct and any(c["sequence"] != p["sequence"] for c,p in zip((chains[i],chains[j]),proteins)):
            mismatched_constructs.append([chains[i]["id"],chains[j]["id"]])
            continue
        contacts = interface(chains[i],chains[j],gates.get("contact_cutoff",5))
        if len(contacts["target_residues"]) < gates.get("min_interface_residues",3) or len(contacts["partner_residues"]) < gates.get("min_partner_residues",3):
            continue
        candidates.append((i,j,contacts))
    require(candidates, "CONSTRUCT_SEQUENCE_MISMATCH" if mismatched_constructs else "NO_IDENTITY_VALID_CONTACTING_PAIR",
            "Observed sequences differ from the explicitly requested constructs" if mismatched_constructs else
            "No distinct contacting chains meet identity and construct coverage gates")
    candidates.sort(key=lambda x:(-len(x[2]["residue_pairs"]),chains[x[0]]["id"],chains[x[1]]["id"]))
    rejected=[]; entity_identity=None
    if validator is not None:
        valid=[]
        for x,y,c in candidates:
            try:
                identity=validator({"target_match":matches[0][x],"partner_match":matches[1][y],"interface":c})
                valid.append((x,y,c,identity))
            except EvidenceError as error:
                if error.code not in {"ENTITY_MAPPING_MISSING","STRUCTURE_SPECIES_MISMATCH","STRUCTURE_ACCESSION_MISMATCH"}: raise
                rejected.append({"target_chain":chains[x]["id"],"partner_chain":chains[y]["id"],"code":error.code,"reason":str(error)})
        require(valid,"NO_ENTITY_VALID_PAIR",str(rejected))
        i,j,contacts,entity_identity=valid[0]
    else:
        i,j,contacts = candidates[0]
    evidence = {"target_match":matches[0][i], "partner_match":matches[1][j], "interface":contacts,
                "candidate_pairs":[{"target_chain":chains[x]["id"],"partner_chain":chains[y]["id"],
                                    "contact_pairs":len(c["residue_pairs"])} for x,y,c in candidates],
                "selection_rule":"maximum observed interface contacts after identity and coverage validation"}
    evidence.update(entity_identity=entity_identity,rejected_entity_pairs=rejected)
    return chains[i],chains[j],evidence

def write_pdb(path, chains):
    """Normalize selected physical chains to A/B, preserving all observed protein heavy atoms."""
    lines, serial = [],1
    for ci,chain in enumerate(chains):
        cid = chr(65+ci)
        require(len(chain["residues"]) <= 9999, "PDB_LIMIT", "Chain too long for PDB")
        for ri,(res,atoms) in enumerate(zip(chain["residues"],chain["atoms"]),1):
            for name,element,xyz in atoms:
                # Standard PDB atom-name alignment.
                atomname = name.rjust(4) if len(name)==4 else (" "+name.ljust(3))
                lines.append(f"ATOM  {serial:5d} {atomname} {res['name']:>3s} {cid}{ri:4d}    "
                             f"{xyz[0]:8.3f}{xyz[1]:8.3f}{xyz[2]:8.3f}{1.:6.2f}{0.:6.2f}          {element:>2s}")
                serial += 1
        lines.append("TER")
    Path(path).write_text("\n".join(lines+["END",""]))

def superpose(moving, fixed):
    """Row-vector Kabsch transform moving @ R + t."""
    moving, fixed = np.asarray(moving),np.asarray(fixed)
    require(moving.shape == fixed.shape and moving.shape[0]>=3, "ALIGNMENT_FAILED", "Need >=3 corresponding CAs")
    cm,cf=moving.mean(0),fixed.mean(0)
    u,s,vt=np.linalg.svd((moving-cm).T @ (fixed-cf))
    d=np.eye(3); d[-1,-1]=np.linalg.det(u@vt)
    r=u@d@vt; t=cf-cm@r
    return r,t,float(np.sqrt(np.mean(np.sum((moving@r+t-fixed)**2,axis=1))))

def transform(chain,r,t):
    return {**chain, "residues":[{**x,"ca":x["ca"]@r+t} for x in chain["residues"]],
            "heavy":[x@r+t for x in chain["heavy"]],
            "atoms":[[(n,e,x@r+t) for n,e,x in aa] for aa in chain["atoms"]]}

def competition(native_target,native_partner,designed_target,designed_binder,predicted_target,predicted_binder,cutoff=5):
    require(native_target["sequence"]==predicted_target["sequence"]==designed_target["sequence"],
            "TARGET_CHANGED","Target sequences must be identical for competition evaluation")
    ca=lambda c: np.array([r["ca"] for r in c["residues"]])
    r,t,trmsd=superpose(ca(predicted_target),ca(native_target))
    binder=transform(predicted_binder,r,t)
    rd,td,_=superpose(ca(designed_target),ca(native_target))
    designed=transform(designed_binder,rd,td)
    require(len(designed["residues"])==len(binder["residues"]),"BINDER_LENGTH_CHANGED","Refold length differs")
    brmsd=float(np.sqrt(np.mean(np.sum((ca(designed)-ca(binder))**2,axis=1))))
    _,_,fold_rmsd=superpose(ca(predicted_binder),ca(designed_binder))
    native=interface(native_target,native_partner,cutoff)
    predicted=interface(predicted_target,predicted_binder,cutoff)
    # These chains originate from different structures. Their author chain IDs may
    # coincide without representing the same physical chain.
    projected=interface({**native_target,"id":"reference_target"},
                        {**binder,"id":"projected_binder"},cutoff)
    a,b=set(native["target_residues"]),set(predicted["target_residues"])
    projected_residues=set(projected["target_residues"])
    # Overlapping atom coordinates after target alignment indicate incompatible simultaneous occupancy.
    distances=cKDTree(np.concatenate(native_partner["heavy"])).query(np.concatenate(binder["heavy"]),k=1)[0]
    return {"target_ca_rmsd":trmsd,"binder_ca_rmsd_after_target_alignment":brmsd,
            "binder_ca_rmsd_after_self_alignment":fold_rmsd,
            "native_interface_coverage":len(a&b)/max(len(a),1),
            "binder_interface_native_fraction":len(a&b)/max(len(b),1),
            "partner_overlap_atom_count_2A":int(np.sum(distances<2.0)),
            "contact_cutoff_angstrom":cutoff,
            "coverage_semantics":"native target residue indices intersect contacts in the actual predicted complex",
            "predicted_complex_interface":predicted,
            "reference_projection_interface":projected,
            "reference_projection_native_interface_coverage":len(a&projected_residues)/max(len(a),1)}

