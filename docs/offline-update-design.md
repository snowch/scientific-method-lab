# Offline access and updates

Copyright © 2026 Christopher Snow.

This course reuses the verified release and two-phase restart protocol described in [CUDA C++ Lab](https://github.com/snowch/cuda-cpp-lab/blob/main/docs/offline-update-design.md). The existing per-lesson runner uses a fully self-hosted Pyodide 0.27.7 runtime. Python preparation can still begin while a visible lesson is read; it does not run the learner’s code. This change preserves the current Run Python and Stop controls.

## Learner experience

App status is available in every page header. Small version checks happen automatically; they do not download the whole course. Normal online visits request current HTML, whose dependencies are pinned to one immutable release. An open lesson is never replaced automatically.

Choose **Save offline copy** before disconnecting. The saved copy includes all 30 lessons, worked examples, reference pages, diagrams, the local font, Python sources, Pyodide, NumPy, SciPy, pandas, Matplotlib and their pinned dependency closure. CSV, notes and report downloads are generated locally and work offline. External reference websites and other labs require a connection.

**Up to date online** describes online freshness. Only a complete byte-count and SHA-256 verification permits **Downloaded and ready to use offline** and its tick. **Update offline copy** stages the next complete release and then offers **Restart to update**. It needs no second download. Cancellation keeps verified files for resumption; interrupted transfers resume when the connection returns. A failed update leaves the previously verified copy usable. **Repair offline copy** recovers missing or damaged files while online.

Removing the offline copy requires confirmation. It removes only this course's downloaded files, not notes, report drafts, recorded capstone runs, preferences or other labs. Browsers can still evict storage; readiness is verified rather than inferred from a completion flag.

## Saved work and restart

The service worker asks every open course window to prepare before switching the selected release. Active experiments, CSV generation, text composition or unavailable storage veto the restart. Each window saves and reads back an IndexedDB snapshot and stores its own snapshot token in session storage. Editing and navigation are briefly locked while preparing. Abort unlocks every window; commit reloads each window only after all acknowledge.

Snapshots preserve the complete editor source, recoverable draft, predictions, notes, report fields, reading marks, quiz feedback, genuine successful results, ordinary Python errors, plots, disclosures and reading position. Plots are rebuilt from their recorded SVG data; expired blob URLs are not reused. Uploaded CSV text and its filename are saved separately from the browser file picker and restored with an explicit input label. A restored result is identified as an earlier result. Python is never executed automatically during restoration. Existing localStorage keys and portable exports remain intact. Active Python or CSV reading vetoes restart; unused background preparation can be cancelled while saving.

Reading-state setup waits for the course and editor to finish initialising. The loading/recovery dialog is reserved for infrastructure failures; ordinary Python exceptions stay with the editor and can be restored as previous-attempt feedback.

A missing worker is an infrastructure failure. Keep earlier output and show a persistent native recovery dialog with a dimmed backdrop, Reload lesson and Stay on lesson. Reload saves the same verified snapshot first; failed storage blocks it. Ordinary experiment validation remains inline.

## Build and publication

The build clears only its owned output directory; custom output directories must be empty. It fingerprints the output and worker contract, copies assets to `releases/<id>/`, pins HTML assets, and emits exact bytes and SHA-256 for every required file. Font and worker imports resolve relative to their pinned modules/stylesheets. Responsive figure srcset URLs are pinned too. Versioned engine directories such as engine/0.27.7 are valid paths; dot traversal remains rejected. The vendored loader uses its local index URL for fallback rather than retrying a public CDN. Service-worker installation does not silently download the course.

Before publication, discover legacy dependency aliases from published HTML, JavaScript imports, versioned workers, stylesheets and the prior runtime manifest, then preserve them along with the two prior immutable releases. A newly fingerprinted build must not erase an old worker that an open lesson has yet to load. Requests retry transient transport failures up to three times; bad hashes and missing declared dependencies still stop publication. Verify fetched bytes; abort publication if preservation fails. The publish job consumes the already-tested build artifact, so a publication-only retry does not repeat numerical and browser checks. Tests import the actual retention helpers and exercise the publication entry point, guarding against incorrect adapter import paths.

## Functional verification

`npm run check` retains the existing native numerical checks, generated worked output, complete real-WASM lesson journeys and responsive/keyboard checks.

`npm run test:offline` checks every immutable asset hash and byte count, the local-only loader, responsive pins and the actual publisher imports. Its real browser journey saves on the overview before initialising Python, closes the browser and HTTP server, reopens offline, runs original and edited examples, restores code/notes/plots/progress and ordinary Python errors, exercises Stop/busy veto, runs unvisited lessons and exports results and reports. The Scientific Method report also tests a restored uploaded CSV. Intentional cache eviction must retain genuine output, show a persistent recovery dialog and describe the copy as needing repair.

The separate small-release fixture checks cancelled/resumed saves, failure without replacing the verified old copy, resumed transfer on reconnection, two-window busy/storage veto and atomic restart. Fixture records check protocol behaviour; they are not claimed as Python execution.

Functional tests and author review do not establish learning effectiveness or physical Android performance.

## Publication artifact closure

Verify the artifact downloaded by the publish job, not only the build directory in the check job. Actions uploads must include hidden files. The publish gate reads both manifests and verifies the presence, length and SHA-256 of every required immutable file before retaining older releases or deploying. Tests deliberately remove and corrupt a required hidden file; both failures must block publication.

`.nojekyll` is a deployment marker, not course content. Keep it outside the offline manifest. The first Python deployment listed the empty marker while Actions omitted hidden files, which prevented completion of a public offline save despite local tests passing. A narrow migration removes only that exact empty marker from retained manifests; every actual lesson/runtime byte still requires its original hash. Public verification must audit the deployed files and perform a fresh-browser save and cold offline run.

Pages artifact listings can lag a successful upload. Use an attempt-specific artifact name and wait for two consistent API listings before asking Pages to deploy. A bounded timeout fails publication without changing the live site. For publication-only recovery, `publish-verified.yml` accepts a completed main-branch course run only when its `check` job passed. It downloads that run’s verified artifact, checks its source commit and every promised file, preserves older assets and deploys without rebuilding or rerunning lessons. Both publication paths share a concurrency group.
