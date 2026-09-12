"""Normalize a researched batch into a reviewable inventory; never elevate detail coverage."""
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
import json,re,hashlib,sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
group=ROOT/sys.argv[1]
programs=json.loads((group/'programs.json').read_text()); manifests=json.loads((group/'universities.json').read_text())
out=ROOT/'data/program-index';out.mkdir(exist_ok=True);audit=ROOT/'.maintenance/catalog-evidence';audit.mkdir(exist_ok=True)

def metadata(uid):
 found=[]
 if group.name=='root':
  m=json.loads((group/(uid+'-manifest.json')).read_text())
  for source in m['sources']:
   f=group/source['raw_file'];raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
   found.append({**source,'raw_file':str(f.relative_to(ROOT)),'bytes':len(raw)})
  return found
 for f in (group/uid).rglob('*.json'):
  if not (f.name.endswith('.meta.json') or f.name.endswith('.source.json')):continue
  j=json.loads(f.read_text());url=j.get('url') or j.get('requested_url');sha=j.get('sha256')
  if not url or not sha:continue
  candidates=[]
  for key in ['raw_path','raw_file','file']:
   v=j.get(key)
   if isinstance(v,str):candidates += [Path(v),f.parent/v,group/v]
  stem=f.name.replace('.meta.json','').replace('.source.json','')
  candidates += [f.with_name(stem+ext) for ext in ['.html','.json','.txt']]
  file=next((x for x in candidates if x.is_file() and x!=f),None)
  if file is None:continue
  raw=file.read_bytes()
  assert hashlib.sha256(raw).hexdigest()==sha, f'Hash differs: {file}'
  assert not raw.rstrip().endswith(b'[Truncated]'), f'Incomplete source {file}'
  found.append({'url':url,'sha256':sha,'bytes':len(raw),'raw_file':str(file.resolve().relative_to(ROOT)),'meta_file':str(f.relative_to(ROOT))})
 return found

def identity(p):
 # An official code is stable across label corrections; name is included where one code groups variants.
 key='|'.join(str(p.get(k) or '') for k in ['university_id','raw_key','name_en','degree_label','campus'])
 prefix=re.sub('[^a-z0-9]+','-',p['name_en'].lower()).strip('-')[:65].rstrip('-') or 'program'
 return p['university_id']+'-'+prefix+'-'+hashlib.sha256(key.encode()).hexdigest()[:10]

for m in manifests:
 uid=m['university_id'];ps=[dict(p) for p in programs if p['university_id']==uid]
 if not ps:continue
 metas=metadata(uid)
 if not metas:
  print(uid,'NO VERIFIABLE RAW METADATA - skipped');continue
 sources_requested={p['discovery_source_url'] for p in ps}
 selected=[x for x in metas if x['url'] in sources_requested]
 if not selected:selected=[x for x in metas if re.search(r'(index|directory|program-search|programs|majors|concentrations)',Path(x['meta_file']).name)]
 if not selected:selected=metas
 complete=m.get('status')=='complete' or any(m.get(k) is True for k in ['provably_complete','can_prove_complete','can_prove_full'])
 gaps=m.get('gaps') or m.get('unresolved') or []
 scope=m.get('scope') or m.get('filter_rules') or '本科官方目录；条目类型及排除规则见证据记录。'
 if not isinstance(scope,str):scope='；'.join(scope)
 method=m.get('method') or m.get('pagination_evidence') or m.get('page_coverage') or m.get('page_evidence') or m.get('completeness_basis') or '完整性按官方目录内容与分页记录审查；原始核对记录见仓库。'
 if not isinstance(method,str):method=json.dumps(method,ensure_ascii=False)
 rules=m.get('filter_rules') or '排除独立辅修、证书及非本科项目；具体边界见统计范围。'
 if not isinstance(rules,str):rules='；'.join(rules)
 id_counts=Counter(identity(p) for p in ps)
 for p in ps:
  p['id']=identity(p)
  if id_counts[p['id']]>1:p['id']+='-'+hashlib.sha256(str(p.get('official_url')).encode()).hexdigest()[:6]
  # Unknown degree labels remain explicitly unknown, rather than guessed BA/BSc.
  if not p.get('degree_label'):p['degree_label']='本科项目（学位名称尚未核实）'
  if not p.get('official_url'):
   p['official_url']=p['discovery_source_url'];p['official_url_kind']='directory_only'
  mapping_file=ROOT/'data/catalog-mappings.json'
  if mapping_file.exists():
   for mapping in json.loads(mapping_file.read_text()):
    if mapping['university_id']==uid and mapping['inventory_id']==p['id']:p['detailed_program_id']=mapping['detailed_program_id']
  p.pop('university_id')
 data={'university_id':uid,'checked_at':m.get('checked_at','2026-09-12'),'coverage':{'status':'complete' if complete else 'partial','count':len(ps),'scope':scope,'method':method,'exclusions':rules,'sources':selected,'gaps':gaps},'programs':ps}
 (out/(uid+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (audit/(uid+'.json')).write_text(json.dumps({'original_manifest':m,'raw_sources':metas},ensure_ascii=False,indent=2)+'\n')
 print(uid,len(ps),data['coverage']['status'])
