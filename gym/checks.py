"""The check primitive.

A *check* is one named, human-readable statement about a submission, e.g.
``"ReLU zeroes negative values"``. Checks are written once, in a module's
``checks.py``, and are then run two ways:

* by pytest in CI, parametrised so the PR bot can print the names verbatim
* by Pyodide in the browser playground, via :func:`run_checks`

Never write an assertion anywhere else, or the two runners will drift apart.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

CORE = "core"
STRETCH = "stretch"


@dataclass(frozen=True)
class Check:
    """One named assertion about a learner's submission.

    Args:
        name: Plain English, present tense, describing what *should* be true.
            This is the text that appears on the pull request, so write it for
            the person reading the failure, not for yourself.
        fn: Callable taking the learner's imported module. It should raise
            ``AssertionError`` (or any exception) to fail.
        tier: ``"core"`` for everyone, ``"stretch"`` for optional extensions.
        hint: Optional nudge shown only when the check fails. Point at the idea,
            never at the answer.
    """

    name: str
    fn: Callable[[Any], None]
    tier: str = CORE
    hint: str = ""

    def run(self, submission: Any) -> dict:
        """Run this check, capturing the failure rather than raising."""
        try:
            self.fn(submission)
        except Exception as exc:  # noqa: BLE001 - a learner can raise anything
            return {
                "name": self.name,
                "tier": self.tier,
                "passed": False,
                "error": f"{type(exc).__name__}: {exc}",
                "hint": self.hint,
            }
        return {"name": self.name, "tier": self.tier, "passed": True, "error": "", "hint": ""}


@dataclass
class CheckSuite:
    """Everything a module needs to be runnable by both runners."""

    entrypoint: str
    """Filename the learner is expected to submit, e.g. ``"nn.py"``."""

    checks: list[Check] = field(default_factory=list)

    def core(self) -> list[Check]:
        """The checks everyone is expected to pass."""
        return [c for c in self.checks if c.tier == CORE]

    def stretch(self) -> list[Check]:
        """The optional ones. These never block a merge."""
        return [c for c in self.checks if c.tier == STRETCH]


def run_checks(checks: Iterable[Check], submission: Any) -> list[dict]:
    """Run every check and return plain dicts (JSON-friendly, Pyodide-friendly)."""
    return [check.run(submission) for check in checks]


# --- assertion helpers -------------------------------------------------------
# These exist so failure messages are useful. `assert x.shape == (2, 3)` tells a
# learner nothing; `expected shape (2, 3), got (3, 2)` tells them where to look.


def require(obj: Any, name: str) -> Any:
    """Fetch an attribute, failing with a message aimed at a beginner."""
    if not hasattr(obj, name):
        raise AssertionError(
            f"could not find `{name}` - is it defined, and spelled exactly like this?"
        )
    return getattr(obj, name)


def assert_shape(array: Any, expected: tuple[int, ...], what: str) -> None:
    actual = getattr(array, "shape", None)
    if actual is None:
        raise AssertionError(f"{what} should be a NumPy array, got {type(array).__name__}")
    if tuple(actual) != tuple(expected):
        raise AssertionError(f"{what} should have shape {tuple(expected)}, got {tuple(actual)}")


def assert_close(actual: Any, expected: Any, what: str, tol: float = 1e-6) -> None:
    import numpy as np

    actual_arr, expected_arr = np.asarray(actual), np.asarray(expected)
    if actual_arr.shape != expected_arr.shape:
        raise AssertionError(
            f"{what} should have shape {expected_arr.shape}, got {actual_arr.shape}"
        )
    if not np.allclose(actual_arr, expected_arr, atol=tol, rtol=tol):
        worst = float(np.max(np.abs(actual_arr - expected_arr)))
        raise AssertionError(f"{what} is off by up to {worst:.3g} (tolerance {tol:g})")


def assert_equal(actual: Any, expected: Any, what: str) -> None:
    if actual != expected:
        raise AssertionError(f"{what} should be {expected!r}, got {actual!r}")
