"""
构建多样化人类蛋白质反筛库：
覆盖激酶、蛋白酶、核受体、GPCR、离子通道、代谢酶、
表观遗传靶标、转运蛋白等，共 ~100 个代表性靶标。
每个靶标：下载 PDB → 准备 receptor PDBQT → 计算 pocket center（HETATM 配体质心）
"""
import os, json, urllib.request
from pathlib import Path
from Bio.PDB import PDBParser
import numpy as np

OUT_DIR  = Path("/home/huangym/zjy/ppi_gen_project/structures/offtargets_db")
DB_OUT   = Path("/home/huangym/zjy/ppi_gen_project/core/denovo/offtarget_db.json")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Curated diverse human drug target library
# Format: name -> (pdb_id, chain_receptor, description)
# Selected to cover all major druggable protein families
# ------------------------------------------------------------------
TARGETS = {
    # === Kinases (serine/threonine & tyrosine) ===
    "CDK2":      ("1hcl", "A", "Cyclin-dependent kinase 2"),
    "EGFR":      ("1iep", "A", "EGF receptor kinase"),
    "ABL1":      ("2hyy", "A", "BCR-ABL tyrosine kinase"),
    "SRC":       ("2src", "A", "Proto-oncogene Src kinase"),
    "BRAF":      ("1uwh", "A", "BRAF serine/threonine kinase"),
    "AKT1":      ("3cqw", "A", "AKT1 serine/threonine kinase"),
    "MAPK14":    ("1a9u", "A", "p38 MAP kinase"),
    "JAK2":      ("2xj4", "A", "JAK2 kinase"),
    "VEGFR2":    ("2oh4", "A", "VEGF receptor 2"),
    "PLK1":      ("2ojx", "A", "Polo-like kinase 1"),
    "Aurora_A":  ("1mq4", "A", "Aurora kinase A"),
    "ROCK1":     ("2esm", "A", "Rho-associated kinase 1"),
    "PI3K":      ("2rd0", "A", "PI3-kinase gamma"),

    # === Proteases ===
    "Thrombin":  ("1ppb", "H", "Serine protease thrombin"),
    "FactorXa":  ("1fjs", "L", "Coagulation factor Xa"),
    "BACE1":     ("2b8v", "A", "Beta-site APP cleaving enzyme 1"),
    "HIV_PR":    ("3oxc", "A", "HIV-1 protease"),
    "MMP3":      ("1g49", "A", "Matrix metalloproteinase 3"),
    "ACE":       ("1o86", "A", "Angiotensin-converting enzyme"),
    "Cathepsin_L":("2xu3","A", "Cathepsin L"),
    "DPP4":      ("2bug", "A", "Dipeptidyl peptidase 4"),
    "NS3_HCV":   ("3kql", "A", "HCV NS3/4A protease"),

    # === Nuclear receptors ===
    "ERalpha":   ("1ere", "A", "Estrogen receptor alpha"),
    "ARec":      ("1t7r", "A", "Androgen receptor"),
    "PPARgamma": ("1prg", "A", "PPAR gamma"),
    "GR":        ("1m2z", "A", "Glucocorticoid receptor"),
    "RAR":       ("1fby", "A", "Retinoic acid receptor"),
    "VDR":       ("1db1", "A", "Vitamin D receptor"),
    "FXR":       ("1osv", "A", "Farnesoid X receptor"),

    # === GPCRs ===
    "Beta2AR":   ("2rh1", "A", "Beta-2 adrenergic receptor"),
    "A2A":       ("3eml", "A", "Adenosine A2A receptor"),
    "D3R":       ("3pbl", "A", "Dopamine D3 receptor"),
    "CXCR4":     ("3odu", "A", "Chemokine receptor CXCR4"),

    # === Ion channels ===
    "hERG":      ("5va1", "A", "hERG potassium channel"),

    # === Metabolic enzymes ===
    "CYP3A4":    ("4k9v", "A", "Cytochrome P450 3A4"),
    "CYP2D6":    ("2f9q", "A", "Cytochrome P450 2D6"),
    "DHFR":      ("1kms", "A", "Dihydrofolate reductase"),
    "HMGCR":     ("1hwk", "A", "HMG-CoA reductase"),
    "COX2":      ("6cox", "A", "Cyclooxygenase-2"),
    "MAO_A":     ("2bxr", "A", "Monoamine oxidase A"),
    "MAO_B":     ("2bk3", "A", "Monoamine oxidase B"),
    "ALDH":      ("1o02", "A", "Aldehyde dehydrogenase"),
    "IMPDH":     ("1jr1", "A", "Inosine 5-monophosphate dehydrogenase"),
    "PNMT":      ("1hnn", "A", "Phenylethanolamine N-methyltransferase"),
    "TYMS":      ("1syh", "A", "Thymidylate synthase"),

    # === Epigenetic targets ===
    "BRD4":      ("3mxf", "A", "Bromodomain BRD4"),
    "HDAC2":     ("3max", "A", "Histone deacetylase 2"),
    "HDAC8":     ("1t64", "A", "Histone deacetylase 8"),
    "EZH2":      ("5ij0", "A", "Histone methyltransferase EZH2"),
    "LSD1":      ("2z5u", "A", "Lysine demethylase LSD1"),
    "PRMT5":     ("4x61", "A", "Protein arginine methyltransferase 5"),
    "DOT1L":     ("3qow", "A", "DOT1-like histone methyltransferase"),
    "SIRT2":     ("3zgv", "A", "Sirtuin-2 deacetylase"),

    # === DNA damage / repair ===
    "PARP1":     ("4hm9", "A", "Poly ADP-ribose polymerase 1"),
    "TopoisoII": ("1zxm", "A", "DNA topoisomerase II"),
    "DNAPK":     ("5lua", "A", "DNA-dependent protein kinase"),
    "WEE1":      ("3cr0", "A", "WEE1 kinase"),
    "CHK1":      ("1nvs", "A", "Checkpoint kinase 1"),

    # === Chaperones ===
    "HSP90a":    ("1yet", "A", "HSP90 alpha ATPase domain"),
    "HSP70":     ("2qwl", "A", "HSP70 ATPase domain"),

    # === GTPases / signaling ===
    "KRAS_G12C": ("6oim", "A", "KRAS G12C mutant"),
    "RAC1":      ("2c2h", "A", "Rac1 GTPase"),
    "CDC42":     ("1cf4", "A", "CDC42 GTPase"),

    # === Transport / carrier proteins ===
    "HSA":       ("1ao6", "A", "Human serum albumin"),

    # === Phosphatases ===
    "PTP1B":     ("1c83", "A", "Protein tyrosine phosphatase 1B"),
    "SHP2":      ("5ei2", "A", "SHP-2 phosphatase"),
    "PP2A":      ("2iae", "A", "Protein phosphatase 2A"),

    # === E3 ligases / UPS ===
    "MDM2":      ("1rv1", "A", "MDM2 ubiquitin ligase"),
    "XIAP_BIR3": ("1g73", "A", "XIAP BIR3 domain"),

    # === Transcription factors / PPI ===
    "PCNA":      ("1vym", "A", "PCNA sliding clamp"),
    "RAD51":     ("1szp", "A", "RAD51 recombinase"),

    # === Aminoacyl-tRNA synthetases (off-target concern) ===
    "ILERS":     ("1ile", "A", "Isoleucyl-tRNA synthetase"),

    # === Other important drug targets ===
    "PDE4B":     ("1ro6", "A", "Phosphodiesterase 4B"),
    "PDE5":      ("1t9s", "A", "Phosphodiesterase 5A"),
    "CA2":       ("1ca2", "A", "Carbonic anhydrase II"),
    "AChE":      ("1eve", "A", "Acetylcholinesterase"),
    "LDHA":      ("1i0z", "A", "Lactate dehydrogenase A"),
    "IDH1":      ("4umx", "A", "Isocitrate dehydrogenase 1"),
    "PKM2":      ("3gr4", "A", "Pyruvate kinase M2"),
    "GLS":       ("3vod", "A", "Glutaminase"),
    "FASN":      ("2vz8", "A", "Fatty acid synthase thioesterase"),
    "RRM2":      ("2ug0", "A", "Ribonucleotide reductase M2"),

    # === Viral targets (cross-reactivity check) ===
    "NS5B_HCV":  ("2dxs", "A", "HCV RNA polymerase NS5B"),
    "RT_HIV":    ("1hni", "A", "HIV reverse transcriptase"),
}

