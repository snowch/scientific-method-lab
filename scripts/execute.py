# Copyright © 2026 Christopher Snow
"""Execute the exact learner examples and produce honest worked records."""
import contextlib, io, json, platform, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy, scipy, pandas
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from visuals import illustration
from figure_style import capture_figures
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.spines.top':False,
    'axes.spines.right':False,'figure.figsize':(6.2,4.2),'figure.facecolor':'white',
    'axes.facecolor':'white','axes.labelcolor':'#233b35','text.color':'#233b35',
    'svg.hashsalt':'scientific-method-lab','savefig.bbox':'tight'})

def execute(lesson):
    code = (ROOT/'python'/lesson['code']).read_text()
    namespace = {'__name__':'__main__'}
    output = io.StringIO()
    plt.close('all')
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        exec(compile(code, lesson['code'], 'exec'), namespace)
    images,narrow=capture_figures()
    plt.close('all')
    return dict(stdout=output.getvalue(),figures=images,figures_narrow=narrow,illustration=illustration(lesson,namespace,output.getvalue()))

if __name__=='__main__':
    course=json.loads((ROOT/'src/course.json').read_text())
    result={l['slug']:execute(l) for l in course['lessons']}
    record={'environment':{'python':platform.python_version(),'numpy':numpy.__version__,
        'scipy':scipy.__version__,'pandas':pandas.__version__,'matplotlib':matplotlib.__version__,
        'kind':'Executed during the site build; timing results describe the build machine, not your browser.'},'lessons':result}
    destination=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'.cache/worked.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(record))
    print(f'Executed {len(result)} published Python examples; generated {sum(len(r["figures"]) for r in result.values())} figures.')
