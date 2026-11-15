"""Module 03 - the training loop.

Copy this to `submissions/<your-handle>/03-training-loop/train.py` and fill in the
TODOs there. Leave this starter alone so the next person gets a clean copy.

Keep every class, function, argument and attribute name as written. The checks
look them up by name.

`MLP` is given to you, gradients and all - you wrote the idea of those in module
02. Everything else here is the bookkeeping around it, and that is what you are
here to build.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from gym.data import train_test_split, two_moons
from gym.seed import set_seed

# =============================================================================
# 0. The model - given, do not edit
# =============================================================================


class MLP:
    """A one-hidden-layer classifier: `tanh` hidden units, a sigmoid output.

    It exposes exactly what a training loop needs:

    * `parameters()` - the arrays that learn
    * `gradients()` - one array per parameter, same order, same shapes
    * `loss_and_grad(X, y)` - runs a batch through, **adds** the gradients into
      `gradients()` and returns the mean loss. It adds rather than overwrites,
      like `+=` in your module 02 `backward()`, so someone has to clear them
      between steps. That someone is you.
    * `predict(X)` - hard 0/1 labels
    """

    def __init__(self, in_features: int = 2, hidden: int = 16, *, seed: int = 0) -> None:
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, np.sqrt(2.0 / in_features), size=(in_features, hidden))
        self.b1 = np.zeros(hidden)
        self.W2 = rng.normal(0.0, np.sqrt(1.0 / hidden), size=(hidden, 1))
        self.b2 = np.zeros(1)
        self._grads = [np.zeros_like(p) for p in self.parameters()]

    def parameters(self) -> list[np.ndarray]:
        return [self.W1, self.b1, self.W2, self.b2]

    def gradients(self) -> list[np.ndarray]:
        return self._grads

    def _forward(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        hidden = np.tanh(X @ self.W1 + self.b1)
        logits = (hidden @ self.W2 + self.b2)[:, 0]
        return hidden, 1.0 / (1.0 + np.exp(-logits))

    def loss_and_grad(self, X: np.ndarray, y: np.ndarray) -> float:
        n = len(X)
        hidden, p = self._forward(X)
        eps = 1e-12
        loss = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))

        d_logits = ((p - y) / n)[:, None]
        d_hidden = d_logits @ self.W2.T
        d_pre = d_hidden * (1.0 - hidden**2)

        dW1, db1, dW2, db2 = self._grads
        dW1 += X.T @ d_pre
        db1 += d_pre.sum(axis=0)
        dW2 += hidden.T @ d_logits
        db2 += d_logits.sum(axis=0)
        return float(loss)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self._forward(X)[1] >= 0.5).astype(np.int64)


# =============================================================================
# 1. A config that cannot drift
# =============================================================================


@dataclass
class TrainConfig:
    """Every knob of one training run, in one place.

    TODO: make this a *frozen* dataclass, so `config.lr = 1.0` raises an error.
    A run's settings should not change halfway through it.

    TODO: give it four fields - `lr` (float), `epochs` (int), `batch_size` (int)
    and `seed` (int). Choose defaults that train well; the checks always pass
    their own values, but a sensible default is kind to the next reader.
    """


# =============================================================================
# 2. Data: Dataset and DataLoader
# =============================================================================


class Dataset:
    """Inputs `X` and labels `y`, addressable one sample at a time.

    TODO: keep `X` and `y`.
    TODO: `__len__` - how many samples there are.
    TODO: `__getitem__(i)` - the pair `(X[i], y[i])`.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray) -> None:
        raise NotImplementedError


