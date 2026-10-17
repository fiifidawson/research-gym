"""Module 01 - the forward pass of a neural network, built out of classes.

Copy this to `submissions/<your-handle>/01-oop-refresher/nn.py` and fill in the
TODOs there. Leave this starter alone so the next person gets a clean copy.

Keep every class, argument and attribute name as written. The checks look them
up by name, and module 02 imports this file.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

# =============================================================================
# 1. Base class
# =============================================================================


class Layer(ABC):
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

    def __call__(self, x: np.ndarray):
        return self.forward(x)

    def parameters(self) -> list[np.ndarray]:
        return []

    def __repr__(self,):
        return f"{self.__class__.__name__}()"

    @abstractmethod
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Run this layer on a batch of inputs, shape (batch, features)."""
        pass


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
        self.in_features = in_features
        self.out_features = out_features
        self.W = np.random.default_rng(seed).normal(
            loc=0,
            scale=np.sqrt(2 / self.in_features),
            size=(in_features, out_features)
        )
        self.b = np.zeros(out_features)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: x @ W + b. NumPy broadcasts b across the batch.
        return x @ self.W + self.b

    def parameters(self) -> list[np.ndarray]:
        # TODO: both arrays, weights first.
        return [self.W, self.b]

    def __repr__(self) -> str:
        # TODO: exactly `Linear(in_features=3, out_features=2)`.
        return f"{self.__class__.__name__}(in_features={self.in_features}, out_features={self.out_features})"


# =============================================================================
# 3. A layer without weights
# =============================================================================


class ReLU(Layer):
    """Zero out negatives, keep everything else."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: return a new array. `x[x < 0] = 0` modifies the caller's array.
        return np.maximum(x, 0, out=x)


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
        self.layers = layers

    def forward(self, x: np.ndarray) -> np.ndarray:
        # TODO: feed x through each layer in turn.
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self) -> list[np.ndarray]:
        # TODO: one flat list of every child's parameters, in order.
        return [param for layer in self.layers for param in layer.parameters()]

    def __len__(self) -> int:
        # TODO: len(model)
        return len(self.layers)

    def __getitem__(self, index: int) -> Layer:
        # TODO: model[0]
        return self.layers[index]

    def __repr__(self) -> str:
        # TODO: exactly
        # `Sequential(Linear(in_features=2, out_features=4), ReLU(), Linear(in_features=4, out_features=1))`
        # Reuse the children's repr rather than rebuilding their text.
        return f"{self.__class__.__name__}({", ".join([str(layer) for layer in self.layers])})"


# =============================================================================
# 5. A function
# =============================================================================


def num_parameters(layer: Layer) -> int:
    """Total number of individual values a layer is holding.

    TODO: sum `.size` over `layer.parameters()`. Works for any Layer, including
    a Sequential, because they all answer `parameters()`.
    """
    return sum([param.size for param in layer.parameters()])


# =============================================================================
# 6. Stretch - optional
# =============================================================================


class Tanh(Layer):
    """TODO (stretch): np.tanh, as a Layer."""
    def forward(self, x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

class LayerNorm(Layer):
    """TODO (stretch): normalise each row to zero mean and unit variance.

    Args:
        dim: Size of the last axis.
        eps: Added inside the square root so a constant row can't divide by zero.

    Store `self.gamma` (ones, shape (dim,)) and `self.beta` (zeros, shape (dim,)),
    return both from `parameters()`, and compute
    `gamma * (x - mean) / sqrt(var + eps) + beta` over the last axis.
    """
    def __init__(self, dim: int, eps: float | None = 0.01) -> None:
        self.dim = dim
        self.eps = eps
        self.gamma = np.ones(dim)
        self.beta = np.zeros(dim)

    def parameters(self) -> list[np.ndarray]:
        return [self.gamma, self.beta]

    def __repr__(self,):
        return f"{self.__class__.__name__}(dim={self.dim}, eps={self.eps})"

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Run this layer on a batch of inputs, shape (batch, features)."""
        return self.gamma * (x - x.mean(axis=-1, keepdims=True)) / np.sqrt(x.var(axis=-1, keepdims=True) + self.eps) + self.beta


# TODO (stretch): give Sequential an `__iter__` so `for layer in model:` works.
class Sequential(Sequential):

    def __iter__(self,):
        for layer in self.layers:
            yield layer

if __name__ == "__main__":
    # Scratch space. Nothing here is checked.
    model = Sequential(Linear(2, 4, seed=0), ReLU(), Linear(4, 1, seed=1))
    print(model)
    print("parameters:", num_parameters(model))
    print("output:", model(np.zeros((3, 2))))
