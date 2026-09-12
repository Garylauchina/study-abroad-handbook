import {test} from 'node:test';
import assert from 'node:assert/strict';
import {filterPrograms,filterUniversities,readFilters,writeFilters,paginate} from '../docs/assets/javascripts/catalog.mjs';
import {readFileSync} from 'node:fs';
const items=[
 {id:'a',country_id:'uk',university_id:'sheffield',subject:'计算机',name:'计算机科学',name_en:'Computer Science BSc',university_name:'谢菲尔德大学',university_name_en:'University of Sheffield',country_name:'英国'},
 {id:'b',country_id:'uk',university_id:'manchester',subject:'商科',name:'管理学',name_en:'Management BSc',university_name:'曼彻斯特大学',university_name_en:'University of Manchester',country_name:'英国'},
 {id:'c',country_id:'singapore',university_id:'nus',subject:'计算机',name:'计算机科学',name_en:'Bachelor of Computing',university_name:'新加坡国立大学',university_name_en:'National University of Singapore',country_name:'新加坡'},
];
test('filters intersect and understand Chinese, English, abbreviations and pasted fullwidth text',()=>{
 assert.equal(filterPrograms(items).length,3);
 assert.deepEqual(filterPrograms(items,{country:'uk',subject:'计算机'}).map(x=>x.id),['a']);
 assert.deepEqual(filterPrograms(items,{q:'  ＮＵＳ  计算机　'}).map(x=>x.id),['c']);
 assert.deepEqual(filterPrograms(items,{q:'Sheffield science'}).map(x=>x.id),['a']);
 assert.equal(filterPrograms(items,{q:'unlisted-university'}).length,0);
 assert.equal(filterPrograms(items,{country:'uk',university:'nus'}).length,0);
});
test('filters round trip through a shareable project URL and reset without discarding its anchor',()=>{
 const filters={q:'计算机 NUS',country:'singapore',university:'nus',subject:'计算机',depth:'detailed',view:'programs',page:2};
 const url=writeFilters(filters,'https://garylauchina.github.io/study-abroad-handbook/#program-finder');
 assert.deepEqual(readFilters(url.search),filters);
 assert.equal(url.searchParams.has('q'),false,'Catalog must not trigger the theme full-text search overlay');
 assert.equal(url.searchParams.get('query'),'计算机 NUS');
 assert.equal(url.pathname,'/study-abroad-handbook/');
 assert.equal(writeFilters({},url).href,'https://garylauchina.github.io/study-abroad-handbook/#program-finder');
});
test('QS directory preserves all published top-100 places, mainland exclusion and school search without program records',()=>{
 const catalog=JSON.parse(readFileSync(new URL('../docs/assets/data/catalog-index.json',import.meta.url)));
 const {universities,programs}=catalog;
 assert.equal(universities.length,96);
 assert.equal(new Set(universities.map(u=>u.country_id)).size,22);
 const detailed=filterPrograms(programs,{depth:'detailed'});
 assert.ok(detailed.length>=36,'Previously researched program details must remain available');
 for (const id of ['sheffield','manchester','monash','unsw','nus','ntu']) {
   assert.ok(filterPrograms(detailed,{university:id}).length>=4);
 }
 for (const id of ['imperial','ucl','hku','cuhk','melbourne','sydney']) {
   assert.ok(filterPrograms(detailed,{university:id}).length>=2);
 }
 assert.ok(new Set(detailed.map(p=>p.university_id)).size>=12);
 assert.ok(filterPrograms(detailed,{country:'hong-kong'}).length>=4);
 assert.ok(filterPrograms(detailed,{country:'hong-kong',subject:'计算机'}).length>=2);
 assert.ok(filterPrograms(programs,{subject:'工程'}).length>=6);
 assert.ok(filterPrograms(programs,{subject:'经济'}).length>=3);
 assert.ok(universities.every(u=>u.qs_rank<=100));
 assert.equal(universities.filter(u=>u.qs_rank===100).length,2);
 assert.equal(filterUniversities(universities,{country:'hong-kong'}).length,5);
 assert.equal(filterUniversities(universities,{country:'taiwan'}).length,1);
 assert.equal(filterUniversities(universities,{q:'Massachusetts'}).length,1);
 assert.equal(filterUniversities(universities,{q:'麻省理工'}).length,1);
 const mit=filterUniversities(universities,{q:'Massachusetts'})[0];
 assert.equal(mit.program_count,filterPrograms(programs,{university:mit.id}).length);
 assert.equal(filterUniversities(universities,{country:'uk',university:mit.id}).length,0);
 assert.deepEqual([...universities].sort((a,b)=>a.qs_rank-b.qs_rank),universities);
 assert.equal(readFilters('?subject=计算机').view,'programs');
 assert.equal(readFilters('?depth=enriched').view,'programs');
 assert.equal(readFilters('?view=unknown').view,'universities');
});
test('pagination bounds large results, preserves order and distinguishes directory entries from detailed records',()=>{
 const records=Array.from({length:5003},(_,i)=>({id:String(i),detail_status:i%3?'directory':'detailed'}));
 assert.deepEqual(paginate(records,2).items.map(p=>p.id),records.slice(24,48).map(p=>p.id));
 assert.equal(paginate(records,999999).page,209);
 assert.equal(paginate(records,999999).items.length,11);
 assert.equal(paginate([],0).page,1);
 assert.equal(paginate([],0).pages,1);
 assert.equal(filterPrograms(records,{depth:'detailed'}).length,1668);
 assert.equal(readFilters('?page=-20').page,1);
 assert.equal(readFilters('?page=abc').page,1);
 assert.equal(writeFilters({page:1},'https://example.com/?page=7').search,'');
});
