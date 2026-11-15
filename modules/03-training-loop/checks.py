"""Checks for module 03 - the training loop.

Read this file. It is the spec. If a check's name and its code disagree, the
code wins, and that is a bug worth an issue.

The Trainer checks run your loop against a tiny fake model and a fake optimizer
defined below, so a bug in one of your classes does not hide a bug in another.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from gym.checks import (
    CORE,
    STRETCH,
    Check,
    CheckSuite,
    assert_close,
    assert_equal,
    assert_shape,
    require,
)

# --- helpers ---------------------------------------------------------------------


def _data(n):
    """Make n samples whose first feature and label are both the sample's own index."""
    X = np.column_stack([np.arange(n, dtype=float), np.arange(n) * 10.0])
    return X, np.arange(n)


def _loader(m, n, batch_size, **kwargs):
    X, y = _data(n)
    return require(m, "DataLoader")(require(m, "Dataset")(X, y), batch_size, **kwargs)


def _batches(loader):
    """One epoch, as a list of lists of sample ids."""
    return [[int(i) for i in X_batch[:, 0]] for X_batch, _ in loader]


def _flat(batches):
    return [i for batch in batches for i in batch]


class _Quadratic:
    """A one-weight fake model. Its gradients accumulate, like the real MLP's."""

    def __init__(self):
        self.w = np.array([0.0])
        self._grads = [np.zeros(1)]
        self.grad_when_called = []

    def parameters(self):
        return [self.w]

    def gradients(self):
        return self._grads

    def loss_and_grad(self, X, y):
        self.grad_when_called.append(float(self._grads[0][0]))
        self._grads[0] += 2.0 * (self.w - 3.0)
        return float(((self.w - 3.0) ** 2)[0])

    def predict(self, X):
        return (X[:, 0] > 0).astype(np.int64)


class _BatchSizeLoss(_Quadratic):
    """Its loss is the size of the batch it was given, so weighting is visible."""

    def loss_and_grad(self, X, y):
        return float(len(X))


class _CountingSGD:
    """A minimal optimizer that counts its steps."""

    def __init__(self, model, lr=0.1):
        self.model, self.lr, self.steps = model, lr, 0

    def step(self):
        self.steps += 1
        for p, g in zip(self.model.parameters(), self.model.gradients(), strict=True):
            p -= self.lr * g

    def zero_grad(self):
        for g in self.model.gradients():
            g[...] = 0.0


def _trainer(m, model, epochs):
    config = SimpleNamespace(lr=0.1, epochs=epochs, batch_size=4, seed=0)
    optimizer = _CountingSGD(model)
    return require(m, "Trainer")(model, optimizer, config), optimizer


def _config(m, **overrides):
    values = {"lr": 0.5, "epochs": 50, "batch_size": 32, "seed": 0}
    values.update(overrides)
    return require(m, "TrainConfig")(**values)


# --- core: config ----------------------------------------------------------------


def config_stores_its_settings(m):
    config = require(m, "TrainConfig")(lr=0.3, epochs=7, batch_size=16, seed=5)
    assert_close(require(config, "lr"), 0.3, "config.lr")
    assert_equal(require(config, "epochs"), 7, "config.epochs")
    assert_equal(require(config, "batch_size"), 16, "config.batch_size")
    assert_equal(require(config, "seed"), 5, "config.seed")


def config_cannot_be_changed(m):
    config = _config(m)
    try:
        config.lr = 99.0
    except Exception:  # noqa: BLE001 - which error depends on how it was frozen
        return
    raise AssertionError("assigning to config.lr should raise an error, but it was allowed")


# --- core: data ------------------------------------------------------------------


def dataset_reports_its_length(m):
    X, y = _data(10)
    assert_equal(len(require(m, "Dataset")(X, y)), 10, "len(Dataset)")


def dataset_returns_the_pair_at_an_index(m):
    X, y = _data(10)
    x_i, y_i = require(m, "Dataset")(X, y)[3]
    assert_close(x_i, X[3], "dataset[3] input")
    assert_equal(int(y_i), 3, "dataset[3] label")


def loader_yields_every_sample_once(m):
    ids = sorted(_flat(_batches(_loader(m, 10, 4, shuffle=True, seed=0))))
    assert_equal(ids, list(range(10)), "the samples seen in one epoch")


def loader_batches_have_the_right_size(m):
    loader = _loader(m, 10, 4, shuffle=True, seed=0)
    assert_equal([len(b) for b in _batches(loader)], [4, 4, 2], "batch sizes for 10 samples")
    X_batch, y_batch = next(iter(loader))
    assert_shape(X_batch, (4, 2), "the first X batch")
    assert_shape(y_batch, (4,), "the first y batch")


