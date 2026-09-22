"""Tiny datasets, generated rather than downloaded.

Pure NumPy on purpose: these have to work inside Pyodide in the browser, where
there is no filesystem to download into.
"""

from __future__ import annotations

import numpy as np


def two_moons(n: int = 200, noise: float = 0.1, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Two interleaving half circles - the classic 'needs a hidden layer' dataset.

    Returns:
        ``(X, y)`` with X of shape ``(n, 2)`` and y of shape ``(n,)`` holding 0/1.
    """
    generator = np.random.default_rng(seed)
    n_out = n // 2
    n_in = n - n_out

    theta_out = np.linspace(0, np.pi, n_out)
    theta_in = np.linspace(0, np.pi, n_in)

    outer = np.stack([np.cos(theta_out), np.sin(theta_out)], axis=1)
    inner = np.stack([1 - np.cos(theta_in), 0.5 - np.sin(theta_in)], axis=1)

    X = np.concatenate([outer, inner], axis=0)
    X += generator.normal(0.0, noise, size=X.shape)
    y = np.concatenate([np.zeros(n_out, dtype=np.int64), np.ones(n_in, dtype=np.int64)])

    order = generator.permutation(n)
    return X[order], y[order]


def train_test_split(
    X: np.ndarray, y: np.ndarray, test_fraction: float = 0.2, seed: int = 0
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Shuffle once, then cut. Seeded, so the split is the same for everyone."""
    if not 0.0 < test_fraction < 1.0:
        raise ValueError(f"test_fraction must be between 0 and 1, got {test_fraction}")

    order = np.random.default_rng(seed).permutation(len(X))
    cut = int(len(X) * (1 - test_fraction))
    train, test = order[:cut], order[cut:]
    return X[train], y[train], X[test], y[test]
