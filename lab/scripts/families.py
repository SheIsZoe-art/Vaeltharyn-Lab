"""Source-linked derivation queue; no inferred Vaeltharyn spelling is emitted."""
from pathlib import Path
import json,gzip,sys,collections
LAB=Path(__file__).resolve().parents[1];sys.path.insert(0,str(LAB/'scripts'))
from compare import dump
def load(name):
 with gzip.open(LAB/'data'/name,'rt',encoding='utf-8') as f:return [json.loads(line) for line in f]
def main():
 entries=load('oewn-entries.jsonl.gz');senses={s['id']:(e,s) for e in entries for s in e['senses']};records=[];seen=set()
 rules={('a','r'):['adjective + is'],('a','n'):['adjective + eth'],('n','a'):['noun + va'],('v','n'):['verb stem + eth (action)','verb stem + or (agent)','verb stem + el (instrument)']}
 for entry in entries:
  if not entry['existing_ids']:continue
  for sense in entry['senses']:
   for relation in sense['relations']:
    if relation['relType'] not in ('derivation','pertainym') or relation['target'] not in senses:continue
    target,ts=senses[relation['target']];key=(sense['id'],ts['id'])
    if key in seen:continue
    seen.add(key);hints=rules.get((entry['pos'],target['pos']),[])
    records.append({'base_source_sense':sense['id'],'base_lemma':entry['lemma'],'base_pos':entry['pos'],'existing_base_candidates':entry['existing_ids'],'target_source_sense':ts['id'],'target_synset':ts['synset'],'target_lemma':target['lemma'],'target_pos':target['pos'],'existing_target_candidates':target['existing_ids'],'source_relation':relation['relType'],'possible_rules':hints,'classification':'already_covered_candidate' if target['existing_ids'] else 'productive_construction_candidate' if hints else 'sense_review','status':'unreviewed','vaeltharyn':None,'note':'Source derivation links do not establish which Vaeltharyn sense, argument roles or derivation rule is appropriate.'})
 dump(LAB/'data/derivation-review.jsonl.gz',records)
 report={'source_linked_pairs':len(records),'classifications':dict(collections.Counter(r['classification'] for r in records)),'automatic_new_words':0,'human_validated':0}
 (LAB/'reports/families.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
