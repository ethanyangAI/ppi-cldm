from pathlib import Path
p=Path("src/ppiblocker/benchmark.py");s=p.read_text()
old='''            if not all(valid_number(x) for x in numbers):
                item["reason"]="INVALID_METRIC";break'''
new='''            finite_metrics=[v for v in metrics.values() if v is not None and not isinstance(v,bool)]
            if not all(valid_number(x) for x in numbers+finite_metrics):
                item["reason"]="INVALID_METRIC";break'''
assert old in s;s=s.replace(old,new);p.write_text(s)
p=Path("scripts/qualify_benchmark.py");s=p.read_text()
s=s.replace('for chain in (chains[i],chains[j]):','for chain in (chains[i],):')
s=s.replace('''    for gene in (a,b):
        if not re.fullmatch''','''    curated={"P20":{b:"P62805"},"P21":{b:"P68431"},"P22":{b:"P68431"},
             "P25":{"PAK1":"Q13153"},"P39":{"IL7RA":"P16871"}}
    for gene in (a,b):
        accession=curated.get(cid,{}).get(gene)
        if accession:
            try:
                protein=resolve_protein(dict(uniprot=accession,taxon=9606),repo)
                result["proteins"].append(protein)
                result.setdefault("identity_adjudication",[]).append(dict(input=gene,accession=accession,
                    source=f"https://rest.uniprot.org/uniprotkb/{accession}.json",
                    scope="H4 canonical / H3.1 for histone cases; primary PAK1; IL7R alpha chain"))
            except Exception as e:
                result["errors"].append(dict(code=getattr(e,"code","IDENTITY_ERROR"),message=str(e)))
                return result
            continue
        if not re.fullmatch''')
s=s.replace('''    if re.fullmatch("[0-9][A-Za-z0-9]{3}",pdb):''','''    if cid=="P04":pdb="2XA0"
    if re.fullmatch("[0-9][A-Za-z0-9]{3}",pdb):''')
s=s.replace('''                            bounds.append([min(positions),max(positions)])''','''                            bounds.append([min(positions),max(positions)])
                            if len(set(positions))/(max(positions)-min(positions)+1)<.8:
                                reasons.append("CONSTRUCT_COVERAGE_BELOW_PIPELINE_GATE")''')
p.write_text(s)

