# 03 · The training loop

**Submit:** `submissions/<your-handle>/03-training-loop/train.py`
**Starter:** [`starter/train.py`](starter/train.py) · **Checks:** [`checks.py`](checks.py)

## What you're building

Everything around a model that makes it learn: a config, a `Dataset`, a `DataLoader`, an `SGD`
optimizer and a `Trainer`. At the end, one call to `train(config)` fits a small network to the
two-moons dataset and tells you how well it did.

The network itself, `MLP`, is given to you, gradients included. You wrote the idea of those in
module 02; this module is about the bookkeeping around them.

## Why

A training loop is a little maths wrapped in a lot of bookkeeping. Most of the bugs in real
experiments live in the bookkeeping: a shuffle that isn't seeded, a gradient nobody cleared, a
learning rate that drifted. Write it once, by hand, and you can debug anyone's.

`torch.utils.data.DataLoader`, `torch.optim.SGD` and a Lightning-style `Trainer` are these same
classes with more engineering. In module 04 they stop being new ideas and become an API.

## Read first

- [Iterator types](https://docs.python.org/3/library/stdtypes.html#iterator-types) - what `__iter__`
  promises, and why a class can be looped over more than once.
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) - especially `frozen=True`.
- [NumPy random generators](https://numpy.org/doc/stable/reference/random/generator.html) - the
  state of a `Generator` moves forward every time you draw from it.
- Karpathy's [micrograd](https://github.com/karpathy/micrograd) - the training loop at the end of
  its demo is the loop you're about to write.

## Core

Copy `starter/train.py` into your folder and work through the TODOs. Keep the names exactly as
given - the checks look them up by name.

1. **`TrainConfig`** - a *frozen* dataclass with `lr`, `epochs`, `batch_size` and `seed`. Changing
   a field after the fact raises an error.
2. **`Dataset(X, y)`** - `len(ds)` is the number of samples; `ds[i]` is the pair `(X[i], y[i])`.
3. **`DataLoader(dataset, batch_size, *, shuffle=True, seed=None)`** - `for X_batch, y_batch in
   loader:` gives one epoch of arrays, `batch_size` rows at a time, the last batch possibly
   smaller. `len(loader)` is the number of batches. With a seed, the shuffle is reproducible, yet a
   new epoch comes in a new order.
4. **`SGD(parameters, gradients, lr)`** - `step()` moves each parameter against its gradient, in
   place. `zero_grad()` sets each gradient to zero, in place.
5. **`Trainer(model, optimizer, config)`** - `fit(loader)` runs `config.epochs` epochs and returns
   the mean training loss of each. `evaluate(X, y)` returns accuracy.
6. **`train(config)`** - wires it all together: seeds, data, split, model, optimizer, trainer. Same
   config in, same numbers out.

Two things to hold on to while you write:

- The model **adds** its gradients into the arrays it owns, the way `+=` does in your module 02
  `backward()`. If nobody resets them between steps, each step uses the sum of every step so far.
- A random generator has memory. Where you create it decides whether epoch two repeats epoch one.

## Stretch

Optional, doesn't block a merge.

- `DataLoader(..., drop_last=True)` - throw away the smaller final batch.
- `SGD(..., momentum=0.9)` - keep a velocity per parameter.

## Checking it

Open the pull request. The check comments with every item above, passed or failed. Push again and
the comment updates. 21 core checks; when they're all green, ask for a review.

For instant feedback, the Playground page on the site runs the same `checks.py` in your browser.

The Trainer checks run your loop against a tiny fake model, so a bug in your `SGD` can't hide a bug
in your `Trainer`. Read [`checks.py`](checks.py); it's the spec.

**Done:** 21/21 core, one approval, merged.

## Next

Module 04 rebuilds the same `MLP` as an `nn.Module` and checks it against the result you get here.