ATYPE_MAP = {'C':'C','N':'NA','O':'OA','S':'SA','P':'P',
             'F':'F','CL':'Cl','BR':'Br','I':'I','H':'HD',
             'FE':'Fe','ZN':'Zn','MG':'Mg','CA':'Ca','MN':'Mn',
             'CU':'Cu','NI':'Ni','CO':'Co'}

def download_pdb(pdb_id, out_path):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    urllib.request.urlretrieve(url, out_path)

def prepare_pdbqt(pdb_path, chain_r, out_pdbqt):
    lines_out = []
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith('ATOM'):
                continue
            if line[21] != chain_r:
                continue
            elem = line[76:78].strip() if len(line) > 76 else ''
            if not elem:
                name = line[12:16].strip()
                elem = ''.join(c for c in name if c.isalpha())[:2].upper()
            atype = ATYPE_MAP.get(elem, elem[:1] if elem else 'C')
            pdbqt_line = line[:54]
            occ  = line[54:60].strip() or '1.00'
            bfac = line[60:66].strip() or '0.00'
            try:
                pdbqt_line += f'{float(occ):6.2f}{float(bfac):6.2f}    0.0000 {atype:<2}\n'
            except:
                continue
            lines_out.append(pdbqt_line)
    if not lines_out:
        raise ValueError(f"No ATOM records for chain {chain_r} in {pdb_path}")
    with open(out_pdbqt, 'w') as f:
        f.writelines(lines_out)
    return len(lines_out)

