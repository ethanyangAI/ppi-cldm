import argparse
import json
import sys
from .common import EvidenceError, read_json
from .pipeline import prepare,predict,design,evaluate,reevaluate,all_stages

def main():
    parser=argparse.ArgumentParser(description="Identity-verified protein interaction pose and computational blocker pipeline")
    parser.add_argument("--root",required=True,help="Authoritative project root; contains isolated step runs")
    subs=parser.add_subparsers(dest="command",required=True)
    for name in ("prepare","run"):
        p=subs.add_parser(name);p.add_argument("config")
    for name in ("predict","design","evaluate","reevaluate"):
        p=subs.add_parser(name);p.add_argument("manifest",help="Explicit upstream manifest, never latest")
    args=parser.parse_args()
    try:
        fn={"prepare":prepare,"predict":predict,"design":design,"evaluate":evaluate,"reevaluate":reevaluate,"run":all_stages}[args.command]
        path=fn(args.root,getattr(args,"config",None) or args.manifest)
        print(json.dumps({"manifest":str(path),"status":read_json(path)["status"]},ensure_ascii=False))
        return 0 if read_json(path)["status"] not in ("POSE_REJECTED","PREDICTION_INCOMPLETE","EVALUATION_INCOMPLETE") else 2
    except EvidenceError as e:
        print(json.dumps({"error":e.code,"message":str(e)}),file=sys.stderr);return 2

if __name__=="__main__":
    sys.exit(main())

