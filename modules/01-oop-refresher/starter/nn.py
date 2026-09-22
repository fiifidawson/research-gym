"""Module 01 - the forward pass of a neural network, built out of classes.

Copy this to `submissions/<your-handle>/01-oop-refresher/nn.py` and fill in the
TODOs there. Leave this starter alone so the next person gets a clean copy.

Keep every class, argument and attribute name as written. The checks look them
up by name, and module 02 imports this file.
"""

from __future__ import annotations

import numpy as np

# =============================================================================
# 1. Base class
# =============================================================================


class Layer:
    """Anything that turns an array into another array.

    TODO: make this abstract, so `Layer()` raises TypeError and a subclass that
    forgets `forward` fails loudly. Inherit from `abc.ABC`, decorate `forward`
    with `@abstractmethod`.

    TODO: add `__call__`, so `layer(x)` runs `layer.forward(x)`. Write it here
    once and every subclass inherits it.

    TODO: add `parameters()` returning an empty list. Layers with weights
    override it.

    TODO: add `__repr__` returning the class name plus empty brackets, e.g.
    `ReLU()`. `Linear` will override it.
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
        seed: Seed for the weight initialisation. The same seed has to give the
            same weights.
    """

    def __init__(self, in_features: int, out_features: int, *, seed: int | None = None) -> None:
        # TODO: store in_features and out_features - __repr__ needs them.
        #
        # TODO: build `self.W`, shape (in_features, out_features), and `self.b`,
        # shape (out_features,).
        #   - b starts at zero
        #   - W is drawn from `np.random.default_rng(seed).normal(...)` with
        #     standard deviation sqrt(2 / in_features), which is He init
        #   - not np.random.randn: it reads a global seed, so the `seed=`
        #     argument above would have no effect
        raise NotImplementedError

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: x @ W + b. NumPy broadcasts b across the batch.
        raise NotImplementedError

    def parameters(self) -> list[np.ndarray]:
        # TODO: both arrays, weights first.
        raise NotImplementedError

    def __repr__(self) -> str:
        # TODO: exactly `Linear(in_features=3, out_features=2)`.
        raise NotImplementedError


# =============================================================================
# 3. A layer without weights
# =============================================================================


class ReLU(Layer):
    """Zero out negatives, keep everything else."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: return a new array. `x[x < 0] = 0` modifies the caller's array.
        raise NotImplementedError


# =============================================================================
# 4. A layer made of layers
# =============================================================================


class Sequential(Layer):
    """Runs the layers it holds, front to back.

    A Sequential is a Layer and contains Layers. That is how every framework
    composes a model, and how you'll assemble a transformer block in module 08.
    """

    def __init__(self, *layers: Layer) -> None:
        # TODO: keep the layers. Note the *args - Sequential(a, b, c).
        raise NotImplementedError

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: feed x through each layer in turn.
        raise NotImplementedError

    def parameters(self) -> list[np.ndarray]:
        # TODO: one flat list of every child's parameters, in order.
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO: len(model)
        raise NotImplementedError

    def __getitem__(self, index: int) -> Layer:
        # TODO: model[0]
        raise NotImplementedError

    def __repr__(self) -> str:
        # TODO: exactly
        # `Sequential(Linear(in_features=2, out_features=4), ReLU(), Linear(in_features=4, out_features=1))`
        # Reuse the children's repr rather than rebuilding their text.
        raise NotImplementedError


# =============================================================================
# 5. A function
# =============================================================================


def num_parameters(layer: Layer) -> int:
    """Total number of individual values a layer is holding.

    TODO: sum `.size` over `layer.parameters()`. Works for any Layer, including
    a Sequential, because they all answer `parameters()`.
    """
    raise NotImplementedError


# =============================================================================
# 6. Stretch - optional
# =============================================================================


class Tanh(Layer):
    """TODO (stretch): np.tanh, as a Layer."""


class LayerNorm(Layer):
    """TODO (stretch): normalise each row to zero mean and unit variance.

    Args:
        dim: Size of the last axis.
        eps: Added inside the square root so a constant row can't divide by zero.

    Store `self.gamma` (ones, shape (dim,)) and `self.beta` (zeros, shape (dim,)),
    return both from `parameters()`, and compute
    `gamma * (x - mean) / sqrt(var + eps) + beta` over the last axis.
    """


# TODO (stretch): give Sequential an `__iter__` so `for layer in model:` works.


if __name__ == "__main__":
    # Scratch space. Nothing here is checked.
    model = Sequential(Linear(2, 4, seed=0), ReLU(), Linear(4, 1, seed=1))
    print(model)
    print("parameters:", num_parameters(model))
    print("output:", model(np.zeros((3, 2))))
