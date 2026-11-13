// Copyright © 2026 Christopher Snow
// Decoration only. The native textarea remains the editing and accessibility surface.
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const keywords=new Set('and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield True False None'.split(' '));
const builtins=new Set('print range len int float str list set dict tuple sum min max abs round enumerate zip sorted isinstance open bool'.split(' '));
const tokens=/((?:[rubf]{0,2})(?:"""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)|#[^\n]*|\b[A-Za-z_]\w*\b|\b\d+(?:\.\d*)?(?:[eE][+-]?\d+)?\b)/gi;
export function highlightPython(source){
 let output='',last=0;
 for(const match of source.matchAll(tokens)){
  output+=escape(source.slice(last,match.index));const text=match[0];let type='';
  if(text.startsWith('#'))type='comment';
  else if(/^[rubf]{0,2}["']/i.test(text))type='string';
  else if(keywords.has(text))type='keyword';
  else if(builtins.has(text))type='builtin';
  else if(/^\d/.test(text))type='number';
  else if(/^\s*\(/.test(source.slice(match.index+text.length)))type='function';
  output+=type?`<span class="token-${type}">${escape(text)}</span>`:escape(text);
  last=match.index+text.length;
 }
 return output+escape(source.slice(last));
}
export function attachEditor(textarea){
 const root=document.getElementById('code-editor'),pre=document.getElementById('code-highlight'),code=pre?.querySelector('code'),gutter=document.getElementById('line-numbers');
 if(!root||!pre||!code||!gutter)return()=>{};
 const sync=()=>{pre.scrollTop=textarea.scrollTop;pre.scrollLeft=textarea.scrollLeft;gutter.style.transform=`translateY(-${textarea.scrollTop}px)`};
 const update=()=>{code.innerHTML=highlightPython(textarea.value)+'\n';gutter.replaceChildren(...Array.from({length:textarea.value.split('\n').length},(_,i)=>{const line=document.createElement('span');line.textContent=i+1;return line}));sync()};
 textarea.addEventListener('input',update);textarea.addEventListener('scroll',sync,{passive:true});
 root.classList.add('is-highlighted');update();return update;
}
