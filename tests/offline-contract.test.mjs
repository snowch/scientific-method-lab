// Copyright © 2026 Christopher Snow.
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { validateRelease } from "../src/release-contract.mjs";

test("complete Python course has verified immutable assets, pinned responsive figures and no loader CDN fallback", async () => {
  const release = validateRelease(
      JSON.parse(await readFile("dist/release.json")),
    ),
    course = JSON.parse(await readFile("src/course.json"));
  for (const file of release.files) {
    const body = await readFile(
      "dist/releases/" + release.id + "/" + file.path,
    );
    assert.equal(body.length, file.bytes, file.path);
    assert.equal(
      createHash("sha256").update(body).digest("hex"),
      file.sha256,
      file.path,
    );
  }
  for (const lesson of course.lessons) {
    const page = await readFile(
      "dist/lessons/" + lesson.slug + ".html",
      "utf8",
    );
    assert.match(page, /id="app-status-open"/);
    assert.match(page, new RegExp("releases/" + release.id + "/offline.mjs"));
    for (const [, sources] of page.matchAll(/srcset="([^\"]+)"/g))
      for (const source of sources.split(","))
        assert.ok(
          source.trim().startsWith("../releases/" + release.id + "/"),
          source,
        );
  }
  for (const name of ["pyodide.js", "pyodide.mjs"]) {
    const source = await readFile(
      "dist/releases/" + release.id + "/engine/0.27.7/" + name,
      "utf8",
    );
    assert.ok(source.includes("n.setCdnUrl(r.indexURL)"));
    assert.ok(!source.includes("n.setCdnUrl(`https://cdn.jsdelivr.net/"));
  }
  assert.throws(
    () =>
      validateRelease({
        ...release,
        files: [
          ...release.files,
          { path: "engine/../escape", bytes: 0, sha256: "a".repeat(64) },
        ],
      }),
    /Invalid/,
  );
  // This catches publication-only imports before the browser matrix.
  execFileSync(process.execPath, ["scripts/retain-for-publish.mjs"], {
    env: { ...process.env, PUBLISHED_COURSE_URL: "" },
    stdio: "pipe",
  });
});
