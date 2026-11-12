// Copyright © 2026 Christopher Snow
const root=new URL('.',import.meta.url);
const $=id=>document.getElementById(id);
const prefix='sml:v1:';
let storageAvailable=true;
function get(key,fallback=''){
 try{return localStorage.getItem(prefix+key)??fallback}catch{storageAvailable=false;return fallback}
}
function put(key,value){
 try{localStorage.setItem(prefix+key,String(value));return true}catch{
  storageAvailable=false;
  const target=$('save-note')||$('progress-status');
  if(target)target.textContent='Browser storage is unavailable or full. Export your work before leaving this page.';
  return false;
 }
}
function download(name,body,type='application/json'){
 const url=URL.createObjectURL(new Blob([body],{type}));
 const anchor=document.createElement('a');anchor.href=url;anchor.download=name;anchor.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function updateReadMarks(){
 document.querySelectorAll('[data-read]').forEach(el=>el.textContent=get('read:'+el.dataset.read)==='true'?'✓ Read':'');
}
$('theme')?.addEventListener('click',()=>{
 const theme=document.documentElement.dataset.theme==='dark'?'light':'dark';
 document.documentElement.dataset.theme=theme;
 try{localStorage.setItem('sml:theme',theme)}catch{}
 setThemeLabel();
});
function setThemeLabel(){const dark=document.documentElement.dataset.theme==='dark';$('theme')?.setAttribute('aria-label',`Switch to ${dark?'light':'dark'} theme`)}
setThemeLabel();
const course=await fetch(new URL('course.json',root)).then(response=>{if(!response.ok)throw new Error('Course data could not load. Please reload.');return response.json()}).catch(error=>{
 const target=$('status')||$('progress-status');if(target)target.textContent=error.message;return null;
});
if(course){
 updateReadMarks();
 if($('search'))initializeOverview(course);
 const lesson=course.lessons.find(l=>l.slug===document.querySelector('[data-slug]')?.dataset.slug);
 if(lesson)initializeLesson(lesson);
 document.documentElement.dataset.ready='true';
}
function initializeOverview({lessons}){
 function progress(){
  const read=lessons.filter(l=>get('read:'+l.slug)==='true').length;
  $('progress-count').textContent=`${read} / ${lessons.length} read`;
  $('course-progress').value=read;
  if(read){
   $('progress-title').textContent=read===lessons.length?'A course read. More questions ahead.':'Your investigation continues.';
   $('progress-text').textContent='Reading marks record progress, not mastery. Your drafts stay on this browser.';
   const next=lessons.find(l=>get('read:'+l.slug)!=='true');
   if(next){$('start-course').href='lessons/'+next.slug+'.html';$('start-course').innerHTML='Continue investigating <span>↗</span>'}
  }
  updateReadMarks();
 }
 progress();
 if(!storageAvailable)$('progress-status').textContent='Browser storage is unavailable. Use exports to keep your work.';
 $('search').addEventListener('input',()=>{
  const words=$('search').value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let count=0;
  document.querySelectorAll('.lesson-row').forEach(row=>{const match=words.every(word=>row.dataset.search.includes(word));row.hidden=!match;if(match)count++});
  document.querySelectorAll('.module').forEach(module=>module.hidden=![...module.querySelectorAll('.lesson-row')].some(row=>!row.hidden));
  $('search-count').textContent=`${count} investigation${count===1?'':'s'}`;
  $('search-empty').hidden=count!==0;
 });
 $('export-progress').addEventListener('click',()=>{
  const data={};
  try{for(let i=0;i<localStorage.length;i++){const key=localStorage.key(i);if(key.startsWith(prefix))data[key.slice(prefix.length)]=localStorage.getItem(key)}}catch{}
  download('scientific-method-lab-progress.json',JSON.stringify({course:'scientific-method-lab',schema:1,exported_at:new Date().toISOString(),data},null,2));
  $('progress-status').textContent='Exported saved reading marks, attempts and drafts. Run results and CSV inputs require their own exports.';
 });
 $('import-progress').addEventListener('change',async()=>{
  const file=$('import-progress').files[0];if(!file)return;
  try{
   if(file.size>1_000_000)throw new Error('Progress file must be smaller than 1 MB.');
   const record=JSON.parse(await file.text());
   if(record.course!=='scientific-method-lab'||record.schema!==1||!record.data||typeof record.data!=='object'||Array.isArray(record.data))throw new Error('Not a version 1 Scientific Method Lab progress file.');
   const slugs=new Set(lessons.map(l=>l.slug));
   const fields=new Set(['code','prediction','notes','quiz','report-question','report-plan','report-source','report-finding','report-limits']);
   const entries=Object.entries(record.data);
   for(const[key,value]of entries){
    const [type,slug,field,...extra]=key.split(':');
    if(extra.length||!slugs.has(slug)||typeof value!=='string'||value.length>300_000||!((type==='read'&&!field&&(value==='true'||value==='false'))||(type==='draft'&&fields.has(field))))throw new Error('Progress file contains an invalid record. Nothing has been imported.');
   }
   let saved=0;for(const[key,value]of entries)if(put(key,value))saved++;
   progress();$('progress-status').textContent=saved===entries.length?`Imported ${saved} saved records. Matching records in this browser were replaced.`:'Some records could not be saved. Export your work and check browser storage.';
  }catch(error){$('progress-status').textContent=error.message}
  $('import-progress').value='';
 });
}
function initializeLesson(lesson){
 const slug=lesson.slug;
 const initialCode=$('code').value;
 let worker=null,timer=null,busy=false,lastRun=null,csv=null,csvName=null,revision=0;
 const initialQuiz=get(`draft:${slug}:quiz`);
 const draftKey=id=>`draft:${slug}:${id}`;
 $('code').value=get(draftKey('code'),initialCode);
 document.querySelectorAll('[data-save]').forEach(el=>{
  el.value=get(draftKey(el.dataset.save));
  el.addEventListener('input',()=>put(draftKey(el.dataset.save),el.value));
 });
 if(!storageAvailable)$('save-note').textContent='Browser storage is unavailable. Export your work before leaving.';
 $('mark-read').checked=get('read:'+slug)==='true';
 $('mark-read').addEventListener('change',()=>{put('read:'+slug,$('mark-read').checked);updateReadMarks()});
 function stale(){
  if(!lastRun)return;
  const changed=$('code').value!==lastRun.source || csv!==lastRun.input_csv;
  $('output-provenance').textContent=changed?'Code or input changed. Output and run export still describe the previous execution. Run again to update.':`Output from your completed ${lastRun.error?'erroring':'successful'} execution at ${new Date(lastRun.executed_at).toLocaleTimeString()}.`;
  $('output-provenance').classList.toggle('stale',changed);
 }
 $('code').addEventListener('input',()=>{put(draftKey('code'),$('code').value);stale()});
 $('code').addEventListener('keydown',event=>{
  if(event.key==='Tab'&&!event.shiftKey){event.preventDefault();const start=event.target.selectionStart,end=event.target.selectionEnd;event.target.setRangeText('    ',start,end,'end');event.target.dispatchEvent(new Event('input'))}
  if((event.ctrlKey||event.metaKey)&&event.key==='Enter'){event.preventDefault();if(!busy)run()}
 });
 $('restore').addEventListener('click',()=>{$('code').value=initialCode;put(draftKey('code'),initialCode);stale();$('status').textContent='Published example restored. Run to get fresh output.'});
 $('download-code').addEventListener('click',()=>download(slug+'.py',$('code').value,'text/x-python'));
 $('export-run').addEventListener('click',()=>{
  if(!lastRun)return;
  const notes={prediction:$('prediction').value,notes:$('notes').value};
  download(slug+'-run.json',JSON.stringify({...lastRun,notes},null,2));
 });
 function controls(running){
  busy=running;$('run').disabled=running;$('stop').disabled=!running;$('restore').disabled=running;
  if($('csv-upload'))$('csv-upload').disabled=running;
  if($('clear-csv'))$('clear-csv').disabled=running||csv===null;
 }
 function terminate(message){
  revision++;clearTimeout(timer);worker?.terminate();worker=null;controls(false);$('status').textContent=message;
  $('output-provenance').textContent=lastRun?'Execution stopped. The visible output and export still describe the previous completed run.':'Execution stopped before a complete result was recorded.';
 }
 $('stop').addEventListener('click',()=>terminate('Stopped. No result was saved for the cancelled run. Run again to restart Python.'));
 async function run(){
  if(busy)return;
  const source=$('code').value,input=csv,inputName=csvName,runRevision=++revision;
  controls(true);$('status').textContent='Loading Python and statistics packages. First run can take a moment…';
  if(lastRun)$('output-provenance').textContent='A new execution is in progress. The visible output still belongs to the previous run.';
  const fail=message=>{
   if(runRevision!==revision)return;
   terminate('Python could not finish. Check the message, then edit or run again.');
   $('output').textContent=message;$('output').classList.add('error');$('plots').replaceChildren();
   $('output-provenance').textContent='Execution failed before a complete result could be recorded. Previous completed run export, if any, is unchanged.';
  };
  timer=setTimeout(()=>fail('Python initialization exceeded two minutes. Check your connection and run again.'),120000);
  if(!worker){try{worker=new Worker(new URL('worker.js',root))}catch(error){fail(error.message);return}}
  worker.onerror=event=>fail(event.message||'The Python worker could not load.');
  worker.onmessage=({data})=>{
   if(runRevision!==revision)return;
   if(data.type==='running'){
    clearTimeout(timer);$('status').textContent='Running your Python…';
    timer=setTimeout(()=>fail('Execution exceeded 45 seconds and was stopped. Reduce the work or fix a loop, then run again.'),45000);return;
   }
   if(data.type==='error'){fail(data.message);return}
   if(data.type!=='result')return;
   clearTimeout(timer);controls(false);
   const {stdout,error,figures,versions}=data.value;
   lastRun={schema:1,course:'scientific-method-lab',lesson:slug,executed_at:new Date().toISOString(),source,input_csv:input,input_name:inputName,stdout,error,figures_svg_base64:figures,versions,environment:{user_agent:navigator.userAgent,timing_scope:'Local browser Pyodide; see executed source for boundaries.'}};
   $('output').textContent=(stdout||'No text was printed.')+(error?'\n'+error:'');
   $('output').classList.toggle('error',!!error);
   $('plots').replaceChildren(...figures.map((svg,i)=>{const image=document.createElement('img');image.className='plot';image.src='data:image/svg+xml;base64,'+svg;image.alt=`Plot ${i+1} generated by your actual Python execution. Read its axis labels and the text output to interpret it.`;return image}));
   $('status').textContent=error?'Python reported an error. Edit the code and run again.':'Completed. Inspect the output, then change one thing.';
   $('export-run').disabled=false;stale();
  };
  worker.postMessage({source,csv:input});
 }
 $('run').addEventListener('click',run);
 window.addEventListener('pagehide',()=>{clearTimeout(timer);worker?.terminate()});
 let quizAttempt=null;
 try{quizAttempt=JSON.parse(initialQuiz)}catch{}
 if(quizAttempt&&Number.isInteger(quizAttempt.answer)&&quizAttempt.answer>=0&&quizAttempt.answer<lesson.options.length){
  const choice=document.querySelector(`input[name=answer][value="${quizAttempt.answer}"]`);if(choice)choice.checked=true;
 }
 $('quiz').addEventListener('submit',event=>{
  event.preventDefault();const selected=document.querySelector('input[name=answer]:checked');
  if(!selected){$('quiz-feedback').textContent='Choose an answer first, then check your reasoning.';return}
  const answer=Number(selected.value),correct=answer===lesson.correct;
  put(draftKey('quiz'),JSON.stringify({answer,correct,at:new Date().toISOString()}));
  const feedback=$('quiz-feedback');feedback.replaceChildren();feedback.classList.toggle('incorrect',!correct);
  const title=document.createElement('b');title.textContent=correct?'That reasoning fits.':'Reconsider the comparison.';
  const text=document.createElement('span');text.textContent=lesson.feedback;
  feedback.append(title,text);feedback.focus({preventScroll:true});
 });
 if($('csv-upload')){
  $('csv-upload').addEventListener('change',async()=>{
   const file=$('csv-upload').files[0];if(!file)return;
   try{
    if(file.size>1_000_000)throw new Error('CSV must be smaller than 1 MB.');
    const text=await file.text();if(!text.trim())throw new Error('The file is empty.');
    csv=text;csvName=file.name;
    $('csv-status').textContent=`Selected ${file.name}. Input stays on this device. Run Python to validate and analyse it.`;
    $('clear-csv').disabled=false;stale();
   }catch(error){$('csv-status').textContent=error.message+' The previous input is unchanged.'}
   $('csv-upload').value='';
  });
  $('clear-csv').addEventListener('click',()=>{csv=null;csvName=null;$('clear-csv').disabled=true;$('csv-status').textContent='No file selected. The code will use invented starter data.';stale()});
  $('export-report').addEventListener('click',()=>{
   const fields=[['question','Question & useful threshold'],['plan','Prospective experiment plan'],['source','Data source & conditions'],['finding','Finding & uncertainty'],['limits','Limitations & next test']];
   const body=['# Scientific Method Lab · Investigation',`Exported ${new Date().toISOString()}`];
   for(const[id,label]of fields)body.push(`## ${label}\n\n${$('report-'+id).value||'[Not recorded]'}`);
   body.push('## Execution record');
   if(lastRun){
    body.push(`Executed ${lastRun.executed_at}. Input: ${lastRun.input_name||'No uploaded file; inspect source for starter data.'}\n\nVersions: ${JSON.stringify(lastRun.versions)}`);
    body.push('### Exact executed Python\n\n```python\n'+lastRun.source+'\n```');
    body.push('### Actual output\n\n```text\n'+lastRun.stdout+(lastRun.error||'')+'\n```');
    if(lastRun.input_csv!==null)body.push('### Exact input CSV\n\n```csv\n'+lastRun.input_csv+'\n```');
    if($('code').value!==lastRun.source||csv!==lastRun.input_csv)body.push('The editor or selected input changed after this run. The record above preserves the completed execution.');
   }else body.push('No execution was recorded on this page. Do not describe the worked output as your own measurement.');
   body.push('## Field notes\n\n'+($('notes').value||'[Not recorded]'));
   download('scientific-method-investigation.md',body.join('\n\n')+'\n','text/markdown');
   $('report-status').textContent='Investigation exported. Save your original data and run JSON alongside it.';
  });
 }
 controls(false);
}
