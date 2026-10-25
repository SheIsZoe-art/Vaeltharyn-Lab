"""One source-to-canon correspondence ledger; no implicit sense approval."""
from pathlib import Path
import collections,hashlib,json,sys
LAB=Path(__file__).resolve().parents[1];REPO=LAB.parent;sys.path.insert(0,str(REPO))
from compare import baseline,dump,POS,MORPH_POS,source_terms
from model import jsonlines,read,assessments,proposals,SCHEMA
from vaeltharyn.search import norm,rows
def build():
 index=baseline();lex=list(rows(REPO/'data/lexicon/fr/entries.csv'));ids={r['id'] for r in lex}
 links={};linked={'fr':set(),'en':set()};counts={};source_entry_ids=set();sense_ids=set();sense_to_entry={}
 broad_parts=collections.defaultdict(set)
 for row in lex:
  if row['categorie']=='part':
   for term in source_terms(row,'fr'):broad_parts[norm(term)].add(row['id'])
 def add(source,target,method,decision=None):
  assert target['kind']!='lexeme' or target['id'] in ids
  identity='LNK-'+hashlib.sha256(json.dumps([source,target],sort_keys=True).encode()).hexdigest()[:20]
  if identity not in links:
   links[identity]={'id':identity,'source':source,'target':target,'relation':'uncertain','status':'unreviewed','human_validated':False,'evidence':[],'assessment_ids':[],'proposal_ids':[]}
  link=links[identity]
  if method not in link['evidence']:link['evidence'].append(method)
  if decision:
   field='assessment_ids' if decision['id'] in assessment_ids else 'proposal_ids'
   if field=='assessment_ids' and link['assessment_ids'] and link['relation']!=decision['relation']:
    raise ValueError('Conflicting context assessments for '+identity)
   if decision['id'] not in link[field]:link[field].append(decision['id'])
   if field=='assessment_ids':
    link['relation']=decision['relation'];link['status']='written_context_check'
   elif not link['assessment_ids']:link['status']='proposed_change'
  return link
 assessment_records=assessments();assessment_ids={r['id'] for r in assessment_records}
 for lang,name,resource in [('fr','morphalou-lemmas.jsonl.gz','morphalou'),('en','oewn-entries.jsonl.gz','oewn')]:
  total=matched=ambiguous=edges=source_senses=0
  for record in jsonlines(LAB/'data'/name):
   total+=1;source_entry_ids.add(record['id']);pos=record['pos']
   if lang=='fr':assert pos==MORPH_POS.get(record['source_category'],'unknown')
   matches=sorted(index.get((lang,norm(record['lemma']),pos),[])) if pos not in ('unknown','other','part') else []
   matched+=bool(matches);ambiguous+=len(matches)>1;edges+=len(matches);linked[lang].update(matches)
   source={'kind':'entry','resource':resource,'id':record['id']}
   for target_id in matches:add(source,{'kind':'lexeme','id':target_id},'exact_lemma_and_specific_pos')
   if lang=='fr' and pos not in ('n','a','v','r'):
    for target_id in broad_parts.get(norm(record['lemma']),[]):
     link=add(source,{'kind':'lexeme','id':target_id},'label_match_with_underspecified_target_category')
     link['status']='quarantined_pos'
   for sense in record.get('senses',[]):
    sense_ids.add(sense['id']);sense_to_entry[sense['id']]=record['id'];source_senses+=1
  counts[lang]={'source_records':total,'source_records_with_candidates':matched,'source_records_without_candidates':total-matched,'source_records_with_multiple_candidates':ambiguous,'automatic_candidate_edges':edges,'distinct_canonical_entries_with_candidates':len(linked[lang]),'canonical_entries_without_candidates':len(ids-linked[lang])}
  if lang=='en':counts[lang]['source_senses']=source_senses
 for decision in assessment_records+proposals():
  for target_id in decision['canonical_ids']:
   for source_id in decision.get('source_sense_ids',[]):
    assert source_id in sense_ids
    add({'kind':'sense','resource':'oewn','id':source_id},{'kind':'lexeme','id':target_id},'written_context_analysis',decision)
  for expression_key in decision.get('existing_expression_keys',[]):
   add({'kind':'context','resource':'lab','id':decision['id']},{'kind':'expression','id':expression_key},'existing_expression_reference',decision)
 dump(LAB/'data/alignments.jsonl.gz',(links[k] for k in sorted(links)))
 report={'schema_version':SCHEMA,'baseline_commit':read(LAB/'baseline.json')['commit'],'canonical_entries':len(ids),'sources':counts,'cross_source':{'entries_with_candidates_in_both':len(linked['fr']&linked['en']),'entries_with_candidates_in_either':len(linked['fr']|linked['en']),'entries_without_automatic_candidates':len(ids-(linked['fr']|linked['en']))},'correspondences':{'total':len(links),'relations':dict(collections.Counter(r['relation'] for r in links.values())),'statuses':dict(collections.Counter(r['status'] for r in links.values())),'semantic_equivalence_validated':sum(r['human_validated'] and r['relation']=='same_sense' for r in links.values())},'review':{'documented_contexts':len(assessment_records),'proposed_changes':len(proposals()),'proposal_classifications':dict(collections.Counter(r['classification'] for r in proposals())),'preserved_cases':len(assessment_records)+len(proposals())},'counting':'Candidate counts are form/POS matches, not semantic coverage. All canonical entries remain in the single frozen baseline, including entries with no external link.','canonical_source_modified':False}
 (LAB/'reports/coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 checks={p.relative_to(REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (LAB/'data').glob('*.gz')}
 (LAB/'reports/data-integrity.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2));return report
if __name__=='__main__':build()
