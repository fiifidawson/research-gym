# Your setup, and how testing works

Short version: **you do not need to install anything.** Opening the pull request runs the tests.

This page is for when you want more than that — instant feedback while you work, or a proper local
environment. All of it is optional, and none of it changes what counts.

---

## Three ways to get feedback

| | Where it runs | How fast | Needs installing | Counts? |
|---|---|---|---|---|
| **The pull request** | GitHub's machines | ~1 minute | nothing | **yes — this is the only one that does** |
| **The playground** | your browser | instant | nothing | no, practice only |
| **Locally** | your machine | instant | Python | no, but identical |

They run **the same checks** — literally the same `checks.py` file — so they cannot disagree. Pick
whichever suits you and switch freely.

---

## 1. The pull request (the default, nothing to install)

1. Press <kbd>.</kbd> on any repo page. That opens [github.dev](https://github.dev), a full editor
   in your browser.
2. Create your file under `submissions/<your-handle>/<module-id>/`, and write it.
3. **Source Control** panel → message → ✓ → **Publish branch**.
4. Open the pull request on github.com.

A comment appears listing every check by name — ✅ or ❌, with the error and a nudge for the failures.
Push again and **the same comment updates**; push as often as you like.

Full walkthrough with pictures of each button: [CONTRIBUTING.md](CONTRIBUTING.md).

## 2. The playground (instant, still nothing to install)

Open the **Playground** page on the site, pick your module, paste or drop your file, hit **Run**
(or <kbd>Ctrl</kbd>/<kbd>Cmd</kbd>+<kbd>Enter</kbd>). Same checks, same names, no round trip. Your
draft is kept in your browser between visits.

It runs Python properly, via [Pyodide](https://pyodide.org) — it is not a simulation.

**Limit:** NumPy modules only (00–03). PyTorch cannot run in a browser, so from module 04 the pull
request is the only runner.

---

## 3. A local environment (optional)

Worth it if you like an editor with autocomplete, or you want a debugger. Not worth it just to run
the checks.

### Install

You need **Python 3.10 or newer** (CI uses 3.11). Check with `python --version`.

```bash
git clone https://github.com/<org>/research-gym
cd research-gym

python -m venv .venv
source .venv/bin/activate          # Windows PowerShell:  .venv\Scripts\Activate.ps1

pip install -e ".[checks]"
```

That last line installs NumPy, pytest and the reporting plugin, and puts `gym/` on your path.

<details><summary>Prefer <code>uv</code>? (faster, same result)</summary>

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[checks]"
```
</details>

<details><summary>Prefer conda?</summary>

```bash
conda create -n research-gym python=3.11 -y
conda activate research-gym
pip install -e ".[checks]"
```
</details>

### Check the install worked

Run module 01's checks against the starter. **They should all fail** — the starter is nothing but
TODOs. Failures here mean the plumbing works:

```bash
pytest modules/01-oop-refresher/tests
```

If you get `22 failed`, you are set up correctly. If you get an *error* instead, see
[Troubleshooting](#troubleshooting).

### Run the checks against your own work

Point `SUBMISSION_DIR` at your folder. This is exactly what CI does:

```bash
SUBMISSION_DIR=submissions/your-handle/01-oop-refresher pytest modules/01-oop-refresher/tests
```

<details><summary>Windows PowerShell</summary>

```powershell
$env:SUBMISSION_DIR = "submissions/your-handle/01-oop-refresher"
pytest modules/01-oop-refresher/tests
```

Unset it again with `Remove-Item Env:SUBMISSION_DIR` when you switch modules.
</details>

Without `SUBMISSION_DIR`, the module's own `starter/` is used — which is why the command above fails
by design.

### Useful variations

```bash
pytest modules/01-oop-refresher/tests -v              # list every check by name
pytest modules/01-oop-refresher/tests -m "not stretch"  # core only, the ones that must pass
pytest modules/01-oop-refresher/tests -m stretch      # only the optional ones
pytest modules/01-oop-refresher/tests -k zeroes       # just the checks matching a word
pytest modules/01-oop-refresher/tests -x              # stop at the first failure
```

`-k` takes an *expression*, so a phrase with spaces will not work — use one word (`zeroes`), or
join them (`-k "ReLU and zeroes"`).

### Reading a failure

```
AssertionError: Linear.W should have shape (3, 2), got (2, 3)
```

The checks are written to say what was expected and what arrived. If one ever fails without telling
you that much, **that is a bug in the check** — open an issue with the `bug` template. Fixing it is
a real contribution.

To see the exact check that failed, look at [`modules/<id>/checks.py`](modules/01-oop-refresher/checks.py).
It is the spec and you are meant to read it.

### Style

CI runs `ruff` on the files your pull request touched, and only those.

```bash
ruff check submissions/your-handle/01-oop-refresher    # what CI checks
ruff format submissions/your-handle/01-oop-refresher   # fix the formatting
```

In VS Code, install the **Ruff** extension and turn on format-on-save; then you can forget this
section exists.

### Running the site locally

```bash
python .github/scripts/build_browser_bundle.py   # copies checks.py where the browser can fetch it
python -m http.server -d docs
```

Then open <http://localhost:8000>. Re-run the first command whenever a `checks.py` changes, or the
playground will be running a stale copy.

---

## Troubleshooting

| What you see | What it means |
|---|---|
| `ModuleNotFoundError: No module named 'gym'` | You skipped `pip install -e ".[checks]"`, or the venv is not active. |
| `ModuleNotFoundError: No module named 'numpy'` | Same — the install also brings NumPy. |
| `expected to find 'nn.py' at ...` | Your file is missing, in the wrong folder, or renamed. The name must match the starter exactly. |
| `import file mismatch` | Stale bytecode. Delete the `__pycache__` folders and retry. |
| Everything fails with the *same* error | Your file did not import at all — a syntax error, or a `raise NotImplementedError` still in place. Fix that one thing and the rest will start running. |
| `ERROR: Wrong expression passed to '-k'` | `-k` cannot take a phrase with spaces. Use a single word. |
| The playground says the bundle is missing | Run `python .github/scripts/build_browser_bundle.py`. |
| The playground disagrees with CI | It should be impossible — they share one file. Rebuild the bundle; if it persists, that is a genuine bug, please report it. |

---

## What CI actually runs

No secrets — it is the same commands you would type:

```bash
python .github/scripts/resolve_targets.py --base <base> --head <head> --author <you>   # what did this PR submit?
SUBMISSION_DIR=<your folder> pytest modules/<module>/tests --json-report               # run the checks
python .github/scripts/render_report.py ...                                            # turn that into the comment
```

It is all in [`.github/workflows/submission-check.yml`](.github/workflows/submission-check.yml), and
you are welcome to read it. Knowing what your CI does is a research-engineering skill in itself.
