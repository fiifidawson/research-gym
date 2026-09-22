"""Module 01 - a neural network's forward pass, built out of classes.

Copy this file to `submissions/<your-handle>/01-oop-refresher/nn.py` and fill in
the TODOs there. Leave this starter alone so the next person gets a clean copy.

Keep every class name, argument name and attribute name exactly as written. The
checks look them up by name, and so will module 02, which builds on this file.
"""

from __future__ import annotations

import numpy as np

# =============================================================================
# 1. The base class
# =============================================================================


class Layer:
    """Anything that turns an array into another array.

    TODO: make this abstract, so that `Layer()` raises TypeError and a subclass
    that forgets `forward` fails loudly instead of silently.
        - inherit from `abc.ABC`
        - decorate `forward` with `@abstractmethod`

    TODO: give it `__call__`, so `layer(x)` runs `layer.forward(x)`. Write it
    once, here - every subclass inherits it for free. That is the whole point of
    a base class, and it is exactly what `torch.nn.Module` does.

    TODO: give it `parameters()` returning an empty list. Layers with weights
    will override it; layers without weights already have the right answer.

    TODO: give it `__repr__` returning something like `ReLU()` - the class name
    followed by empty brackets. `Linear` will override this.
    """

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Run this layer on a batch of inputs, shape (batch, features)."""
        raise NotImplementedError


# =============================================================================
# 2. A layer with weights
# =============================================================================


class Linear(Layer):
    """The affine map `x @ W + b`.

    Args:
        in_features: Size of each input row.
        out_features: Size of each output row.
        seed: Seed for the weight initialisation. Passing a seed has to make the
            weights reproducible - that is not a detail, it is the difference
            between an experiment you can rerun and one you cannot.
    """

    def __init__(self, in_features: int, out_features: int, *, seed: int | None = None) -> None:
        # TODO: store in_features and out_features, you need them for __repr__.
        #
        # TODO: build `self.W` with shape (in_features, out_features) and
        # `self.b` with shape (out_features,).
        #   - biases start at zero
        #   - weights start random, drawn with
        #     `np.random.default_rng(seed).normal(...)`. Use a standard
        #     deviation of sqrt(2 / in_features) - that is He initialisation,
        #     and you will meet the reason it matters in module 03.
        #   - do NOT use np.random.randn: it reads a hidden global seed, so the
        #     same `seed=` argument would give you different weights.
        raise NotImplementedError

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: return x @ W + b. NumPy broadcasts the bias across the batch.
        raise NotImplementedError

    def parameters(self) -> list[np.ndarray]:
        # TODO: return both arrays, weights first.
        raise NotImplementedError

    def __repr__(self) -> str:
        # TODO: exactly `Linear(in_features=3, out_features=2)`.
        raise NotImplementedError


# =============================================================================
# 3. A layer without weights
# =============================================================================


class ReLU(Layer):
    """Zero out the negatives, keep everything else."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: return a NEW array. `x[x < 0] = 0` edits the caller's array,
        # which is the kind of bug that costs an afternoon.
        raise NotImplementedError


# =============================================================================
# 4. A layer made of layers
# =============================================================================


class Sequential(Layer):
    """Runs the layers it holds, front to back.

    A Sequential *is* a Layer and *contains* Layers. Being comfortable with that
    sentence is most of what module 01 is for: it is how every deep learning
    framework composes a model, and it is how you will assemble a transformer
    block in module 08.
    """

    def __init__(self, *layers: Layer) -> None:
        # TODO: keep the layers. Note the *args - `Sequential(a, b, c)`.
        raise NotImplementedError

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: feed x through each layer in turn and return the result.
        raise NotImplementedError

    def parameters(self) -> list[np.ndarray]:
        # TODO: one flat list holding every child layer's parameters, in order.
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO: so that len(model) works.
        raise NotImplementedError

    def __getitem__(self, index: int) -> Layer:
        # TODO: so that model[0] works.
        raise NotImplementedError

    def __repr__(self) -> str:
        # TODO: exactly
        # `Sequential(Linear(in_features=2, out_features=4), ReLU(), Linear(in_features=4, out_features=1))`
        # Reuse the children's own repr rather than rebuilding their text.
        raise NotImplementedError


# =============================================================================
# 5. A function, because not everything needs to be a class
# =============================================================================


def num_parameters(layer: Layer) -> int:
    """Total number of individual numbers a layer is carrying around.

    TODO: sum `.size` over `layer.parameters()`. Works for any Layer, including
    a Sequential, because they all answer `parameters()` - that is polymorphism
    doing something useful rather than something from a textbook.
    """
    raise NotImplementedError


# =============================================================================
# 6. Stretch - skip these if you are short on time, they are not required
# =============================================================================


class Tanh(Layer):
    """TODO (stretch): np.tanh, in the shape of a Layer."""


class LayerNorm(Layer):
    """TODO (stretch): normalise each row to zero mean and unit variance.

    Args:
        dim: Size of the last axis.
        eps: Added inside the square root so a constant row cannot divide by zero.

    Store `self.gamma` (ones, shape (dim,)) and `self.beta` (zeros, shape (dim,)),
    return both from `parameters()`, and compute
    `gamma * (x - mean) / sqrt(var + eps) + beta` over the last axis.

    You will build this again in PyTorch in module 08. Transformers are full of it.
    """


# TODO (stretch): give Sequential an `__iter__` so `for layer in model:` works.


if __name__ == "__main__":
    # A scratch space for you. Nothing here is checked - run it however you like.
    model = Sequential(Linear(2, 4, seed=0), ReLU(), Linear(4, 1, seed=1))
    print(model)
    print("parameters:", num_parameters(model))
    print("output:", model(np.zeros((3, 2))))