class DataLoader:
    """Hands a Dataset out in batches, one epoch per `for` loop.

    `for X_batch, y_batch in loader:` yields arrays: `X_batch` has shape
    `(batch, features)`, `y_batch` shape `(batch,)`.

    TODO: keep the arguments. Build one `np.random.default_rng(seed)` here, in
    `__init__` - not inside `__iter__`. Think about why: what would happen to the
    shuffle order if every epoch started from a fresh generator?

    TODO: `__iter__` - this is the heart of the module. Work out the order the
    samples come in (a fresh shuffle each time when `shuffle=True`, the dataset's
    own order when not), then yield them `batch_size` at a time. The last batch
    may be smaller. A class with `__iter__` can be looped over again and again;
    that is why this is a class and not a bare generator function.

    TODO: `__len__` - the number of batches in one epoch. Mind the last, smaller
    one.

    TODO (stretch): `drop_last=True` throws that smaller last batch away.
    """

    def __init__(
        self,
        dataset: Dataset,
        batch_size: int,
        *,
        shuffle: bool = True,
        seed: int | None = None,
        drop_last: bool = False,
    ) -> None:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


# =============================================================================
# 3. The optimizer
# =============================================================================


class SGD:
    """Plain stochastic gradient descent.

    Args:
        parameters: The arrays to update. These are the model's own arrays.
        gradients: One array per parameter, same order, same shapes.
        lr: Learning rate.
        momentum: Stretch. 0.0 means plain SGD.

    TODO: keep the arguments.

    TODO: `step()` - move every parameter a little way *against* its gradient.
    Do it **in place** (`p -= ...`, not `p = p - ...`). The model holds those very
    arrays; rebind the name and the model never sees the update.

    TODO: `zero_grad()` - set every gradient array back to zero, in place, for the
    same reason.

    TODO (stretch): momentum. Keep a velocity per parameter; each step,
    `v = momentum * v + grad`, then move by `lr * v`.
    """

    def __init__(
        self,
        parameters: list[np.ndarray],
        gradients: list[np.ndarray],
        lr: float,
        momentum: float = 0.0,
    ) -> None:
        raise NotImplementedError

    def step(self) -> None:
        raise NotImplementedError

    def zero_grad(self) -> None:
        raise NotImplementedError


# =============================================================================
# 4. The loop
# =============================================================================


class Trainer:
    """Runs the model over the data, epoch after epoch.

    TODO: keep `model`, `optimizer` and `config`.

    TODO: `fit(loader)` - for each of `config.epochs` epochs, go through the
    loader. For every batch, in this order:
        1. clear the gradients
        2. `model.loss_and_grad(X_batch, y_batch)`
        3. take one optimizer step
    Return a list with one number per epoch: the mean loss over that epoch's
    *samples*. A batch of 2 should count for less than a batch of 32, so weight
    each batch's loss by its size.

    TODO: `evaluate(X, y)` - the fraction of rows `model.predict(X)` gets right,
    a float between 0 and 1.
    """

    def __init__(self, model: MLP, optimizer: SGD, config: TrainConfig) -> None:
        raise NotImplementedError

    def fit(self, loader: DataLoader) -> list[float]:
        raise NotImplementedError

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        raise NotImplementedError


# =============================================================================
# 5. One call, start to finish
# =============================================================================


def train(config: TrainConfig) -> tuple[list[float], float]:
    """Train an MLP on two moons and report how it did.

    Returns `(history, test_accuracy)`: the per-epoch training loss from
    `Trainer.fit`, and the accuracy on data the model never trained on.

    TODO: seed everything from `config.seed`. `set_seed` is imported for you; the
    DataLoader and the MLP take a `seed=` too.

    TODO: build the data with `two_moons()`, split it with `train_test_split()`,
    wrap the training part in a Dataset and a DataLoader (`config.batch_size`).

    TODO: build the MLP, an SGD over its parameters and gradients, and a Trainer.
    Fit, then evaluate on the test part.

    Same config in, same numbers out. That is what a frozen seed buys you.
    """
    raise NotImplementedError


if __name__ == "__main__":
    # Scratch space. Nothing here is checked.
    config = TrainConfig(lr=0.5, epochs=50, batch_size=32, seed=0)
    history, accuracy = train(config)
    print("loss, first and last epoch:", history[0], history[-1])
    print("test accuracy:", accuracy)
