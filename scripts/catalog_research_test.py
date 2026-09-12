"""Release checks for source integrity and the boundary of shared admission rules."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from catalog_research import attach_research, validate_record
from render_catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]


class ResearchTests(unittest.TestCase):
    def test_every_school_has_a_directory_and_existing_details_survive(self):
        _, schools, programs = load_catalog()
        self.assertEqual(len(schools), 96)
        self.assertTrue(all(s.get('catalog_coverage') for s in schools))
        original = [p for f in (ROOT/'data/catalog').glob('*.json') for p in json.loads(f.read_text())['programs']]
        actual = {p['id']: p for p in programs}
        self.assertEqual(len(original), 36)
        for expected in original:
            record = actual[expected['id']]
            self.assertEqual(record['detail_status'], 'detailed')
            for field in ['sections', 'sources', 'entry_summary', 'tuition_summary', 'outcomes_summary']:
                self.assertEqual(record[field], expected[field], expected['id'])

    def test_special_paths_do_not_inherit_inapplicable_rules(self):
        _, schools, programs = load_catalog()
        def find(uid, name):
            return next(p for p in programs if p['university_id']==uid and p['name_en']==name)
        online = find('uzh', 'Religious Studies and Theology')
        self.assertNotIn('admissions', online['school_profile']['sections'])
        self.assertNotIn('applications', online['school_profile']['sections'])
        self.assertIn('C1', online['research']['sections']['admissions'][0]['text'])
        medicine = find('uzh', 'Humanmedizin')
        self.assertNotIn('admissions', medicine['school_profile']['sections'])
        ordinary = find('uzh', 'Mathematik')
        self.assertIn('admissions', ordinary['school_profile']['sections'])
        school = next(s for s in schools if s['id']=='uzh')
        self.assertIn('admissions', school['profile']['sections'], 'Exceptions must not mutate the shared school object')
        self.assertFalse(any(p['university_id']=='uzh' and p['name_en']=='Spatial Data Science' for p in programs))

    def test_unknown_research_does_not_erase_known_catalog_fields(self):
        source = {'id':'official','title':'Official program','url':'https://example.edu/program','checked_at':'2026-09-12','supports':'Program structure','sha256':'a'*64}
        record = {'inventory_id':'test-degree','sections':{'overview':[{'label':'Structure','text':'180 ECTS','source_ids':['official']}]},'sources':[source], 'display_fields':{'language':None,'duration':'3 years'}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root/'data/program-research'; folder.mkdir(parents=True)
            (folder/'test.json').write_text(json.dumps({'university_id':'test','programs':[record]}))
            programs = [{'id':'test-degree','university_id':'test','detail_status':'directory','language':'English'}]
            attach_research(root, [{'id':'test'}], programs)
            self.assertEqual(programs[0]['language'], 'English')
            self.assertEqual(programs[0]['duration'], '3 years')
            self.assertEqual(programs[0]['research_scope'], 'program')
        broken = copy.deepcopy(record)
        broken['sections']['overview'][0]['source_ids'] = ['not-present']
        with self.assertRaisesRegex(AssertionError, 'unresolved citation'):
            validate_record(broken, 'broken')
        broken = copy.deepcopy(record); broken['sources'][0]['sha256'] = 'wrong'
        with self.assertRaisesRegex(AssertionError, 'fingerprint'):
            validate_record(broken, 'broken')


if __name__ == '__main__':
    unittest.main()
