// Copyright © 2026 Christopher Snow
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
const entries=await fs.readdir('dist/lessons');
const pages=['dist/index.html','dist/field-notes.html',...entries.filter(f=>f.endsWith('.html')).map(f=>'dist/lessons/'+f)];
let checked=0;
for(const page of pages){
 const html=await fs.readFile(page,'utf8');
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 assert.equal(ids.length,new Set(ids).size,'Duplicate ID in '+page);
 for(const match of html.matchAll(/(?:href|src)="([^"]+)"/g)){
  const url=match[1];if(/^(https?:|data:|mailto:)/.test(url))continue;
  const[file,fragment]=url.split('#');const destination=file?path.resolve(path.dirname(page),file):path.resolve(page);
  await fs.access(destination).catch(()=>{throw new Error(`Broken local link ${url} in ${page}`)});
  if(fragment){const target=await fs.readFile(destination,'utf8');assert.ok(target.includes(`id="${fragment}"`),`Missing fragment ${url} in ${page}`)}
  checked++;
 }
 assert.ok(html.includes('<main id="main"'),'Missing main landmark');
}
console.log(`PASS: ${pages.length} static pages, ${checked} relative links and fragments, unique IDs.`);
