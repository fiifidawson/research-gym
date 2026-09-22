"""Seeding, in one obvious place.

Half this cohort rated reproducible experiments as Beginner or None. The fix is
not a lecture, it is that every module from 01 onward makes seeding the normal
way to get a random number.
"""

from __future__ import annotations

import os
import random

import numpy as np


def set_seed(seed: int) -> None:
    """Seed every source of randomness we might be using.

    PyTorch is seeded too when it happens to be installed, so the same call keeps
    working once the cohort reaches module 04.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    try:
        import torch
    except ImportError:
        return

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def rng(seed: int | None = None) -> np.random.Generator:
    """A NumPy generator. Prefer this over the global ``np.random`` functions."""
    return np.random.default_rng(seed)
