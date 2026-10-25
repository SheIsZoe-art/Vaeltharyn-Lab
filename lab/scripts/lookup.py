"""Indexed laboratory queries with a single correspondence ledger."""
from pathlib import Path
from contextlib import closing
import argparse,gzip,hashlib,json,os,sqlite3,sys,tempfile,urllib.request,zipfile
from model import LAB,REPO,SCHEMA,read,jsonlines,proposals,assessments
sys.path.insert(0,str(REPO))
from vaeltharyn.search import norm,lookup,connect
from vaeltharyn.resources import manifest
def fetch():
 cache=REPO/'.cache/external';cache.mkdir(parents=True,exist_ok=True)
 for source in read(LAB/'sources/lock.json')['files']:
  if source['file'] not in ('morphalou-3.1.zip','english-wordnet-2025.xml.gz'):continue
  path=cache/source['file']
  if not path.exists():
   temp=path.with_suffix(path.suffix+'.download')
   try:
    with urllib.request.urlopen(source['url'],timeout=45) as response,temp.open('wb') as output:
     while chunk:=response.read(1024*1024):output.write(chunk)
    with temp.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==source['sha256'],'Source hash mismatch'
    temp.replace(path)
   finally:
    if temp.exists():temp.unlink()
  with path.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==source['sha256']
 return {'status':'pass','sources':'pinned files verified'}
def source_db():
 paths=sorted((LAB/'data').glob('*.jsonl.gz'))+[LAB/'mappings/assessments.json',LAB/'proposals/batch-001.json']
 stamp=hashlib.sha256(json.dumps([SCHEMA,[(p.relative_to(LAB).as_posix(),p.stat().st_size,p.stat().st_mtime_ns) for p in paths]]).encode()).hexdigest()
 directory=REPO/'.cache';directory.mkdir(exist_ok=True);target=directory/'lab-sources.sqlite3'
 if target.exists():
  with closing(sqlite3.connect(target.as_uri()+'?mode=ro',uri=True)) as db:
   if db.execute('SELECT value FROM meta').fetchone()[0]==stamp:return target
 fd,name=tempfile.mkstemp(prefix='lab-',suffix='.sqlite3',dir=directory);os.close(fd)
 try:
  with closing(sqlite3.connect(name)) as db:
   db.executescript('PRAGMA journal_mode=OFF; CREATE TABLE meta(value TEXT); CREATE TABLE items(id TEXT PRIMARY KEY,lang TEXT,term TEXT,pos TEXT,payload TEXT); CREATE TABLE synsets(id TEXT PRIMARY KEY,payload TEXT); CREATE TABLE senses(id TEXT PRIMARY KEY,entry_id TEXT,synset_id TEXT); CREATE TABLE links(id TEXT PRIMARY KEY,source_id TEXT,target_id TEXT,target_kind TEXT,status TEXT,payload TEXT); CREATE TABLE decisions(id TEXT PRIMARY KEY,kind TEXT,payload TEXT); CREATE TABLE dependencies(decision_id TEXT,canonical_id TEXT,PRIMARY KEY(decision_id,canonical_id));')
   for file in ('morphalou-lemmas.jsonl.gz','oewn-entries.jsonl.gz'):
    for record in jsonlines(LAB/'data'/file):
     db.execute('INSERT INTO items VALUES(?,?,?,?,?)',(record['id'],record['lang'],norm(record['lemma']),record['pos'],json.dumps(record,ensure_ascii=False,separators=(',',':'))))
     for sense in record.get('senses',[]):db.execute('INSERT INTO senses VALUES(?,?,?)',(sense['id'],record['id'],sense['synset']))
   for record in jsonlines(LAB/'data/oewn-synsets.jsonl.gz'):db.execute('INSERT INTO synsets VALUES(?,?)',(record['id'],json.dumps(record,ensure_ascii=False,separators=(',',':'))))
   for record in jsonlines(LAB/'data/alignments.jsonl.gz'):db.execute('INSERT INTO links VALUES(?,?,?,?,?,?)',(record['id'],record['source']['id'],record['target']['id'],record['target']['kind'],record['status'],json.dumps(record,ensure_ascii=False,separators=(',',':'))))
   for kind,records in [('assessment',assessments()),('proposal',proposals())]:
    for record in records:
     db.execute('INSERT INTO decisions VALUES(?,?,?)',(record['id'],kind,json.dumps(record,ensure_ascii=False,separators=(',',':'))))
     db.executemany('INSERT INTO dependencies VALUES(?,?)',[(record['id'],identity) for identity in record['canonical_ids']])
   db.executescript('CREATE INDEX find_term ON items(lang,term); CREATE INDEX links_source ON links(source_id,status); CREATE INDEX links_target ON links(target_id,target_kind,status); CREATE INDEX dependency_target ON dependencies(canonical_id);')
   db.execute('INSERT INTO meta VALUES(?)',(stamp,));db.commit();assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
  os.replace(name,target)
 finally:
  if os.path.exists(name):os.unlink(name)
 return target
