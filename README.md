# research-gym

Build a neural network from scratch, then an LLM. One module at a time, submitted as a pull request
that gets checked automatically and reviewed by someone on the team.

You don't run tests yourself. Opening the pull request runs them, and a comment tells you which
checks passed and which didn't.

## Start

1. Read [`modules/00-onboarding/TASK.md`](modules/00-onboarding/TASK.md) — a ten-minute module that
   walks the whole loop once.
2. Then [module 01](modules/01-oop-refresher/TASK.md).

You can do all of it from the browser. Press <kbd>.</kbd> on any repo page for an editor.
[CONTRIBUTING.md](CONTRIBUTING.md) has the steps.

## Modules

| | Phase | |
|---|---|---|
| 00 | Onboarding | One pull request, reviewed and merged. |
| 01–03 | Fundamentals | `Layer`, `Linear`, `Sequential`, then autograd, then a training loop. NumPy only. |
| 04–05 | PyTorch | The same model in PyTorch, then configs, seeds and run directories. |
| 06–11 | LLM from scratch | Tokenizer, attention, GPT, pretraining, fine-tuning. Follows [Raschka's book](https://sebastianraschka.com/llms-from-scratch/), a chapter each. |
| 12–14 | Research | Reproduce a result, evaluate it, then LoRA / DPO / GRPO. |

Each module has **core** checks that have to pass and **stretch** checks that don't.

Modules 02 onwards are stubs. [Writing one](CONTRIBUTING.md#writing-a-module) is a good way to learn
the material properly.

## Layout

```
modules/01-oop-refresher/
  TASK.md        what to build
  starter/nn.py  skeleton with TODOs - copy it, don't edit it
  checks.py      the checks, by name
  tests/         hands checks.py to pytest

submissions/
  your-handle/01-oop-refresher/nn.py     your work, and only yours

docs/            the site
gym/             shared helpers (seeding, toy data, the Check type)
```

Each check is written once, in `checks.py`. CI runs it through pytest; the
[playground](https://REPLACE-ME.github.io/research-gym/playground.html) runs the same file in your
browser via Pyodide. They can't disagree.

Everyone works in their own folder under `submissions/`, so nobody hits a merge conflict and
everyone can read everyone else's solution once it's merged.

## Rules

- One module per pull request.
- Only edit files in `submissions/<your-handle>/`.
- Don't edit `checks.py` or `tests/`. If a check looks wrong, open an issue.
- Review someone else's pull request each week.

The check enforces the first three and explains itself if you trip one.

## Local setup

Optional. The pull request is the test runner.

```bash
pip install -e ".[checks]"
SUBMISSION_DIR=submissions/your-handle/01-oop-refresher pytest modules/01-oop-refresher/tests
```

[ENVIRONMENT.md](ENVIRONMENT.md) covers the rest: venv/uv/conda, Windows commands, pytest flags,
serving the site, troubleshooting.

Setting up a fresh copy of this repo: [SETUP.md](SETUP.md).

## Licence

[MIT](LICENSE). The book isn't included - buy it.
