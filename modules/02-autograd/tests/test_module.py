"""Runs this module's checks under pytest.

There is nothing module-specific here on purpose - every module's test file is
this same file. The assertions all live in ``../checks.py`` so that the pull
request bot and the browser playground run identical code.
"""

from pathlib import Path

import pytest

from gym.checks import STRETCH
from gym.loader import load_suite

SUITE = load_suite(Path(__file__).resolve().parent.parent)

CASES = [
    pytest.param(check, marks=pytest.mark.stretch) if check.tier == STRETCH else check
    for check in SUITE.checks
]


@pytest.mark.parametrize("check", CASES, ids=[c.name for c in SUITE.checks])
def test_check(check, submission):
    check.fn(submission)
