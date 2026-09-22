"""Wires a submission into the checks.

Every module's test file is the same six lines; the work happens here. The
``SUBMISSION_DIR`` environment variable decides whose code is under test - CI
sets it from the files the pull request touched. With it unset, the module's own
``starter/`` directory is used, which is how you confirm a starter is importable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gym.loader import load_submission, load_suite  # noqa: E402


def _module_dir(request: pytest.FixtureRequest) -> Path:
    """The ``modules/NN-name/`` directory owning the running test file."""
    return Path(request.node.path).resolve().parent.parent


@pytest.fixture(scope="module")
def suite(request):
    return load_suite(_module_dir(request))


@pytest.fixture(scope="module")
def submission(request, suite):
    module_dir = _module_dir(request)
    override = os.environ.get("SUBMISSION_DIR")
    source = Path(override) if override else module_dir / "starter"
    return load_submission(source, suite.entrypoint)
