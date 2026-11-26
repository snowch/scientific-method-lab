// Copyright © 2026 Christopher Snow. Actual Pyodide after browser close and HTTP server shutdown.
const { chromium, expect } = require("playwright/test"),
  assert = require("node:assert/strict"),
  fs = require("node:fs/promises"),
  path = require("node:path"),
  os = require("node:os"),
  { createServer } = require("node:http");
(async () => {
  const root = path.resolve("dist"),
    course = JSON.parse(await fs.readFile("src/course.json")),
    slug = JSON.parse(await fs.readFile("package.json")).name,
    first = course.lessons[0],
    last = course.lessons.at(-1),
    scientific = slug === "scientific-method-lab",
    profile = await fs.mkdtemp(path.join(os.tmpdir(), slug + "-offline-"));
  const errors = [],
    outside = [];
  let context,
    online = true,
    engineRequests = 0;
  const server = createServer(async (req, res) => {
    try {
      let name = new URL(req.url, "http://local").pathname;
      if (!name.startsWith("/" + slug + "/")) throw Error();
      name = name.slice(slug.length + 2) || "index.html";
      const file = path.resolve(root, name);
      if (!file.startsWith(root + path.sep)) throw Error();
      const body = await fs.readFile(file);
      res.writeHead(200, {
        "Content-Type":
          {
            ".html": "text/html",
            ".js": "text/javascript",
            ".mjs": "text/javascript",
            ".css": "text/css",
            ".json": "application/json",
            ".svg": "image/svg+xml",
            ".wasm": "application/wasm",
            ".ttf": "font/ttf",
            ".woff2": "font/woff2",
          }[path.extname(file)] || "application/octet-stream",
        "Cache-Control": "no-store",
        "Content-Length": body.length,
      });
      res.end(body);
    } catch {
      res.writeHead(404).end();
    }
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = "http://127.0.0.1:" + server.address().port + "/" + slug + "/";
  async function open() {
    context = await chromium.launchPersistentContext(profile, {
      headless: true,
      executablePath:
        process.env.CHROMIUM ||
        (require("node:fs").existsSync("/usr/bin/chromium")
          ? "/usr/bin/chromium"
          : chromium.executablePath()),
      viewport: { width: 390, height: 950 },
      reducedMotion: "reduce",
      acceptDownloads: true,
    });
    context.on("request", (r) => {
      if (r.url().includes("/engine/")) engineRequests++;
      if (/^https?:/.test(r.url()) && !r.url().startsWith(base))
        outside.push(r.url());
    });
    const p = await context.newPage();
    p.on("pageerror", (e) => errors.push(e.message));
    return p;
  }
  async function visit(p, lesson) {
    await p.goto(base + "lessons/" + lesson.slug + ".html");
    await expect(p.locator("html")).toHaveAttribute("data-ready", "true");
  }
  async function run(p) {
    await p.locator("#run").click();
    await expect(p.locator("#status")).toHaveText("Completed.", {
      timeout: 150000,
    });
  }
  async function reading(p) {
    return p.evaluate(async () => {
      const script = document.querySelector('script[src*="/offline.mjs"]').src;
      return (
        await import(new URL("./experiment-state.mjs", script))
      ).saveReadingState();
    });
  }
  async function reload(p) {
    await reading(p);
    await p.reload();
    await expect(p.locator("html")).toHaveAttribute("data-ready", "true");
  }
  try {
    let p = await open();
    await p.goto(base);
    await expect(p.locator("html")).toHaveAttribute("data-ready", "true");
    assert.equal(engineRequests, 0, "Overview does not initialise Python");
    for (const width of [320, 390, 820, 1440])
      for (const theme of ["light", "dark"]) {
        await p.setViewportSize({ width, height: 1000 });
        if ((await p.locator("html").getAttribute("data-theme")) !== theme)
          await p.locator("#theme").click();
        assert.equal(
          await p.evaluate(
            () => document.documentElement.scrollWidth > innerWidth,
          ),
          false,
        );
        await p.locator("#app-status-open").click();
        await expect(p.locator("#app-status-dialog")).toBeVisible();
        await fs.mkdir("test-results", { recursive: true });
        await p.screenshot({
          path: "test-results/offline-status-" + width + "-" + theme + ".png",
        });
        await p.keyboard.press("Escape");
        await expect(p.locator("#app-status-dialog")).toBeHidden();
        await expect(p.locator("#app-status-open")).toBeFocused();
      }
    await p.locator("#app-status-open").click();
    await expect(p.locator("#download-update")).toHaveText(
      "Save offline copy",
      { timeout: 30000 },
    );
    await p.locator("#download-update").click();
    await expect(p.locator("#offline-status")).toContainText(
      "Downloaded and ready to use offline",
      { timeout: 180000 },
    );
    await expect(p.locator("#app-status-open [data-badge='saved']")).toBeVisible();
    await expect(p.locator("#app-status-open")).toHaveAccessibleDescription(/Downloaded and ready to use offline/);
    await context.close();
    context = null;
    server.closeAllConnections();
    await new Promise((r) => server.close(r));
    online = false;
    p = await open();
    await context.setOffline(true);
    await visit(p, first);
    await run(p);
    const original = await p.locator("#output").textContent();
    console.log(slug, "REAL COLD OFFLINE OUTPUT:", original.trim());
    if (scientific) {
      await expect(p.locator("#plots img").first()).toBeVisible();
      await expect
        .poll(() =>
          p
            .locator("#plots img")
            .first()
            .evaluate((n) => n.complete && n.naturalWidth > 0),
        )
        .toBe(true);
    }
    const source = await p.locator("#code").inputValue(),
      edited = scientific
        ? source.replace(
            "minimum_reduction_pct = 20",
            "minimum_reduction_pct = 10",
          )
        : source.replace("64, 72, 80, 88", "64, 72, 80, 98");
    assert.notEqual(source, edited);
    await p.locator("#code").fill(edited);
    await run(p);
    const result = await p.locator("#output").textContent();
    assert.notEqual(result, original);
    assert.match(
      result,
      scientific
        ? /Pairs meeting 10%: 5/
        : /Population ATE \(score points\): 4\.666/,
    );
    await p.locator("#lesson-notes>summary").click();
    await p.locator("#notes").fill("My offline notes survive an update.");
    await p.locator("#mark-read").check();
    await reload(p);
    await expect(p.locator("#code")).toHaveValue(edited);
    await expect(p.locator("#notes")).toHaveValue(
      "My offline notes survive an update.",
    );
    await expect(p.locator("#mark-read")).toBeChecked();
    await expect(p.locator("#output")).toHaveText(result);
    await expect(p.locator("#status")).toContainText("Saved earlier result");
    if (scientific) {
      await expect(p.locator("#plots img").first()).toBeVisible();
      await expect
        .poll(() =>
          p
            .locator("#plots img")
            .first()
            .evaluate((n) => n.complete && n.naturalWidth > 0),
        )
        .toBe(true);
    }
    await p.locator("#code").fill("while True:\n    pass\n");
    await p.locator("#run").click();
    await expect(p.locator("#status")).toContainText("Running your Python", {
      timeout: 150000,
    });
    const veto = await reading(p).then(
      () => "",
      (e) => e.message,
    );
    assert.match(veto, /Finish|stop/i);
    await p.locator("#stop").click();
    await expect(p.locator("#status")).toContainText("Stopped");
    await p.locator("#code").fill(edited);
    await run(p);
    await p
      .locator("#code")
      .fill("raise ValueError('offline error evidence')\n");
    await p.locator("#run").click();
    await expect(p.locator("#run-error")).toBeVisible({ timeout: 150000 });
    await expect(p.locator("#runtime-recovery-dialog")).toHaveCount(0);
    await reload(p);
    await expect(p.locator("#error-summary")).toContainText(
      "offline error evidence",
    );
    await expect(p.locator("#status")).toContainText("Saved Python error");
    await p.locator("#code").fill(edited);
    await run(p);
    const middle = course.lessons[Math.floor(course.lessons.length / 2)];
    await visit(p, middle);
    await run(p);
    await expect(p.locator("#output")).not.toBeEmpty();
    await visit(p, last);
    if (scientific) {
      await p
        .locator("#csv-upload")
        .setInputFiles({
          name: "paired-offline.csv",
          mimeType: "text/csv",
          buffer: Buffer.from(
            "run_id,a_ms,b_ms\nr1,100,80\nr2,120,90\nr3,90,75\nr4,110,85\nr5,100,79\nr6,130,105\n",
          ),
        });
      await expect(p.locator("#csv-status")).toContainText("File selected");
    }
    await run(p);
    const finalOutput = await p.locator("#output").textContent();
    await p.locator("#report-question").fill("My offline report");
    await reload(p);
    await expect(p.locator("#report-question")).toHaveValue(
      "My offline report",
    );
    await expect(p.locator("#output")).toHaveText(finalOutput);
    if (scientific)
      await expect(p.locator("#csv-status")).toContainText(
        "paired-offline.csv",
      );
    const tools = p
      .locator("#export-run")
      .locator("xpath=ancestor::details[1]");
    if (!(await tools.evaluate((n) => n.open)))
      await tools.locator(":scope>summary").click();
    const [record] = await Promise.all([
      p.waitForEvent("download"),
      p.locator("#export-run").click(),
    ]);
    const exported = JSON.parse(await fs.readFile(await record.path(), "utf8"));
    assert.equal(exported.stdout, finalOutput);
    if (scientific) {
      assert.equal(exported.input_name, "paired-offline.csv");
      assert.match(exported.input_csv, /r6,130,105/);
    }
    const [report] = await Promise.all([
      p.waitForEvent("download"),
      p.locator("#export-report").click(),
    ]);
    assert.match(
      await fs.readFile(await report.path(), "utf8"),
      /My offline report/,
    );
    await p.goto(base + "field-notes.html");
    await expect(p.locator("html")).toHaveAttribute("data-ready", "true");
    await expect(p.locator("main")).toBeVisible();
    // Eviction after a complete save is reported as infrastructure, preserving genuine output.
    await visit(p, first);
    await run(p);
    const retained = await p.locator("#output").textContent();
    await p.locator("#editor-tools>summary").click();
    await p.locator("#restart-python").click();
    await p.evaluate(async () => {
      const base = new URL(
          document.querySelector('meta[name="gpu-base"]').content,
          location.href,
        ),
        id = document.querySelector('meta[name="gpu-release"]').content;
      const names = await caches.keys();
      const name = names.find((n) => n.endsWith(":release-" + id));
      if (!name) throw Error("No saved course cache");
      const cache = await caches.open(name),
        url = new URL("engine/0.27.7/pyodide.js", base).href;
      if (!(await cache.delete(url)))
        throw Error("Expected saved Python loader");
    });
    await p.locator("#run").click();
    await expect(p.locator("#runtime-recovery-dialog")).toBeVisible({
      timeout: 30000,
    });
    await expect(p.locator("#output")).toHaveText(retained);
    await p.keyboard.press("Escape");
    await expect(p.locator("#runtime-recovery-dialog")).toBeHidden();
    await p.locator("#app-status-open").click();
    await expect(p.locator("#offline-status")).not.toContainText(
      "Downloaded and ready to use offline",
      { timeout: 30000 },
    );
    await expect(p.locator("#download-update")).toHaveText(
      "Repair offline copy",
      { timeout: 30000 },
    );
    assert.deepEqual(outside, []);
    assert.deepEqual(errors, []);
    console.log(
      "PASS",
      slug,
      "real cold/offline Python, original+edit, restored code/notes/plots/progress, busy veto and Stop, unvisited lessons, CSV/result/report exports, evicted-asset recovery, 4 widths × 2 themes and keyboard dialogs.",
    );
  } finally {
    await context?.close();
    if (online) {
      server.closeAllConnections();
      await new Promise((r) => server.close(r));
    }
    await fs.rm(profile, { recursive: true, force: true });
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
