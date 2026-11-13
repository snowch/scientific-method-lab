// Copyright © 2026 Christopher Snow
importScripts('./engine/pyodide.js');
const figureHelper = null;
let ready;
async function initialize(){
 const py=await loadPyodide({indexURL:'./engine/'});
 await py.loadPackage(['numpy','scipy','pandas','matplotlib']);
 await py.runPythonAsync(`import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.spines.top':False,'axes.spines.right':False,'figure.figsize':(6.2,4.2),'figure.facecolor':'white','axes.facecolor':'white','axes.labelcolor':'#233b35','text.color':'#233b35','savefig.bbox':'tight'})`);
 await py.runPythonAsync(figureHelper);
 return py;
}
self.onmessage=async({data})=>{
 try{
  ready ||= initialize().catch(error=>{ready=null;throw error});
  const py=await ready;
  if(py.FS.analyzePath('/home/pyodide/data.csv').exists)py.FS.unlink('/home/pyodide/data.csv');
  if(data.csv!==null)py.FS.writeFile('/home/pyodide/data.csv',data.csv);
  py.globals.set('_source',data.source);
  postMessage({type:'running'});
  const value=await py.runPythonAsync(`import io, json, platform, traceback, base64
import numpy, scipy, pandas, matplotlib
from contextlib import redirect_stdout, redirect_stderr
plt.close('all')
_buffer = io.StringIO()
_namespace = {'__name__': '__main__'}
_failure = None
with redirect_stdout(_buffer), redirect_stderr(_buffer):
    try:
        exec(compile(_source, 'investigation.py', 'exec'), _namespace)
    except Exception:
        _failure = traceback.format_exc()
_wide, _narrow = capture_figures()
_images = [base64.b64encode(s.encode()).decode() for s in _wide]
_narrow_images = [base64.b64encode(s.encode()).decode() for s in _narrow]
plt.close('all')
json.dumps({'stdout': _buffer.getvalue(), 'error': _failure, 'figures': _images, 'figures_narrow': _narrow_images, 'versions': {'python': platform.python_version(), 'pyodide': '0.27.7', 'numpy': numpy.__version__, 'scipy': scipy.__version__, 'pandas': pandas.__version__, 'matplotlib': matplotlib.__version__}})`);
  postMessage({type:'result',value:JSON.parse(value)});
 }catch(error){postMessage({type:'error',message:String(error.message||error)})}
};
