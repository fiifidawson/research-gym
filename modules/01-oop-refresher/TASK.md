# 01 · OOP refresher

**Submit:** `submissions/<your-handle>/01-oop-refresher/nn.py`
**Starter:** [`starter/nn.py`](starter/nn.py) · **Checks:** [`checks.py`](checks.py)

## What you're building

The forward pass of a small neural network, in NumPy, built out of classes: `Layer`, `Linear`,
`ReLU`, `Sequential`, and a `num_parameters` function.

No gradients. That's module 02.

## Why

Every deep learning framework rests on one idea: a model is an object that holds parameters and
turns an input into an output, and a model made of models is the same kind of object.
`torch.nn.Module` is that, with a lot of engineering on top.

Build the small version now and PyTorch in module 04 is an API to learn rather than a new concept.
The transformer block in module 08 is this same `Sequential` pattern.

## Read first

- [Python data model](https://docs.python.org/3/reference/datamodel.html#special-method-names) -
  `__call__`, `__repr__`, `__len__`, `__getitem__`.
- [`abc`](https://docs.python.org/3/library/abc.html) - abstract base classes.
- [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) - why `x @ W + b` works.
- [NumPy random generators](https://numpy.org/doc/stable/reference/random/generator.html) - `default_rng`.

## Core

Copy `starter/nn.py` into your folder and work through the TODOs. Keep the names exactly as given -
the checks look them up by name, and module 02 imports this file.

1. **`Layer`** - abstract. `forward` is abstract. `__call__`, `parameters()` and `__repr__` are
   defined here once and inherited.
2. **`Linear(in_features, out_features, *, seed=None)`** - `W` of shape `(in, out)`, `b` of zeros.
   He init, std `sqrt(2 / in_features)`, from `np.random.default_rng(seed)`. `forward` returns
   `x @ W + b`. `parameters()` returns `[W, b]`. `__repr__` is exactly
   `Linear(in_features=3, out_features=2)`.
3. **`ReLU`** - returns a new array, doesn't modify its input.
4. **`Sequential(*layers)`** - is a `Layer` and contains `Layer`s. Chains `forward`, flattens
   `parameters()`, supports `len()` and indexing, builds its `repr` from its children's.
5. **`num_parameters(layer)`** - a function. Works on a `Linear` or a `Sequential` without knowing
   which one it got.

Use `default_rng(seed)`, not `np.random.randn`. The latter reads a global, so the same `seed=`
argument gives different weights on different runs. One of the checks tests for this.

## Stretch

Optional, doesn't block a merge.

- `Tanh`
- `LayerNorm(dim, eps=1e-5)` - `gamma` and `beta` as parameters, normalising the last axis. You'll
  build it again in PyTorch in module 08.
- `Sequential.__iter__`

## Checking it

Open the pull request. The check comments with every item above, passed or failed. Push again and
the comment updates. 18 core checks; when they're all green, ask for a review.

For instant feedback, the Playground page on the site runs the same `checks.py` in your browser.

**Done:** 18/18 core, one approval, merged.

## Next

Module 02 adds a backward pass to everything here, and imports this file. Module 04 replaces it with
a few lines of PyTorch.
