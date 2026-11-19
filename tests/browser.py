# Copyright © 2026 Christopher Snow
"""Drive real Wasm executions, exports, recovery and responsive reading paths."""
import contextlib, json, math, os, re, subprocess, sys, time
from pathlib import Path
from runtime_startup import check_runtime_startup
from playwright.sync_api import sync_playwright
from quiet_checks import check_quiet_layout
from learner_edits import EDITS
ROOT=Path(__file__).resolve().parents[1]
COURSE=json.loads((ROOT/'src/course.json').read_text())
LESSONS=COURSE['lessons']
RESULTS=ROOT/'test-results';RESULTS.mkdir(exist_ok=True)
PORT=os.environ.get('SML_TEST_PORT','5174')
ORIGIN=f'http://127.0.0.1:{PORT}/'
BASE=ORIGIN+'scientific-method-lab/'

def visit(page,url):
    page.goto(url)
    page.wait_for_selector('html[data-ready="true"]')

def wait_result(page):
    page.wait_for_function("document.querySelector('#status').textContent.startsWith('Completed') || document.querySelector('#status').textContent.includes('error') || document.querySelector('#status').textContent.includes('could not')",timeout=150000)
    status=page.locator('#status').inner_text()
    assert status.startswith('Completed'),status+'\n'+page.locator('#error-summary').text_content()

def open_optional(page,identifier):
    details=page.locator('#'+identifier)
    if not details.evaluate('e=>e.open'):details.locator(':scope > summary').click()

def restore_example(page):
    open_optional(page,'editor-tools')
    page.locator('#restore').click()

def download(page,selector,path):
    if selector=='#download-code':open_optional(page,'editor-tools')
    if selector=='#export-run':open_optional(page,'run-tools')
    with page.expect_download() as info:page.locator(selector).click()
    info.value.save_as(path)

