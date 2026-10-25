"""Reproducible lexical inventories; form matches never certify sense coverage."""
from pathlib import Path
import csv,gzip,hashlib,io,json,re,sys,collections,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parent))
from vaeltharyn.search import norm,rows
LAB=ROOT;REPO=ROOT.parent
POS={'n':'n','v':'v','adj':'a','adv':'r','a':'a','s':'a','r':'r','num':'num','part':'part'}
MORPH_POS={'Nom commun':'n','Adjectif qualificatif':'a','Adverbe':'r','Verbe':'v','Préposition':'prep','Pronom':'pron','Déterminant':'det','Conjonction':'conj','Nombre':'num','Interjection':'interj','':'unknown'}
def dump(path,records):
 with path.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as gz:
  with io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as out:
   for record in records:out.write(json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n')
def source_terms(row,lang):
 head=row['francais'] if lang=='fr' else row['english_headword']
 if head:return [head]
 head=row['sens'] if lang=='fr' else row['meaning']
 if '—' in head or len(head)>100:return []
 return [t.strip() for t in head.split(',') if t.strip()]
def baseline():
 index=collections.defaultdict(set);byid={}
 for lang in ('fr','en'):
  for row in rows(REPO/f'data/lexicon/{lang}/entries.csv'):
   identity=row['id'];byid[identity]=row
   cat=POS.get(row['categorie'] if lang=='fr' else row['category'],'other')
   for term in source_terms(row,lang):index[(lang,norm(term),cat)].add(identity)
 for alias in json.loads((REPO/'data/expressions/aliases.json').read_text(encoding='utf-8')):
  for target in alias['targets']:
   if target['registry']=='lexicon':
    cat=POS.get(byid[target['key']]['category'],'other');index[(alias['lang'],norm(alias['term']),cat)].add(target['key'])
 return index
def main():
 lock=json.loads((LAB/'sources/lock.json').read_text(encoding='utf-8'));cache=REPO/'.cache/external'
 for source in lock['files']:
  if source['file'] not in ('morphalou-3.1.zip','english-wordnet-2025.xml.gz'):continue
  with (cache/source['file']).open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==source['sha256']
 index=baseline();stats={};morph=[];seen=set();form_ids=set();category_counts=collections.Counter();match=0
 with zipfile.ZipFile(cache/'morphalou-3.1.zip') as archive:
  for name in sorted(n for n in archive.namelist() if n.endswith('.csv')):
   with archive.open(name) as raw,io.TextIOWrapper(raw,encoding='utf-8-sig',newline=None) as text:
    for row in csv.reader(text,delimiter=';'):
     if len(row)>10 and row[9] and row[10].isdigit():form_ids.add(row[10])
     if len(row)<9 or not row[0] or not row[1].isdigit():continue
     identity='morphalou-'+row[1]
     if identity in seen:continue
     seen.add(identity);category=row[2];category_counts[category]+=1
     pos=MORPH_POS.get(category,'unknown')
     matches=sorted(index.get(('fr',norm(row[0]),pos),[]));match+=bool(matches)
     morph.append({'id':identity,'lang':'fr','lemma':row[0],'pos':pos,'source_category':category,'subcategory':row[3],'locution':row[4],'gender':row[5],'linked_lemmas':row[6],'source_ipa':row[7],'origins':row[8],'sense_definition':None,'license':'LGPL-LR'})
 dump(LAB/'data/morphalou-lemmas.jsonl.gz',morph)
 stats['fr']={'source_lemma_records':len(morph),'unique_normalized_lemmas':len({norm(r['lemma']) for r in morph}),'unique_source_form_ids':len(form_ids),'lemma_pos_matches_requiring_sense_review':match,'unresolved_records':len(morph)-match,'source_categories':dict(category_counts),'automatic_new_vaeltharyn_words':0}
 del morph,form_ids
 entries=[];synsets=[];counts=collections.Counter();matched_entries=matched_senses=0;sense_total=relation_total=0
 with gzip.open(cache/'english-wordnet-2025.xml.gz','rb') as stream:
  for _,element in ET.iterparse(stream,events=['end']):
   if element.tag=='LexicalEntry':
    lemma=element.find('Lemma');word=lemma.get('writtenForm');pos=POS.get(lemma.get('partOfSpeech'),'other');matches=sorted(index.get(('en',norm(word),pos),[]))
    senses=[]
    for sense in element.findall('Sense'):
     links=[dict(r.attrib) for r in sense.findall('SenseRelation')]
     senses.append({'id':sense.get('id'),'synset':sense.get('synset'),'relations':links});relation_total+=len(links)
    entries.append({'id':element.get('id'),'lang':'en','lemma':word,'pos':pos,'forms':[f.attrib for f in element.findall('Form')],'senses':senses,'license':'CC-BY-4.0; WordNet notice'})
    counts[pos]+=1;sense_total+=len(senses);matched_entries+=bool(matches);matched_senses+=len(senses) if matches else 0;element.clear()
   elif element.tag=='Synset':
    definitions=[d.text or '' for d in element.findall('Definition')];examples=[e.text or '' for e in element.findall('Example')]
    relations=[r.attrib for r in element.findall('SynsetRelation')];relation_total+=len(relations)
    synsets.append({'id':element.get('id'),'pos':element.get('partOfSpeech'),'ili':element.get('ili'),'lexfile':element.get('lexfile'),'definitions':definitions,'examples':examples,'relations':relations,'license':'CC-BY-4.0; WordNet notice'});element.clear()
 dump(LAB/'data/oewn-entries.jsonl.gz',entries);dump(LAB/'data/oewn-synsets.jsonl.gz',synsets)
 stats['en']={'edition':'2025 core','source_lexical_entries':len(entries),'unique_normalized_lemmas':len({norm(r['lemma']) for r in entries}),'source_senses':sense_total,'source_synsets':len(synsets),'source_relations':relation_total,'lemma_pos_matches_requiring_sense_review':matched_entries,'sense_candidates_on_matched_entries':matched_senses,'unresolved_entries':len(entries)-matched_entries,'categories':dict(counts),'automatic_new_vaeltharyn_words':0}
 from reconcile import build
 build()
if __name__=='__main__':main()
