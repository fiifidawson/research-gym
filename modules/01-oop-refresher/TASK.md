# 01 · OOP refresher

**Build:** `Layer`, `Linear`, `ReLU`, `Sequential` and `num_parameters`, in NumPy.
**Submit:** `submissions/<your-handle>/01-oop-refresher/nn.py`
**Starter:** [`starter/nn.py`](starter/nn.py) · **Checks:** [`checks.py`](checks.py) · [practise in the browser](https://REPLACE-ME.github.io/research-gym/playground.html?module=01-oop-refresher)

---

## Why this matters

Eight of us filled in the skills survey and eight of us put "Intermediate" next to
object-oriented programming. Nobody put Advanced. That is not a coincidence — OOP is the thing
most people learn just well enough to read and never quite well enough to design with.

It matters here specifically, because every deep learning framework is one idea:

> A model is an object that holds parameters and knows how to turn an input into an output.
> A model made of models is the same kind of object.

`torch.nn.Module` is that sentence, plus a decade of engineering. If you build the small version
yourself this week, PyTorch in module 04 will feel like a library rather than a mystery, and the
transformer block in module 08 will be forty lines instead of a wall.

You are writing the forward pass only. Gradients are module 02 — resist the urge.

## Read first

Twenty minutes, not two hours. Skim, build, come back when something bites.

- [The Python data model](https://docs.python.org/3/reference/datamodel.html#special-method-names) —
  `__call__`, `__repr__`, `__len__`, `__getitem__`. Most of this module lives on that page.
- [`abc` — abstract base classes](https://docs.python.org/3/library/abc.html) — why `Layer()` should refuse.
- [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) — why `x @ W + b` works.
- [NumPy random generators](https://numpy.org/doc/stable/reference/random/generator.html) — why `default_rng(seed)`
  and not `np.random.randn`.

## Build this (core)

Copy `starter/nn.py` to your folder and work through the TODOs. Keep every name identical — the
checks look them up by name, and module 02 imports this file.

1. **`Layer`** — abstract. `forward` is abstract; `__call__`, `parameters()` and `__repr__` are
   written *once* here and inherited. If you find yourself writing `__call__` in three subclasses,
   that is the lesson knocking.
2. **`Linear(in_features, out_features, *, seed=None)`** — `W` of shape `(in, out)`, `b` of zeros.
   He initialisation, standard deviation `sqrt(2 / in_features)`, drawn from
   `np.random.default_rng(seed)`. `forward` returns `x @ W + b`. `parameters()` returns `[W, b]`.
   `__repr__` returns exactly `Linear(in_features=3, out_features=2)`.
3. **`ReLU`** — returns a *new* array. No parameters; it should not need to say so.
4. **`Sequential(*layers)`** — is a `Layer`, contains `Layer`s. Chains `forward`, flattens
   `parameters()`, supports `len()` and `model[i]`, and its `repr` is built from its children's.
5. **`num_parameters(layer)`** — a plain function. Works on a `Linear` and on a `Sequential`
   without knowing which it got.

**Why the seed is a check and not a footnote:** five of the eight of us rated reproducible
experiments Beginner or None. `np.random.randn` reads a hidden global; two people running your code
get two answers and neither knows. Every module from here on seeds explicitly.

## Stretch

Optional. Take them if module 01 was comfortable — and if it was, consider reviewing someone else's
pull request this week, which is worth more than any of these.

- `Tanh` — you now know where it goes and what it inherits.
- `LayerNorm(dim, eps=1e-5)` — `gamma` and `beta` as parameters, normalising the last axis. You will
  build this again in PyTorch in module 08; transformers are full of it.
- `Sequential.__iter__` — so `for layer in model:` reads the way it should.

## How you'll know it works

Open the pull request. A check runs and comments with every item above, passed or failed, in
English. Push again and the comment updates. When all 18 core checks are green, ask for a review.

Impatient? The [browser playground](https://REPLACE-ME.github.io/research-gym/playground.html?module=01-oop-refresher) runs the
identical checks with no round trip — it is literally the same `checks.py` file.

**Done means:** 18/18 core, one approving review, merged. Stretch checks never block a merge.

## If you want a local setup

Optional, and it changes nothing about what counts — but [ENVIRONMENT.md](../../ENVIRONMENT.md)
has it: install, run the checks the way CI does, and a troubleshooting table.

## Where this goes next

Module 02 gives every operation in this file a backward pass, and you will import `nn.py` to do it.
Module 04 replaces all of it with six lines of PyTorch — and you will know exactly what those six
lines are doing.