def loader_length_counts_batches(m):
    assert_equal(len(_loader(m, 10, 4)), 3, "len(loader) for 10 samples, batch size 4")
    assert_equal(len(_loader(m, 8, 4)), 2, "len(loader) for 8 samples, batch size 4")


def loader_keeps_order_without_shuffle(m):
    batches = _batches(_loader(m, 10, 4, shuffle=False))
    assert_equal(_flat(batches), list(range(10)), "the order with shuffle=False")


def same_seed_gives_the_same_shuffle(m):
    first = _batches(_loader(m, 20, 4, shuffle=True, seed=3))
    second = _batches(_loader(m, 20, 4, shuffle=True, seed=3))
    assert_equal(first, second, "the batch order for two loaders with the same seed")


def loader_reshuffles_every_epoch(m):
    loader = _loader(m, 20, 4, shuffle=True, seed=0)
    first, second = _batches(loader), _batches(loader)
    assert_equal(sorted(_flat(second)), list(range(20)), "the samples seen in the second epoch")
    if first == second:
        raise AssertionError("the second epoch came in the same order as the first")


# --- core: optimizer -------------------------------------------------------------


def sgd_steps_against_the_gradient_in_place(m):
    p, g = np.array([1.0, 2.0]), np.array([0.5, -1.0])
    require(m, "SGD")([p], [g], lr=0.1).step()
    assert_close(p, [0.95, 2.1], "the parameter array after one step")


def sgd_zero_grad_clears_in_place(m):
    g = np.ones(3)
    require(m, "SGD")([np.zeros(3)], [g], lr=0.1).zero_grad()
    assert_close(g, np.zeros(3), "the gradient array after zero_grad")


# --- core: trainer ---------------------------------------------------------------


def fit_returns_one_loss_per_epoch(m):
    model = _Quadratic()
    trainer, _ = _trainer(m, model, epochs=4)
    history = trainer.fit(_loader(m, 10, 4, shuffle=False))
    assert_equal(len(history), 4, "the number of losses fit returns for 4 epochs")


def fit_takes_one_step_per_batch(m):
    trainer, optimizer = _trainer(m, _Quadratic(), epochs=3)
    trainer.fit(_loader(m, 10, 4, shuffle=False))
    assert_equal(optimizer.steps, 9, "optimizer steps for 3 epochs of 3 batches")


def fit_clears_gradients_before_every_step(m):
    model = _Quadratic()
    trainer, _ = _trainer(m, model, epochs=2)
    trainer.fit(_loader(m, 10, 4, shuffle=False))
    if any(g != 0.0 for g in model.grad_when_called):
        raise AssertionError(
            "gradients were not zero when a batch started - "
            f"saw {model.grad_when_called}, expected all zeros"
        )


def fit_weights_each_batch_by_its_size(m):
    trainer, _ = _trainer(m, _BatchSizeLoss(), epochs=1)
    history = trainer.fit(_loader(m, 10, 4, shuffle=False))
    # Batches of 4, 4 and 2 give losses 4, 4 and 2: (4*4 + 4*4 + 2*2) / 10 samples.
    assert_close(history[0], 3.6, "the epoch loss for batches of 4, 4 and 2")


def evaluate_returns_accuracy(m):
    trainer, _ = _trainer(m, _Quadratic(), epochs=1)
    X = np.array([[1.0], [-1.0], [2.0], [-2.0]])
    y = np.array([1, 0, 0, 0])
    assert_close(trainer.evaluate(X, y), 0.75, "accuracy when 3 of 4 predictions are right")


# --- core: the whole thing -------------------------------------------------------


def training_is_reproducible(m):
    train = require(m, "train")
    history_a, accuracy_a = train(_config(m, epochs=10))
    history_b, accuracy_b = train(_config(m, epochs=10))
    assert_close(history_a, history_b, "the loss curve of two runs with the same config", 1e-12)
    assert_equal(accuracy_a, accuracy_b, "the test accuracy of two runs with the same config")


def different_seeds_give_different_runs(m):
    train = require(m, "train")
    history_a, _ = train(_config(m, epochs=10, seed=0))
    history_b, _ = train(_config(m, epochs=10, seed=1))
    if np.allclose(history_a, history_b):
        raise AssertionError("seeds 0 and 1 gave the same loss curve - is the seed being used?")


