// Copyright © 2026 Christopher Snow
// Small explicit notation format: $LaTeX$ for mathematics, `code` for Python.
export const escapeText=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
export function renderRich(value,renderMath){
 const text=String(value);let result='',start=0;
 for(const match of text.matchAll(/`([^`\n]+)`|\$([^$\n]+)\$/g)){
  result+=escapeText(text.slice(start,match.index));
  result+=match[1]!==undefined?`<code class="inline-python">${escapeText(match[1])}</code>`:renderMath(match[2]);
  start=match.index+match[0].length;
 }
 return result+escapeText(text.slice(start));
}