def link_result(db,where,args,limit,include_quarantined=False):
 quarantined=db.execute('SELECT count(*) FROM links WHERE ('+where+") AND status='quarantined_pos'",args).fetchone()[0]
 condition=where if include_quarantined else '('+where+") AND status!='quarantined_pos'"
 total=db.execute('SELECT count(*) FROM links WHERE '+condition,args).fetchone()[0];items=[]
 for payload, in db.execute('SELECT payload FROM links WHERE '+condition+' ORDER BY id LIMIT ?',[*args,limit]):
  link=json.loads(payload);source_id=link['source']['id']
  if link['source']['kind']=='sense':
   record=db.execute('SELECT entry_id FROM senses WHERE id=?',(source_id,)).fetchone();source_id=record[0] if record else source_id
  source=db.execute('SELECT payload FROM items WHERE id=?',(source_id,)).fetchone()
  if source:
   raw=json.loads(source[0]);link['source_label']={key:raw[key] for key in ('id','lemma','lang','pos')}
  annotations=[]
  for identity in link['assessment_ids']+link['proposal_ids']:
   raw=db.execute('SELECT payload FROM decisions WHERE id=?',(identity,)).fetchone()
   if raw:annotations.append(json.loads(raw[0]))
  if annotations:link['annotations']=annotations
  items.append(link)
 return {'total':total,'quarantined_count':quarantined,'items':items}
def entry(identity,limit=8,include_quarantined=False):
 if not 1<=limit<=100:raise ValueError('limit must be between 1 and 100')
 if identity.startswith('VLX-'):
  from edition import entry as edition_entry
  return edition_entry(identity)
 with closing(connect(REPO,manifest(REPO))) as db:
  row=db.execute("SELECT payload FROM records WHERE kind='entry' AND key=?",(identity,)).fetchone()
 if row is None:raise ValueError('Unknown canonical entry ID: '+identity)
 with closing(sqlite3.connect(source_db().as_uri()+'?mode=ro',uri=True)) as db:
  links=link_result(db,"target_id=? AND target_kind='lexeme'",[identity],limit,include_quarantined)
  changes=[json.loads(p) for p, in db.execute("SELECT d.payload FROM decisions d JOIN dependencies x ON x.decision_id=d.id WHERE x.canonical_id=? AND d.kind='proposal' ORDER BY d.id",(identity,))]
 return {'schema_version':SCHEMA,'canonical_entry':json.loads(row[0]),'correspondences':links,'proposed_changes':changes,'canonical_data_modified':False}
def query(lang,terms,include_proposals=False,include_sources=False,limit=8,include_alignments=False,include_quarantined=False):
 if not 1<=limit<=100:raise ValueError('limit must be between 1 and 100')
 from edition import query as edition_query
 result={'schema_version':SCHEMA,'baseline':lookup(REPO,lang,terms,limit),'proposal_mode':include_proposals,'proposals':{},'documented_contexts':{},'source_candidates':{},'correspondences':{},'warning':'Form/POS candidates and written context checks do not establish validated semantic equivalence.'}
 if include_proposals:
  resolved={r['case_id']:r for r in read(LAB/'edition/resolutions.json')}
  for term in terms:
   found=[r for r in proposals() if r['forms'].get(lang) and norm(term)==norm(r['forms'][lang])]
   for item in found:
    if item['id'] in resolved:item['edition_resolution']=resolved[item['id']]
   result['proposals'][term]={'total':len(found),'items':found[:limit]}
 if include_alignments:
  for term in terms:
   found=[r for r in assessments() if r['forms'].get(lang) and norm(term)==norm(r['forms'][lang])]
   result['documented_contexts'][term]={'total':len(found),'items':found[:limit]}
 if include_sources or include_alignments:
  if include_sources and lang=='vh':raise ValueError('External sources are French/English, not Vaeltharyn')
  with closing(sqlite3.connect(source_db().as_uri()+'?mode=ro',uri=True)) as db:
   for term in terms:
    if include_alignments:
     identities=[r['id'] for r in result['baseline']['results'][term]['entries']]
     if identities:
      placeholders=','.join('?' for _ in identities)
      result['correspondences'][term]=link_result(db,"target_kind='lexeme' AND target_id IN ("+placeholders+')',identities,limit,include_quarantined)
     else:result['correspondences'][term]={'total':0,'quarantined_count':0,'items':[]}
    if not include_sources:continue
    total=db.execute('SELECT count(*) FROM items WHERE lang=? AND term=?',(lang,norm(term))).fetchone()[0];records=[]
    for raw, in db.execute('SELECT payload FROM items WHERE lang=? AND term=? ORDER BY id LIMIT ?',(lang,norm(term),limit)):
     record=json.loads(raw);source_ids=[record['id']]+[s['id'] for s in record.get('senses',[])]
     record['correspondences']=link_result(db,'source_id IN ('+','.join('?' for _ in source_ids)+')',source_ids,limit,include_quarantined)
     from edition import source_links
     edition_links=source_links(source_ids)
     record['experimental_dictionary_links']={'total':len(edition_links),'items':edition_links[:limit],'scope':'Only the specified definition is represented, not all senses of the source entry.'}
     if lang=='en':record['sense_details']={s['synset']:json.loads(db.execute('SELECT payload FROM synsets WHERE id=?',(s['synset'],)).fetchone()[0]) for s in record['senses']}
     records.append(record)
    result['source_candidates'][term]={'total':total,'items':records}
 result['lab_dictionary']=edition_query(lang,terms,limit)
 return result
