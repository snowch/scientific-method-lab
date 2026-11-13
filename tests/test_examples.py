# Copyright © 2026 Christopher Snow
"""Check the published experiments, statistical examples and CSV failure paths."""
import contextlib, importlib.util, io, json, os, tempfile, unittest
from pathlib import Path
import numpy as np
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('execute',ROOT/'scripts/execute.py')
execute=importlib.util.module_from_spec(spec);spec.loader.exec_module(execute)
COURSE=json.loads((ROOT/'src/course.json').read_text())
LESSONS=COURSE['lessons']
class CourseTests(unittest.TestCase):
    def test_bootstrap_illustration_preserves_run_units(self):
        record=execute.execute(LESSONS[17])['illustration']
        original={r['id']:r['value'] for r in record['original']}
        resample=record['resample']
        self.assertEqual(len(resample),len(original))
        self.assertLess(len(set(r['id'] for r in resample)),len(resample))
        for row in resample:self.assertEqual(row['value'],original[row['id']])
    def test_responsive_plot_capture_keeps_executed_values(self):
        import matplotlib.pyplot as plt
        from figure_style import capture_figures
        plt.close('all')
        figure,ax=plt.subplots();line,=ax.plot([0,1,2],[4,1,7],label='Executed series')
        ax.set_xlabel('Measured input');ax.set_ylabel('Outcome');ax.legend()
        wide,narrow=capture_figures()
        self.assertEqual(len(wide),1);self.assertEqual(len(narrow),1)
        self.assertNotEqual(wide[0],narrow[0])
        np.testing.assert_array_equal(line.get_xdata(),[0,1,2])
        np.testing.assert_array_equal(line.get_ydata(),[4,1,7])
        plt.close('all')

    def test_phone_colour_scale_preserves_scatter_data(self):
        import matplotlib.pyplot as plt
        from figure_style import capture_figures
        plt.close('all')
        figure,ax=plt.subplots()
        points=ax.scatter([1,3],[2,4],c=[.1,.8],vmin=0,vmax=1)
        figure.colorbar(points,ax=ax,label='Background load')
        offsets=points.get_offsets().copy();colours=points.get_array().copy()
        capture_figures()
        np.testing.assert_array_equal(points.get_offsets(),offsets)
        np.testing.assert_array_equal(points.get_array(),colours)
        self.assertEqual((points.norm.vmin,points.norm.vmax),(0,1))
        self.assertEqual(points.colorbar.orientation,'horizontal')
        plt.close('all')
    def test_every_published_example_executes(self):
        for lesson in LESSONS:
            with self.subTest(lesson=lesson['slug']):
                record=execute.execute(lesson)
                self.assertTrue(record['stdout'].strip())
                self.assertNotIn('Traceback',record['stdout'])
                self.assertNotIn('RuntimeWarning',record['stdout'])
    def test_paired_ratio_has_correct_direction_and_threshold(self):
        logs=np.log(np.array([120,108,132,114,126])/100)
        estimate=np.exp(logs.mean())
        low,high=np.exp(stats.t.interval(.95,4,loc=logs.mean(),scale=stats.sem(logs)))
        self.assertAlmostEqual(estimate,1.196989,places=5)
        self.assertGreater(low,1)
        self.assertLess(low,1.25)
        self.assertGreater(high,1.25)
        self.assertAlmostEqual(100*(1-1/1.2),16.6666667,places=5)
    def test_permutation_preserves_pairs(self):
        code=(ROOT/'python'/LESSONS[21]['code']).read_text()
        namespace={}
        with contextlib.redirect_stdout(io.StringIO()):exec(code,namespace)
        self.assertEqual(len(namespace['test'].null_distribution),256)
        self.assertEqual(namespace['test'].pvalue,2/256)
    def test_examples_and_fresh_tasks_are_complete(self):
        self.assertEqual(len(LESSONS),30)
        self.assertEqual(len({l['slug'] for l in LESSONS}),30)
        for l in LESSONS:
            self.assertIn(l['minutes'],range(5,10))
            self.assertEqual(len(l['options']),3)
            self.assertIn(l['correct'],range(3))
            self.assertGreaterEqual(len(l['explain']),3)
            self.assertEqual(len(l['hints']),2)
            self.assertTrue(l['goal'] and l['limit'] and l['kind'])
        for m in range(6):self.assertEqual(sum(l['module']==m for l in LESSONS),5)
    def run_capstone(self,text):
        prior=os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as directory:
                os.chdir(directory)
                Path('data.csv').write_text(text)
                return execute.execute(LESSONS[-1])
        finally:os.chdir(prior)
    def test_csv_import_uses_actual_input(self):
        data='run_id,a_ms,b_ms\na,100,80\nb,105,85\nc,110,88\nd,95,79\ne,120,94\n'
        result=self.run_capstone(data)
        self.assertIn('uploaded CSV',result['stdout'])
        self.assertIn('Pairs: 5',result['stdout'])
        self.assertNotIn('INVENTED starter',result['stdout'])
    def test_csv_rejects_bad_structure_and_values(self):
        samples=[
            'a,b\n1,2\n',
            'run_id,a_ms,b_ms\na,100,80\na,105,85\nc,110,88\nd,95,79\ne,120,94\n',
            'run_id,a_ms,b_ms\na,-1,80\nb,105,85\nc,110,88\nd,95,79\ne,120,94\n',
            'run_id,a_ms,b_ms\na,inf,80\nb,105,85\nc,110,88\nd,95,79\ne,120,94\n']
        for sample in samples:
            with self.subTest(sample=sample):
                with self.assertRaises((AssertionError,ValueError)):self.run_capstone(sample)
if __name__=='__main__':unittest.main()