def training_reduces_the_loss(m):
    history, _ = require(m, "train")(_config(m))
    assert_equal(len(history), 50, "the number of losses for 50 epochs")
    if not history[-1] < 0.5 * history[0]:
        raise AssertionError(
            f"loss went from {history[0]:.3f} to {history[-1]:.3f}, expected it to at least halve"
        )


def the_model_separates_the_moons(m):
    _, accuracy = require(m, "train")(_config(m))
    if accuracy < 0.9:
        raise AssertionError(f"test accuracy was {accuracy:.2f}, expected at least 0.90")


# --- stretch ---------------------------------------------------------------------


def loader_can_drop_the_last_batch(m):
    loader = _loader(m, 10, 4, shuffle=False, drop_last=True)
    assert_equal([len(b) for b in _batches(loader)], [4, 4], "batch sizes with drop_last=True")
    assert_equal(len(loader), 2, "len(loader) with drop_last=True")


def sgd_supports_momentum(m):
    p, g = np.array([0.0]), np.array([1.0])
    optimizer = require(m, "SGD")([p], [g], lr=0.1, momentum=0.9)
    optimizer.step()
    optimizer.step()
    # velocities 1.0 then 0.9 * 1.0 + 1.0 = 1.9, so the weight moves 0.1 and then 0.19
    assert_close(p, [-0.29], "the parameter after two momentum steps")


SUITE = CheckSuite(
    entrypoint="train.py",
    checks=[
        Check("TrainConfig stores lr, epochs, batch_size and seed", config_stores_its_settings),
        Check(
            "TrainConfig cannot be changed after it is made",
            config_cannot_be_changed,
            CORE,
            hint="a frozen dataclass",
        ),
        Check("Dataset reports how many samples it holds", dataset_reports_its_length),
        Check(
            "Dataset returns the (x, y) pair at an index",
            dataset_returns_the_pair_at_an_index,
            CORE,
            hint="__getitem__",
        ),
        Check(
            "DataLoader yields every sample exactly once per epoch", loader_yields_every_sample_once
        ),
        Check(
            "DataLoader batches have batch_size rows, the last may be smaller",
            loader_batches_have_the_right_size,
            CORE,
            hint="slice the order list batch_size at a time; the last slice just runs short",
        ),
        Check(
            "len(DataLoader) is the number of batches",
            loader_length_counts_batches,
            CORE,
            hint="10 samples in batches of 4 is 3 batches, not 2.5",
        ),
        Check(
            "DataLoader keeps the dataset order when shuffle=False",
            loader_keeps_order_without_shuffle,
        ),
        Check(
            "The same seed gives the same shuffle order",
            same_seed_gives_the_same_shuffle,
            CORE,
            hint="np.random.default_rng(seed), not the global np.random",
        ),
        Check(
            "DataLoader reshuffles on every epoch",
            loader_reshuffles_every_epoch,
            CORE,
            hint="make the generator once in __init__ and draw a new permutation in __iter__",
        ),
        Check(
            "SGD moves parameters against the gradient, in place",
            sgd_steps_against_the_gradient_in_place,
            CORE,
            hint="p -= ... edits the array; p = p - ... only rebinds the name",
        ),
        Check(
            "SGD.zero_grad clears gradients in place",
            sgd_zero_grad_clears_in_place,
            CORE,
            hint="the model holds these exact arrays",
        ),
        Check("Trainer.fit returns one loss per epoch", fit_returns_one_loss_per_epoch),
        Check("Trainer takes one optimizer step per batch", fit_takes_one_step_per_batch),
        Check(
            "Trainer clears the gradients before every step",
            fit_clears_gradients_before_every_step,
            CORE,
            hint="the model adds into its gradients; nothing resets them but you",
        ),
        Check(
            "Trainer weights each batch's loss by its size",
            fit_weights_each_batch_by_its_size,
            CORE,
            hint="a batch of 2 should count for less than a batch of 4",
        ),
        Check("Trainer.evaluate returns the accuracy", evaluate_returns_accuracy),
        Check(
            "Training is reproducible: same config, same loss curve",
            training_is_reproducible,
            CORE,
            hint="pass config.seed to set_seed, the DataLoader and the MLP",
        ),
        Check("Different seeds give different runs", different_seeds_give_different_runs),
        Check("Training reduces the loss", training_reduces_the_loss),
        Check("The trained model separates the two moons", the_model_separates_the_moons),
        Check(
            "DataLoader can drop the last, smaller batch", loader_can_drop_the_last_batch, STRETCH
        ),
        Check("SGD supports momentum", sgd_supports_momentum, STRETCH),
    ],
)