def export():
 target=LAB/'dist';target.mkdir(exist_ok=True);output=target/'vaeltharyn-lab-0.3.0-review.zip'
 names=['baseline.json','config.json','proposals/batch-001.json','mappings/assessments.json','data/alignments.jsonl.gz','reports/coverage.json','reports/review-checks.json','reports/data-integrity.json','reports/migration.json','sources/lock.json','sources/consultation.json','LICENSES.md']
 names+=['edition/entries.json','edition/manifest.json','edition/excluded.json','edition/reused-routes.json','edition/resolutions.json','reports/edition.json','reports/edition-validation.json','sources/french-definitions-lock.json']
 paths=[LAB/name for name in names]+list((LAB/'sources/licenses').glob('*'))+list((LAB/'docs').rglob('*.md'))
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  for path in sorted(paths):
   info=zipfile.ZipInfo(path.relative_to(LAB).as_posix(),date_time=(2026,10,25,0,0,0));info.external_attr=0o100644<<16;data=path.read_bytes()
   if path.name=='LICENSES.md':data=data.replace(b'../LICENSE.md',b'PROJECT-LICENSE.md')
   archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
  info=zipfile.ZipInfo('PROJECT-LICENSE.md',date_time=(2026,10,25,0,0,0));info.external_attr=0o100644<<16
  archive.writestr(info,(REPO/'LICENSE.md').read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 sha=hashlib.sha256(output.read_bytes()).hexdigest();output.with_suffix('.zip.sha256').write_text(sha+'  '+output.name+'\n',encoding='utf-8')
 return {'schema_version':SCHEMA,'archive':str(output),'bytes':output.stat().st_size,'sha256':sha,'contains':'464 defined experimental entries, 12 historical-case resolutions, central correspondence ledger, historical proposals, source licenses and guides; baseline and raw inventories distributed separately'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='command',required=True)
 for command in ('fetch','report','export'):subs.add_parser(command)
 q=subs.add_parser('query');q.add_argument('--lang',choices=['fr','en','vh'],required=True);q.add_argument('--proposals',action='store_true');q.add_argument('--source-candidates',action='store_true');q.add_argument('--alignments',action='store_true');q.add_argument('--include-quarantined',action='store_true');q.add_argument('--limit',type=int,default=8);q.add_argument('terms',nargs='+')
 e=subs.add_parser('entry');e.add_argument('identity');e.add_argument('--limit',type=int,default=8);e.add_argument('--include-quarantined',action='store_true')
 args=parser.parse_args()
 try:
  if args.command=='fetch':out=fetch()
  elif args.command=='report':out={'coverage':read(LAB/'reports/coverage.json'),'review':read(LAB/'reports/review-checks.json'),'experimental_dictionary':read(LAB/'reports/edition.json')}
  elif args.command=='export':out=export()
  elif args.command=='entry':out=entry(args.identity,args.limit,args.include_quarantined)
  else:out=query(args.lang,args.terms,args.proposals,args.source_candidates,args.limit,args.alignments,args.include_quarantined)
  print(json.dumps(out,ensure_ascii=False,indent=2))
 except (OSError,ValueError,KeyError,sqlite3.Error,AssertionError) as error:parser.exit(2,str(error)+'\n')
if __name__=='__main__':main()
