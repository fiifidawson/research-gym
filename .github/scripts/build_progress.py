"""Regenerate docs/data/progress.json from what is actually on main.

Run after every merge. It re-runs each merged submission against its module's
checks rather than trusting a record written at merge time, so the dashboard
cannot drift away from the truth - if someone changes a check, every row updates
on the next push.

Running merged code is safe here in the sense that matters: it has already been
through a pull request and a human review.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from gym.checks import STRETCH  # noqa: E402
from gym.loader import load_submission, load_suite  # noqa: E402

SUBMISSIONS = REPO_ROOT / "submissions"
MODULES = REPO_ROOT / "modules"


def evaluate(module: str, submission_dir: Path) -> dict:
    """Run one module's checks against one submission."""
    blank = {
        "core_passed": 0,
        "core_total": 0,
        "stretch_passed": 0,
        "stretch_total": 0,
        "status": "submitted",
    }
    try:
        suite = load_suite(MODULES / module)
    except Exception:
        return blank

    core = [c for c in suite.checks if c.tier != STRETCH]
    stretch = [c for c in suite.checks if c.tier == STRETCH]
    blank |= {"core_total": len(core), "stretch_total": len(stretch)}

    try:
        submission = load_submission(submission_dir, suite.entrypoint)
    except ModuleNotFoundError as exc:
        # e.g. torch is not installed on the docs runner. Not the learner's fault.
        print(f"  {submission_dir.name}: skipped, {exc}")
        return blank
    except Exception:
        return blank | {"status": "broken"}

    core_passed = sum(1 for c in core if c.run(submission)["passed"])
    stretch_passed = sum(1 for c in stretch if c.run(submission)["passed"])

    if core_passed == len(core) and stretch_passed == len(stretch) and stretch:
        status = "complete+stretch"
    elif core_passed == len(core):
        status = "complete"
    elif core_passed:
        status = "partial"
    else:
        status = "submitted"

    return {
        "core_passed": core_passed,
        "core_total": len(core),
        "stretch_passed": stretch_passed,
        "stretch_total": len(stretch),
        "status": status,
    }


def read_profile(handle: str) -> dict | None:
    path = SUBMISSIONS / handle / "00-onboarding" / "profile.json"
    if not path.is_file():
        return None
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return {
        "handle": handle,
        "name": profile.get("name", handle),
        "role": profile.get("role", ""),
        "track": profile.get("track", ""),
        "here_for": profile.get("here_for", ""),
        "links": profile.get("links", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/data/progress.json")
    args = parser.parse_args()

    people, progress = [], {}

    for handle_dir in sorted(p for p in SUBMISSIONS.iterdir() if p.is_dir()):
        handle = handle_dir.name
        if handle.startswith("_"):
            continue

        profile = read_profile(handle)
        if profile:
            people.append(profile)

        rows = {}
        for module_dir in sorted(p for p in handle_dir.iterdir() if p.is_dir()):
            if not (MODULES / module_dir.name / "checks.py").is_file():
                continue
            try:
                rows[module_dir.name] = evaluate(module_dir.name, module_dir)
            except Exception:  # noqa: BLE001 - one bad submission must not lose the rest
                traceback.print_exc()
                rows[module_dir.name] = {
                    "status": "broken",
                    "core_passed": 0,
                    "core_total": 0,
                    "stretch_passed": 0,
                    "stretch_total": 0,
                }
        if rows:
            progress[handle] = rows

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "people": people,
        "progress": progress,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"{args.out.relative_to(REPO_ROOT)}: {len(people)} people, {len(progress)} with work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
