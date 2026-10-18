"""Explicit historical receipt roles for delivery validation; no current source exception."""
from pathlib import Path
from native_resource_closure_v2 import historical_gap
MSA=(
("74915aaf1ae3f21b5c2d7169ff53f1fd5d776772e0c89ea778f4572db831df9e",46425,"steps/23_common_review/runs/msa_content_12983/msa.json","edfd913d745b84e8412bcb13a46dd2862f63fc9757d8e9c69c7e7ff153b9e61f"),
("e52a1598f3736e4c83512811e7a84037206a9cb1c13066981492345554b42d08",46094,"steps/23_common_review/runs/msa_12975/msa.json","7084743586acf57dceef5260060949962b25ebb11d2e311650b9586208734d00"))
LEGACY="b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd"
class HistoricalScopeVerifier:
    def __init__(self,resolver,policy=None):
        self.resolver=resolver;self.root=resolver.authority;self.policy=policy or {}
        if self.policy:
            actual=self.policy.get("entries",[])
            expected={(str(self.root/"source/rebuild/benchmark_common_review.py"),sha,size,str(self.root/parent),p_sha,("source",)) for sha,size,parent,p_sha in MSA}
            observed={(e["logical_path"],e["expected_sha256"],e["expected_bytes"],e["parent_path"],e["parent_sha256"],tuple(e["field"])) for e in actual}
            if len(actual)!=2 or observed!=expected:raise ValueError("Only two exact approved MSA derivation entries allowed")
            for e in actual:
                if e["status"]!="HISTORICAL_UNRESOLVED_MSA_DERIVATION" or e.get("current_execution_allowed") is not False:raise ValueError("Historical policy enables unknown current source")
    def metadata(self,h):
        if h.get("status")!="HISTORICAL_UNRESOLVED_PROVENANCE" or h.get("current_PASS_allowed") is not False:raise ValueError("Historical metadata lacks non-current status")
        r=h["original"];k=(r["path"],r["sha256"])
        if k not in self.resolver.unresolved:raise ValueError("Historical metadata not declared in exact alias index")
        known=self.resolver.unresolved[k]
        if known["original"]!=r:raise ValueError("Historical metadata changes exact missing receipt")
        if h.get("subtype")=="HISTORICAL_UNRESOLVED_MSA_DERIVATION":
            if not self.policy or historical_gap(r,h.get("parent"),tuple(h.get("trail",[])),self.policy,self.resolver) is None:
                raise ValueError("MSA metadata does not bind exact approved parent/field policy")
        elif r["path"]==str(self.root/"source/rebuild/benchmark_runtime.py") and r["sha256"]==LEGACY and r.get("bytes")==33676:
            # This permits a labelled registry record only, never a current receipt edge.
            pass
        else:raise ValueError("Unknown historical source exception")
        return True
    def edge(self,r,parent,trail):
        return historical_gap(r,str(parent),tuple(trail),self.policy,self.resolver) is not None
    def logical_parents(self,physical,sha):
        p=Path(physical).absolute();result=[]
        for entry in self.resolver.entries.values():
            a=entry["archived"]
            if a["sha256"]==sha and self.resolver.map_path(a["path"])==p:
                result.append(entry["original"]["path"])
        return sorted(set(result)) or [str(p)]

