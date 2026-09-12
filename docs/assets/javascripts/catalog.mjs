// Static school and program links remain usable if JavaScript or data loading fails.
export function normalize(value) {
  return String(value ?? '').normalize('NFKC').toLocaleLowerCase().replace(/[\s\u200b]+/g, ' ').trim();
}
export function filterPrograms(programs, filters = {}) {
  const terms = normalize(filters.q).split(' ').filter(Boolean);
  return programs.filter(p => (!filters.country || p.country_id === filters.country)
    && (!filters.university || p.university_id === filters.university)
    && (!filters.subject || p.subject === filters.subject)
    && terms.every(term => normalize([p.name,p.name_en,p.university_name,p.university_name_en,p.university_id,...(p.aliases || []),p.country_name,p.subject].join(' ')).includes(term)));
}
export function filterUniversities(universities, filters = {}) {
  const terms = normalize(filters.q).split(' ').filter(Boolean);
  return universities.filter(u => (!filters.country || u.country_id === filters.country)
    && (!filters.university || u.id === filters.university)
    && terms.every(term => normalize([u.name,u.name_en,u.qs_name_en,u.id,...(u.aliases || []),u.country_name,u.city].join(' ')).includes(term)));
}
export function readFilters(search) {
  const params = new URLSearchParams(search);
  const filters = Object.fromEntries(['q','country','university','subject'].map(key => [key, params.get(key === 'q' ? 'query' : key) || '']));
  // A shared older URL with a subject should still open its program results.
  filters.view = params.get('view') === 'programs' || filters.subject ? 'programs' : 'universities';
  return filters;
}
export function writeFilters(filters, url) {
  const next = new URL(url);
  for (const key of ['q','country','university','subject','view']) {
    const parameter = key === 'q' ? 'query' : key; // q belongs to Material's full-text search overlay.
    if (filters[key] && !(key === 'view' && filters[key] === 'universities')) next.searchParams.set(parameter, filters[key]);
    else next.searchParams.delete(parameter);
  }
  return next;
}
async function initialize() {
  const finder = document.getElementById('program-finder');
  if (!finder) return;
  const form = finder.querySelector('form');
  const fields = Object.fromEntries(['q','country','university','subject'].map(key => [key, form.elements.namedItem(key)]));
  const status = document.getElementById('catalog-status');
  const programCards = [...finder.querySelectorAll('[data-program-id]')];
  const universityCards = [...finder.querySelectorAll('[data-university-id]')];
  const countryLinks = [...document.querySelectorAll('[data-country-filter]')];
  const countryButtons = [];
  const viewControls = finder.querySelector('.catalog-view-controls');
  const viewButtons = [...viewControls.querySelectorAll('button')];
  let view = 'universities';
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
    function update(changeUrl=true) {
      const filters = {...Object.fromEntries(Object.entries(fields).map(([key,field])=>[key,field.value])),view};
      const isPrograms = view === 'programs';
      document.getElementById('catalog-query-label').textContent = isPrograms ? '搜索学校或专业' : '搜索学校';
      fields.q.placeholder = isPrograms ? '例如：计算机、NUS、商科' : '例如：MIT、香港大学、曼彻斯特';
      const matches = new Set((isPrograms ? filterPrograms(programs,filters) : filterUniversities(universities,filters)).map(item=>item.id));
      for (const button of countryButtons) {
        const selected = button.dataset.countryFilter === filters.country;
        button.setAttribute('aria-pressed', String(selected));
        button.querySelector('b').textContent = selected ? '✓ 已选' : '筛选';
        if (selected && button.closest('details')) button.closest('details').open = true;
      }
      viewButtons.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.catalogView === view)));
      document.getElementById('catalog-universities').hidden = isPrograms;
      document.getElementById('catalog-programs').hidden = !isPrograms;
      document.getElementById('catalog-subject-label').hidden = !isPrograms;
      fields.subject.disabled = !isPrograms;
      form.classList.toggle('university-filters',!isPrograms);
      (isPrograms ? programCards : universityCards).forEach(card => {card.hidden = !matches.has(isPrograms ? card.dataset.programId : card.dataset.universityId);});
      const empty = document.getElementById('catalog-empty');
      empty.hidden = matches.size !== 0;
      empty.textContent = isPrograms ? '当前条件下暂无已收录的专业详情。可切换“大学”查看学校与官网入口，或减少筛选条件。' : '没有匹配的大学。可以减少筛选条件，或清除筛选查看全部学校。';
      status.textContent = isPrograms
        ? `找到 ${matches.size} 个专业，共收录 ${programs.length} 个。招生年度、学费和毕业调查范围见各项目。`
        : `找到 ${matches.size} 所大学，共收录 ${universities.length} 所。按 QS 2027 原始名次排序；“=”表示并列。`;
      if (changeUrl) history.replaceState(null,'',writeFilters(filters,window.location.href));
    }
    function restore() {
      const values=readFilters(window.location.search);
      view=values.view;
      fields.country.value=values.country;
      syncUniversity();
      for (const key of ['q','university','subject']) fields[key].value=values[key];
      update(false);
    }
    form.addEventListener('submit', event => {event.preventDefault();update();});
    fields.q.addEventListener('input',()=>update());
    for (const key of ['country','university','subject']) fields[key].addEventListener('change',()=>{if(key==='country')syncUniversity();update();});
    form.addEventListener('reset',event=>{
      event.preventDefault();
      for (const field of Object.values(fields)) field.value='';
      syncUniversity();
      update();
    });
    for (const button of viewButtons) button.addEventListener('click',()=>{
      view=button.dataset.catalogView;
      if (view==='universities') fields.subject.value='';
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
    viewControls.hidden=false;
  } catch (error) {
    form.hidden=true;
    status.textContent='筛选数据暂时加载失败。你仍可浏览下面的大学、专业，或通过国家和地区进入详情。';
    console.error(error);
  }
}
if (typeof document !== 'undefined') initialize();
