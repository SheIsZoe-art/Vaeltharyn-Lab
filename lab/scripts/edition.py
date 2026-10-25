"""Defined experimental dictionary additions; the stable corpus is never rewritten."""
from functools import lru_cache
import hashlib,json,collections,re,sys
from model import LAB,REPO,read,jsonlines
sys.path.insert(0,str(REPO))
from vaeltharyn.search import rows,norm
from check import morphology

@lru_cache(maxsize=2)
def _records(stamp):return read(LAB/'edition/entries.json')

def records():
 p=LAB/'edition/entries.json'
 return _records((p.stat().st_size,p.stat().st_mtime_ns))

@lru_cache(maxsize=2)
def _index(stamp):
 result=collections.defaultdict(dict)
 for r in records():
  for lang in ('fr','en'):
   for term in r['headwords'][lang]+(r.get('search_descriptions_en',[]) if lang=='en' else []):result[(lang,norm(term))][r['id']]=r
  for term in morphology({'mot':r['word'],'categorie':r['category'],'valence':r['valency']}):result[('vh',norm(term))][r['id']]=r
 return result

def query(lang,terms,limit=8):
 path=LAB/'edition/entries.json';index=_index((path.stat().st_size,path.stat().st_mtime_ns))
 return {'edition':read(LAB/'edition/manifest.json'),'results':{term:{'total':len(index[(lang,norm(term))]),'entries':list(index[(lang,norm(term))].values())[:limit]} for term in terms},'scope':'Defined experimental additions; baseline results are supplied separately.'}

def entry(identity):
 record=next((r for r in records() if r['id']==identity),None)
 if record is None:raise ValueError('Unknown experimental entry ID: '+identity)
 return {'edition_entry':record,'edition':read(LAB/'edition/manifest.json'),'canonical_data_modified':False}

def source_links(identities):
 wanted=set(identities)
 return [{'target_id':r['id'],'target_word':r['word'],'binding':b} for r in records() for b in r['source_bindings'] if b['source_id'] in wanted]

def validate():
 additions=records();base=list(rows(REPO/'data/lexicon/fr/entries.csv'));baseline={r['id']:r for r in base};byid={r['id']:r for r in additions}
 assert len(byid)==len(additions) and len({r['word'] for r in additions})==len(additions)
 assert not set(byid)&set(baseline)
 morph_ids={r['id'] for r in jsonlines(LAB/'data/morphalou-lemmas.jsonl.gz')}
 senses={s['id'] for r in jsonlines(LAB/'data/oewn-entries.jsonl.gz') for s in r['senses']}
 forms=collections.defaultdict(set)
 for r in additions:
  assert r['definition_fr'].strip() and r['definition_en'].strip() and r['ipa'] and r['syllables']>0
  assert not r['human_validated'] and not r['audio_evaluated']
  assert r['source_references'] or r['formation']['base_ids'],r['word']
  assert r['id']=='VLX-'+hashlib.sha256((r['word']+'|'+r['category']).encode()).hexdigest()[:16]
  assert r['category'] in ('n','adj','adv','v')
  assert re.fullmatch(r'[a-z]+(?:-[a-z]+)*',r['word'])
  for parent in r['formation']['base_ids']:assert parent in baseline or parent in byid
  if r['formation'].get('suffix'):
   parent=baseline[r['formation']['base_ids'][0]];suffix=r['formation']['suffix']
   stem=parent['mot'][:-2] if r['formation']['rule']=='verb_to_action' else parent['mot']
   assert r['word']==stem+suffix
   assert parent['definition_fr'] in r['definition_fr']
   assert r['selection_evidence']['parent_definition_fr_exact_match']==parent['definition_fr']
   assert r['selection_evidence']['parent_gloss_distinct_count']==1
   expected={'adj_to_adv':('adj','adv','is'),'adj_to_property':('adj','n','eth'),'noun_to_relative':('n','adj','va'),'verb_to_action':('v','n','eth')}
   assert (parent['categorie'],r['category'],suffix)==expected[r['formation']['rule']]
  for b in r['source_bindings']:
   assert b['scope'] in ('specified_definition_only','recorded_definition_only')
   assert b['source_id'] in (morph_ids if b['resource']=='morphalou' else senses)
  for f in morphology({'mot':r['word'],'categorie':r['category'],'valence':r['valency']}):forms[f].add(r['id'])
 for r in base:
  for f in morphology(r)&forms.keys():
   for identity in forms[f]:assert r['id'] in byid[identity]['formation']['base_ids'],(f,identity,r['id'])
 example_tokens={t for r in additions for ex in r['examples'] for t in re.findall(r'[a-z]+(?:-[a-z]+)*',ex['vh'].lower())}
 known=set(forms)
 for r in base:known.update(morphology(r)&example_tokens)
 assert not example_tokens-known,sorted(example_tokens-known)
 for form,owners in forms.items():
  for a in owners:
   for b in owners-{a}:assert a in byid[b]['formation']['base_ids'] or b in byid[a]['formation']['base_ids'],(form,a,b)
 manifest=read(LAB/'edition/manifest.json');assert manifest['added_entries']==len(additions) and manifest['dictionary_entries']==len(base)+len(additions)
 report=read(LAB/'reports/edition.json');assert report['targets_fully_completed'] is False
 resolutions=read(LAB/'edition/resolutions.json');old={r['id']:r for r in read(LAB/'proposals/batch-001.json')}
 for r in resolutions:assert r['case_id'] in old and r['edition_entry_id'] in byid
 return {'status':'pass','added_entries_checked':len(additions),'baseline_entries':len(base),'dictionary_entries':len(base)+len(additions),'unrelated_morphological_collisions':0,'source_bindings_checked':sum(len(r['source_bindings']) for r in additions),'edition_sha256':hashlib.sha256((LAB/'edition/entries.json').read_bytes()).hexdigest()}

if __name__=='__main__':
 report=validate();(LAB/'reports/edition-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
