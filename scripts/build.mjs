// Copyright © 2026 Christopher Snow
import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {esc,header,footer,renderHome,renderLesson} from './layout.mjs';
const course=JSON.parse(await fs.readFile('src/course.json','utf8'));
const {lessons,modules}=course;
await fs.rm('dist',{recursive:true,force:true});
await fs.mkdir('dist/lessons',{recursive:true});
execFileSync('python3',['scripts/execute.py'],{stdio:'inherit'});
const worked=JSON.parse(await fs.readFile('.cache/worked.json','utf8'));
// Content-addressed assets keep newly deployed markup and interaction code in sync.
const assets={};
for(const file of ['app.js','style.css','worker.js','editor.mjs','rich-text.mjs'])assets[file]=await fs.readFile('src/'+file,'utf8');
assets['worker.js']=assets['worker.js'].replace('const figureHelper = null;', 'const figureHelper = '+JSON.stringify(await fs.readFile('scripts/figure_style.py','utf8'))+';');
assets['style.css']+='\n'+await fs.readFile('src/quiet.css','utf8');
const version=createHash('sha256').update(Object.values(assets).join('\n')).digest('hex').slice(0,12);
for(const [file,content]of Object.entries(assets)){
 await fs.writeFile('dist/'+file,content);
 const dot=file.lastIndexOf('.');const name=file.slice(0,dot)+'.'+version+file.slice(dot);
 let published=content;
 for(const module of ['editor.mjs','rich-text.mjs'])published=published.replaceAll("'./"+module+"'","'./"+module.replace('.', '.'+version+'.')+"'");
 if(file==='app.js')published=published.replace("'worker.js'","'worker."+version+".js'");
 await fs.writeFile('dist/'+name,published);
}

await fs.mkdir('dist/vendor',{recursive:true});
for(const file of ['katex.mjs','katex.min.css'])await fs.copyFile('node_modules/katex/dist/'+file,'dist/vendor/'+file);
await fs.cp('node_modules/katex/dist/fonts','dist/vendor/fonts',{recursive:true});
await fs.copyFile('node_modules/katex/LICENSE','dist/vendor/KATEX-LICENSE.txt');
await fs.copyFile('src/course.json','dist/course.json');
await fs.cp('src/fonts','dist/fonts',{recursive:true});
await fs.cp('python','dist/python',{recursive:true});
await fs.writeFile('dist/worked-environment.json',JSON.stringify(worked.environment,null,2));
await fs.writeFile('dist/.nojekyll','');
await fs.writeFile('dist/favicon.svg','<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><rect width="36" height="36" rx="10" fill="#315bf6"/><path d="m10 25 8-15 8 15M13 20h10" fill="none" stroke="white" stroke-width="2" stroke-linecap="round"/><circle cx="18" cy="10" r="3" fill="#a6c4ff"/></svg>');
const shell=(title,body,p='')=>`<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="Learn the scientific method through 30 short investigations. Design fair experiments, run real Python statistics in your browser and make claims your evidence can support."><title>${esc(title)} · Scientific Method Lab</title><link rel="icon" href="${p}favicon.svg"><link rel="stylesheet" href="${p}vendor/katex.min.css"><link rel="stylesheet" href="${p}style.${version}.css"><script>try{document.documentElement.dataset.theme=localStorage.getItem('sml:theme')||'light'}catch{}</script><script type="module" src="${p}app.${version}.js"></script></head><body>${header(p)}${body}${footer(p)}</body></html>`;
await fs.writeFile('dist/index.html',shell('Course overview',renderHome(course)));
for(const [i,l]of lessons.entries()){
 const code=await fs.readFile('python/'+l.code,'utf8');
 const record=worked.lessons[l.slug];
 const figures=[];
 for(const [j,svg]of record.figures.entries()){
  const filename=l.slug+'-'+j+'.svg';await fs.writeFile('dist/lessons/'+filename,svg);
  const narrowFilename=l.slug+'-'+j+'-narrow.svg';await fs.writeFile('dist/lessons/'+narrowFilename,record.figures_narrow[j]);
  figures.push(`<figure class="worked-figure"><picture><source media="(max-width:700px)" srcset="${narrowFilename}"><img class="plot" src="${filename}" alt="${esc(l.plot||'Plot from the published example')}" loading="lazy"></picture><figcaption><a href="${filename}" target="_blank" rel="noopener">Open full-size figure ↗</a></figcaption></figure>`);
 }
 const body=renderLesson({lesson:{...l,worked:record},index:i,lessons,modules,code,figures});
 await fs.writeFile('dist/lessons/'+l.slug+'.html',shell(l.title,body,'../'));
}
const glossary={
 'Treatment':'A condition deliberately assigned in an experiment.',
 'Response':'The outcome measured under a stated procedure and boundary.',
 'Confounder':'A variable related to treatment and outcome that can tangle their observed relationship.',
 'Experimental unit':'The smallest unit independently assigned a treatment; repeated readings within it are subsamples.',
 'Block / pair':'Observations grouped by a shared condition so treatments can be compared within that group.',
 'Randomisation':'A chance procedure for assigning treatment or order; it does not guarantee exact balance in one experiment.',
 'Interaction':'The effect of one factor depends on another factor’s level.',
 'Population / sample':'The collection you want to describe / the subset you observe.',
 'Standard deviation':'Spread of individual observations around their mean, in the observations’ units.',
 'Standard error':'Estimated variability of an estimator across repeated samples under a stated model.',
 'Confidence interval':'An interval from a procedure with a stated repeated-sampling coverage target, under its assumptions.',
 'Bootstrap':'Resample observed units with replacement and recalculate a statistic to approximate sampling variation.',
 'Null model':'A reference claim plus assumptions that describe how observations would vary if that claim held.',
 'p-value':'A tail probability for the observed statistic under a specified null model and test rule; not the probability the null is true.',
 'Power':'Probability a specified test rejects its null under a particular alternative model.',
 'Effect size':'The magnitude of a difference or relationship, expressed in an interpretable unit or scale.',
 'Residual':'An observed value minus its model prediction.',
 'Reproducibility / replication':'Here: rerunning a calculation on saved inputs / collecting new evidence to examine a finding. Usage varies across fields.'};
