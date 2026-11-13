# Design and implementation review

The learning-design and UX skills were read before drafting and revisited during
implementation. This is an author review and executable verification record,
not an independent learner study.

## Material inspected

- Assembly Lab's authoring guide, learning-design skill and project guidance,
  as references for bite-sized scope, concrete outcomes and fresh application.
- Event Streaming Lab's learning-design and UX skills, build and worker source.
- Primary references linked per lesson: NIST experimental design and confidence
  intervals, SciPy 1.14 method documentation, NumPy, pandas, Python clocks, the
  ASA p-value statement and Center for Open Science preregistration guidance.
- The complete scientific-method curriculum and exact executable examples.

## Decisions and corrections

| Finding | Effect | Correction and evidence |
| --- | --- | --- |
| One early question asked about bootstrap before teaching resampling | Unsupported prerequisite in an independent task | Replaced with a new matched-device comparison requiring only the pairing taught there |
| Session-level example used standard error before the later spread lesson | An unexplained term carried the comparison | Added a local plain-language definition; later lesson develops the formula and distinction from SD |
| Sample-size planning introduced a t test before the null-model module | The simulation's decision rule lacked preparation | Added explicit null, statistic, two-sided-test and p-value definitions, keeping the later detailed construction |
| Native Matplotlib 3.8.4 wheels can conflict with NumPy 2 | Build/runtime confusion and possible installation failure | Use native 3.9.4 with NumPy 2.0.2; retain Pyodide's supported patched 3.8.4 and publish each environment |
| Font self-hosting left a malformed CSS fragment | Root typography and theme variables failed | Removed the fragment; browser computed styles confirm DM Sans and the intended parchment background |
| Stop left the prior output caption saying a new run was in progress | Cancellation state could mislead about which run produced the visible record | Added an explicit stopped-run provenance caption; next execution remains available |
| Narrow header retained the Source link through a specificity conflict | Crowded header and unnecessary line wrapping | Increased specificity for the narrow-screen rule |
| Small metadata labels were difficult to read | Reduced usability of timing and provenance labels | Raised CSS text sizes below 11px to 11px; code output remains contained and scrollable |

The visual direction uses parchment, forest green, a muted copper accent,
Literata headings and DM Sans text. Fonts and licences are self-hosted. The
opening graphic is calculated from the first lesson's invented paired inputs;
it is labelled as invented and is not a fabricated measurement.

## What implementation checks establish

Native tests execute all 30 published examples, verify paired-ratio direction
and the useful threshold, check exact paired permutation enumeration, and
exercise valid and invalid CSV input. Build output comes from those examples.
Link checks cover all 32 generated pages and local fragments. Browser checks
execute all examples through real self-hosted Pyodide, compare numeric output
with native records (except machine-dependent timings), and exercise exports,
input provenance, draft persistence, errors, Stop/restart and feedback.

Desktop and narrow screenshots, both colour themes, 390px and 320px reflow,
JavaScript-free reading, and no third-party runtime/font requests are checked.
No automated screenshot or multiple-choice result proves a learner understands
the method. Native timing results do not describe the browser or other devices.

All 30 examples passed in individual page workers in the initial browser pass.
Final command results and any remaining corrections are recorded below after
verification completes. The initial browser pass launched a separate worker on
every lesson. The retained suite executes all published sources in a shared
worker with fresh run namespaces, then checks every actual page separately;
this checks run isolation and avoids repeating package-import overhead.

## Remaining evidence gaps

No novice participant has been observed working through the course. Lesson-time
estimates are author estimates. Screen-reader behaviour has not been manually
checked with assistive technology. Real scientific analyses can require designs
and models beyond this core course; deferred subjects are listed in the field
notes and learning-design brief.

## Verification history

- Initial full check: native examples and numerical tests passed; all 32 pages
  and 1,575 local links passed; all 30 examples passed in separate real browser
  workers. A later rendered-state assertion failed. Investigation identified a test
  reading a closed disclosure and a possible asynchronous draft-restore race.
  This run is recorded as failed, not as a passing suite.
- Added an explicit page-ready marker and browser-test wait, so state assertions
  inspect completed restoration. Retained the fresh-browser import round-trip.
- Retained suite uses one worker for all example sources (fresh variables per
  run), then visits each real lesson separately at both phone widths. This makes
  the identical code/runtime check much faster without reducing page coverage.
- A subsequent pass reached the JavaScript-free reading check, whose assertion
  tried to read rendered text inside a closed native disclosure. That assertion
  failed because closed content is not rendered. The test now opens the worked
  example through its native summary before inspecting output; no JavaScript
  is enabled for this check.

