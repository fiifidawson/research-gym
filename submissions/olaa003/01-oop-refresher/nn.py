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
    """Anything that turns an array into another array."""

    @abstractmethod
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Run this layer on a batch of inputs, shape (batch, features)."""
        ...

    def __call__(self, x):
        return self.forward(x)

    def parameters(self):
        return []

    def __repr__(self):
        return f"{self.__class__.__name__} + ()"


# =============================================================================
# 2. A layer with weights
# =============================================================================


class Linear(Layer):
    """
    The affine map `x @ W + b`.

    Args:
        in_features: Size of each input row.
        out_features: Size of each output row.
        seed: Seed for the weight initialisation. The same seed has to give the
            same weights.
    """

    def __init__(self, in_features: int, out_features: int, *, seed: int | None = None) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.W = np.random.default_rng(seed).normal(loc=0.0,
    scale=np.sqrt(2 / self.in_features), size=(self.in_features, self.out_features),)
        self.b = np.zeros(self.out_features)


    def forward(self, x: np.ndarray) -> np.ndarray:
        return x @ self.W + self.b
        

    def parameters(self) -> list[np.ndarray]:
        return [self.W, self.b]

    def __repr__(self) -> str:
        return f"Linear(in_features={self.in_features}, out_features={self.out_features})"


# =============================================================================
# 3. A layer without weights
# =============================================================================


class ReLU(Layer):
    """Zero out negatives, keep everything else."""

    def forward(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
 
    def __repr__(self) -> str:
        return "ReLU()"
    

# =============================================================================
# 4. A layer made of layers
# =============================================================================


class Sequential(Layer):
    """Runs the layers it holds, front to back.
    
    A Sequential is a Layer and contains Layers. That is how every framework
    composes a model, and how you'll assemble a transformer block in module 08.
    """

    def __init__(self, *layers: Layer) -> None:
        super().__init__()
        for i, layer in enumerate(layers):
            setattr(self, f"layer_{i}", layer)
        self.layers = list(layers)

    def forward(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def parameters(self) -> list[np.ndarray]:
        return [param for layer in self.layers for param in layer.parameters()]

    def __len__(self) -> int:
        return len(self.layers)

    def __getitem__(self, index: int) -> Layer:
        return self.layers[index]

    def __iter__(self):
        return iter(self.layers)  

    def __repr__(self) -> str:
        layers_repr = ", ".join(repr(layer) for layer in self.layers)
        return f"Sequential({layers_repr})"


# =============================================================================
# 5. A function
# =============================================================================


def num_parameters(layer: Layer) -> int:
    """Total number of individual values a layer is holding."""
    return sum(param.size for param in layer.parameters())



# =============================================================================
# 6. Stretch - optional
# =============================================================================


class Tanh(Layer):
    """TODO (stretch): np.tanh, as a Layer."""
    def forward(self, x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    def parameters(self) -> list[np.ndarray]:
            return []

    def __repr__(self) -> str:
        return "Tanh()"
    

class LayerNorm(Layer):
    """normalise each row to zero mean and unit variance.

    Args:
        dim: Size of the last axis.
        eps: Added inside the square root so a constant row can't divide by zero.

    Store `self.gamma` (ones, shape (dim,)) and `self.beta` (zeros, shape (dim,)),
    return both from `parameters()`, and compute
    `gamma * (x - mean) / sqrt(var + eps) + beta` over the last axis.
    """

    def __init__(self, dim, eps):
        super().__init__()
        self.gamma = np.ones(dim)
        self.beta = np.zeros(dim)
        self.eps = eps

    def forward(self, x: np.ndarray) -> np.ndarray:
        mean = x.mean(axis=-1, keepdims=True)
        var = x.var(axis=-1, keepdims=True)
        return self.gamma * (x - mean) / np.sqrt(var + self.eps) + self.beta

    def parameters(self) -> list[np.ndarray]:
        return [self.gamma, self.beta]


if __name__ == "__main__":
    # Scratch space. Nothing here is checked.
    model = Sequential(Linear(2, 4, seed=0), ReLU(), Linear(4, 1, seed=1))
    print(model)
    print("parameters:", num_parameters(model))
    print("output:", model(np.zeros((3, 2))))