def get_pocket_center(pdb_path, chain_r):
    p = PDBParser(QUIET=True)
    s = p.get_structure('x', pdb_path)
    coords = []
    # Try HETATM ligands first (excluding water, metals)
    skip_res = {'HOH','WAT','SO4','PO4','GOL','EDO','PEG','DMS','MPD',
                'FMT','ACE','CL','NA','MG','ZN','FE','CA','MN','CU'}
    for model in s:
        for chain in model:
            if chain.id != chain_r:
                continue
            for res in chain.get_residues():
                if res.id[0] == ' ':
                    continue  # skip ATOM residues
                if res.get_resname().strip() in skip_res:
                    continue
                for atom in res.get_atoms():
                    coords.append(atom.get_coord())
    if len(coords) >= 3:
        return np.mean(coords, axis=0).tolist()
    # Fall back: centroid of chain
    for model in s:
        for chain in model:
            if chain.id == chain_r:
                coords = [a.get_coord() for a in chain.get_atoms()]
                if coords:
                    return np.mean(coords, axis=0).tolist()
    return None

if __name__ == '__main__':
    db = {}
    ok, fail = 0, 0

    for name, (pdb_id, chain_r, desc) in TARGETS.items():
        pdb_path  = OUT_DIR / f"{name}_{pdb_id}.pdb"
        pdbqt_path= OUT_DIR / f"{name}_receptor.pdbqt"

        try:
            if not pdb_path.exists():
                download_pdb(pdb_id, pdb_path)

            n_atoms = prepare_pdbqt(pdb_path, chain_r, pdbqt_path)

            center = get_pocket_center(pdb_path, chain_r)
            if center is None:
                raise ValueError("could not compute pocket center")

            db[name] = {
                "pdb_id": pdb_id,
                "chain_receptor": chain_r,
                "description": desc,
                "pdb_path": str(pdb_path),
                "pdbqt_path": str(pdbqt_path),
                "pocket_center": [round(c, 2) for c in center],
                "box_size": [25, 25, 25],
            }
            print(f"  OK  {name:20s}  {n_atoms:4d} atoms  center={[round(c,1) for c in center]}")
            ok += 1

        except Exception as e:
            print(f"  FAIL {name:20s}  {e}")
            fail += 1

    with open(DB_OUT, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"\nDone: {ok} OK, {fail} failed -> {DB_OUT}")
