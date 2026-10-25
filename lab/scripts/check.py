"""Check isolation, sense references, productive morphology and reproducible data."""
from pathlib import Path
from contextlib import closing
import collections,gzip,hashlib,json,re,sys
LAB=Path(__file__).resolve().parents[1];REPO=LAB.parent;sys.path.insert(0,str(REPO))
from vaeltharyn.search import rows,norm
from model import cases,assessments,proposals,RELATIONS
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def records(name):
 with gzip.open(LAB/'data'/name,'rt',encoding='utf-8') as stream:
  for line in stream:yield json.loads(line)
def morphology(row):
 word=row['mot'];cat=row['categorie'];forms={word}
 if cat=='n':forms.update(word+s+n+c for s in ('','il','aun','va') for n in ('','i') for c in ('','en','or','ath','ul'))
 elif cat=='adj':forms.update([word+'is',word+'eth'])
 elif cat=='v':
  stem=word[:-2];forms.update(p+stem+m+e for p in ('','ra','vi') for m in ('','ir','el') for e in ('em','es','e','om','os','en'))
  forms.update(stem+s for s in ('a','ai','in','or','el','eth'))
  if row['valence'].startswith('tr'):forms.add(stem+'un')
 return forms
def main():
 base=load(LAB/'baseline.json');allowed={'README.md','.gitignore'};checked=0
 for name,expected in base['files'].items():
  if name in allowed:continue
  raw=(REPO/name).read_bytes()
  if not name.startswith('data/'):raw=raw.replace(b'\r\n',b'\n')
  assert hashlib.sha256(raw).hexdigest()==expected,name;checked+=1
 lex=list(rows(REPO/'data/lexicon/fr/entries.csv'));words={r['mot']:r for r in lex};ids={r['id'] for r in lex}
 batch=cases();assert len({r['id'] for r in batch})==len(batch)
 assert all(not r['human_validated'] for r in batch)
 sense_lookup={s['id']:(e,s) for e in records('oewn-entries.jsonl.gz') for s in e['senses']}
 synsets={r['id']:r for r in records('oewn-synsets.jsonl.gz')}
 grammar_tokens=set();prospective={};new_forms={};phonology=[]
 for proposal in batch:
  assert set(proposal['canonical_ids'])<=ids
  if 'classification' in proposal:assert proposal['classification'] in ('missing_alias','additional_sense','productive_construction','new_word')
  else:assert proposal['relation'] in RELATIONS and proposal['scope']=='specified_context_only'
  assert proposal['note_fr'] and proposal['note_en']
  for sense_id in proposal.get('source_sense_ids',[]):
   entry,sense=sense_lookup[sense_id]
   assert entry['lemma']==proposal['forms']['en'] and entry['pos']==proposal['pos']
   assert sense['synset'] in proposal['source_synsets'] and sense['synset'] in synsets
  text=proposal['forms'].get('vh')
  if text:
   grammar_tokens.update(re.findall(r'[a-záéíóúý]+(?:-[a-záéíóúý]+)*',text.casefold()))
  else:assert proposal['status']=='unresolved_sense'
  if proposal.get('formation'):
   f=proposal['formation'];baseword=f['base'];assert words[baseword]['categorie']=='adj'
   assert f['suffix'] in ('eth','is') and text==baseword+f['suffix']
   assert proposal['pos']==('n' if f['suffix']=='eth' else 'r')
   if text in words:assert proposal['classification']=='already_covered'
   else:
    prospective[text]=proposal
    forms={text+n+c for n in ('','i') for c in ('','en','or','ath','ul')} if proposal['pos']=='n' else {text}
    for form in forms:new_forms.setdefault(form,[]).append(text)
   source_ipa=words[baseword]['api'];suffix_ipa='ɛθ' if f['suffix']=='eth' else 'is'
   ipa=source_ipa.rstrip('/')+'.'+suffix_ipa+'/' if source_ipa else None
   syllables=len(re.findall(r'ae|oe|ai|ei|au|oi|[aáeéiíoóuúyý]',baseword))+1
   phonology.append({'form':text,'base':baseword,'rule':f['rule'],'ipa_annotation':ipa,'syllables':syllables,'status':'written_morphophonology_only','audio_evaluated':False})
 found=set();collisions=collections.defaultdict(set)
 for row in lex:
  forms=morphology(row);found.update(grammar_tokens&forms)
  for hit in forms&new_forms.keys():
   for origin in new_forms[hit]:
    if row['mot']==prospective[origin]['formation']['base']:continue
    collisions[origin].add(row['mot'])
 for word in prospective:found.add(word)
 found.update(p+'-'+c for p in ('mi','ti','se','min','tin','sen','si') for c in ('en','or','ath','ul'))
 missing=grammar_tokens-found
 assert not missing,sorted(missing)
 # A detected collision must stop packaging; it is not silently approved.
 assert not collisions,{k:sorted(v) for k,v in collisions.items()}
 assert not any(re.search(r'\bmi (?:nu )?vele\b',p['forms'].get('vh') or '',re.I) for p in batch)
 classes=dict(collections.Counter(r['classification'] for r in proposals()));statuses=dict(collections.Counter(r['status'] for r in proposals()))
 report={'status':'pass','schema_version':2,'baseline_files_verified':checked,'baseline_linguistic_data_unchanged':True,'documented_context_assessments':len(assessments()),'proposed_changes':len(proposals()),'preserved_cases':len(batch),'classifications':classes,'proposal_statuses':statuses,'human_validated':0,'new_roots':0,'prospective_derived_forms':len(prospective),'unexpected_morphological_collisions':0,'covered_phrase_tokens':len(grammar_tokens),'source_sense_links_checked':sum(len(p.get('source_sense_ids',[])) for p in batch),'registers':dict(collections.Counter(p['register_source'] for p in batch)),'phonology':phonology,'audio_evaluated':False,'automatic_promotion':False}
 (LAB/'reports/review-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 data={p.relative_to(REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (LAB/'data').glob('*.gz')}
 (LAB/'reports/data-integrity.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='phonology'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
