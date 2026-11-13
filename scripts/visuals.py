# Copyright © 2026 Christopher Snow
"""Explanatory references from executed source or explicitly stated models.

Separate from learner execution, including the build machine's measured timings.
Every numerical reference has a visible provenance/interpretation caption.
"""
import html, re
import numpy as np

class Canvas:
 def __init__(self,w,alt,h=320):self.w=w;self.h=h;self.alt=alt;self.parts=[]
 def add(self,s):self.parts.append(s)
 def text(self,x,y,t,anchor='middle',cls=''):self.add(f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" class="{cls}">{html.escape(str(t))}</text>')
 def line(self,x,y,X,Y,cls='axis'):self.add(f'<path d="M{x:g},{y:g} L{X:g},{Y:g}" class="{cls}"/>')
 def arrow(self,x,y,X,Y,cls='curve'):
  self.line(x,y,X,Y,cls);a=np.arctan2(Y-y,X-x)
  for d in [-.45,.45]:self.line(X,Y,X-9*np.cos(a+d),Y-9*np.sin(a+d),cls)
 def rect(self,x,y,w,h,cls='tile'):self.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="3" class="{cls}"/>')
 def dot(self,x,y,r=4,cls='point'):self.add(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" class="{cls}"/>')
 def finish(self):return f'<svg class="concept-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{html.escape(self.alt,quote=True)}">'+''.join(self.parts)+'</svg>'

def chart(w,alt,xlim,ylim,xlabel,ylabel,curves=(),points=(),vlines=(),bands=(),hist=None):
 c=Canvas(w,alt);L,R,T,B=64,w-28,42,260
 X=lambda a:L+(a-xlim[0])/(xlim[1]-xlim[0])*(R-L)
 Y=lambda b:B-(b-ylim[0])/(ylim[1]-ylim[0])*(B-T)
 for a in np.linspace(*xlim,5):c.line(X(a),T,X(a),B,'grid');c.text(X(a),B+23,f'{a:.3g}')
 for b in np.linspace(*ylim,5):c.line(L,Y(b),R,Y(b),'grid');c.text(L-9,Y(b)+5,f'{b:.3g}','end')
 c.line(L,B,R,B);c.line(L,T,L,B);c.text(L,27,ylabel,'start');c.text((L+R)/2,309,xlabel)
 if ylim[0]<0<ylim[1]:c.line(L,Y(0),R,Y(0))
 for lo,hi in bands:c.rect(X(lo),T,X(hi)-X(lo),B-T,'band')
 if hist:
  counts,edges,extreme=hist
  for n,a,b in zip(counts,edges,edges[1:]):c.rect(X(a),Y(n),max(1,X(b)-X(a)-1),Y(0)-Y(n),'hist extreme' if extreme(a,b) else 'hist')
 for k,(xs,ys) in enumerate(curves):
  c.add('<path class="curve curve-'+str(k)+'" d="'+' '.join(('M' if j==0 else 'L')+f'{X(a):.2f},{Y(b):.2f}' for j,(a,b) in enumerate(zip(xs,ys)))+'"/>')
 for a,b,k in points:c.dot(X(a),Y(b),5,'point point-'+str(k))
 for a in vlines:c.line(X(a),T,X(a),B,'reference')
 return c.finish()

def strip(w,alt,rows,domain,xlabel,vertical=()):
 # Rows carry (label, low, high, centre, class); empty intervals can be points.
 c=Canvas(w,alt,h=110+len(rows)*64);L,R=46,w-30;X=lambda a:L+(a-domain[0])/(domain[1]-domain[0])*(R-L)
 for a in vertical:c.line(X(a),28,X(a),c.h-62,'reference')
 for i,(label,lo,hi,mid,k) in enumerate(rows):
  y=56+i*64;c.text(L,y-17,label,'start');c.line(X(lo),y,X(hi),y,'interval curve-'+str(k));c.line(X(lo),y-6,X(lo),y+6,'curve curve-'+str(k));c.line(X(hi),y-6,X(hi),y+6,'curve curve-'+str(k));c.dot(X(mid),y,5,'point point-'+str(k))
 B=c.h-62;c.line(L,B,R,B)
 for a in ([1,1.1,1.25,1.4] if xlabel=='A/B time ratio' else np.linspace(*domain,4)):c.line(X(a),B,X(a),B+6);c.text(X(a),B+28,f'{a:.3g}')
 c.text((L+R)/2,c.h-12,xlabel);return c.finish()

def picture(index,w,ns,stdout):
 c=Canvas(w,'');caption='';title='See the reasoning';formula=None;legend=[]
 if index==1:
  title='Make “faster” measurable';caption='Illustrative decision rule, not measured data: against a 100 ms reference, a 20% reduction requires a time of at most 80 ms. The workload and correct answers must stay the same.';formula=r'\mathrm{reduction}=100\,\frac{A-B}{A}\%'
  L,R=34,w-30;scale=(R-L)/100
  for y,val,label,k in [(84,100,'A · 100 ms reference',0),(188,80,'B · at most 80 ms',1)]:c.text(L,y-20,label,'start');c.rect(L,y,val*scale,40,'tile tile-'+str(k))
  c.text(w/2,285,'same job · same correct result')
 elif index in (2,5,10,14,20,24,27):
  title={2:'Find where predictions diverge',5:'Compare observation with prediction',10:'Look for an interaction',14:'Order carries information',20:'More evidence, same effect',24:'One test versus a search',27:'Fit the shape, not just the slope'}[index]
  if index==2:
   caption='Authored prediction models, not measurements. The solid repeat-key model predicts no saving with unique keys; the dashed fixed-setup model still predicts 15 ms.';curves=[(ns['repeat_fraction'],ns['repeat_model']),(ns['repeat_fraction'],ns['setup_model'])];domain=(0,1);yrange=(0,45);xl='Repeat fraction';yl='Saving (ms)';legend=['Repeated-key model','Fixed-setup model']
  elif index==5:
   caption='Invented observations and a reference model. The gap is observed minus predicted saving; it remains positive even when no keys repeat. An omitted cause or measurement offset needs a new discriminating test.';curves=[(ns['repeat_fraction'],ns['prediction']),(ns['repeat_fraction'],ns['observed'])];domain=(0,1);yrange=(0,60);xl='Repeat fraction';yl='Saving (ms)';legend=['Model prediction','Invented observation']
  elif index==10:
   caption='Four invented cells. Switching the cache on adds 10 ms for unique keys but saves 40 ms for repeated keys. These lines describe an interaction; they do not estimate uncertainty.';curves=[([0,1],[100,110]),([0,1],[100,60])];domain=(0,1);yrange=(50,120);xl='Cache: 0 off, 1 on';yl='Time (ms)';legend=['Unique keys','Repeated keys'];formula=r'(-40)-(+10)=-50\;\mathrm{ms}'
  elif index==14:
   original=ns['elapsed'];order=[0,11,1,10,2,9,3,8,4,7,5,6];curves=[(np.arange(1,13),original),(np.arange(1,13),original[order])];domain=(1,12);yrange=(90,160);xl='Position in sequence';yl='Time (ms)';legend=['Published order','Same values, rearranged'];caption='The same twelve invented values have the same histogram in both orders. Their time patterns differ. Rearranging here is a teaching illustration, not a correction to historical observations.'
  elif index==20:
   data=re.findall(r'n=\s*(\d+) simulated detection fraction=([\d.]+)',stdout);xx,yy=zip(*[(int(a),float(b)) for a,b in data]);curves=[(xx,yy)];domain=(0,100);yrange=(0,1);xl='Independent sample size';yl='Detection fraction';caption='Actual seeded reference output: 600 normal experiments at each tested count, a 3 ms effect, SD 10 ms, and a two-sided t test with p < 0.05. Lines join the three tested counts; other counts were not simulated here.'
  elif index==24:
   xx=np.arange(1,51);yy=1-.95**xx;curves=[(xx,yy),(xx,np.full_like(xx,.05,dtype=float))];domain=(0,50);yrange=(0,1);xl='Number of tests';yl='Probability';legend=['Unadjusted: independent tests','Bonferroni error bound'];caption='Reference formula under independent true-null tests with a 0.05 false-positive rate each. With 20 tests, the chance of at least one false rejection is about 64%. The dashed Bonferroni bound needs valid individual tests, but not independence.';formula=r'P(\text{any false rejection})=1-(1-0.05)^m'
  else:
   curves=[(ns['size'],ns['elapsed']),(ns['size'],ns['prediction'])];domain=(0,10);yrange=(-30,240);xl='Input size';yl='Time (ms)';legend=['Authored quadratic response','Fitted straight line'];caption='The authored response is quadratic. The fitted line follows the overall rise while missing curvature. The residual plot in the experiment exposes the remaining pattern; a fitted slope alone cannot establish model adequacy.'
  svg=chart(w,caption,domain,yrange,xl,yl,curves=curves,points=[(a,b,k) for k,(xs,ys) in enumerate(curves) for a,b in zip(xs,ys)] if index in (2,5,10,20,27) else [])
  return dict(svg=svg,caption=caption,title=title,formula=formula,legend=legend)
 elif index==3:
  caption='An illustration of the invented design: cache condition and workload change together. The observed difference combines both changes; normalising a column does not automatically identify the cache effect.'
  return dict(title='Two inputs changed',caption=caption,kind='comparison',cards=[['Control','Cache off','1,000 requests'],['Treatment','Cache on','500 requests']],conclusion='Elapsed time depends on the whole comparison.')
 elif index==4:
  caption='Authored rounding model. Reference durations 11–14 ms all display as 10 ms; 21–22 ms display as 20 ms. Repeating a rounded reading does not recover the discarded resolution.'
  X=lambda x:38+(x-10)/14*(w-76)
  c.text(26,46,'Reference (ms)','start');c.text(26,224,'Displayed (ms)','start')
  for a,b in zip(ns['reference_ms'],ns['displayed']):c.line(X(a),94,X(b),182,'connector');c.dot(X(a),94,5)
  for a in [10,14,18,22,24]:c.text(X(a),78,str(a))
  for b in sorted(set(ns['displayed'])):c.dot(X(b),182,7,'point point-1');c.text(X(b),259,str(int(b)))
 elif index==6:
  caption='Invented before/after values. Treated: 120 → 90 ms (−30). Control: 100 → 80 ms (−20). The adjusted difference is −10 ms, conditional on the control representing the untreated trend.';legend=['Treated service','Control service'];formula=r'(-30)-(-20)=-10\;\mathrm{ms}'
  return dict(title='Subtract the shared change',caption=caption,formula=formula,legend=legend,svg=chart(w,caption,(0,1),(60,140),'0 before, 1 after','Time (ms)',curves=[([0,1],[120,90]),([0,1],[100,80])],points=[(0,120,0),(1,90,0),(0,100,1),(1,80,1)]))
 elif index==7:
  caption='The actual seeded reference schedule: six A and six B positions. Balanced counts do not guarantee equal average positions. The seed reproduces this schedule, not a proof of balance or generalisation.'
  cols=6 if w>400 else 4;gap=8;cw=(w-48-gap*(cols-1))/cols
  for j,label in enumerate(ns['labels']):
   x=24+(j%cols)*(cw+gap);y=50+(j//cols)*88;c.text(x+cw/2,y-10,str(j+1));c.rect(x,y,cw,44,'tile tile-'+str(label=='B' and 1 or 0));c.text(x+cw/2,y+29,label)
  c.h=60+int(np.ceil(12/cols))*88
 elif index==8:
  frame=ns['pairs'];rows=[(row.machine,row.b_ms,row.a_ms,row.b_ms,0) for row in frame.itertuples()];caption='Five invented matched machines. Each horizontal segment connects B and A on the same machine. Pairing retains the comparison within a block; these lines are not confidence intervals.'
  return dict(title='Keep the pair together',caption=caption,svg=strip(w,caption,rows,(50,220),'Elapsed time (ms)'),formula=r'd_i=B_i-A_i')
 elif index==9:
  title='Count sessions, not just readings';caption='Structure of the seeded model: six independent session offsets, with twenty readings per session. The dots are subsamples. More readings within a session do not create more independent sessions.';cols=3;cw=(w-56)/3
  for j in range(6):
   x=20+j%3*(cw+8);y=22+j//3*144;c.rect(x,y,cw,125);c.text(x+cw/2,y+27,'S'+str(j+1))
   for q in range(20):c.dot(x+12+(q%5)*(cw-24)/4,y+49+(q//5)*17,3)
  c.h=340;c.text(w/2,329,'20 readings per session')
 elif index==11:
  caption='Invented observations: both means are 50 ms. Repeated marks are separated vertically only to make all five values visible. The dashed mean hides the very different distribution of waits.';L,R=46,w-28;X=lambda a:L+a/220*(R-L)
  c.line(X(50),48,X(50),235,'reference')
  for vals,y,label,k in [(ns['a'],95,'Service A',0),(ns['b'],195,'Service B',1)]:
   c.text(L,y-34,label,'start')
   for j,a in enumerate(vals):c.dot(X(a),y+(j-2)*9,5,'point point-'+str(k))
  c.line(L,250,R,250)
  for a in [0,50,100,150,200]:c.text(X(a),280,str(a))
  c.text(w/2,311,'Response time (ms)')
 elif index==12:
  caption='Reference normal model with population mean 100 ms and SD 15 ms. The long line is ±1 SD for an individual observation; the short line is ±1 sampling SD of a mean of 100 independent observations. Neither line is a 95% interval.';formula=r'\widehat{\mathrm{SE}}(\bar x)=\frac{s}{\sqrt n}'
  return dict(title='Spread of what?',caption=caption,formula=formula,svg=strip(w,caption,[('Individual · SD 15',85,115,100,0),('Mean of 100 · SD 1.5',98.5,101.5,100,1)],(70,130),'Time (ms)',vertical=[100]))
 elif index==13:
  mobile=int(np.sum(ns['random_sample']==140));caption=f'Constructed population: 800 desktop requests at 40 ms and 200 mobile requests at 140 ms. The seeded random sample includes {mobile} mobile requests out of 100; a larger desktop-only sample would still exclude that group.';legend=['Desktop','Mobile']
  for j,(label,pct) in enumerate([('Population',80),('Desktop-only sample',100),('Random sample',100-mobile)]):
   y=55+j*86;L=24;span=w-48;c.text(L,y-14,label,'start');c.rect(L,y,span*pct/100,38);c.text(L+span*pct/200,y+26,str(pct)+'%')
   if pct<100:c.rect(L+span*pct/100,y,span*(100-pct)/100,38,'tile tile-1');c.text(L+span*(pct+(100-pct)/2)/100,y+26,str(100-pct)+'%')
 elif index==15:
  data=ns['data'];caption=f'Invented requests: four recorded successes and two timeouts. The recorded-time mean is {data.elapsed_ms.mean():g} ms, conditional on a time being available. A timeout is not a zero or an exactly 200 ms observation.'
  cols=3 if w>400 else 2;cw=(w-48-(cols-1)*10)/cols
  for j,row in enumerate(data.itertuples()):
   x=24+j%cols*(cw+10);y=28+j//cols*92;c.rect(x,y,cw,72,'tile tile-'+str(row.status=='timeout' and 1 or 0));c.text(x+cw/2,y+27,'Request '+str(row.request));c.text(x+cw/2,y+55,'timeout' if row.status=='timeout' else str(int(row.elapsed_ms))+' ms')
  c.h=int(np.ceil(6/cols))*92+50
 elif index==16:
  x=ns['x'];lo,hi=ns['low'],ns['high'];caption=f'Invented sample: range {x.min():g}–{x.max():g} ms; 95% t interval for the population mean {lo:.2f}–{hi:.2f} ms. The two lines describe different quantities. This interval relies on the sampling and distribution assumptions in the lesson.'
  return dict(title='A range for which quantity?',caption=caption,formula=r'\bar x\;\pm\;t_{0.975,n-1}\frac{s}{\sqrt n}',svg=strip(w,caption,[('Observed range',x.min(),x.max(),x.mean(),0),('95% interval for mean',lo,hi,x.mean(),1)],(95,106),'Elapsed time (ms)'))
 elif index==17:
  lo,hi,means,covered=[ns[k] for k in ['low','high','means','covered']]
  hits=np.flatnonzero(covered)[:3];misses=np.flatnonzero(~covered)[:3];selected=np.r_[hits,misses]
  title='What counts as covering?'
  caption=f'{len(hits)} covering intervals and {len(misses)} misses selected from the seeded reference to illustrate the definition. This selected diagram must not be used to estimate frequency. Across all 500 independent normal-sample intervals, coverage was {covered.mean():.1%}. The population mean stays fixed at 100 ms.'
  c.h=420;L,R,T,B=58,w-28,48,340
  domain=(min(80,np.floor(lo[selected].min()/5)*5),max(120,np.ceil(hi[selected].max()/5)*5))
  X=lambda a:L+(a-domain[0])/(domain[1]-domain[0])*(R-L)
  c.line(X(100),T-12,X(100),B+12,'reference');c.text(12,24,'Run','start')
  for j,i in enumerate(selected):
   y=T+j*(B-T)/max(1,len(selected)-1);c.text(L-15,y+6,str(i+1),'end');c.line(X(lo[i]),y,X(hi[i]),y,'interval' if covered[i] else 'interval curve-1')
   if not covered[i]:c.line(X(means[i])-4,y-4,X(means[i])+4,y+4,'cross');c.line(X(means[i])-4,y+4,X(means[i])+4,y-4,'cross')
  for a in np.linspace(*domain,5):c.text(X(a),383,f'{a:.3g}')
  c.text(w/2,412,'Interval for mean (ms)')
 elif index==18:
  diffs=ns['difference_ms'];indices=[0,0,2,3,4,7,7,1];caption='One illustrated resample of the eight invented independent run differences. Sampling with replacement repeats run IDs and keeps the resample size at eight. Repeated copies are not new experiments. The Python below generates 4,000 resamples.'
  return dict(title='Resample whole run differences',kind='resample',caption=caption,original=[dict(id=i+1,value=int(v)) for i,v in enumerate(diffs)],resample=[dict(id=i+1,value=int(diffs[i])) for i in indices])
 elif index==19:
  lo,hi,mid=ns['low'],ns['high'],ns['ratio'];caption=f'Invented paired reference: estimate {mid:.3f}, with a 95% t interval {lo:.3f}–{hi:.3f} for the geometric mean A/B ratio. The interval is above 1 but crosses the useful threshold 1.25. Positive benefit and established minimum benefit are different claims.';formula=r'20\%\text{ less time}\;\Longleftrightarrow\;A/B\ge1.25'
  return dict(title='Benefit versus useful benefit',caption=caption,formula=formula,svg=strip(w,caption,[('95% A/B ratio interval',lo,hi,mid,0)],(.95,1.4),'A/B time ratio',vertical=[1,1.25]))
 elif index==21:
  values=ns['null_means'];bound=abs(ns['observed_mean']);edges=np.unique(np.r_[np.linspace(-9,9,31),-bound,bound]);counts,edges=np.histogram(values,bins=edges);caption=f'Actual seeded null-model reference: {len(values):,} means from independent normal differences centred at zero. Amber tails are at least as far from zero as ±{bound:g} ms. Their fraction estimates a probability under this model, not a probability the null is true.'
  return dict(title='Count both extreme tails',caption=caption,svg=chart(w,caption,(-9,9),(0,int(counts.max()*1.15)),'Mean difference (ms)','Simulated experiments',vlines=[-bound,bound],hist=(counts,edges,lambda a,b:b<=-bound+1e-9 or a>=bound-1e-9)),legend=['Null-model means','At least as extreme'])
 elif index==22:
  caption='Eight invented pairs generate 2⁸ = 256 within-pair label patterns under the stated null and assignment assumptions. This illustration flips the first pair only. No outcome is exchanged with a different block.'
  return dict(title='Swap labels inside the block',kind='comparison',caption=caption,formula=r'2^8=256',cards=[['Original labels',f'A₁ = {ns["a"][0]} · B₁ = {ns["b"][0]}',f'A₂ = {ns["a"][1]} · B₂ = {ns["b"][1]}'],['Flip first pair',f'A₁ = {ns["b"][0]} · B₁ = {ns["a"][0]}',f'A₂ = {ns["a"][1]} · B₂ = {ns["b"][1]}']],conclusion='Each row remains the same block. Times in ms.')
 elif index==23:
  data=re.findall(r'n=\s*(\d+) mean=([-\d.]+) ms p=([\deE+.-]+)',stdout);caption='Actual seeded reference output. The generator always uses a 0.2 ms mean effect and SD 1 ms. Estimated effects fluctuate; p-values also reflect sampling sensitivity. A small p-value does not establish a useful effect.'
  return dict(title='Magnitude and p-value are separate',kind='table',headings=['Sample size','Mean (ms)','p-value'],rows=data,caption=caption)
 elif index==25:
  return dict(title='The next look reuses earlier data',kind='prefixes',looks=ns['looks'],caption='These five tests use increasing prefixes of the same simulated experiment: 20, 40, 60, 80 and 100 observations. They share data and are dependent. This is the naive stopping rule being examined, not a valid sequential-testing design.')
 elif index==26:
  caption='Causal structure of the authored generator: background load affects queue length and response time. There is no queue → response path in this model. Their association alone does not identify the effect of intervening on the queue.';title='One common cause, two outputs';cx=w/2
  c.rect(cx-108,28,216,54);c.text(cx,62,'Background load');left=80;right=w-80
  c.arrow(cx-40,89,left,192);c.arrow(cx+40,89,right,192)
  c.rect(left-64,204,128,52);c.text(left,237,'Queue');c.rect(right-68,204,136,52);c.text(right,237,'Response');c.h=292
 elif index==28:
  group=ns['data'].groupby('environment').reduction_pct.mean();rows=[(str(label),min(0,v),max(0,v),v,0 if v>0 else 1) for label,v in group.items()];caption='Four invented pairs per environment. These are arithmetic means of within-pair percentage reductions. Opposite signs reveal a boundary hidden by pooling; no uncertainty or generalisation claim is established by this small table.'
  return dict(title='State where the effect holds',caption=caption,svg=strip(w,caption,rows,(-15,30),'Mean time reduction (%)',vertical=[0]))
 elif index==29:
  return dict(title='Name the timed boundary',kind='boundary',caption='The reference diagram describes the published procedure, not timing results. Construction and query generation are outside the timer; both lookup methods must return the same hit count. All twelve blocks share one runtime and device, so independence is not established.')
 elif index==30:
  return dict(title='Keep the claim attached to its evidence',kind='evidence',caption='A report preserves the plan, source data, exact executed code, analysis and limits. Upload validation checks CSV structure, not the independence or provenance needed for inference. Invented starter values are not evidence of a real benefit.')
 else:raise ValueError(f'No visual for lesson {index}')
 c.alt=caption;return dict(title=title,caption=caption,formula=formula,legend=legend,svg=c.finish())

def illustration(lesson,namespace,stdout):
 index=int(lesson['code'].split('-')[0]);wide=picture(index,640,namespace,stdout);narrow=picture(index,320,namespace,stdout)
 if 'svg' not in wide:return wide
 narrow_formulas={19:r'\begin{gathered}20\%\text{ less time}\\A/B\ge1.25\end{gathered}',24:r'\begin{gathered}P(\text{any false rejection})\\=1-(1-0.05)^m\end{gathered}'}
 return {**{k:v for k,v in wide.items() if k!='svg'},'narrow_formula':narrow_formulas.get(index),'kind':'svg','wide':wide['svg'],'narrow':narrow['svg']}
