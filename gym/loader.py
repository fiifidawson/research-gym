"""Importing code from a path.

Used by the pytest runner to load (a) a module's ``checks.py`` and (b) whichever
submission is under test. Not used in the browser, so it is free to use the
standard library as much as it likes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


@dataclass
class DataSubmission:
    """What checks receive when a module asks for a data file rather than code.

    Module 00 submits a ``profile.json``; everything from 01 onwards submits a
    ``.py`` file and gets the imported module instead.
    """

    path: Path
    handle: str

    def read_text(self) -> str:
        return self.path.read_text(encoding="utf-8")

    def load_json(self):
        try:
            return json.loads(self.read_text())
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"{self.path.name} is not valid JSON: {exc.msg} (line {exc.lineno}, "
                f"column {exc.colno}). A trailing comma is the usual culprit."
            ) from exc


def import_from_path(path: Path, name: str) -> ModuleType:
    """Import a single .py file under a throwaway module name."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"expected a Python file at {path}")

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build an import spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def load_suite(module_dir: Path):
    """Load the :class:`~gym.checks.CheckSuite` declared by a module."""
    module_dir = Path(module_dir)
    suite_module = import_from_path(module_dir / "checks.py", f"_checks_{module_dir.name}")
    try:
        return suite_module.SUITE
    except AttributeError as exc:  # pragma: no cover - authoring error
        raise AttributeError(f"{module_dir/'checks.py'} must define SUITE") from exc


def load_submission(submission_dir: Path, entrypoint: str) -> ModuleType | DataSubmission:
    """Load a learner's file, with an error message they can act on."""
    submission_dir = Path(submission_dir)
    target = submission_dir / entrypoint

    if not target.is_file():
        raise AssertionError(
            f"expected to find `{entrypoint}` at {submission_dir.as_posix()}/{entrypoint}.\n"
            f"Copy the starter file there and fill in the TODOs - keep the filename identical."
        )

    if not entrypoint.endswith(".py"):
        return DataSubmission(path=target, handle=submission_dir.parent.name)

    # A submission may want to import a sibling helper file it wrote.
    added = str(submission_dir.resolve())
    sys.path.insert(0, added)
    try:
        return import_from_path(target, f"_submission_{submission_dir.name}_{Path(entrypoint).stem}")
    finally:
        if sys.path and sys.path[0] == added:
            sys.path.pop(0)
