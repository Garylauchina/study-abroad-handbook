// Static school and program links remain usable if JavaScript or data loading fails.
export function normalize(value) {
  return String(value ?? '').normalize('NFKC').toLocaleLowerCase().replace(/[\s\u200b]+/g, ' ').trim();
}
export function filterPrograms(programs, filters = {}) {
  const terms = normalize(filters.q).split(' ').filter(Boolean);
  return programs.filter(p => (!filters.country || p.country_id === filters.country)
    && (!filters.university || p.university_id === filters.university)
    && (!filters.subject || p.subject === filters.subject || (p.subjects || []).includes(filters.subject))
    && (!filters.depth || p.detail_status === filters.depth)
    && terms.every(term => normalize([p.name,p.name_en,p.university_name,p.university_name_en,p.university_id,...(p.aliases || []),p.country_name,p.subject,...(p.subjects || [])].join(' ')).includes(term)));
}
export function filterUniversities(universities, filters = {}) {
  const terms = normalize(filters.q).split(' ').filter(Boolean);
  return universities.filter(u => (!filters.country || u.country_id === filters.country)
    && (!filters.university || u.id === filters.university)
    && terms.every(term => normalize([u.name,u.name_en,u.qs_name_en,u.id,...(u.aliases || []),u.country_name,u.city].join(' ')).includes(term)));
}
export function readFilters(search) {
  const params = new URLSearchParams(search);
  const filters = Object.fromEntries(['q','country','university','subject','depth'].map(key => [key, params.get(key === 'q' ? 'query' : key) || '']));
  // A shared older URL with a subject should still open its program results.
  filters.view = params.get('view') === 'programs' || filters.subject || filters.depth ? 'programs' : 'universities';
  filters.page = Math.max(1, Number.parseInt(params.get('page'),10) || 1);
  return filters;
}
export function writeFilters(filters, url) {
  const next = new URL(url);
  for (const key of ['q','country','university','subject','depth','view','page']) {
    const parameter = key === 'q' ? 'query' : key; // q belongs to Material's full-text search overlay.
    if (filters[key] && !(key === 'view' && filters[key] === 'universities') && !(key === 'page' && filters[key] <= 1)) next.searchParams.set(parameter, filters[key]);
    else next.searchParams.delete(parameter);
  }
  return next;
}
export function paginate(items, page=1, pageSize=24) {
  const size = Math.max(1, Math.floor(pageSize) || 24);
  const pages = Math.max(1, Math.ceil(items.length / size));
  const current = Math.min(pages, Math.max(1, Math.floor(page) || 1));
  return {items:items.slice((current-1)*size,current*size),page:current,pages,total:items.length};
}
function element(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text) node.textContent = text;
  return node;
}
function programCard(p, base) {
  const card = element('article','program-card');
  card.dataset.programId = p.id;
  const meta = element('div','program-meta');
  meta.append(element('span','',p.country_name),element('span','',p.subject));
  const school = element('p','program-school',p.university_name);
  const rank = element('span','qs-rank',`大学 QS 2027 · ${p.qs_rank_display}`);
  const depth = element('span','program-depth',p.research_scope === 'school' ? '仅补学校共用资料' : ({detailed:'含详细资料',enriched:'部分专业资料已核实',directory:'目录已核对 · 详情待补'})[p.detail_status]);
  const title = element('h3');
  const titleLink = element('a','',p.name);
  titleLink.href = new URL(p.url,base).href;
  title.append(titleLink);
  const facts = p.detail_status === 'detailed' ? element('dl','program-facts') : element('p','directory-note',p.entry_summary);
  for (const [label,text] of (p.detail_status === 'detailed' ? [['入学',p.entry_summary],['学费',p.tuition_summary],['毕业',p.outcomes_summary]] : [])) {
    facts.append(element('dt','',label),element('dd','',text));
  }
  const open = element('a','program-open','查看专业资料 →');
  open.href = titleLink.href;
  card.append(meta,school,rank,depth,title,element('p','program-english',p.name!==p.name_en ? p.name_en : ''),
    element('p','program-cohort',`${p.intake==='尚未核实' ? '入学年度待核实' : p.intake+' 入学'} · ${p.degree_label || p.degree}`),facts,open);
  return card;
}
async function initialize() {
  const finder = document.getElementById('program-finder');
  if (!finder) return;
  const form = finder.querySelector('form');
  const fields = Object.fromEntries(['q','country','university','subject','depth'].map(key => [key, form.elements.namedItem(key)]));
  const status = document.getElementById('catalog-status');
  const programGrid = finder.querySelector('#catalog-programs .program-grid');
  const universityCards = [...finder.querySelectorAll('[data-university-id]')];
  const countryLinks = [...document.querySelectorAll('[data-country-filter]')];
  const countryButtons = [];
  const viewControls = finder.querySelector('.catalog-view-controls');
  const viewButtons = [...viewControls.querySelectorAll('button')];
  const pager = finder.querySelector('.catalog-pagination');
  const pageButtons = [...pager.querySelectorAll('button')];
  let view = 'universities', page = 1;
  const options = [...fields.university.options].map(option => option.cloneNode(true));
  const syncUniversity = () => {
    const selected = fields.university.value;
    fields.university.replaceChildren(...options.filter(o => !o.value || !fields.country.value || o.dataset.country === fields.country.value).map(o => o.cloneNode(true)));
    if ([...fields.university.options].some(o => o.value === selected)) fields.university.value = selected;
  };
  try {
    const response = await fetch(new URL(finder.dataset.catalogUrl, document.baseURI));
    if (!response.ok) throw new Error(`Catalog HTTP ${response.status}`);
    const {programs,universities} = await response.json();
    if (!Array.isArray(programs) || !Array.isArray(universities)) throw new Error('Catalog data is incomplete');
    const base = new URL('./',document.baseURI);
    function update(changeUrl=true, resetPage=true) {
      if (resetPage) page = 1;
      const filters = {...Object.fromEntries(Object.entries(fields).map(([key,field])=>[key,field.value])),view,page};
      const isPrograms = view === 'programs';
      document.getElementById('catalog-query-label').textContent = isPrograms ? '搜索学校或专业' : '搜索学校';
      fields.q.placeholder = isPrograms ? '例如：计算机、Medicine、Law' : '例如：MIT、香港大学、曼彻斯特';
      const matches = isPrograms ? filterPrograms(programs,filters) : filterUniversities(universities,filters);
      const result = paginate(matches,page);
      page = result.page;
      for (const button of countryButtons) {
        const selected = button.dataset.countryFilter === filters.country;
        button.setAttribute('aria-pressed', String(selected));
        button.querySelector('b').textContent = selected ? '✓ 已选' : '筛选';
        if (selected && button.closest('details')) button.closest('details').open = true;
      }
      viewButtons.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.catalogView === view)));
      document.getElementById('catalog-universities').hidden = isPrograms;
      document.getElementById('catalog-programs').hidden = !isPrograms;
      for (const key of ['subject','depth']) {
        document.getElementById(`catalog-${key}-label`).hidden = !isPrograms;
        fields[key].disabled = !isPrograms;
      }
      form.classList.toggle('university-filters',!isPrograms);
      if (isPrograms) programGrid.replaceChildren(...result.items.map(p=>programCard(p,base)));
      else {
        const visible = new Set(result.items.map(u=>u.id));
        universityCards.forEach(card=>{card.hidden=!visible.has(card.dataset.universityId);});
      }
      const empty = document.getElementById('catalog-empty');
      empty.hidden = matches.length !== 0;
      empty.textContent = isPrograms ? '当前条件下暂无专业条目。可以减少筛选条件，或切换“大学”查看目录覆盖情况。' : '没有匹配的大学。可以减少筛选条件，或清除筛选查看全部学校。';
      status.textContent = isPrograms
        ? `找到 ${matches.length} 个专业条目：${matches.filter(p=>p.detail_status==='detailed').length} 个含详细资料，${matches.filter(p=>p.research_scope==='program').length} 个补有专业资料，${matches.filter(p=>p.research_scope==='school').length} 个仅补学校共用资料。其余详情待补。`
        : `找到 ${matches.length} 所大学，共收录 ${universities.length} 所。按 QS 2027 原始名次排序；“=”表示并列。`;
      pager.hidden = matches.length === 0 || result.pages === 1;
      pager.querySelector('.catalog-page-position').textContent = `第 ${page} / ${result.pages} 页 · 每页 24 项`;
      pageButtons.forEach(button=>{button.disabled=Number(button.dataset.pageStep)<0 ? page===1 : page===result.pages;});
      if (changeUrl) history.replaceState(null,'',writeFilters({...filters,page},window.location.href));
    }
    function restore() {
      const values=readFilters(window.location.search);
      view=values.view;
      page=values.page;
      fields.country.value=values.country;
      syncUniversity();
      for (const key of ['q','university','subject','depth']) fields[key].value=values[key];
      update(false,false);
    }
    form.addEventListener('submit', event => {event.preventDefault();update();});
    fields.q.addEventListener('input',()=>update());
    for (const key of ['country','university','subject','depth']) fields[key].addEventListener('change',()=>{if(key==='country')syncUniversity();update();});
    form.addEventListener('reset',event=>{
      event.preventDefault();
      for (const field of Object.values(fields)) field.value='';
      syncUniversity();
      update();
    });
    for (const button of pageButtons) button.addEventListener('click',()=>{
      page += Number(button.dataset.pageStep);
      update(true,false);
      status.scrollIntoView({block:'start',behavior:'smooth'});
    });
    for (const button of viewButtons) button.addEventListener('click',()=>{
      view=button.dataset.catalogView;
      if (view==='universities') {fields.subject.value='';fields.depth.value='';}
      update();
    });
    for (const link of countryLinks) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = link.className;
      button.dataset.countryFilter = link.dataset.countryFilter;
      button.setAttribute('aria-label', `${link.querySelector('strong').textContent}大学与专业`);
      button.setAttribute('aria-controls', 'catalog-results');
      button.append(...link.childNodes);
      button.addEventListener('click', () => {
        fields.country.value = fields.country.value === button.dataset.countryFilter ? '' : button.dataset.countryFilter;
        fields.university.value = '';
        syncUniversity();
        update();
      });
      link.replaceWith(button);
      countryButtons.push(button);
    }
    window.addEventListener('popstate',restore);
    restore();
    finder.querySelector('.catalog-fallback-note').hidden=true;
    viewControls.hidden=false;
  } catch (error) {
    form.hidden=true;
    status.textContent='筛选数据暂时加载失败。你仍可通过下面的大学入口浏览专业清单和详情。';
    console.error(error);
  }
}
if (typeof document !== 'undefined') initialize();