server=subprocess.Popen([sys.executable,'-m','http.server',PORT,'--bind','127.0.0.1','--directory',str(ROOT/'.preview')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    import urllib.request
    for _ in range(50):
        try:
            urllib.request.urlopen(BASE,timeout=1);break
        except Exception:time.sleep(.1)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=None if os.environ.get('CI') else os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
        # No third-party request should be needed for fonts, code, plots or runtime.
        context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(ORIGIN) or route.request.url.startswith(('data:','blob:')) else route.abort())
        page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        visit(page,BASE)
        assert page.locator('.lesson-row').count()==30
        assert page.locator('.lesson-row h4').first.evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=17
        assert page.locator('#start-course').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=16
        assert page.evaluate('getComputedStyle(document.documentElement).backgroundColor')=='rgb(249, 250, 252)'
        assert 'DM Sans' in page.evaluate('getComputedStyle(document.documentElement).fontFamily')
        assert 'Sora' in page.locator('h1').evaluate('(el)=>getComputedStyle(el).fontFamily')
        open_optional(page,'course-example')
        page.locator('#demo-means').click()
        assert page.locator('#evidence-demo').get_attribute('data-view')=='means'
        assert page.locator('#demo-means').get_attribute('aria-pressed')=='true'
        assert '50 ms' in page.locator('#demo-caption').inner_text()
        page.locator('#demo-runs').click()
        assert page.locator('#demo-runs').get_attribute('aria-pressed')=='true'
        page.screenshot(path=str(RESULTS/'overview-desktop.png'),full_page=True)
        page.locator('#search').fill('confidence')
        assert 0<page.locator('.lesson-row:visible').count()<30
        page.locator('#search').fill('no-such-topic-zzzz')
        assert page.locator('#search-empty').is_visible()
        page.locator('#search').fill('')
        page.evaluate("localStorage.setItem('sml:v1:read:make-a-claim-testable','true')")
        visit(page,BASE)
        assert page.locator('#start-label').inner_text()=='Continue to the next unread lesson'
        assert page.locator('#start-course').get_attribute('href')=='lessons/'+LESSONS[1]['slug']+'.html'
        # Follow the published example and literal edits on each lesson page.
        visit(page,BASE+'lessons/'+LESSONS[0]['slug']+'.html')
        assert not page.locator('#run-result').is_visible()
        assert not page.locator('#stop').is_visible()
        assert not page.locator('#export-run').is_visible()
        initial_code=page.locator('#code').input_value()
        page.locator('#code').press('Tab')
        assert page.evaluate('document.activeElement.id')=='run'
        assert page.locator('#code').input_value()==initial_code
        assert 'Ctrl+Enter' in page.locator('#editor-help').inner_text()
        assert page.locator('.outcome,.on-this-page,.mobile-course-bar').count()==0
        assert page.locator('.explanation p').first.evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=20
        assert page.locator('#code').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=16
        assert page.locator('#output').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=16
        assert page.locator('#code').evaluate('el=>getComputedStyle(el).lineHeight')==page.locator('.code-gutter').evaluate('el=>getComputedStyle(el).lineHeight')
        assert page.locator('#code-editor').evaluate("el=>el.classList.contains('is-highlighted')")
        assert page.locator('#code-highlight .token-keyword').count()>0
        assert len(LESSONS)==len(EDITS)
        worked=json.loads((ROOT/'.cache/worked.json').read_text())['lessons']
        for i,(lesson,variants) in enumerate(zip(LESSONS,EDITS,strict=True)):
            visit(page,BASE+'lessons/'+lesson['slug']+'.html')
            source=(ROOT/'python'/lesson['code']).read_text()
            editor=page.locator('#code')
            assert editor.input_value()==source
            assert page.locator('.experiment-prep').is_visible()
            assert page.locator('.observation',has_text='What to compare').is_visible()
            assert page.locator('.change-task').is_visible()
            assert not page.locator('.lab-workspace .worked').evaluate('el=>el.open')
            assert page.locator('#code-highlight code').text_content()==source+'\n'
            page.locator('#run').click();wait_result(page)
            actual=page.locator('#output').inner_text()
            assert len(actual)>10
            if i!=28:
                native=worked[lesson['slug']]['stdout'].strip()
                # Floating formatting across native and Wasm may differ at last digits.
                a_nums=re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',actual)
                b_nums=re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',native)
                assert len(a_nums)==len(b_nums),(lesson['slug'],actual,native)
                for a,b in zip(a_nums,b_nums):assert math.isclose(float(a),float(b),rel_tol=2e-4,abs_tol=2e-4),(lesson['slug'],a,b)
            native_record=worked[lesson['slug']]
            assert page.locator('#plots img').count()==len(native_record['figures'])
            assert page.locator('#plots picture source[media="(max-width:700px)"]').count()==len(native_record['figures'])
            if i==0:
                assert page.locator('#plots img').count()==1
                assert page.locator('.concept-figure').is_visible()
                assert page.locator('.explanation .katex').count()>=3
                assert page.locator('.lab-workspace .worked').count()==1
                assert page.locator('#plots a').get_attribute('href').startswith('blob:')
                page.screenshot(path=str(RESULTS/'lesson-desktop.png'),full_page=True)
            original_provenance=page.locator('#output-provenance').inner_text()
            assert 'published example' in original_provenance
            if i!=28:
                assert page.locator('#example-takeaway').is_visible()
            for replacements,expected in variants:
                edited=source
                for before,after in replacements:
                    assert edited.count(before)==1,(lesson['slug'],before)
                    edited=edited.replace(before,after)
                page.locator('#back-to-editor').press('Enter')
                assert page.evaluate('document.activeElement.id')=='code'
                editor.fill(edited)
                page.locator('#run').press('Enter');wait_result(page)
                revised=page.locator('#output').inner_text()
                assert revised!=actual,(lesson['slug'],revised)
                assert all(text in revised for text in expected),(lesson['slug'],revised,expected)
                assert 'edited code' in page.locator('#output-provenance').inner_text()
                assert not page.locator('#example-takeaway').is_visible()
                assert not page.locator('#run-error').is_visible()
            # Leave the persisted editor unchanged so later recovery starts from a known state.
            restore_example(page)
            print(f'PASS original and {len(variants)} documented edit(s) on route {i+1:02d}: {lesson["slug"]}',flush=True)
        # Check additional numerical relationships and plot labels on the lesson routes.
        visit(page,BASE+'lessons/'+LESSONS[0]['slug']+'.html')
        page.locator('#code').fill(initial_code.replace('minimum_reduction_pct = 20','minimum_reduction_pct = 10'))
        page.locator('#run').press('Enter');wait_result(page)
        assert 'Pairs meeting 10%: 5' in page.locator('#output').inner_text()
        assert 'Useful threshold (10%)' in page.locator('#plots img').evaluate('img=>fetch(img.src).then(r=>r.text())')
        visit(page,BASE+'lessons/'+LESSONS[16]['slug']+'.html')
        for level in ('0.95','0.99'):
            source=(ROOT/'python'/LESSONS[16]['code']).read_text().replace('confidence_level = 0.95','confidence_level = '+level)
            page.locator('#code').fill(source)
            page.locator('#run').click();wait_result(page)
            output=page.locator('#output').inner_text()
            assert f'Confidence level: {float(level):.0%}' in output
            width=float(re.search(r'Mean interval width \(ms\): ([\d.]+)',output)[1])
            coverage=float(re.search(r'Coverage fraction: ([\d.]+)',output)[1])
            if level=='0.95':first_width,first_coverage=width,coverage
            else:assert width>first_width and coverage>=first_coverage
        assert '99% interval for mean elapsed time (ms)' in page.locator('#plots img').evaluate('img=>fetch(img.src).then(r=>r.text())')
        page.set_viewport_size({'width':390,'height':844})
        visit(page,BASE+'lessons/'+LESSONS[28]['slug']+'.html')
        assert page.locator('#timing-setup').is_visible()
        assert page.locator('#run').get_attribute('aria-describedby')=='timing-setup'
        open_optional(page,'prediction-notes')
        page.locator('#prediction').fill('Eight paired blocks. A reduction of 10% would be useful.')
        timing=page.locator('#code').input_value().replace('block_count = 12','block_count = 8')
        page.locator('#code').fill(timing)
        page.locator('#run').click();wait_result(page)
        timing_output=page.locator('#output').inner_text()
        assert len(re.findall(r'^block-\d+,',timing_output,re.M))==8
        assert 'Paired blocks share one runtime' in timing_output
        # CSV input must replace starter data; exports preserve executed inputs.
        visit(page,BASE+'lessons/'+LESSONS[-1]['slug']+'.html')
        assert 'at least five' in page.locator('.upload-panel').inner_text()
        assert 'invented starter data' in page.locator('#input-kind').inner_text()
        csv='run_id,a_ms,b_ms\na,100,80\nb,105,85\nc,110,88\nd,95,79\ne,120,94\n'
        page.evaluate('''() => {
            const original=File.prototype.text;
            File.prototype.text=function(){
                return new Promise((resolve,reject)=>{
                    window.finishCsvRead=()=>{
                        File.prototype.text=original;
                        original.call(this).then(resolve,reject);
                    };
                });
            };
        }''')
        page.locator('#csv-upload').focus()
        page.locator('#csv-upload').set_input_files({'name':'paired-runs.csv','mimeType':'text/csv','buffer':csv.encode()})
        page.wait_for_function("document.querySelector('#csv-status').textContent.startsWith('Reading')")
        assert page.locator('#run').is_disabled()
        assert page.locator('#csv-upload').is_disabled()
        page.evaluate('window.finishCsvRead()')
        page.wait_for_function("document.querySelector('#input-kind').textContent.includes('paired-runs.csv')")
        assert page.evaluate('document.activeElement.id')=='csv-upload'
        source=page.locator('#code').input_value().replace('minimum_reduction_pct = 20','minimum_reduction_pct = 10')
        page.locator('#code').fill(source)
        page.locator('#run').click();wait_result(page)
        successful_output=page.locator('#output').inner_text()
        assert 'uploaded CSV' in successful_output and 'Pairs: 5' in successful_output
        assert '10% reduction requires A/B >= 1.111.' in successful_output
        assert 'paired-runs.csv' in page.locator('#output-provenance').inner_text()
        page.locator('#report-question').fill('Is a 10% reduction established for these independent runs?')
        page.locator('#report-source').fill('Browser test fixture, invented paired runs.')
        download(page,'#export-run',RESULTS/'run.json')
        record=json.loads((RESULTS/'run.json').read_text())
        assert record['input_csv']==csv and record['versions']['scipy']=='1.14.1'
        old_source=record['source']
        page.locator('#code').fill(old_source+'\n# changed after execution\n')
        assert 'changed' in page.locator('#output-provenance').inner_text()
        download(page,'#export-run',RESULTS/'run-after-edit.json')
        assert json.loads((RESULTS/'run-after-edit.json').read_text())['source']==old_source
        download(page,'#export-report',RESULTS/'investigation.md')
        report=(RESULTS/'investigation.md').read_text()
        assert 'changed after this run' in report and csv.strip() in report
        # Invalid CSV must fail visibly, then recover to starter input.
        restore_example(page)
        short_csv='run_id,a_ms,b_ms\na,100,80\nb,105,85\n'
        page.locator('#csv-upload').set_input_files({'name':'short.csv','mimeType':'text/csv','buffer':short_csv.encode()})
        page.wait_for_function("document.querySelector('#input-kind').textContent.includes('short.csv')")
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('reported an error')",timeout=90000)
        assert 'at least five paired runs' in page.locator('#error-summary').inner_text()
        assert 'short.csv' in page.locator('#error-input').inner_text()
        assert page.locator('#output').inner_text()==successful_output
        assert 'paired-runs.csv' in page.locator('#output-provenance').inner_text()
        download(page,'#export-run',RESULTS/'run-after-error.json')
        assert json.loads((RESULTS/'run-after-error.json').read_text())==record
        download(page,'#export-report',RESULTS/'investigation-after-error.md')
        report_after_error=(RESULTS/'investigation-after-error.md').read_text()
        assert 'paired-runs.csv' in report_after_error and csv.strip() in report_after_error
        report_output=report_after_error.split('### Actual output',1)[1]
        assert 'short.csv' not in report_after_error and 'at least five' not in report_output
        page.locator('#clear-csv').click();page.locator('#run').click();wait_result(page)
        assert 'INVENTED starter' in page.locator('#output').inner_text()
        assert 'invented starter data' in page.locator('#input-kind').inner_text()
        assert not page.locator('#run-error').is_visible()
        page.set_viewport_size({'width':1440,'height':1000})
        # Editor error and Stop must leave a viable next action.
        visit(page,BASE+'lessons/'+LESSONS[0]['slug']+'.html')
        page.locator('#code').fill("print('before failure')\nraise ValueError('deliberate test error')")
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('reported an error')",timeout=150000)
        assert 'deliberate test error' in page.locator('#error-summary').inner_text()
        assert not page.locator('#run-result').is_visible()
        assert not page.locator('#export-run').is_visible()
        open_optional(page,'error-details')
        assert 'before failure' in page.locator('#error-trace').inner_text()
        page.locator('#code').fill('while True: pass')
        page.locator('#run').press('Enter');page.wait_for_function("document.querySelector('#status').textContent==='Running your Python…'",timeout=30000)
        assert page.locator('#stop').is_visible()
        assert page.evaluate('document.activeElement.id')=='stop'
        page.locator('#stop').press('Enter');assert 'Stopped' in page.locator('#status').inner_text()
        assert page.evaluate('document.activeElement.id')=='run'
        restore_example(page)
        assert page.locator('#code-highlight code').text_content()==page.locator('#code').input_value()+'\n'
        page.locator('#run').click();wait_result(page)
        # Feedback needs an attempt and respects wrong/correct answers.
        page.locator('#quiz button').click();assert 'Choose an answer' in page.locator('#quiz-feedback').inner_text()
        page.locator('input[name=answer][value="1"]').check();page.locator('#quiz button').click()
        assert 'Reconsider' in page.locator('#quiz-feedback').inner_text()
        page.locator('input[name=answer][value="0"]').check();page.locator('#quiz button').click()
        assert 'reasoning fits' in page.locator('#quiz-feedback').inner_text()
        open_optional(page,'prediction-notes')
        page.locator('#prediction').fill('My saved prediction')
        open_optional(page,'lesson-notes')
        page.locator('#notes').fill('A note to preserve')
        page.locator('#code').fill(page.locator('#code').input_value()+'\n# saved draft')
        download(page,'#download-code',RESULTS/'downloaded.py')
        assert '# saved draft' in (RESULTS/'downloaded.py').read_text()
        page.reload();page.wait_for_selector('html[data-ready=true]')
        assert page.locator('#notes').input_value()=='A note to preserve'
        assert 'reasoning fits' in page.locator('#quiz-feedback').inner_text()
        assert page.locator('#prediction').input_value()=='My saved prediction'
        assert '# saved draft' in page.locator('#code').input_value()
        assert page.locator('#mark-read').is_checked()
        restore_example(page)
        assert page.locator('#code').input_value()==initial_code
        page.reload();page.wait_for_selector('html[data-ready=true]')
        open_optional(page,'editor-tools')
        page.locator('#recover-draft').click()
        assert '# saved draft' in page.locator('#code').input_value()
        assert page.evaluate('document.activeElement.id')=='code'
        page.locator('#code').evaluate('el=>{el.scrollTop=70;el.scrollLeft=30;el.dispatchEvent(new Event("scroll"))}')
        assert page.locator('#code').evaluate('el=>el.scrollLeft')==page.locator('#code-highlight').evaluate('el=>el.scrollLeft')
        # Theme persists, mobile has no page-wide overflow, all reading routes work.
        page.locator('#theme').click();assert page.locator('html').get_attribute('data-theme')=='dark'
        page.reload();assert page.locator('html').get_attribute('data-theme')=='dark'
        assert page.evaluate('getComputedStyle(document.documentElement).backgroundColor')=='rgb(16, 26, 43)'
        page.screenshot(path=str(RESULTS/'lesson-dark.png'),full_page=True)
        for width in [390,320]:
            page.set_viewport_size({'width':width,'height':844})
            for lesson in LESSONS:
                visit(page,BASE+'lessons/'+lesson['slug']+'.html')
                assert page.locator('h1').inner_text()==lesson['title']
                assert page.locator('.concept-figure').is_visible()
                clipped=page.locator('.concept-figure svg:visible').evaluate_all('''svgs=>svgs.flatMap(svg=>{const f=svg.getBoundingClientRect();return [...svg.querySelectorAll('text')].flatMap(t=>{const r=t.getBoundingClientRect();return r.left<f.left-1||r.right>f.right+1||r.top<f.top-1||r.bottom>f.bottom+1?[t.textContent]:[]})})''')
                assert not clipped,('diagram labels',width,lesson['slug'],clipped)
                assert not page.locator('.concept-figure .math-display:visible').evaluate_all('els=>els.some(e=>e.scrollWidth>e.clientWidth+1)'),('equation reflow',width,lesson['slug'])
                assert page.locator('.explanation p').first.evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=18
                assert page.locator('#code').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=16
                assert page.locator('#output').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')>=16
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,lesson['slug'])
                page.locator('#mark-read').check()
            visit(page,BASE)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),('overview',width)
            if width==390:page.screenshot(path=str(RESULTS/'overview-mobile-dark.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        page.locator('#theme').click()
        visit(page,BASE+'lessons/'+LESSONS[0]['slug']+'.html')
        page.locator('#course-menu-toggle').click()
        assert page.locator('#course-menu-toggle').get_attribute('aria-expanded')=='true'
        assert page.locator('#course-sidebar').is_visible()
        page.keyboard.press('Escape')
        assert page.locator('#course-menu-toggle').get_attribute('aria-expanded')=='false'
        assert not page.locator('#course-sidebar').is_visible()
        assert page.evaluate('document.activeElement.id')=='course-menu-toggle'
        page.screenshot(path=str(RESULTS/'lesson-mobile.png'),full_page=True)
        visit(page,BASE+'field-notes.html')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        # Larger browser text must reflow rather than force the whole page sideways.
        for width in [1440,390,320]:
            page.set_viewport_size({'width':width,'height':1000})
            for route in ['', 'lessons/'+LESSONS[0]['slug']+'.html', 'field-notes.html']:
                visit(page,BASE+route)
                page.evaluate("document.documentElement.style.fontSize='200%'")
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),('200% text',width,route)
            page.evaluate("document.documentElement.style.fontSize=''")
        page.set_viewport_size({'width':390,'height':844})
        # Portable progress can restore notes in a genuinely fresh browser context.
        visit(page,BASE)
        page.locator('.portable-progress summary').click()
        download(page,'#export-progress',RESULTS/'progress.json')
        assert page.locator('#progress-count').inner_text()=='30 / 30 read'
        fresh=browser.new_context(viewport={'width':1440,'height':1000})
        second=fresh.new_page();visit(second,BASE)
        assert second.locator('#progress-count').inner_text()=='0 / 30 read'
        second.locator('.portable-progress summary').click()
        second.locator('#import-progress').set_input_files(str(RESULTS/'progress.json'))
        second.wait_for_function("document.querySelector('#progress-status').textContent.startsWith('Imported')")
        assert second.locator('#progress-count').inner_text()=='30 / 30 read'
        visit(second,BASE+'lessons/'+LESSONS[0]['slug']+'.html')
        assert second.locator('#notes').input_value()=='A note to preserve'
        assert '# saved draft' in second.evaluate("localStorage.getItem('sml:v1:draft:make-a-claim-testable:restore-backup')")
        # Static reading does not need JS or any runtime assets.
        reading=browser.new_context(java_script_enabled=False,reduced_motion='reduce')
        static=reading.new_page();requests=[];static.on('request',lambda req:requests.append(req.url))
        for lesson in LESSONS:
            response=static.goto(BASE+'lessons/'+lesson['slug']+'.html')
            assert response.status==200
            assert static.locator('.explanation p').first.inner_text().startswith(re.split(r'[$`]',lesson['explain'][0])[0])
            assert static.locator('.concept-figure').is_visible()
            assert static.locator('.concept-figure figcaption').inner_text().strip()
            assert static.locator('.concept-figure .katex-error').count()==0
            static.locator('.worked summary').click()
            assert static.locator('.worked pre').inner_text().strip()
        assert not any('/engine/' in url for url in requests)
        assert errors==[],errors
        check_quiet_layout(browser,ROOT,BASE,LESSONS)
        check_runtime_startup(browser, BASE, LESSONS[0]['slug'])
        browser.close()
        print('PASS: 30 real Wasm experiments; native numerical agreement; CSV validation and provenance; feedback; error and Stop recovery; drafts; portable exports; mobile 390/320px; both themes; JavaScript-free reading.',flush=True)
finally:
    server.terminate();server.wait(timeout=10)
