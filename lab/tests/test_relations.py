from pathlib import Path
import hashlib,json,sys,unittest,zipfile
LAB=Path(__file__).resolve().parents[1];REPO=LAB.parent
sys.path.insert(0,str(LAB/'scripts'));sys.path.insert(0,str(REPO))
from model import read,jsonlines,proposals,assessments,cases,RELATIONS
from lab import entry,query,export
from vaeltharyn.search import rows

class RelationTests(unittest.TestCase):
 def test_single_authoritative_ledger(self):
  for file in ('morphalou-lemmas.jsonl.gz','oewn-entries.jsonl.gz'):
   for r in jsonlines(LAB/'data'/file):self.assertFalse({'existing_ids','classification','classification_verified'}&r.keys())
  self.assertFalse((LAB/'data/derivation-review.jsonl.gz').exists())
  self.assertIn('lab/data/alignments.jsonl.gz',read(LAB/'reports/data-integrity.json'))
 def test_all_cases_preserved_but_only_changes_queued(self):
  self.assertEqual(len(proposals()),84);self.assertEqual(len(assessments()),46)
  self.assertTrue(all(r['classification']!='already_covered' for r in proposals()))
  self.assertTrue(all('classification' not in r for r in assessments()))
  combined=cases();self.assertEqual(len({r['id'] for r in combined}),130)
  sha=hashlib.sha256(json.dumps(sorted(r['id'] for r in combined)).encode()).hexdigest()
  self.assertEqual(sha,read(LAB/'reports/migration.json')['preserved_case_ids_sha256'])
  self.assertFalse((LAB/'review/batch-001.json').exists())
 def test_all_canonical_entries_remain_counted(self):
  report=read(LAB/'reports/coverage.json');self.assertEqual(report['canonical_entries'],65045)
  for lang in ('fr','en'):
   source=report['sources'][lang]
   self.assertEqual(source['distinct_canonical_entries_with_candidates']+source['canonical_entries_without_candidates'],65045)
  self.assertEqual(report['cross_source']['entries_with_candidates_in_either']+report['cross_source']['entries_without_automatic_candidates'],65045)
 def test_foreign_keys_and_relation_scope(self):
  canonical={r['id'] for r in rows(REPO/'data/lexicon/fr/entries.csv')};source_ids=set();sense_ids=set()
  for file in ('morphalou-lemmas.jsonl.gz','oewn-entries.jsonl.gz'):
   for row in jsonlines(LAB/'data'/file):source_ids.add(row['id']);sense_ids.update(s['id'] for s in row.get('senses',[]))
  expression_ids=set()
  for reg in read(REPO/'corpus.json')['expressions']:expression_ids.update(reg['id']+':'+r.get('key',r.get('id')) for r in read(REPO/reg['records']))
  a={r['id'] for r in assessments()};p={r['id'] for r in proposals()};seen=set()
  for r in jsonlines(LAB/'data/alignments.jsonl.gz'):
   self.assertNotIn(r['id'],seen);seen.add(r['id']);self.assertIn(r['relation'],RELATIONS)
   self.assertIn(r['source']['id'],source_ids if r['source']['kind']=='entry' else sense_ids if r['source']['kind']=='sense' else a|p)
   self.assertIn(r['target']['id'],canonical if r['target']['kind']=='lexeme' else expression_ids)
   self.assertTrue(set(r['assessment_ids'])<=a);self.assertTrue(set(r['proposal_ids'])<=p)
   if r['status']=='unreviewed':self.assertEqual(r['relation'],'uncertain')
  self.assertEqual(len(seen),read(LAB/'reports/coverage.json')['correspondences']['total'])
 def test_quarantine_is_opt_in(self):
  first=next(r for r in jsonlines(LAB/'data/alignments.jsonl.gz') if r['status']=='quarantined_pos');identity=first['target']['id']
  normal=entry(identity,100);self.assertGreater(normal['correspondences']['quarantined_count'],0)
  self.assertTrue(all(r['status']!='quarantined_pos' for r in normal['correspondences']['items']))
  explicit=entry(identity,100,True);self.assertIn(first['id'],{r['id'] for r in explicit['correspondences']['items']})
 def test_unmatched_entries_are_queryable(self):
  result=entry('VX-002edc4764a80a57');self.assertEqual(result['canonical_entry']['fr']['mot'],'karmaelun');self.assertEqual(result['correspondences']['total'],0)
  with self.assertRaises(ValueError):entry('VX-does-not-exist')
 def test_contexts_are_not_pending_changes(self):
  result=query('en',['affection'],True,False,8,True)
  self.assertEqual(result['proposals']['affection']['total'],0);self.assertGreater(result['documented_contexts']['affection']['total'],0)
 def test_rationalized_zip(self):
  with zipfile.ZipFile(export()['archive']) as z:
   for name in ('config.json','data/alignments.jsonl.gz','mappings/assessments.json','proposals/batch-001.json'):self.assertIn(name,z.namelist())
   self.assertNotIn('review/batch-001.json',z.namelist())

if __name__=='__main__':unittest.main()
