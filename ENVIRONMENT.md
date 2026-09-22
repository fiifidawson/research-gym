# Setup and testing

You don't need to install anything. Opening the pull request runs the tests.

This page is for when you want more: instant feedback, or a local environment. All optional.

## Three ways to get feedback

| | Runs on | Speed | Install | Counts |
|---|---|---|---|---|
| Pull request | GitHub | ~1 min | nothing | yes, this is the one |
| Playground | your browser | instant | nothing | no |
| Local | your machine | instant | Python | no |

All three run the same `checks.py`, so they give the same answers.

## Pull request

1. Press <kbd>.</kbd> on any repo page for an editor in your browser.
2. Write your file under `submissions/<your-handle>/<module-id>/`.
3. Source Control panel → message → ✓ → Publish branch.
4. Open the pull request.

A comment appears listing every check, with the error and a hint for the failures. Push again and
the same comment updates.

Steps in full: [CONTRIBUTING.md](CONTRIBUTING.md).

## Playground

The Playground page on the site. Pick a module, paste or drop your file, Run (or
<kbd>Ctrl</kbd>/<kbd>Cmd</kbd>+<kbd>Enter</kbd>). Your draft is kept in your browser.

It runs real Python via [Pyodide](https://pyodide.org). NumPy modules only (00–03) — PyTorch can't
run in a browser, so from module 04 the pull request is the only runner.

## Local

### Install

Python 3.10 or newer; CI uses 3.11.

```bash
git clone https://github.com/<org>/research-gym
cd research-gym

python -m venv .venv
source .venv/bin/activate          # Windows PowerShell:  .venv\Scripts\Activate.ps1

pip install -e ".[checks]"
```

<details><summary>uv</summary>

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[checks]"
```
</details>

<details><summary>conda</summary>

```bash
conda create -n research-gym python=3.11 -y
conda activate research-gym
pip install -e ".[checks]"
```
</details>

### Check it worked

```bash
pytest modules/01-oop-refresher/tests
```

**22 failed** means the install is fine — with no submission specified it runs against the starter,
which is all TODOs. An *error* instead means something's wrong; see below.

### Run against your work

```bash
SUBMISSION_DIR=submissions/your-handle/01-oop-refresher pytest modules/01-oop-refresher/tests
```

<details><summary>Windows PowerShell</summary>

```powershell
$env:SUBMISSION_DIR = "submissions/your-handle/01-oop-refresher"
pytest modules/01-oop-refresher/tests
```

`Remove-Item Env:SUBMISSION_DIR` when you switch modules.
</details>

This is exactly what CI does.

### Flags

```bash
pytest modules/01-oop-refresher/tests -v                # list every check by name
pytest modules/01-oop-refresher/tests -m "not stretch"  # core only
pytest modules/01-oop-refresher/tests -m stretch        # optional only
pytest modules/01-oop-refresher/tests -k zeroes         # checks matching a word
pytest modules/01-oop-refresher/tests -x                # stop at the first failure
```

`-k` takes an expression, so a phrase with spaces won't work. Use one word, or `-k "ReLU and zeroes"`.

### Reading a failure

```
AssertionError: Linear.W should have shape (3, 2), got (2, 3)
```

Checks say what was expected and what arrived. If one fails without telling you that much, it's a
bug in the check — open an issue.

The checks themselves are in [`modules/<id>/checks.py`](modules/01-oop-refresher/checks.py). They're
the spec; read them.

### Style

```bash
ruff check submissions/your-handle/01-oop-refresher
ruff format submissions/your-handle/01-oop-refresher
```

CI runs the same thing on the files your pull request touched. The Ruff extension for VS Code with
format-on-save does it for you.

### The site

```bash
python .github/scripts/build_browser_bundle.py
python -m http.server -d docs
```

<http://localhost:8000>. Re-run the first command when a `checks.py` changes, or the playground runs
a stale copy.

## Troubleshooting

| | |
|---|---|
| `No module named 'gym'` | Missed `pip install -e ".[checks]"`, or the venv isn't active. |
| `No module named 'numpy'` | Same. |
| `expected to find 'nn.py' at ...` | File missing, misplaced or renamed. The name must match the starter. |
| `import file mismatch` | Stale bytecode. Delete the `__pycache__` folders. |
| Everything fails with the same error | Your file didn't import — a syntax error, or a `raise NotImplementedError` still there. |
| `Wrong expression passed to '-k'` | `-k` can't take a phrase with spaces. |
| Playground says the bundle is missing | Run `build_browser_bundle.py`. |
| Playground disagrees with CI | Shouldn't be possible; they share a file. Rebuild the bundle, then report it. |

## What CI runs

```bash
python .github/scripts/resolve_targets.py --base <base> --head <head> --author <you>
SUBMISSION_DIR=<your folder> pytest modules/<module>/tests --json-report
python .github/scripts/render_report.py ...
```

All of it is in [`.github/workflows/submission-check.yml`](.github/workflows/submission-check.yml).
