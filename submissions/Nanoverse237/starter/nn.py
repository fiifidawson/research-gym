"""Module 01: a forward pass built from composable layers.

This is a separate solution; the supplied starter is left unchanged.
The optional Tanh, LayerNorm, and iteration exercises are included.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

import numpy as np


class Layer(ABC):
    """Common interface for anything that maps an array to another array."""

    @abstractmethod
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Subclasses must supply their own forward computation."""
        raise NotImplementedError

    def __call__(self, x: np.ndarray) -> np.ndarray:
        # Python calls this method when you write layer(x).
        # self.forward selects the implementation on the actual subclass.
        return self.forward(x)

    def parameters(self) -> list[np.ndarray]:
        # A layer without trainable arrays has nothing to return.
        return []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Linear(Layer):
    """An affine transformation: a weighted sum plus a bias."""

    def __init__(self, in_features: int, out_features: int, *, seed: int | None = None) -> None:
        self.in_features = in_features
        self.out_features = out_features

        # A local random generator makes seed= reproducible without changing
        # NumPy's global random state. He initialization suits ReLU networks.
        rng = np.random.default_rng(seed)
        self.W = rng.normal(
            loc=0.0,
            scale=np.sqrt(2 / in_features),
            size=(in_features, out_features),
        )
        self.b = np.zeros(out_features)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # (batch, in_features) @ (in_features, out_features)
        # produces (batch, out_features). The bias is added to every row.
        return x @ self.W + self.b

    def parameters(self) -> list[np.ndarray]:
        # Return the actual arrays, so later training can update them.
        return [self.W, self.b]

    def __repr__(self) -> str:
        return (
            f"Linear(in_features={self.in_features}, "
            f"out_features={self.out_features})"
        )


class ReLU(Layer):
    """Keep positive values and replace negative values with zero."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        # Without out=, maximum creates a new array and leaves x untouched.
        return np.maximum(0, x)


class Sequential(Layer):
    """A layer that runs its child layers in order."""

    def __init__(self, *layers: Layer) -> None:
        # *layers collects positional arguments into a tuple.
        self.layers = layers

    def forward(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            # Each output becomes the input to the next layer.
            x = layer(x)
        return x

    def parameters(self) -> list[np.ndarray]:
        parameters = []
        for layer in self.layers:
            # extend adds arrays individually; append would add a nested list.
            parameters.extend(layer.parameters())
        return parameters

    def __len__(self) -> int:
        return len(self.layers)

    def __getitem__(self, index: int) -> Layer:
        return self.layers[index]

    def __iter__(self) -> Iterator[Layer]:
        return iter(self.layers)

    def __repr__(self) -> str:
        children = ", ".join(repr(layer) for layer in self.layers)
        return f"Sequential({children})"


def num_parameters(layer: Layer) -> int:
    """Count scalar values, rather than the number of parameter arrays."""
    return sum(parameter.size for parameter in layer.parameters())


# Optional stretch exercises.
class Tanh(Layer):
    """A smooth activation with outputs between -1 and 1."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        return np.tanh(x)


class LayerNorm(Layer):
    """Normalize over the last axis, then apply a learned scale and shift."""

    def __init__(self, dim: int, eps: float = 1e-5) -> None:
        self.dim = dim
        self.eps = eps
        self.gamma = np.ones(dim)
        self.beta = np.zeros(dim)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # keepdims preserves a length-1 final axis for correct broadcasting.
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return self.gamma * (x - mean) / np.sqrt(var + self.eps) + self.beta

    def parameters(self) -> list[np.ndarray]:
        return [self.gamma, self.beta]


if __name__ == "__main__":
    model = Sequential(Linear(2, 4, seed=0), ReLU(), Linear(4, 1, seed=1))
    print(model)
    print("parameters:", num_parameters(model))
    print("output:", model(np.zeros((3, 2))))
