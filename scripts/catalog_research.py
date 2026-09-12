"""Attach sourced facts while retaining the boundary between school and program rules."""
from pathlib import Path
import json
import re
from urllib.parse import urlsplit

SECTIONS = [('overview', '专业说明'), ('admissions', '入学条件'), ('applications', '申请安排'), ('fees', '学费与资助'), ('outcomes', '毕业生情况')]
DISPLAY_FIELDS = {'name', 'intake', 'duration', 'campus', 'language', 'entry_summary', 'tuition_summary', 'outcomes_summary'}


def validate_record(record, label):
    sources = {s['id']: s for s in record['sources']}
    assert len(sources) == len(record['sources']), f'{label}: duplicate sources'
    cited = set()
    for source in sources.values():
        assert re.fullmatch(r'[a-zA-Z0-9-]+', source['id'])
        assert urlsplit(source['url']).scheme in ('https', 'http')
        assert source['title'] and source['supports']
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', source['checked_at'])
        assert re.fullmatch(r'[a-f0-9]{64}', source['sha256']), f'{label}: missing source fingerprint'
    assert set(record['sections']) <= {s[0] for s in SECTIONS}
    for facts in record['sections'].values():
        for fact in facts:
            assert fact['label'] and fact['text'] and fact['source_ids'], label
            assert set(fact['source_ids']) <= sources.keys(), f'{label}: unresolved citation'
            cited.update(fact['source_ids'])
    assert cited == sources.keys(), f'{label}: unused sources'
    for key, value in record.get('display_fields', {}).items():
        assert key in DISPLAY_FIELDS, f'{label}: unsupported display field {key}'
        assert value is None or (isinstance(value, str) and value.strip()), f'{label}: invalid display field {key}'


def attach_research(root, universities, programs):
    schools = {u['id']: u for u in universities}
    for path in sorted((root / 'data/program-research').glob('*.json')):
        data = json.loads(path.read_text())
        uid = data['university_id']
        assert uid == path.stem and uid in schools
        profile = data.get('profile')
        if profile:
            validate_record(profile, uid)
            schools[uid]['profile'] = profile
        available = {}
        for p in programs:
            if p['university_id'] != uid:
                continue
            identity = p.get('inventory_identity', p)
            available[identity['id']] = p
            if p['detail_status'] != 'detailed' and profile:
                p['school_profile'] = profile
                p['detail_status'] = 'enriched'
                p['research_scope'] = 'school'
        seen = set()
        for facts in data.get('programs', []):
            iid = facts['inventory_id']
            assert iid in available and iid not in seen, f'{uid}: unknown or duplicate program {iid}'
            seen.add(iid)
            validate_record(facts, iid)
            p = available[iid]
            # Existing researched records keep their stable pages and reviewed cohort facts.
            if p['detail_status'] == 'detailed':
                continue
            p['research'] = facts
            substantive = facts.get('research_status') != 'directory_only' and any(facts['sections'].values())
            p['detail_status'] = 'enriched' if substantive or profile else 'directory'
            p['research_scope'] = 'program' if substantive else ('school' if profile else None)
            if facts.get('excluded_school_sections') and p.get('school_profile'):
                excluded = set(facts['excluded_school_sections'])
                assert excluded <= {s[0] for s in SECTIONS}
                shared = p['school_profile']
                sections = {k:v for k,v in shared['sections'].items() if k not in excluded}
                used = {sid for rows in sections.values() for fact in rows for sid in fact['source_ids']}
                p['school_profile'] = {**shared, 'sections': sections, 'sources': [s for s in shared['sources'] if s['id'] in used]}
            for key, value in facts.get('display_fields', {}).items():
                # Unknown research fields must not erase an already known catalog value.
                if value is not None:
                    p[key] = value


def render_facts(facts, prefix, esc):
    body = ''
    for fact in facts:
        body += f'<p class="catalog-fact"><strong>{esc(fact["label"])}：</strong>{esc(fact["text"]).replace(chr(10), "<br>")}</p>\n'
        body += '<p class="fact-sources">' + ' · '.join(f'<a href="#source-{prefix}{sid}">官方依据</a>' for sid in fact['source_ids']) + '</p>\n\n'
    return body


def render_sources(record, prefix, esc):
    body = ''
    for source in record.get('sources', []):
        body += f'<div class="catalog-source" id="source-{prefix}{source["id"]}"><div><a href="{esc(source["url"])}">{esc(source["title"])} ↗</a><p>{esc(source["supports"])}</p><small>核验 {esc(source["checked_at"])}</small></div></div>\n'
    return body


def profile_markdown(profile, esc):
    body = '## 学校共用申请资料\n\n以下是已核实的学校规则，适用资格与年度在各条中说明；具体专业还可能要求先修科目、考试、作品集或另行申请。\n\n'
    for key, title in SECTIONS:
        facts = profile['sections'].get(key, [])
        if facts:
            body += f'### {title}\n\n' + render_facts(facts, 'u-', esc)
    body += '### 学校资料来源\n\n' + render_sources(profile, 'u-', esc)
    return body + '\n'
