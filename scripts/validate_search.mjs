// Exercise the built search worker, so indexed words alone cannot count as a pass.
import { readFileSync } from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const root = path.resolve(process.argv[2] || 'site');
const html = readFileSync(path.join(root, 'index.html'), 'utf8');
const config = JSON.parse(html.match(/<script\b[^>]*\bid="__config"[^>]*>([\s\S]*?)<\/script>/)[1]);
const index = JSON.parse(readFileSync(path.join(root, 'search/search_index.json'), 'utf8'));
const workerUrl = new URL(config.search, 'https://search.invalid/');
const listeners = [];
let pending;
const stack = [];
const context = {
  console, URL, URLSearchParams, performance, TextDecoder, TextEncoder,
  setTimeout, clearTimeout, setInterval, clearInterval, queueMicrotask,
  location: workerUrl,
  addEventListener(type, listener) { if (type === 'message') listeners.push(listener); },
  postMessage(message) {
    if (pending && message.type === pending.type) {
      clearTimeout(pending.timer); pending.resolve(message); pending = undefined;
    }
  },
};
context.self = context;
const sandbox = vm.createContext(context);
function execute(url) {
  assert.equal(url.origin, 'https://search.invalid');
  const file = path.resolve(root, '.' + decodeURIComponent(url.pathname));
  assert.ok(file.startsWith(root + path.sep));
  stack.push(url);
  try { vm.runInContext(readFileSync(file, 'utf8'), sandbox, { filename: file, timeout: 10000 }); }
  finally { stack.pop(); }
}
context.importScripts = (...urls) => urls.forEach(url => execute(new URL(url, stack.at(-1) || workerUrl)));
function request(message, type) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { pending = undefined; reject(new Error('Search worker timed out')); }, 10000);
    pending = { type, resolve, timer };
    const handlers = [...listeners, ...(typeof context.onmessage === 'function' ? [context.onmessage] : [])];
    assert.ok(handlers.length, 'Search worker did not register a handler');
    const event = { data: message, target: context, currentTarget: context, type: 'message' };
    for (const handler of handlers) {
      try { Promise.resolve(handler.call(context, event)).catch(error => { clearTimeout(timer); reject(error); }); }
      catch (error) { clearTimeout(timer); reject(error); }
    }
  });
}
execute(workerUrl);
await request({ type: 0, data: { ...index, options: { suggest: true } } }, 1);
for (const [query, route] of [
  ['预算', 'tools/budget/'], ['预算计算器', 'tools/budget/'],
  ['高考', 'destinations/uk/'], ['UCAS', 'destinations/uk/'], ['Sheffield', 'catalog/uk/sheffield/'],
  ['NUS', 'catalog/singapore/nus/'], ['南洋理工', 'catalog/singapore/ntu/'], ['Monash', 'catalog/australia/monash/'],
  ['麻省理工', 'catalog/usa/mit/'], ['Purdue', 'catalog/usa/purdue/'],
  ['东京科学', 'catalog/japan/science-tokyo/'], ['UCD', 'catalog/ireland/ucd/'],
  ['Sheffield Mechanical', 'catalog/uk/sheffield/sheffield-mechanical-engineering-beng/'],
  ['Manchester Economics', 'catalog/uk/manchester/manchester-economics-bsc/'],
  ['Monash Mechanical', 'catalog/australia/monash/monash-mechanical-engineering/'],
  ['UNSW Economics', 'catalog/australia/unsw/unsw-economics/'],
  ['NUS Electrical', 'catalog/singapore/nus/nus-electrical-engineering/'],
  ['NTU Economics', 'catalog/singapore/ntu/ntu-economics/'],
]) {
  const response = await request({ type: 2, data: query, options: { suggest: true } }, 3);
  const locations = response.data.items.flat().map(item => item.location);
  assert.ok(locations.some(location => location.startsWith(route)), `${query} failed to find ${route}`);
  console.log(`Search ${query}: ${route}`);
}
const empty = await request({ type: 2, data: 'zzqvnonexistentphrase99442' }, 3);
assert.equal(empty.data.items.length, 0, 'Search retained results from an earlier query');
console.log(`Actual search engine checks passed (${index.docs.length} index entries)`);
