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
await fs.writeFile('dist/index.html',shell('Turn curiosity into evidence',renderHome(course)));
for(const [i,l]of lessons.entries()){
 const code=await fs.readFile('python/'+l.code,'utf8');
 const record=worked.lessons[l.slug];
 const figures=[];
 for(const [j,svg]of record.figures.entries()){
  const filename=l.slug+'-'+j+'.svg';await fs.writeFile('dist/lessons/'+filename,svg);
  const narrowFilename=l.slug+'-'+j+'-narrow.svg';await fs.writeFile('dist/lessons/'+narrowFilename,record.figures_narrow[j]);
  figures.push(`<figure class="worked-figure"><picture><source media="(max-width:700px)" srcset="${narrowFilename}"><img class="plot" src="${filename}" alt="Plot generated from the published Python during the build. Refer to its labelled axes and the text output." loading="lazy"></picture><figcaption><a href="${filename}" target="_blank" rel="noopener">Open full-size figure ↗</a></figcaption></figure>`);
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
const notes=`<main id="main" class="field-notes"><div class="eyebrow">THE FIELD NOTES</div><h1>Know your tools.<br><em>Question your evidence.</em></h1><p class="standfirst">A guide to the course, the runtime and the limits of each result.</p><nav class="on-this-page" aria-label="Field notes sections"><a href="#before-you-start">Start here</a><a href="#runtime">Runtime</a><a href="#glossary">Glossary</a><a href="#sources">Sources</a></nav><section id="before-you-start"><h2>Before you start</h2><p>You should be able to read Python lists, function calls and a short loop. No prior statistics is assumed. The examples introduce NumPy arrays, pandas tables and SciPy functions where they become useful. This is a scientific reasoning course with Python, rather than a complete introduction to Python syntax.</p><p>The essential route is thirty investigations in six modules. Each takes about 5–9 minutes for the initial reading, experiment and question. Exploring changes or collecting your final investigation takes longer. Work in order the first time; later lessons use ideas you have already practised. There are no prerequisite locks.</p><p>The scientific method is an iterative practice, not a rigid recipe. Observation, measurement, prediction, intervention and model revision inform one another. Statistical methods support that reasoning; they cannot determine whether the question matters or every assumption is justified.</p><p>You can read the explanations, inspect code and open generated worked output without loading Python. JavaScript is needed for code execution, feedback, saved drafts and exports. No account or paid service is required.</p></section><section id="runtime"><h2>What actually runs?</h2><p>CPython runs on your device through <a href="https://pyodide.org/en/0.27.7/">Pyodide 0.27.7</a> in a Web Worker. NumPy 2.0.2, SciPy 1.14.1, pandas 2.2.3 and Matplotlib 3.8.4 are real Python packages. Runtime files and their dependency wheels are pinned, hash-checked during the build and served from this site. <a href="runtime-manifest.json">Inspect the runtime manifest</a>.</p><p>Opening a page does not start Python. The first Run downloads a substantial runtime and package payload, so allow time on a slow connection. The browser may cache assets, but full offline operation is not provided. Each page has its own worker. A run starts with fresh user variables; imported modules remain loaded. Figures are cleared before each run. Uploaded CSV input, when selected, is written to <code>data.csv</code> for that run.</p><p>Stop terminates the worker and cancels execution. The next Run creates a fresh runtime. The initialization limit is two minutes and the execution limit is 45 seconds. An error leaves the code editable so you can fix it and run again. Tools → Restore example restores the published code; it does not clear your notes or uploaded CSV.</p><p>Your source and CSV are not sent to a Python server. The site has no analytics or account backend. Arbitrary Python can still fetch network resources permitted by your browser; this editor is a local learning tool, not an isolation boundary for untrusted code.</p><h3>Worked output and your actual output</h3><p>The build executes every published example to generate worked output and plots. These are labelled as worked examples. Actual output appears only after your browser runs the editor code. Numerical precision and formatting can vary with package versions and platform. Real timing values vary materially by machine and interpreter; build timings are never labelled as your browser’s measurements.</p><p>Mathematical notation uses locally hosted KaTeX 0.16.22. Python syntax stays literal. <a href="vendor/KATEX-LICENSE.txt">KaTeX licence</a>.</p><h3>Data provenance</h3><p>Each lesson labels its inputs: invented values, an authored model, a constructed population, seeded simulation, or measured at execution. A fixed seed reproduces a pseudo-random sequence; it does not turn simulated evidence into measurements of a real system. The capstone uses invented starter data until you explicitly upload a CSV. The importer checks structure, not provenance or independence.</p><h3>Local drafts and portable records</h3><p>Code, predictions, field notes, report fields, answer attempts and reading marks use localStorage under <code>sml:</code> keys. They stay on this browser and origin; clearing site data removes them. Storage errors are announced. Export progress and drafts from the course overview. Importing merges matching course records into this browser. Run exports retain the exact executed source, output, figures, input CSV when present and runtime versions. Editing code after a run does not alter the saved run record.</p><p>CSV uploads are held in memory for the current page and are not saved in progress exports. Preserve your original CSV; a completed run JSON includes the selected input. Run results are also held in memory until exported. Notes and report fields save separately. Reading marks indicate progress, not assessed understanding.</p><h3>Run locally</h3><pre>python -m pip install numpy==2.0.2 scipy==1.14.1 pandas==2.2.3 matplotlib==3.9.4\npython downloaded-investigation.py</pre><p>A downloaded Python file includes the authored inputs and analysis. For the capstone, put your selected CSV beside it as <code>data.csv</code>. Matplotlib figures can be displayed with <code>plt.show()</code> or saved with <code>plt.savefig("figure.svg")</code> in a local script.</p></section><section id="glossary"><h2>A small working glossary</h2><p>Terms are introduced in the course before the activities that need them. This is a reference for returning learners.</p><dl class="glossary">${Object.entries(glossary).map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl></section><section id="sources"><h2>Sources & acknowledgements</h2><p>The lessons use original examples and exercises. The learning structure draws on the author’s Assembly Lab; the Python editor and worker approach draws on Event Streaming Lab; experimental comparison and paired uncertainty draw on Benchmarking Lab. Code in this repository is Apache-2.0; original course prose is CC BY-NC 4.0. Third-party packages retain their own licences, included in their distributed wheels and runtime files.</p><ul class="source-list">${[...new Map(lessons.map(l=>[l.source[1],l.source])).values()].map(([title,url])=>`<li><a href="${url}">${title} ↗</a></li>`).join('')}</ul><p>These sources support the methods; they do not validate the course’s learning effectiveness. Automated execution and browser checks are recorded in the repository. The course has not yet been evaluated in a study with novice learners.</p><h3>Scope</h3><p>The core route covers experiment design, descriptive statistics, basic frequentist inference and reproducible reporting. Bayesian inference, hierarchical models, survival analysis, valid sequential testing, advanced missing-data methods and full regression diagnostics need further study. Seek domain-specific methods when your data collection or decision exceeds these examples.</p></section><a class="button primary" href="index.html#course">Back to the investigations ↗</a></main>`;
await fs.writeFile('dist/field-notes.html',shell('Field notes',notes));
execFileSync('python3',['scripts/prepare-runtime.py'],{stdio:'inherit'});
await fs.rm('.preview/scientific-method-lab',{recursive:true,force:true});
await fs.mkdir('.preview/scientific-method-lab',{recursive:true});
await fs.cp('dist','.preview/scientific-method-lab',{recursive:true});
console.log(`Built ${lessons.length} investigations, overview, field notes and a self-hosted stats runtime.`);
