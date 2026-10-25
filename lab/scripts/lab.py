"""Isolated lexical laboratory. Proposals never become canonical by lookup."""
from pathlib import Path
from contextlib import closing
import argparse,collections,gzip,hashlib,io,json,os,sqlite3,sys,tempfile,urllib.request,zipfile
LAB=Path(__file__).resolve().parents[1];REPO=LAB.parent;sys.path.insert(0,str(REPO))
from vaeltharyn.search import norm,lookup
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def jsonlines(path):
 with gzip.open(path,'rt',encoding='utf-8') as stream:
  for line in stream:yield json.loads(line)
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
 paths=sorted((LAB/'data').glob('*.jsonl.gz'));stamp=hashlib.sha256(json.dumps([(p.name,p.stat().st_size,p.stat().st_mtime_ns) for p in paths]).encode()).hexdigest()
 directory=REPO/'.cache';directory.mkdir(exist_ok=True);target=directory/'lab-sources.sqlite3'
 if target.exists():
  with closing(sqlite3.connect(target.as_uri()+'?mode=ro',uri=True)) as db:
   if db.execute('SELECT value FROM meta').fetchone()[0]==stamp:return target
 fd,name=tempfile.mkstemp(prefix='lab-',suffix='.sqlite3',dir=directory);os.close(fd)
 try:
  with closing(sqlite3.connect(name)) as db:
   db.executescript('PRAGMA journal_mode=OFF; CREATE TABLE meta(value TEXT); CREATE TABLE items(id TEXT PRIMARY KEY,lang TEXT,term TEXT,pos TEXT,payload TEXT); CREATE TABLE synsets(id TEXT PRIMARY KEY,payload TEXT);')
   for file in ('morphalou-lemmas.jsonl.gz','oewn-entries.jsonl.gz'):
    for record in jsonlines(LAB/'data'/file):db.execute('INSERT INTO items VALUES(?,?,?,?,?)',(record['id'],record['lang'],norm(record['lemma']),record['pos'],json.dumps(record,ensure_ascii=False,separators=(',',':'))))
   for record in jsonlines(LAB/'data/oewn-synsets.jsonl.gz'):db.execute('INSERT INTO synsets VALUES(?,?)',(record['id'],json.dumps(record,ensure_ascii=False,separators=(',',':'))))
   db.executescript('CREATE INDEX find_term ON items(lang,term);');db.execute('INSERT INTO meta VALUES(?)',(stamp,));db.commit();assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
  os.replace(name,target)
 finally:
  if os.path.exists(name):os.unlink(name)
 return target
def query(lang,terms,include_proposals=False,include_sources=False,limit=8):
 result={'baseline':lookup(REPO,lang,terms,limit),'proposal_mode':include_proposals,'proposals':{},'source_candidates':{},'warning':'Written-checked proposals are not human-validated. Source form/POS matches do not establish sense equivalence.'}
 if include_proposals:
  proposals=read(LAB/'review/batch-001.json')
  for term in terms:
   found=[r for r in proposals if r['forms'].get(lang) and norm(term)==norm(r['forms'][lang])]
   result['proposals'][term]={'total':len(found),'items':found[:limit]}
 if include_sources:
  if lang=='vh':raise ValueError('External sources are French/English, not Vaeltharyn')
  path=source_db()
  with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as db:
   for term in terms:
    total=db.execute('SELECT count(*) FROM items WHERE lang=? AND term=?',(lang,norm(term))).fetchone()[0]
    records=[]
    for raw, in db.execute('SELECT payload FROM items WHERE lang=? AND term=? ORDER BY id LIMIT ?',(lang,norm(term),limit)):
     record=json.loads(raw)
     if lang=='en':
      record['sense_details']={s['synset']:json.loads(db.execute('SELECT payload FROM synsets WHERE id=?',(s['synset'],)).fetchone()[0]) for s in record['senses']}
     records.append(record)
    result['source_candidates'][term]={'total':total,'items':records}
 return result
def export():
 target=LAB/'dist';target.mkdir(exist_ok=True);output=target/'vaeltharyn-lab-0.1.0-review.zip'
 paths=[LAB/'baseline.json',LAB/'review/batch-001.json',LAB/'reports/coverage.json',LAB/'reports/review-checks.json',LAB/'reports/data-integrity.json',LAB/'sources/lock.json',LAB/'sources/consultation.json',LAB/'LICENSES.md']
 paths+=list((LAB/'sources/licenses').glob('*'))+list((LAB/'docs').rglob('*.md'))
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  for path in sorted(paths):
   info=zipfile.ZipInfo(path.relative_to(LAB).as_posix(),date_time=(2026,10,25,0,0,0));info.external_attr=0o100644<<16
   data=path.read_bytes()
   if path.name=='LICENSES.md':data=data.replace(b'../LICENSE.md',b'PROJECT-LICENSE.md')
   archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
  info=zipfile.ZipInfo('PROJECT-LICENSE.md',date_time=(2026,10,25,0,0,0));info.external_attr=0o100644<<16
  archive.writestr(info,(REPO/'LICENSE.md').read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 sha=hashlib.sha256(output.read_bytes()).hexdigest();output.with_suffix('.zip.sha256').write_text(sha+'  '+output.name+'\n',encoding='utf-8')
 return {'archive':str(output),'bytes':output.stat().st_size,'sha256':sha,'contains':'review data, sources, licenses and guides; no automatic install or canonical replacement'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='command',required=True)
 subs.add_parser('fetch');subs.add_parser('report');subs.add_parser('export')
 q=subs.add_parser('query');q.add_argument('--lang',choices=['fr','en','vh'],required=True);q.add_argument('--proposals',action='store_true');q.add_argument('--source-candidates',action='store_true');q.add_argument('--limit',type=int,default=8);q.add_argument('terms',nargs='+')
 args=parser.parse_args()
 try:
  if args.command=='fetch':out=fetch()
  elif args.command=='report':out={'coverage':read(LAB/'reports/coverage.json'),'review':read(LAB/'reports/review-checks.json')}
  elif args.command=='export':out=export()
  else:
   if not 1<=args.limit<=100:parser.error('--limit must be between 1 and 100')
   out=query(args.lang,args.terms,args.proposals,args.source_candidates,args.limit)
  print(json.dumps(out,ensure_ascii=False,indent=2))
 except (OSError,ValueError,KeyError,sqlite3.Error,AssertionError) as error:parser.exit(2,str(error)+'\n')
if __name__=='__main__':main()