const notes=`<main id="main" class="field-notes"><h1>Course notes</h1><p class="standfirst">What to know before you start, how Python runs and how to keep your work.</p>
<nav class="on-this-page" aria-label="Course notes sections"><a href="#before-you-start">Before you start</a><a href="#runtime">Using Python</a><a href="#glossary">Glossary</a><a href="#sources">Sources</a></nav>
<section id="before-you-start"><h2>Before you start</h2><p>Be ready to read Python lists, function calls and a short loop. The lessons introduce the statistics and the parts of NumPy, pandas and SciPy that they use.</p><p>Work through the 30 investigations in order if the methods are new to you. The first reading, run and question take an estimated 5–9 minutes each. Allow extra time for trying changes and collecting your own data.</p><p>Open Published example output to read examples without running Python. The editor, answer checks and storage need JavaScript.</p></section>
<section id="runtime"><h2>Using Python in your browser</h2><p>Opening a lesson loads the code into the editor. Python and its statistics packages can load while you read. On a slow connection, this can take a while. Each run starts with fresh user variables.</p><p>Use Tab to leave the editor. Ctrl+Enter or ⌘+Enter runs the code from the editor. Stop cancels the current run. The next run starts a fresh Python session. If a run fails, check the error message. The last successful result and its export remain available.</p><p>In Editor tools, Restore example opens the original code. Recover draft reopens the most recently replaced draft. On the report page, Use invented starter data changes the next input without replacing your code.</p>
<h3>Where the results come from</h3><p>Published example output comes from the code run during the site build. Your result comes from the code and input used in your browser when you ran it. Compare timing measurements only after checking that the machines, runtimes and timed work suit your question.</p><p>Invented values illustrate the arithmetic. A seeded simulation repeats a specified model and sequence. Actual timings describe work recorded during execution. If you choose a CSV for the report, justify where its pairs came from and why they are independent.</p>
<h3>Keep your work</h3><p>This browser saves code drafts, predictions, notes, report fields, answer attempts and reading marks when storage is available. Clearing site data removes those copies. In the course overview, use Save or restore your work to export them. Import replaces matching records, so export the current copy first if you want to keep it.</p><p>On a lesson, open Result tools and select Export run to keep the last successful code, output, plots, runtime versions and any input CSV. The selected CSV and the result are held on the open page until you export the run. Keep your original CSV separately.</p>
<details><summary>Python versions and running a downloaded example</summary><p>The browser uses <a href="https://pyodide.org/en/0.27.7/">Pyodide 0.27.7</a> and the packages in the <a href="runtime-manifest.json">runtime manifest</a>. This site serves the packages and verifies their hashes during the build. The browser runs your code locally. Python code can make network requests that your browser allows.</p><p>Use Download Python in Editor tools to get the script. In a local Python environment, install the packages and run the downloaded file.</p><pre>python -m pip install numpy==2.0.2 scipy==1.14.1 pandas==2.2.3 matplotlib==3.9.4
python downloaded-investigation.py</pre><p>For the report example, place your selected CSV beside the script as <code>data.csv</code>. To display or save a plot locally, add <code>plt.show()</code> or <code>plt.savefig("figure.svg")</code> to the end of a plot example. <a href="vendor/KATEX-LICENSE.txt">KaTeX licence</a>.</p></details></section>
<section id="glossary"><h2>Glossary</h2><dl class="glossary">${Object.entries(glossary).map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl></section>
<section id="sources"><h2>Sources and acknowledgements</h2><p>The original examples draw on the author’s Assembly Lab, Event Streaming Lab and Benchmarking Lab. Code is Apache-2.0 and course prose is CC BY-NC 4.0. Third-party packages retain their own licences.</p><ul class="source-list">${[...new Map(lessons.map(l=>[l.source[1],l.source])).values()].map(([title,url])=>`<li><a href="${url}">${title} ↗</a></li>`).join('')}</ul><p>The repository records the source review and functional checks. Learning effectiveness remains unmeasured.</p></section><a class="button primary" href="index.html#course">Back to the investigations</a></main>`;
await fs.writeFile('dist/field-notes.html',shell('Course notes',notes));
execFileSync('python3',['scripts/prepare-runtime.py'],{stdio:'inherit'});
await fs.rm('.preview/scientific-method-lab',{recursive:true,force:true});
await fs.mkdir('.preview/scientific-method-lab',{recursive:true});
await fs.cp('dist','.preview/scientific-method-lab',{recursive:true});
console.log(`Built ${lessons.length} investigations, overview, field notes and a self-hosted stats runtime.`);
