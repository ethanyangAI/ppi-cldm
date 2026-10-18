from __future__ import annotations
import hashlib
import re
from pathlib import Path
from urllib.parse import urlencode
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .common import EvidenceError, atomic_json, digest, read_json, require

AA = set("ACDEFGHIKLMNPQRSTVWY")

def clean_sequence(sequence):
    lines = [s.strip() for s in sequence.splitlines() if not s.startswith(">")]
    sequence = "".join(lines).replace(" ", "").upper()
    require(bool(sequence) and set(sequence) <= AA, "INVALID_SEQUENCE",
            "Use canonical amino acids; ambiguous residues and multiple FASTA records need explicit resolution.")
    require(sequence.count(">") == 0, "INVALID_SEQUENCE", "FASTA format invalid")
    return sequence

class Repository:
    def __init__(self, cache):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "ppiblocker-research/0.1"
        retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.receipts = []

    def get(self, url, binary=False):
        key = hashlib.sha256(url.encode()).hexdigest()
        path = self.cache / (key + (".bin" if binary else ".json"))
        receipt_path = self.cache / (key + ".receipt.json")
        if path.exists():
            require(receipt_path.exists(), "CACHE_UNVERIFIED", str(path))
            receipt = read_json(receipt_path)
            require(digest(path) == receipt["sha256"], "CACHE_CORRUPT", str(path))
        else:
            response = self.session.get(url, timeout=(15, 120))
            if response.status_code == 404:
                raise EvidenceError("NOT_FOUND", url)
            require(response.ok, "REMOTE_UNAVAILABLE", f"{response.status_code}: {url}")
            if binary:
                data = response.content
                temp = path.with_suffix(".part")
                temp.write_bytes(data)
                temp.replace(path)
            else:
                atomic_json(path, response.json())
            receipt = {"retrieved_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "url": url, "path": str(path.resolve()), "sha256": digest(path)}
            atomic_json(receipt_path, receipt)
        self.receipts.append(receipt)
        return path if binary else read_json(path)

    def entry(self, pdb):
        return self.get("https://data.rcsb.org/rest/v1/core/entry/" + pdb.upper())

    def entity(self, pdb, entity):
        return self.get(f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb.upper()}/{entity}")

def resolve_protein(spec, repo):
    require(isinstance(spec, dict), "INVALID_INPUT", "Each protein must be an object")
    result = dict(spec)
    sequence = spec.get("sequence")
    if sequence:
        require(not spec.get("uniprot") and not spec.get("gene"), "CONFLICTING_IDENTITY_INPUT", "Choose accession/gene resolution or an explicit sequence, not both")
        require(sum(line.startswith(">") for line in sequence.splitlines()) <= 1,
                "MULTIPLE_FASTA_RECORDS", "One sequence per protein object")
        result["sequence"] = clean_sequence(sequence)
        result.setdefault("id", "sequence_" + hashlib.sha256(result["sequence"].encode()).hexdigest()[:12])
        result["identity_source"] = "provided_sequence"
    else:
        accession = spec.get("uniprot")
        if not accession:
            require(spec.get("gene") and spec.get("taxon"), "AMBIGUOUS_IDENTITY",
                    "Provide UniProt accession, or exact gene plus taxon, or sequence")
            query = f"gene_exact:{spec['gene']} AND organism_id:{int(spec['taxon'])} AND reviewed:true"
            url = "https://rest.uniprot.org/uniprotkb/search?" + urlencode({"query": query, "format": "json", "size": 25})
            matches = repo.get(url).get("results", [])
            # UniProt gene_exact also matches synonyms. Prefer an unambiguous primary gene
            # name, but never resolve multiple primary matches by hit ordering.
            primary = [m for m in matches if any(
                g.get("geneName", {}).get("value", "").upper() == spec["gene"].upper()
                for g in m.get("genes", []))]
            result["gene_resolution"] = {
                "query_gene": spec["gene"],
                "matched_accessions": [m["primaryAccession"] for m in matches],
                "primary_gene_accessions": [m["primaryAccession"] for m in primary],
                "rule": "unique_primary_name_else_unique_search_hit",
            }
            if primary:
                matches = primary
            require(len(matches) == 1, "AMBIGUOUS_IDENTITY",
                    f"Expected exactly one reviewed gene match; found {[m['primaryAccession'] for m in matches]}")
            accession = matches[0]["primaryAccession"]
        require(bool(re.fullmatch(r"[A-Za-z0-9]+(?:-\d+)?", accession)), "INVALID_ACCESSION", str(accession))
        data = repo.get(f"https://rest.uniprot.org/uniprotkb/{accession}.json")
        actual_taxon = data["organism"]["taxonId"]
        require(not spec.get("taxon") or int(spec["taxon"]) == actual_taxon, "SPECIES_MISMATCH", accession)
        result.update(id=accession, uniprot=accession, taxon=actual_taxon,
                      sequence=clean_sequence(data["sequence"]["value"]), identity_source="uniprot")
    full = result["sequence"]
    if spec.get("residues"):
        bounds = spec["residues"]
        require(len(bounds) == 2 and all(isinstance(x, int) for x in bounds), "INVALID_RANGE", str(bounds))
        a, b = bounds
        require(1 <= a <= b <= len(full), "INVALID_RANGE", str(bounds))
        result["sequence"] = full[a - 1:b]
        result["canonical_start"] = a
    else:
        result["canonical_start"] = 1
    result["sequence_sha256"] = hashlib.sha256(result["sequence"].encode()).hexdigest()
    require(len(result["sequence"]) >= 5, "INVALID_SEQUENCE", "Construct shorter than five residues")
    return result

def search_experimental_pair(proteins, repo, limit=20):
    """Exact reference accession search; sequence-only inputs require explicit structure or prediction."""
    if not all(p.get("uniprot") for p in proteins):
        return []
    nodes = [{"type": "terminal", "service": "text", "parameters": {
        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
        "operator": "exact_match", "value": p["uniprot"].split("-")[0]}} for p in proteins]
    query = {"query": {"type": "group", "logical_operator": "and", "nodes": nodes},
             "return_type": "entry", "request_options": {"paginate": {"start": 0, "rows": limit},
             "results_content_type": ["experimental"]}}
    url = "https://search.rcsb.org/rcsbsearch/v2/query?" + urlencode({"json": __import__("json").dumps(query)})
    response = repo.session.get(url, timeout=(15, 60))
    if response.status_code == 204:
        return []
    require(response.ok, "SEARCH_UNAVAILABLE", f"RCSB returned {response.status_code}; do not interpret as no structures")
    data = response.json()
    key=hashlib.sha256(url.encode()).hexdigest()
    path=repo.cache/(key+".search.json")
    atomic_json(path,data)
    repo.receipts.append({"url":url,"path":str(path.resolve()),"sha256":digest(path),"retrieved_utc":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
    return [r["identifier"] for r in data.get("result_set", [])]

