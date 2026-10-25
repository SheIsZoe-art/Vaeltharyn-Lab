from pathlib import Path
import json,gzip,hashlib,sys,unittest,zipfile
LAB=Path(__file__).resolve().parents[1];sys.path.insert(0,str(LAB/'scripts'))
from lab import query,export
class LaboratoryTests(unittest.TestCase):
 def test_baseline_isolation(self):
  baseline=json.loads((LAB/'baseline.json').read_text(encoding='utf-8'))
  for name,expected in baseline['files'].items():
   if name not in ('README.md','.gitignore'):
    raw=(LAB.parent/name).read_bytes()
    if not name.startswith('data/'):raw=raw.replace(b'\r\n',b'\n')
    self.assertEqual(hashlib.sha256(raw).hexdigest(),expected,name)
 def test_inventory_reconciliation(self):
  report=json.loads((LAB/'reports/coverage.json').read_text(encoding='utf-8'))['sources']
  for lang in ('fr','en'):
   key='source_records'
   unresolved='source_records_without_candidates'
   self.assertEqual(report[lang]['source_records_with_candidates']+report[lang][unresolved],report[lang][key])
  self.assertEqual(report['fr']['source_records'],159271);self.assertEqual(report['en']['source_records'],135969)
  self.assertEqual(report['en']['source_senses'],185129)
 def test_data_checksums(self):
  report=json.loads((LAB/'reports/data-integrity.json').read_text())
  self.assertEqual(len(report),4)
  for name,sha in report.items():self.assertEqual(hashlib.sha256((LAB.parent/name).read_bytes()).hexdigest(),sha)
 def test_proposals_are_opt_in(self):
  term='Je pige.';default=query('fr',[term]);self.assertFalse(default['proposal_mode']);self.assertEqual(default['proposals'],{})
  explicit=query('fr',[term],True);items=explicit['proposals'][term]['items'];self.assertEqual(items[0]['forms']['vh'],'Mi sendraerem se.');self.assertFalse(items[0]['human_validated'])
 def test_polysemy_kept_separate(self):
  result=query('en',['guilt','lie','whisper'],False,True)
  guilt=result['source_candidates']['guilt']['items'][0]
  self.assertGreaterEqual(len(guilt['senses']),2)
  cases=json.loads((LAB/'proposals/batch-001.json').read_text(encoding='utf-8'))
  blocked=next(c for c in cases if c['forms']['en']=='felt guilt');self.assertIsNone(blocked['forms']['vh']);self.assertIn('tythoem',blocked['blocked_equivalents'])
 def test_limits_and_no_fake_validation(self):
  batch=json.loads((LAB/'proposals/batch-001.json').read_text(encoding='utf-8'))
  self.assertEqual(len(batch),84);self.assertTrue(all(not r['human_validated'] for r in batch))
  self.assertTrue(all(r['note_fr'] and r['note_en'] for r in batch))
  report=json.loads((LAB/'reports/review-checks.json').read_text(encoding='utf-8'));self.assertFalse(report['automatic_promotion']);self.assertFalse(report['audio_evaluated'])
 def test_review_zip_scope(self):
  data=export()
  with zipfile.ZipFile(data['archive']) as z:
   self.assertIsNone(z.testzip());self.assertIn('proposals/batch-001.json',z.namelist());self.assertIn('LICENSES.md',z.namelist());self.assertIn('PROJECT-LICENSE.md',z.namelist())
   self.assertFalse(any('entries.csv' in name or name.endswith('.sqlite3') or '..' in name.split('/') for name in z.namelist()))
if __name__=='__main__':unittest.main()
