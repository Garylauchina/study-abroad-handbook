import {test} from 'node:test';
import assert from 'node:assert/strict';
import {filterPrograms,filterUniversities,readFilters,writeFilters} from '../docs/assets/javascripts/catalog.mjs';
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
 const filters={q:'计算机 NUS',country:'singapore',university:'nus',subject:'计算机',view:'programs'};
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
 assert.equal(programs.length,36);
 for (const id of ['sheffield','manchester','monash','unsw','nus','ntu']) {
   assert.equal(filterPrograms(programs,{university:id}).length,4);
 }
 for (const id of ['imperial','ucl','hku','cuhk','melbourne','sydney']) {
   assert.equal(filterPrograms(programs,{university:id}).length,2);
 }
 assert.equal(new Set(programs.map(p=>p.university_id)).size,12);
 assert.equal(filterPrograms(programs,{country:'hong-kong'}).length,4);
 assert.equal(filterPrograms(programs,{country:'hong-kong',subject:'计算机'}).length,2);
 assert.equal(new Set(programs.map(p=>p.subject)).size,4);
 assert.ok(filterPrograms(programs,{subject:'工程'}).length>=6);
 assert.ok(filterPrograms(programs,{subject:'经济'}).length>=3);
 assert.ok(universities.every(u=>u.qs_rank<=100));
 assert.equal(universities.filter(u=>u.qs_rank===100).length,2);
 assert.equal(filterUniversities(universities,{country:'hong-kong'}).length,5);
 assert.equal(filterUniversities(universities,{country:'taiwan'}).length,1);
 assert.equal(filterUniversities(universities,{q:'Massachusetts'}).length,1);
 assert.equal(filterUniversities(universities,{q:'麻省理工'}).length,1);
 const mit=filterUniversities(universities,{q:'Massachusetts'})[0];
 assert.equal(mit.program_count,0);
 assert.equal(filterPrograms(programs,{university:mit.id}).length,0);
 assert.equal(filterUniversities(universities,{country:'uk',university:mit.id}).length,0);
 assert.deepEqual([...universities].sort((a,b)=>a.qs_rank-b.qs_rank),universities);
 assert.equal(readFilters('?subject=计算机').view,'programs');
 assert.equal(readFilters('?view=unknown').view,'universities');
});
