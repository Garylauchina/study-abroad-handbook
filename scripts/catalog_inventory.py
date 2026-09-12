"""Validate official undergraduate inventories without turning unknowns into facts."""
from pathlib import Path
import json
import re
from urllib.parse import urlsplit
from catalog_subjects import classify
from catalog_research import render_facts, render_sources

MISSING = '尚未核实'


def load_inventories(root, universities, detailed):
    schools = {u['id']: u for u in universities}
    details = {p['id']: p for p in detailed}
    added, linked = [], set()
    for path in sorted((root / 'data/program-index').glob('*.json')):
        data = json.loads(path.read_text())
        uid = data['university_id']
        assert path.stem == uid and uid in schools, path
        coverage = data['coverage']
        assert coverage['status'] in ('complete', 'partial')
        assert coverage['scope'] and coverage['count'] == len(data['programs'])
        assert coverage['sources'] and coverage['method'] and coverage['exclusions']
        for source in coverage['sources']:
            assert urlsplit(source['url']).scheme in ('https', 'http')
            assert re.fullmatch(r'[a-f0-9]{64}', source['sha256']), source
        schools[uid]['catalog_coverage'] = coverage
        for item in data['programs']:
            assert item['name_en'] and item['degree_label'] and item['id'], f'{uid}: empty program identity {item}'
            assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item['id'])
            # Some official legacy course catalogues still publish HTTP links.
            assert urlsplit(item['official_url']).scheme in ('https', 'http')
            assert urlsplit(item['discovery_source_url']).scheme in ('https', 'http')
            if item.get('detailed_program_id'):
                pid = item['detailed_program_id']
                assert pid in details and details[pid]['university_id'] == uid
                assert pid not in linked, f'Duplicate detailed-program mapping: {pid}'
                linked.add(pid)
                details[pid]['inventory_identity'] = item
                continue
            # The source record keeps nulls. Display labels make missing research visible.
            added.append({
                **item, 'university_id': uid, 'name': item.get('name') or item['name_en'],
                'degree': item.get('study_level') or '本科', 'subject': item.get('subject') or classify(item['name_en'])[0],
                'subjects': item.get('subjects') or classify(item['name_en']),
                'intake': item.get('intake') or MISSING,
                'duration': item.get('duration') or MISSING,
                'campus': item.get('campus') or MISSING,
                'language': item.get('language') or MISSING,
                'entry_summary': item.get('entry_note') or '已核对官方目录；具体招生条件尚未核实。',
                'tuition_summary': MISSING, 'outcomes_summary': MISSING,
                'detail_status': 'directory', 'checked_at': data['checked_at'],
            })
    ids = [p['id'] for p in detailed + added]
    assert len(ids) == len(set(ids)), 'Program inventory ID collides with an existing record'
    for p in detailed:
        p['detail_status'] = 'detailed'
    return detailed + added


def coverage_text(programs):
    total = len(programs)
    detailed = sum(p.get('detail_status') == 'detailed' for p in programs)
    enriched = sum(p.get('detail_status') == 'enriched' for p in programs)
    specific = sum(p.get('research_scope') == 'program' for p in programs)
    return f'{total} 个专业条目 · {detailed} 个含详细资料' + (f' · {specific} 个补有专业资料 · {enriched-specific} 个仅补学校共用资料' if enriched else '')


def inventory_markdown(p, esc):
    state = ('部分专业资料已核实，详情仍在补充' if p.get('research_scope') == 'program' else '已补学校共用资料，专业专属详情仍在补充') if p['detail_status'] == 'enriched' else '已核对专业目录，详情仍在补充'
    body = f'\n> **资料状态：{state}。** 下列空缺尚未完成核验；不表示学校未公布，也不表示没有相关要求。学校共用规则与专业专属要求分别标明。\n\n'
    body += '## 专业说明 {#overview}\n\n'
    rows = [('官方名称', p['name_en']), ('授予学位 / 项目类型', p['degree_label']),
            ('目录适用期', p.get('source_period') or MISSING)]
    for key, label in [('entity_type', '条目类型'), ('record_type', '目录条目类别'), ('program_type', '项目类别'), ('parent_degree_label', '所属学位'),
                       ('entry_route', '申请路径'), ('status', '目录状态'),
                       ('registry_status', '注册目录状态')]:
        if p.get(key):
            rows.append((label, p[key]))
    if p.get('requires_prior_degree') is True:
        rows.append(('前置学历', '需先取得大学学位；其他条件仍需查看具体招生说明'))
    for label, value in rows:
        body += f'<p><strong>{label}：</strong>{esc(value)}</p>\n\n'
    if p.get('listing_note'):
        body += f'<p>{esc(p["listing_note"])}</p>\n\n'
    research = p.get('research', {})
    profile = p.get('school_profile', {})
    body += render_facts(research.get('sections', {}).get('overview', []), 'p-', esc)
    for key, title, value in [
        ('admissions', '入学条件', p['entry_summary']),
        ('applications', '申请安排', '申请开放日、截止日及申请通道尚未核实。'),
        ('fees', '学费与资助', '国际生学费、费用年度、计费单位和奖助条件尚未核实。'),
        ('outcomes', '毕业生情况', '专业层面的毕业调查、就业或继续深造数据尚未核实。'),
    ]:
        body += f'## {title} {{#{key}}}\n\n'
        facts = research.get('sections', {}).get(key, [])
        if facts:
            body += render_facts(facts, 'p-', esc)
        else:
            body += esc(value) + '\n\n'
        shared = profile.get('sections', {}).get(key, [])
        if shared:
            body += '<details class="school-policy"><summary>学校共用规则 · 请核对适用资格和年度</summary>\n\n'
            body += render_facts(shared, 'u-', esc) + '</details>\n\n'
    body += '## 官方来源与核验记录 {#sources}\n\n'
    body += f'目录核验日期：**{p["checked_at"]}**；该日期不代表招生、学费与毕业信息已核验。\n\n'
    label = '官方目录中的项目记录（尚无独立详情页）' if p.get('official_url_kind') == 'directory_only' else '官方项目页面或项目所在目录'
    body += f'- [{label}]({p["official_url"]})\n- [官方目录]({p["discovery_source_url"]})\n\n'
    body += render_sources(research, 'p-', esc) + render_sources(profile, 'u-', esc)
    return body
