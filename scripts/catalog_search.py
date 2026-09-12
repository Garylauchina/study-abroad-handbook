"""Keep catalogue discovery searchable without indexing repeated missing-field labels."""
import json
from pathlib import Path


def compact_catalog_search(index, catalog):
    inventory = {p['url']: p for p in catalog['programs'] if p.get('detail_status') != 'detailed'}
    docs, retained = [], set()
    for doc in index['docs']:
        route = doc['location'].split('#')[0]
        p = inventory.get(route)
        if not p:
            docs.append(doc)
            continue
        if route in retained:
            continue
        retained.add(route)
        text = ' '.join(str(p.get(k) or '') for k in
                        ('name', 'name_en', 'subject', 'university_name', 'university_name_en',
                         'university_id', 'country_name', 'degree', 'campus'))
        text += ' ' + ' '.join(p.get('aliases', []))
        docs.append({**doc, 'location': route, 'text': text + (' 部分资料已核实' if p.get('detail_status') == 'enriched' else ' 目录已核对 详情待补')})
    assert retained == inventory.keys(), f'Search misses {inventory.keys() - retained}'
    return {**index, 'docs': docs}


def on_post_build(config):
    root = Path(config.site_dir)
    path = root / 'search/search_index.json'
    index = json.loads(path.read_text())
    catalog = json.loads((root / 'assets/data/catalog-index.json').read_text())
    compacted = compact_catalog_search(index, catalog)
    path.write_text(json.dumps(compacted, ensure_ascii=False, separators=(',', ':')))