## Final verified result

`PATH="$PWD/.venv/bin:$PATH" npm run check` passed on 2026-11-12:

- Six native tests, including all 30 examples and valid/invalid CSV cases.
- Thirty executed worked records and eleven generated figures.
- Thirty-two static pages and 1,575 local links/fragments.
- All 30 published sources executed through real self-hosted browser Pyodide;
  numeric output matched native output within the stated comparison tolerance.
  Machine-dependent timing values were deliberately not compared across engines.
- CSV input provenance, exact source/output exports, report export, invalid-input
  recovery, errors, Stop/restart, drafts, reading marks, answer feedback and
  progress import into a fresh browser context.
- Every lesson at 390px and 320px without page overflow, both themes, computed
  theme colours and typography, and all 30 worked examples opened with JavaScript
  disabled and without requesting Python assets.

A separate focused browser check passed for keyboard navigation to the skip
link, indentation in the editor, leaving the editor with Shift+Tab, Ctrl+Enter
execution and Stop. Screenshots cover desktop, phone, editor and dark-theme
states. Test artifacts are retained by the GitHub Actions workflow.

## Publication environment correction

The first GitHub Actions run (43331260068) installed Python requirements but
failed before course checks: `ubuntu-latest` selected Ubuntu 26.04, which the
pinned Playwright release does not support. The browser installer explicitly
reported that unsupported OS. Both workflow jobs now use Ubuntu 24.04. Course
source and the locally passing checks were unchanged. Deployment is retried by
the corrective push, preserving the failed run's evidence.

## Visual redesign, 2026-11-13

User requested a new design after rejecting the first visual treatment. Applied
`.agents/skills/ux/SKILL.md` and `.agents/skills/learning-design/SKILL.md`, plus the
Sites presentation-led design guidance. The concrete brief is
`docs/visual-redesign.md`.

Reviewed before/after rendered desktop and 390px phone pages. Replaced the
parchment/serif treatment with Sora headings, DM Sans reading text, cool neutral
surfaces, blue actions and a dark Python workspace. The overview now has six
module panels, every lesson remains discoverable, and its interactive example
uses the invented equal-mean datasets from lesson 11. The control changes the
representation, not the data or a claimed execution. The SVG description explains
the vertical spacing. Added a real mobile course menu with Escape/focus recovery.

Rebuilt the lesson hierarchy and kept the outcome, prediction, actual results,
worked example, interpretation, limitations and fresh task distinct. Code and
output share a workspace on wide screens and stack on phones. Syntax colour and
line numbers decorate a native textarea; they do not change executed code.
Source markup is escaped, scrolling is synchronised, and Reset refreshes the
highlighted view. Plain editing remains available without JavaScript. Existing
URLs, local draft keys and export formats are retained.

Findings fixed during visual review:

- Replaced a missing-font arrow glyph in the demo with an inline SVG icon.
- Increased utility text below 11px to 11px and checked phone reflow.
- Shortened the mobile start button and retained a clear resume action.
- Rechecked explicit light/dark surface colours, editor text, focus indicators
  and the distinction between actual and worked results.

The first full redesigned suite passed: six native tests, 30 real Wasm examples,
32 pages and 1,541 local links; interactive-demo state, highlighted/restored code,
scroll sync, menu Escape/focus recovery, both themes, all pages at 390px/320px,
CSV/report exports and JavaScript-free worked output. A final rerun includes the
shortened start/resume copy and a specific partially-complete-course resume check.
Screenshots are under ignored `test-results/redesign/` locally; CI also captures
its regular overview, lesson, phone and dark-theme images as browser evidence.
These are implementation and author-review findings, not a novice learning study.

Final visual follow-up: the phone start action is 46px high without a wrapped
label. A focused forced-colour browser check confirmed the native editor remains
readable when decoration is suppressed. Built CSS, application, editor and worker
assets now use content-addressed filenames so a new deployment does not mix new
markup with stale cached scripts or styles. Stable source copies remain available.

The final `PATH="$PWD/.venv/bin:$PATH" npm run check` rerun passed with the
content-addressed asset build. All 30 native/browser examples, 32 pages, 1,541
local links, partial-course resume action, demo controls, highlighted code,
scroll/Reset behaviour, mobile menu, both themes, CSV/report/progress exports,
error/Stop recovery and JavaScript-free reading passed. Desktop and phone
screenshots were inspected. A separate forced-colour check passed. No runtime
package versions or learner data keys changed.
