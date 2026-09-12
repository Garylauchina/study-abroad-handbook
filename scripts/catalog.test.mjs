import {test} from 'node:test';
import assert from 'node:assert/strict';
import {filterPrograms,readFilters,writeFilters} from '../docs/assets/javascripts/catalog.mjs';
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
 const filters={q:'计算机 NUS',country:'singapore',university:'nus',subject:'计算机'};
 const url=writeFilters(filters,'https://garylauchina.github.io/study-abroad-handbook/#program-finder');
 assert.deepEqual(readFilters(url.search),filters);
 assert.equal(url.searchParams.has('q'),false,'Catalog must not trigger the theme full-text search overlay');
 assert.equal(url.searchParams.get('query'),'计算机 NUS');
 assert.equal(url.pathname,'/study-abroad-handbook/');
 assert.equal(writeFilters({},url).href,'https://garylauchina.github.io/study-abroad-handbook/#program-finder');
});
