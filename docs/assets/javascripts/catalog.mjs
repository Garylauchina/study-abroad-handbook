// Search structured catalog fields; static cards and country links remain usable offline.
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
export function readFilters(search) {
  const params = new URLSearchParams(search);
  return Object.fromEntries(['q','country','university','subject'].map(key => [key, params.get(key === 'q' ? 'query' : key) || '']));
}
export function writeFilters(filters, url) {
  const next = new URL(url);
  for (const key of ['q','country','university','subject']) {
    const parameter = key === 'q' ? 'query' : key; // q belongs to the theme's full-text search overlay.
    if (filters[key]) next.searchParams.set(parameter, filters[key]); else next.searchParams.delete(parameter);
  }
  return next;
}
async function initialize() {
  const finder = document.getElementById('program-finder');
  if (!finder) return;
  const form = finder.querySelector('form');
  const fields = Object.fromEntries(['q','country','university','subject'].map(key => [key, form.elements.namedItem(key)]));
  const status = document.getElementById('catalog-status');
  const cards = [...finder.querySelectorAll('[data-program-id]')];
  const options = [...fields.university.options].map(option => option.cloneNode(true));
  const syncUniversity = () => {
    const selected = fields.university.value;
    fields.university.replaceChildren(...options.filter(o => !o.value || !fields.country.value || o.dataset.country === fields.country.value).map(o => o.cloneNode(true)));
    if ([...fields.university.options].some(o => o.value === selected)) fields.university.value = selected;
  };
  try {
    const response = await fetch(new URL(finder.dataset.catalogUrl, document.baseURI));
    if (!response.ok) throw new Error(`Catalog HTTP ${response.status}`);
    const programs = await response.json();
    function update(changeUrl=true) {
      const filters = Object.fromEntries(Object.entries(fields).map(([key,field])=>[key,field.value]));
      const matches = new Set(filterPrograms(programs,filters).map(p=>p.id));
      cards.forEach(card => {card.hidden = !matches.has(card.dataset.programId);});
      document.getElementById('catalog-empty').hidden = matches.size !== 0;
      status.textContent = `找到 ${matches.size} 个专业，共收录 ${programs.length} 个。入学年度与费用币种见各项目。`;
      if (changeUrl) history.replaceState(null,'',writeFilters(filters,window.location.href));
    }
    function restore() {
      const values=readFilters(window.location.search);
      fields.country.value=values.country;
      syncUniversity();
      for (const key of ['q','university','subject']) fields[key].value=values[key];
      update(false);
    }
    form.addEventListener('submit', event => {event.preventDefault();update();});
    fields.q.addEventListener('input',update);
    for (const key of ['country','university','subject']) fields[key].addEventListener('change',()=>{if(key==='country')syncUniversity();update();});
    form.addEventListener('reset',event=>{
      event.preventDefault();
      for (const field of Object.values(fields)) field.value='';
      syncUniversity();
      update();
    });
    window.addEventListener('popstate',restore);
    restore();
  } catch (error) {
    form.hidden=true;
    status.textContent='筛选数据暂时加载失败。你仍可浏览下面的全部专业，或通过国家、大学进入详情。';
    console.error(error);
  }
}
if (typeof document !== 'undefined') initialize();
