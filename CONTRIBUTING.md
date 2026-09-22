# Contributing

Everything here happens through pull requests — your module work, a fix to a task description, a
link you think people should read. This page is the whole process.

**You do not need a terminal.** The default path below is browser and editor buttons. Every step has
the equivalent command folded underneath if you would rather type it, and some of us would.

Want a local environment anyway? [ENVIRONMENT.md](ENVIRONMENT.md) — optional, and it changes
nothing about what counts.

---

## Submitting a module

### 1. Make a branch

Name it `<your-handle>/<module-id>`, e.g. `nthabiseng/01-oop-refresher`.

On github.com: the branch dropdown on the repo's front page → type the name → **Create branch**.

<details><summary>Same thing, in a terminal</summary>

```bash
git switch main && git pull
git switch -c nthabiseng/01-oop-refresher
```
</details>

### 2. Write your file

Copy the module's starter into **your** folder:

```
submissions/<your-handle>/<module-id>/<entrypoint>
```

So for module 01, `submissions/nthabiseng/01-oop-refresher/nn.py`. Keep the filename exactly as the
starter has it; the checks look it up by name.

Press <kbd>.</kbd> on any repo page to open [github.dev](https://github.dev), a full editor in your
browser — no clone, no install. Or use VS Code, or anything else.

Leave the starter itself alone, so the next person gets a clean copy.

### 3. Commit and push

In github.dev or VS Code, use the **Source Control** panel: type a message, hit the ✓, then
**Sync / Publish branch**.

Keep messages short and in the imperative — `add Linear and ReLU`, not `added stuff`.

<details><summary>Same thing, in a terminal</summary>

```bash
git add submissions/nthabiseng/01-oop-refresher
git commit -m "add Linear and ReLU"
git push -u origin nthabiseng/01-oop-refresher
```
</details>

### 4. Open the pull request

GitHub will offer a **Compare & pull request** button. Fill in the template — it asks four
questions and they take two minutes.

Within a minute, a comment appears listing every check by name, passed or failed, with the error and
a nudge for the ones that failed. **Push again and that same comment updates.** There is no limit on
how many times you push; that is what it is for.

Want feedback faster? The [playground](https://REPLACE-ME.github.io/research-gym/playground.html) runs the identical checks in your
browser, instantly.

### 5. Get a review, then merge

When the core checks are green, request a review. One approval merges it.

While you wait, **review somebody else's**. That is not a nicety — it is half the curriculum.

---

## The rules, and why

| Rule | Why |
|---|---|
| One module per pull request | A reviewer gives useful feedback on forty lines and says "looks good" to four hundred. |
| Only touch `submissions/<your-handle>/` | Nobody can break anybody else's work. Suggestions for someone's code go in a review comment on their PR. |
| Don't edit `checks.py` or `tests/` | They are the shared definition of done. Changing them in your PR just moves the goalposts. |
| Don't mix module work with repo changes | Two purposes, two pull requests. |

All four are enforced by the check, which explains itself rather than just failing.

**If you think a check is wrong** — and occasionally one is — open an issue with the `bug` template
and say what you expected. Fixing a bad check is a real contribution and gets its own pull request.

## Style

`ruff` runs on the files you touched, and only those, so nobody is blocked by a lint error elsewhere.

- Type hints on anything public.
- A docstring saying *why*, when the *what* isn't obvious from the code.
- Names that match the starter exactly.

Don't fight the formatter. `ruff format` settles arguments so reviews can be about the ideas.

## How to give a review that helps

Four of us said in the survey that we couldn't review someone's code today. If that's you, this is
the section to read — and then go and do it badly once, which is how everybody starts.

**Aim for two comments.** One thing that works, one thing that could be better. That's a good review.

**Ask instead of assert.** "What happens if `x` is 1-D here?" invites them to look. "This is wrong"
invites them to defend. The first one finds more bugs.

**Review the code, never the person.** "This allocates a new array each call" — not "you always
forget about allocation".

**Things worth looking for, roughly in order:**

1. Does it do what `TASK.md` asked? The checks cover the letter; you're reading for the spirit.
2. Would you understand this in six months? Names, shapes, a comment where it earns its place.
3. Is anything repeated that the base class could do once? This is module 01's whole point.
4. Is anything random unseeded? That one will bite them in module 05.

**Approve when it's good enough**, not when it's what you would have written. There is a next module.

**Getting reviewed:** assume good faith, it's about the code. You don't have to take every
suggestion — say why, and that's a normal conversation. And "I don't understand this comment" is
always a fine thing to say.

## Adding a reading

The smallest useful contribution, and it counts. Add an entry to
[`docs/data/reading.json`](docs/data/reading.json):

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

`module` can be `general`. The `why` is the important field — say what it's good *for*, not what
it's about. Open a pull request; it appears on the [reading page](https://REPLACE-ME.github.io/research-gym/reading.html) on merge.

## Writing a module

Modules 02 onwards are stubs waiting for an author. Writing one teaches you the material twice and
is the most valuable thing you can do here. Say so in an issue and we'll pair you with someone who
has done that material before.

A module is four things:

```
modules/NN-name/
  TASK.md        Why this matters · Read first · Build this (core) · Stretch · How you'll know
  starter/       a skeleton with TODOs that point at the idea, never the answer
  checks.py      a CheckSuite of named checks
  tests/         copy module 01's test_module.py verbatim — it is module-agnostic
```

Then add the module to [`docs/data/curriculum.json`](docs/data/curriculum.json) and set
`"status": "ready"` when it's done.

**Writing good checks** is most of the work:

- **Name each check as a sentence a beginner can act on.** `"ReLU zeroes negative values"`, not
  `"test_relu_2"`. That name appears on their pull request, unedited.
- **Use the helpers in [`gym/checks.py`](gym/checks.py)** — `assert_shape`, `assert_close`,
  `require`. They produce messages like *"Linear.W should have shape (3, 2), got (2, 3)"*. A bare
  `assert` produces nothing anyone can use.
- **Mark a check `STRETCH`** if it's optional. Stretch never blocks a merge.
- **Add a `hint`** that points at the concept, not the answer: `"__len__ and __getitem__"` — not the
  implementation.
- **Set `browser: true` in the curriculum** only if the module is NumPy-only. PyTorch can't run in
  Pyodide.

Write a reference solution and check it passes, then break it three ways and read the failure
messages as if you were stuck. If a message doesn't tell you what to do next, it isn't finished.

## Asking for help

Open an issue with the **module-help** template. Say which module, what you tried, and what you
expected — writing that down solves it about a third of the time, and when it doesn't, it gets you a
much better answer.

Getting stuck is not a status report on your ability. Everyone here put "Intermediate" next to
something.
