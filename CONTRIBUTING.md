# Contributing

Everything goes through a pull request: module work, a fix to a task, a link worth reading.

You don't need a terminal. The steps below are browser and editor buttons, with the equivalent
commands folded underneath. If you want a local setup anyway, see [ENVIRONMENT.md](ENVIRONMENT.md).

## Submitting a module

**1. Branch.** Name it `<your-handle>/<module-id>`, e.g. `nthabiseng/01-oop-refresher`.

On github.com: branch dropdown → type the name → Create branch.

<details><summary>Terminal</summary>

```bash
git switch main && git pull
git switch -c nthabiseng/01-oop-refresher
```
</details>

**2. Write your file**, at `submissions/<your-handle>/<module-id>/<entrypoint>` — for module 01 that
is `submissions/nthabiseng/01-oop-refresher/nn.py`. Copy the module's starter, keep the filename.

Press <kbd>.</kbd> on any repo page for [github.dev](https://github.dev), an editor in your browser.

Leave the starter itself alone so the next person gets a clean copy.

**3. Commit and push.** In github.dev or VS Code: Source Control panel, message, ✓, then Sync.

<details><summary>Terminal</summary>

```bash
git add submissions/nthabiseng/01-oop-refresher
git commit -m "add Linear and ReLU"
git push -u origin nthabiseng/01-oop-refresher
```
</details>

**4. Open the pull request.** Fill in the template. Within a minute a comment appears listing every
check by name, with the error and a hint for the ones that failed. Push again and that comment
updates. Push as often as you like.

**5. Get a review, then merge.** One approval. While you're waiting, review someone else's.

## Rules

| Rule | Why |
|---|---|
| One module per pull request | Easier to review, and you get better feedback. |
| Only touch `submissions/<your-handle>/` | Nobody can break anybody else's work. |
| Don't edit `checks.py` or `tests/` | They're the shared definition of done. |
| Don't mix module work with repo changes | Two purposes, two pull requests. |

The check enforces all four and says which one you tripped.

If a check looks wrong — it happens — open an issue with the `bug` template. Fixing it is a real
contribution and gets its own pull request.

## Style

`ruff` runs on the files your pull request touched, nothing else. Type hints on public functions, a
docstring when the code doesn't say why, names matching the starter. `ruff format` settles the rest.

## Reviewing

If you've never reviewed code, start here and then do it badly once.

Two comments is a good review: one thing that works, one thing that could be better.

Ask rather than assert. "What happens if `x` is 1-D here?" gets a better result than "this is wrong".

Comment on the code, not the person.

Worth looking for, roughly in order:

1. Does it do what `TASK.md` asked? The checks cover the letter; you're reading for the rest.
2. Would you understand it in six months?
3. Is anything repeated that the base class could do once?
4. Is anything random unseeded?

Approve when it's good enough, not when it's what you'd have written.

Being reviewed: it's about the code. You don't have to take every suggestion — say why. "I don't
understand this comment" is a fine thing to say.

## Adding a reading

Add an entry to [`docs/data/reading.json`](docs/data/reading.json):

```json
{
  "module": "02-autograd",
  "title": "The spelled-out intro to neural networks and backpropagation",
  "url": "https://www.youtube.com/watch?v=VMj-3S1tku0",
  "source": "Andrej Karpathy",
  "kind": "video",
  "minutes": 145,
  "why": "Module 02 is this video, done yourself."
}
```

`module` can be `general`. Say what it's good *for* in `why`, not what it's about. It shows on the
reading page when merged.

## Writing a module

Modules 02 onwards are stubs. Writing one is the best way to learn that material properly. Say so in
an issue and we'll pair you with someone who's done it.

A module is four things:

```
modules/NN-name/
  TASK.md        what you're building · why · read first · core · stretch · checking it
  starter/       skeleton with TODOs pointing at the idea, not the answer
  checks.py      a CheckSuite of named checks
  tests/         copy module 01's test_module.py verbatim; it's module-agnostic
```

Then add it to [`docs/data/curriculum.json`](docs/data/curriculum.json) with `"status": "ready"`.

Writing the checks is most of the work:

- Name each one as a sentence: `"ReLU zeroes negative values"`, not `"test_relu_2"`. The name goes
  on the pull request unedited.
- Use the helpers in [`gym/checks.py`](gym/checks.py) — `assert_shape`, `assert_close`, `require`.
  They produce messages like *"Linear.W should have shape (3, 2), got (2, 3)"*. A bare `assert`
  produces nothing useful.
- Mark optional checks `STRETCH`.
- Add a `hint` pointing at the concept, not the answer.
- Set `browser: true` in the curriculum only for NumPy-only modules. PyTorch can't run in Pyodide.

Write a reference solution, confirm it passes, then break it three ways and read the failure
messages as if you were stuck. If one doesn't tell you what to do next, it isn't finished.

## Asking for help

Open an issue with the `module-help` template: which module, what you tried, what you expected.
