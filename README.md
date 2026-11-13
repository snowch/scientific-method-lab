# Scientific Method Lab

Thirty short investigations for learning to ask testable questions, design fair
experiments and make claims the evidence can support. Python runs locally in the
browser with real NumPy, pandas, SciPy and Matplotlib.

**Course:** https://snowch.github.io/scientific-method-lab/

Each investigation takes about 5–9 minutes for its first reading, experiment and
question. The core route is about 3¼ hours, plus exploration and a final project.
Basic Python reading helps; no prior statistics is assumed.

## The route

1. **Ask a better question:** claims, predictions, variables, instruments and
   evidence that challenges an explanation.
2. **Design a fair test:** controls, randomisation, pairing, experimental units
   and factorial interactions.
3. **Read the observations:** distributions, spread, selection, drift and
   missing outcomes.
4. **Put uncertainty to work:** confidence intervals, repeated-sampling coverage,
   bootstrap units, useful effects and sample-size planning.
5. **Challenge your conclusion:** null models, paired randomisation, p-values,
   multiple testing and optional stopping.
6. **Make the evidence travel:** causal alternatives, residuals, replication,
   real timing collection and an exportable investigation report.

Every page includes an observable goal, optional prediction, editable Python,
actual output, a change to try, an independent question, hints, feedback and
local interpretation limits. Worked output and figures come from executing the
published examples during the build. Invented, simulated and measured data are
labelled separately. Reading progress never claims mastery.

## Development

Requires Node 24 and Python 3.12. Use a project virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run dev
```

Open `http://localhost:5173/scientific-method-lab/`. The prefix is intentional:
local checks exercise the same relative paths GitHub Pages uses.

```sh
python -m playwright install chromium
npm run check
```

`npm run check` executes every example, builds the full site, checks all local
links and fragments, and runs every example in real browser Pyodide. It checks
CSV validation, output provenance, errors, Stop/restart, drafts, exports, progress
import, feedback, themes, narrow layouts and a JavaScript-free reading route.
For an existing system Chromium, set `CHROMIUM_PATH=/usr/bin/chromium` outside CI.
Screenshots and exported test artifacts go to ignored `test-results/`.

The first build downloads pinned Pyodide wheels and verifies the hashes in the
Pyodide lockfile. Runtime assets are served by this site, not fetched from a CDN
by the learner. Native build Matplotlib is 3.9.4 for NumPy 2 compatibility;
Pyodide's patched Matplotlib is 3.8.4. Each worked record and actual run reports
its environment. Figures may differ slightly across renderers; measured timings
will differ materially across machines.

## Publishing

`.github/workflows/pages.yml` runs the same checks on Ubuntu 24.04 for pull requests and pushes.
On a successful push to `main`, it uploads `dist/` and deploys with GitHub Pages
Actions. Pages must use **GitHub Actions** as its source, as already configured.
No API keys, servers or paid services are required.

## Authoring and design

- `src/course.json`: objectives, prose, questions, hints and primary sources.
- `python/`: standalone executable learner examples.
- `scripts/build.mjs`: static generation, executed worked examples and versioned assets.
- `scripts/layout.mjs`: shared navigation, course overview and lesson layouts.
- `src/app.js`, `src/worker.js`: local interaction and Python execution.
- `src/editor.mjs`: syntax colour and line numbers around a native editing surface.
- `src/style.css`, `src/fonts/`: responsive visual system and self-hosted fonts.
- [Learning design brief](docs/learning-design.md).
- [Visual design brief](docs/visual-redesign.md).
- [Review and evidence](docs/review.md).

The design applies the repository's [learning-design skill](.agents/skills/learning-design/SKILL.md)
and [UX skill](.agents/skills/ux/SKILL.md), adapted from the author's existing labs.
The learning route and examples are original. The technical and teaching patterns
are acknowledged in the course's field notes.

Code: Apache-2.0. Original course content: CC BY-NC 4.0. Third-party packages and
fonts retain their own licences. See [LICENSE](LICENSE).
