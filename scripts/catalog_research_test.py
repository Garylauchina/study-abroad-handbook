"""Release checks for source integrity and the boundary of shared admission rules."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from catalog_research import attach_research, validate_record
from render_catalog import load_catalog, validate_source_dates
from import_catalog_research import match_program
from catalog_relations import attach_relations
from render_catalog import related_courses

ROOT = Path(__file__).resolve().parents[1]


class ResearchTests(unittest.TestCase):
    def test_catalog_paths_link_to_stable_pages_without_inheriting_rules(self):
        parent = {'id':'stable-page', 'inventory_identity':{'id':'catalog-parent'}, 'name':'课程 <A>', 'university_id':'school', 'entry_summary':'Parents only'}
        second = {'id':'second-parent', 'name':'另一课程', 'university_id':'school'}
        child = {'id':'internal-stage', 'name':'校内方向', 'university_id':'school', 'parent_program_ids':['catalog-parent','second-parent'], 'entry_summary':'Requires prior study'}
        attach_relations([parent, second, child])
        self.assertEqual(child['entry_summary'], 'Requires prior study')
        self.assertEqual([p['id'] for p in child['related_parents']], ['stable-page','second-parent'])
        self.assertEqual(parent['related_children'], [{'id':'internal-stage','name':'校内方向'}])
        markup = related_courses(child, 'country')
        self.assertIn('/study-abroad-handbook/catalog/country/school/stable-page/', markup)
        self.assertIn('课程 &lt;A&gt;', markup)
        self.assertIn('不等于独立招生项目', markup)
        bad = copy.deepcopy(child); bad['parent_program_ids'] = ['stable-page','catalog-parent']
        with self.assertRaisesRegex(AssertionError, 'Duplicate resolved parent'):
            attach_relations([parent, bad])
        bad = copy.deepcopy(child); bad['parent_program_ids'] = ['missing']
        with self.assertRaisesRegex(AssertionError, 'Unknown parent'):
            attach_relations([parent, bad])
        bad['parent_program_ids'] = ['stable-page']; bad['university_id'] = 'other'
        with self.assertRaisesRegex(AssertionError, 'Cross-school parent'):
            attach_relations([parent, bad])
        parent['inventory_identity']['parent_program_ids'] = ['internal-stage']
        with self.assertRaisesRegex(AssertionError, 'Cyclic program'):
            attach_relations([parent, second, child])

    def test_incremental_updates_retain_each_sources_verification_date(self):
        program = {'checked_at':'2026-09-13', 'sources':[
            {'checked_at':'2026-09-12'}, {'checked_at':'2026-09-13'}]}
        original = copy.deepcopy(program)
        validate_source_dates(program)
        self.assertEqual(program, original)
        program['sources'][1]['checked_at'] = '2026-09-14'
        with self.assertRaisesRegex(AssertionError, 'Source verified after'):
            validate_source_dates(program)
        program['sources'][1]['checked_at'] = '2026-02-30'
        with self.assertRaises(ValueError):
            validate_source_dates(program)

    def test_parallel_degrees_require_unambiguous_identity(self):
        shared = {'raw_key':'psychology','official_url':'https://example.edu/psychology','name_en':'Psychology'}
        inventory = [dict(shared, id='psych-ba', degree_label='BA'), dict(shared, id='psych-bs', degree_label='BS')]
        with self.assertRaisesRegex(AssertionError, 'ambiguous/missing'):
            match_program(inventory, shared, 'example')
        self.assertEqual(match_program(inventory, dict(shared, degree_label='BS'), 'example')['id'], 'psych-bs')
        self.assertEqual(match_program(inventory, dict(shared, inventory_id='psych-ba'), 'example')['degree_label'], 'BA')
        with self.assertRaisesRegex(AssertionError, 'ambiguous/missing'):
            match_program(inventory, dict(shared, inventory_id='psych-ba', degree_label='BS'), 'example')
        with self.assertRaisesRegex(AssertionError, 'ambiguous/missing'):
            match_program(inventory, dict(shared, inventory_id='another-school'), 'example')

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
