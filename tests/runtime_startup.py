"""Browser coverage for preparation and cancellation using the published worker."""
from urllib.parse import urljoin


def check_runtime_startup(browser, base, lesson):
    # These transport faults target the worker's direct network requests.
    # Service-worker cache/update faults have separate end-to-end coverage.
    context = browser.new_context(service_workers="block")
    context.add_init_script("""
      window.workerMessages = [];
      window.workerStarts = 0;
      const OriginalWorker = Worker;
      window.Worker = class extends OriginalWorker {
        constructor(...args) { super(...args); ++workerStarts; }
        postMessage(message, ...args) {
          workerMessages.push(message.type);
          super.postMessage(message, ...args);
        }
      };
      // Test browsers without requestIdleCallback or first-party storage.
      window.requestIdleCallback = undefined;
      Object.defineProperty(navigator, "connection", {value: {effectiveType:"4g",downlink:10}});
      Object.defineProperty(navigator, "deviceMemory", {value:8});
      Object.defineProperty(window, 'localStorage', {
        get() { throw new DOMException('Denied by test', 'SecurityError'); }
      });
    """)
    stalled = []
    wasm = '**/engine/*/pyodide.asm.wasm'
    context.route(wasm, lambda route: stalled.append(route))
    page = context.new_page()
    url = urljoin(base, f'lessons/{lesson}.html')
    try:
        page.goto(base)
        page.wait_for_selector('html[data-ready="true"]')
        assert page.evaluate('workerStarts') == 0

        page.goto(url)
        page.wait_for_function("workerMessages.includes('prepare')")
        assert page.locator('#run-result').is_hidden()
        assert page.locator('#stop').is_hidden()
        page.locator('#code').fill("from pathlib import Path\nPath('/restart-test').touch()\nlearner_value = 7\nprint('CURRENT EDIT')")
        page.locator('#run').evaluate('(button) => { button.click(); button.click(); }')
        assert page.evaluate('workerMessages') == ['prepare', 'run']
        assert page.evaluate('workerStarts') == 1
        for _ in range(200):
            if stalled:
                break
            page.wait_for_timeout(25)
        stalled.pop().continue_()
        page.wait_for_function("document.querySelector('#status').textContent.startsWith('Completed')", timeout=120000)
        assert page.locator('#output').inner_text().strip() == 'CURRENT EDIT'

        page.locator('#code').fill("print('learner_value' in globals())")
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.startsWith('Completed')")
        assert page.locator('#output').inner_text().strip() == 'False'
        assert page.evaluate('workerStarts') == 1

        page.locator('#editor-tools > summary').click()
        page.locator('#restart-python').click()
        assert page.locator('#code').input_value() == "print('learner_value' in globals())"
        page.locator('#code').fill("from pathlib import Path\nprint(Path('/restart-test').exists())")
        context.unroute(wasm)
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.startsWith('Completed')", timeout=120000)
        assert page.locator('#output').inner_text().strip() == 'False'
        assert page.evaluate('workerStarts') == 2
    finally:
        context.close()

    # These transport faults target the worker's direct network requests.
    # Service-worker cache/update faults have separate end-to-end coverage.
    context = browser.new_context(service_workers="block")
    context.add_init_script("""
      Object.defineProperty(navigator, 'connection', {value: {saveData:true}});
      window.workerStarts = 0;
      const OriginalWorker = Worker;
      window.Worker = class extends OriginalWorker {
        constructor(...args) { super(...args); ++workerStarts; }
      };
    """)
    page = context.new_page()
    worker_script = '**/worker.*.js'
    try:
        page.goto(url)
        page.wait_for_selector('html[data-ready="true"]')
        page.wait_for_timeout(650)
        assert page.evaluate('workerStarts') == 0
        page.evaluate("document.querySelector('#run').click(); document.querySelector('#stop').click()")
        assert page.locator('#run-result').is_hidden()
        page.wait_for_function("document.querySelector('#status').textContent.startsWith('Stopped')")
        context.route(worker_script, lambda route: route.fulfill(status=503, body='Unavailable'))
        page.locator('#run').click()
        page.wait_for_selector('#runtime-recovery-dialog', timeout=30000)
        assert page.locator('#run-result').is_hidden()
        assert page.locator('#run').is_enabled()
        assert page.locator('#runtime-recovery-dialog').is_visible()
        page.locator('[data-runtime-stay]').click()
        context.unroute(worker_script)
        page.locator('#code').fill("print('RECOVERED')")
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.startsWith('Completed')", timeout=120000)
        assert page.locator('#output').inner_text().strip() == 'RECOVERED'
        assert page.evaluate('workerStarts') == 3
    finally:
        context.close()
