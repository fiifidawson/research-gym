<h1 align="center">research-gym</h1>

<p align="center">
  <em>Reps until AI research and engineering feel ordinary.</em><br>
  <a href="modules/00-onboarding/TASK.md">Start here</a> &middot;
  <a href="CONTRIBUTING.md">How to contribute</a> &middot;
  <a href="docs/index.html">The dashboard</a>
</p>

---

A shared repo for a small group getting good at AI research and engineering together. You build a
neural network from nothing, then an LLM, one module at a time. Each module is a pull request that a
robot checks and a teammate reviews.

**You never run a test on your own machine.** Opening the pull request *is* running the tests. The
check comments back in plain English, updates itself every time you push, and the same comment is
how your reviewer sees where you got to.

```
┌──────────────┐   ┌───────────────┐   ┌──────────────┐   ┌───────┐
│  write code  │ → │  open the PR  │ → │  get a review│ → │ merge │
└──────────────┘   └───────┬───────┘   └──────────────┘   └───┬───┘
                           │                                  │
                   robot comments with                   your row on the
                   every check, in English                 dashboard ticks
```

## Start here

1. **Read [`modules/00-onboarding/TASK.md`](modules/00-onboarding/TASK.md).** It is a ten-minute
   module whose only purpose is to walk you through the whole loop once, on something where being
   wrong costs nothing.
2. Then take [module 01](modules/01-oop-refresher/TASK.md), and the neural network starts.

No terminal required at any point — [CONTRIBUTING.md](CONTRIBUTING.md) gives the browser/editor path
first, with the equivalent commands tucked into collapsed blocks for anyone who prefers them.

## The track

| | Phase | What happens |
|---|---|---|
| 00 | Onboarding | One pull request, reviewed and merged. The rehearsal. |
| 01–03 | Fundamentals | `Layer`, `Linear`, `Sequential`; then autograd; then a training loop. All NumPy, nothing magic. |
| 04–05 | PyTorch and experiments | The same model in a real framework, then the habits that make a result trustworthy. |
| 06–11 | An LLM from scratch | Tokenizer, attention, GPT, pretraining, fine-tuning — following Sebastian Raschka's [*Build a Large Language Model (From Scratch)*](https://sebastianraschka.com/llms-from-scratch/), chapter by chapter. |
| 12–14 | Research craft | Reproduce a result, evaluate it honestly, then LoRA / DPO / GRPO. |

Every module has **core** checks everyone is expected to pass and **stretch** checks that are
genuinely optional, so the same module works whether this is familiar ground or brand new.

Modules 02 onward are roadmap stubs today. [Writing one is a real contribution](CONTRIBUTING.md#writing-a-module),
and a good way to learn the material twice.

## How it fits together

```
modules/01-oop-refresher/
  TASK.md        what to build, why it matters, what to read
  starter/nn.py  a skeleton full of TODOs — copy it, don't edit it
  checks.py      the spec: named checks like "ReLU zeroes negative values"
  tests/         six lines that hand checks.py to pytest

submissions/
  your-handle/01-oop-refresher/nn.py     ← your work goes here, and nowhere else

docs/            the site, plain HTML, deployed by GitHub Actions
gym/             tiny shared helpers (seeding, toy datasets, the Check type)
```

**One `checks.py`, two runners.** Each check is written exactly once. CI hands the list to pytest so
the pull request comment can print the names verbatim; the
[browser playground](docs/playground.html) loads the very same file into Pyodide for instant
feedback while you work. They cannot disagree, because there is only one copy of each assertion.

Everyone has their own folder under `submissions/`, so eight people can work at once without a
single merge conflict — and so you can read how everyone else solved the same problem the moment
they merge.

## The site

Deployed from `docs/` on every push to `main`:

- **Dashboard** — who has finished what, rebuilt from scratch after each merge by re-running every
  merged submission against the current checks. It cannot quietly go stale.
- **Playground** — the real checks, in your browser, no round trip. NumPy modules only; PyTorch
  cannot run in Pyodide, so from module 04 the pull request is the only runner.
- **Reading** — grouped by module. Adding one is a one-line pull request, and it counts.

## Running things locally (entirely optional)

```bash
pip install -e ".[checks]"

# check a submission the way CI will
SUBMISSION_DIR=submissions/your-handle/01-oop-refresher pytest modules/01-oop-refresher/tests

# serve the site, playground included
python .github/scripts/build_browser_bundle.py
python -m http.server -d docs
```

## House rules

- One module per pull request.
- Only ever edit files inside `submissions/<your-handle>/`. The check enforces this, kindly.
- Don't edit `checks.py` or `tests/` — if a check is wrong, and sometimes one is, open an issue.
  Fixing a bad check is a genuine contribution; it just belongs in its own pull request.
- Review someone else's work each week. Three of us said we couldn't review code today; that is
  exactly the thing this fixes, and the only way to fix it is to do it.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the details, including how to give a review that helps.

## Licence

[MIT](LICENSE). The book is Sebastian Raschka's and is not included here — buy it, it's worth it.
