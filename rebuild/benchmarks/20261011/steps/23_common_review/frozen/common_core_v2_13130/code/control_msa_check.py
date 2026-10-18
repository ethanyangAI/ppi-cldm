"""Verify ColabFold A3M roundtrip by exact per-chain feature semantics, not byte identity."""
import hashlib,json
from pathlib import Path
def fingerprint(obj):
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def parse_raw(path):
 lines=Path(path).read_text().splitlines();meta=lines[0];assert meta.startswith("#");records=[]
 for line in lines[1:]:
  if not line.strip():continue
  if line.startswith(">"):records.append([line[1:],""])
  else:
   assert records and not line.startswith("#")
   records[-1][1]+=line.strip()
 assert records and all(s for h,s in records)
 return meta,records
def parse_features(path):
 from colabfold.batch import get_queries,unserialize_msa
 from alphafold.data import parsers
 qs,is_complex=get_queries(Path(path));assert is_complex and len(qs)==1
 _,seq,lines=qs[0];up,pa,unique,cardinality,_=unserialize_msa(lines,seq)
 def parse_region(blocks):
  result=[]
  for text in blocks:
   parsed=parsers.parse_a3m(text)
   result.append({"sequences":list(parsed.sequences),"deletion_matrix":[list(map(int,r)) for r in parsed.deletion_matrix]})
  return result
 return {"query":unique,"cardinality":cardinality,"unpaired":parse_region(up),"paired":parse_region(pa)}
def verify_roundtrip(input_path,actual_path,target,binder):
 before=parse_features(input_path);after=parse_features(actual_path)
 assert before["query"]==after["query"]==[target,binder],"chain order/full query changed"
 assert before["cardinality"]==after["cardinality"]==[1,1],"chain cardinality changed"
 assert before["unpaired"]==after["unpaired"],"unpaired sequence order or deletion matrix changed"
 assert before["paired"]==after["paired"],"paired sequence order or deletion matrix changed"
 assert len(after["unpaired"])==len(after["paired"])==2
 assert after["unpaired"][1]["sequences"]==[binder]
 assert after["paired"][0]["sequences"]==[target] and after["paired"][1]["sequences"]==[binder]
 meta_a,a=parse_raw(input_path);meta_b,b=parse_raw(actual_path);assert meta_a==meta_b
 # Exact raw alignment strings preserve lowercase insertions, gaps and ordering.
 # The public parser removes repeated query rows. Record the precise kept-row map.
 mapping=[];cursor=0;skipped=[];changed_headers=[]
 for j,(h,s) in enumerate(b):
  while cursor<len(a) and a[cursor][1]!=s:skipped.append(cursor);cursor+=1
  assert cursor<len(a),"Actual raw A3M is not an ordered input subsequence"
  mapping.append(cursor)
  if a[cursor][0]!=h:changed_headers.append(j)
  cursor+=1
 skipped.extend(range(cursor,len(a)));retained={s for _,s in b}
 assert all(a[i][1] in retained for i in skipped),"A nonduplicate alignment row disappeared"
 regions={}
 for label in ("unpaired","paired"):
  regions[label]=[{"chain":i,"row_count":len(c["sequences"]),"ordered_sequences_sha256":fingerprint(c["sequences"]),"deletion_matrix_sha256":fingerprint(c["deletion_matrix"]),"deletion_total":sum(sum(x) for x in c["deletion_matrix"])} for i,c in enumerate(after[label])]
 return {"status":"EXACT_CHAIN_QUERY_PAIRED_UNPAIRED_ORDER_AND_DELETION_MATRICES_VERIFIED","chain_lengths":[len(target),len(binder)],"cardinality":[1,1],"input_raw_row_count":len(a),"actual_raw_row_count":len(b),"actual_row_to_input_row_0based":mapping,"removed_duplicate_input_rows_0based":skipped,"changed_header_actual_rows_0based":changed_headers,"regions":regions,"features_sha256":fingerprint(after),"note":"The actual A3M is retained and hashed separately. Exact input/output per-chain parser features match; removed raw duplicate query rows are explicitly mapped, never set-based acceptance."}

