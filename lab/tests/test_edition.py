from pathlib import Path
import sys,unittest,zipfile
LAB=Path(__file__).resolve().parents[1];sys.path.insert(0,str(LAB/'scripts'))
from edition import records,validate
from lookup import query,entry,export
class EditionTests(unittest.TestCase):
 def test_integrity_and_complete_paradigm_collisions(self):
  result=validate();self.assertEqual(result['added_entries_checked'],464);self.assertEqual(result['dictionary_entries'],65509)
 def test_new_entries_are_active_without_proposals(self):
  result=query('fr',['culpabilité ressentie','plausibilité']);self.assertFalse(result['proposal_mode'])
  self.assertEqual(result['lab_dictionary']['results']['culpabilité ressentie']['entries'][0]['word'],'dhaerim')
  self.assertGreater(result['lab_dictionary']['results']['plausibilité']['total'],0)
 def test_specific_senses_not_homonyms(self):
  r=query('en',['felt guilt','low-pitched'])['lab_dictionary']['results']
  self.assertEqual(r['felt guilt']['entries'][0]['word'],'dhaerim');self.assertEqual(r['low-pitched']['entries'][0]['word'],'dhoeriv')
  self.assertIn('Not seriousness',r['low-pitched']['entries'][0]['note_en'])
  self.assertEqual(query('en',['guilt'])['lab_dictionary']['results']['guilt']['entries'][0]['word'],'dhaerim')
 def test_conjugation_and_id_access(self):
  r=query('vh',['thervyrem'])['lab_dictionary']['results']['thervyrem']['entries'][0]
  self.assertEqual(r['word'],'thervyrar');self.assertEqual(entry(r['id'])['edition_entry']['id'],r['id'])
  with self.assertRaises(ValueError):entry('VLX-unknown')
 def test_historical_proposal_has_current_resolution(self):
  r=query('en',['felt guilt'],True)['proposals']['felt guilt']['items'][0]
  self.assertIsNone(r['forms']['vh']);self.assertEqual(r['edition_resolution']['word'],'dhaerim')
 def test_packaging_includes_usable_dictionary(self):
  with zipfile.ZipFile(export()['archive']) as z:
   self.assertIn('edition/entries.json',z.namelist());self.assertIn('edition/resolutions.json',z.namelist());self.assertIsNone(z.testzip())
 def test_examples_and_validation_claims(self):
  for r in records():
   self.assertTrue(r['definition_fr']);self.assertTrue(r['definition_en']);self.assertFalse(r['human_validated']);self.assertFalse(r['audio_evaluated'])
   if r['status']=='written_sense_and_formation_checked_lab_entry':self.assertTrue(r['examples'])
if __name__=='__main__':unittest.main()
