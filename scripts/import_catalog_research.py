"""Import a reviewed research batch and verify each retained local source hash.

Usage: python scripts/import_catalog_research.py scratch/full-catalog/uk-enrichment
Raw pages remain outside the published repository; only facts and provenance are retained.
"""
from pathlib import Path
from collections import defaultdict
import argparse
import hashlib
import json
from catalog_research import validate_record

ROOT = Path(__file__).resolve().parents[1]


def match_program(inventory, record, uid):
    """Keep parallel degrees distinct even when they share a name and URL."""
    candidates = [p for p in inventory if str(p.get('raw_key')) == str(record.get('raw_key'))]
    if record.get('inventory_id'):
        candidates = [p for p in candidates if p['id'] == record['inventory_id']]
    if len(candidates) > 1 or record.get('inventory_id'):
        candidates = [p for p in candidates if p['official_url'] == record['official_url'] and p['name_en'] == record['name_en']]
    if record.get('degree_label'):
        candidates = [p for p in candidates if p['degree_label'] == record['degree_label']]
    assert len(candidates) == 1, f'{uid}: ambiguous/missing research identity {record.get("raw_key")}'
    return candidates[0]


def run(batch):
    profiles = json.loads((batch / 'profiles.json').read_text())
    facts = json.loads((batch / 'program-facts.json').read_text())
    by_school = defaultdict(list)
    for item in facts:
        by_school[item['university_id']].append(item)
    profile_map = {p['university_id']: p for p in profiles}
    assert len(profile_map) == len(profiles)
    verified = {}
    for uid in sorted(set(profile_map) | set(by_school)):
        inventory = json.loads((ROOT / 'data/program-index' / (uid+'.json')).read_text())['programs']
        evidence = []

        def clean(record):
            record = json.loads(json.dumps(record))
            for source in record['sources']:
                source['sha256'] = source.get('sha256') or source.get('raw_sha256')
            validate_record(record, uid)
            if 'display_fields' in record:
                record['display_fields'] = {k:v for k,v in record['display_fields'].items() if v is not None}
            for source in record['sources']:
                raw = source.get('raw_file') or source.get('raw_path')
                sha = source.get('sha256') or source.get('raw_sha256')
                assert raw and sha, f'{uid}: source lacks raw evidence: {source["url"]}'
                path = (ROOT / raw).resolve()
                if path not in verified:
                    content = path.read_bytes()
                    verified[path] = hashlib.sha256(content).hexdigest()
                    assert not content.rstrip().endswith(b'[Truncated]'), path
                assert verified[path] == sha, f'{uid}: source hash differs: {raw}'
                evidence.append({'url':source['url'],'sha256':sha,'raw_file':str(path.relative_to(ROOT)),'locator':source.get('locator')})
                source.pop('raw_file', None)
                source.pop('raw_path', None)
                source['sha256'] = sha
            return record

        output = {'university_id': uid, 'programs': []}
        if uid in profile_map:
            output['profile'] = clean(profile_map[uid])
        used = set()
        for record in by_school[uid]:
            candidate = match_program(inventory, record, uid)
            item = clean(record)
            item['inventory_id'] = candidate['id']
            assert item['inventory_id'] not in used, item['inventory_id']
            used.add(item['inventory_id'])
            output['programs'].append(item)
        target = ROOT / 'data/program-research' / (uid+'.json')
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
        audit = ROOT / '.maintenance/research-evidence' / (uid+'.json')
        audit.parent.mkdir(exist_ok=True)
        unique = {(s['url'],s['sha256']):s for s in evidence}
        audit.write_text(json.dumps({'university_id':uid,'sources':list(unique.values())},ensure_ascii=False,indent=2)+'\n')
        print(f'{uid}: {len(output["programs"])} program records, {len(unique)} verified sources')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('batch', type=Path)
    run(parser.parse_args().batch.resolve())
