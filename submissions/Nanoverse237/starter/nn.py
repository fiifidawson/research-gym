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
        """Run the forward pass when the layer is called."""
        # Python calls this method when you write layer(x).
        # self.forward selects the implementation on the actual subclass.
        return self.forward(x)

    def parameters(self) -> list[np.ndarray]:
        """Return an empty parameter list for a layer without weights."""
        # A layer without trainable arrays has nothing to return.
        return []

    def __repr__(self) -> str:
        """Return the layer's class name followed by parentheses."""
        return f"{self.__class__.__name__}()"


class Linear(Layer):
    """An affine transformation: a weighted sum plus a bias."""

    def __init__(self, in_features: int, out_features: int, *, seed: int | None = None) -> None:
        """Initialize He-scaled weights and zero biases for the given sizes."""
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
        """Transform each input row using the weights and bias."""
        # (batch, in_features) @ (in_features, out_features)
        # produces (batch, out_features). The bias is added to every row.
        return x @ self.W + self.b

    def parameters(self) -> list[np.ndarray]:
        """Return the weight and bias arrays, in that order."""
        # Return the actual arrays, so later training can update them.
        return [self.W, self.b]

    def __repr__(self) -> str:
        """Return a description containing the input and output sizes."""
        return (
            f"Linear(in_features={self.in_features}, "
            f"out_features={self.out_features})"
        )


class ReLU(Layer):
    """Keep positive values and replace negative values with zero."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Return a new array with negative values replaced by zero."""
        # Without out=, maximum creates a new array and leaves x untouched.
        return np.maximum(0, x)


class Sequential(Layer):
    """A layer that runs its child layers in order."""

    def __init__(self, *layers: Layer) -> None:
        """Store the child layers in the order supplied."""
        # *layers collects positional arguments into a tuple.
        self.layers = layers

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Pass the input through each child layer in order."""
        for layer in self.layers:
            # Each output becomes the input to the next layer.
            x = layer(x)
        return x

    def parameters(self) -> list[np.ndarray]:
        """Return a flat list of the child layers' parameter arrays."""
        parameters = []
        for layer in self.layers:
            # extend adds arrays individually; append would add a nested list.
            parameters.extend(layer.parameters())
        return parameters

    def __len__(self) -> int:
        """Return the number of child layers."""
        return len(self.layers)

    def __getitem__(self, index: int) -> Layer:
        """Return the child layer at the given index."""
        return self.layers[index]

    def __iter__(self) -> Iterator[Layer]:
        """Return an iterator over the child layers in order."""
        return iter(self.layers)

    def __repr__(self) -> str:
        """Return a description listing each child layer."""
        children = ", ".join(repr(layer) for layer in self.layers)
        return f"Sequential({children})"


def num_parameters(layer: Layer) -> int:
    """Count scalar values, rather than the number of parameter arrays."""
    return sum(parameter.size for parameter in layer.parameters())


# Optional stretch exercises.
class Tanh(Layer):
    """A smooth activation with outputs between -1 and 1."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Apply the hyperbolic tangent to each input value."""
        return np.tanh(x)


class LayerNorm(Layer):
    """Normalize over the last axis, then apply a learned scale and shift."""

    def __init__(self, dim: int, eps: float = 1e-5) -> None:
        """Initialize the scale, shift, and numerical stability constant."""
        self.dim = dim
        self.eps = eps
        self.gamma = np.ones(dim)
        self.beta = np.zeros(dim)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Normalize the last axis, then apply the learned scale and shift."""
        # keepdims preserves a length-1 final axis for correct broadcasting.
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return self.gamma * (x - mean) / np.sqrt(var + self.eps) + self.beta

    def parameters(self) -> list[np.ndarray]:
        """Return the scale and shift arrays, in that order."""
        return [self.gamma, self.beta]


if __name__ == "__main__":
    model = Sequential(Linear(2, 4, seed=0), ReLU(), Linear(4, 1, seed=1))
    print(model)
    print("parameters:", num_parameters(model))
    print("output:", model(np.zeros((3, 2))))
