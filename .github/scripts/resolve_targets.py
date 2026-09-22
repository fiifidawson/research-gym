"""Work out what a pull request is submitting, and refuse the confusing cases.

Run by ``submission-check.yml``. Everything it rejects, it rejects with a
sentence a beginner can act on - a pull request check that just says "failed" is
worse than no check at all.

Output is a JSON file:

    {"ok": true, "error": null, "targets": [{"handle": ..., "module": ..., "path": ...}]}
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SUBMISSION_RE = re.compile(r"^submissions/(?P<handle>[^/]+)/(?P<module>[^/]+)/.+")
OWNED_RE = re.compile(r"^submissions/(?P<handle>[^/]+)/.+")
PROTECTED_RE = re.compile(r"^modules/[^/]+/(tests/.+|checks\.py)$")


def changed_files(base: str, head: str) -> list[str]:
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in diff.stdout.splitlines() if line.strip()]


def module_exists(module: str) -> bool:
    return (REPO_ROOT / "modules" / module / "checks.py").is_file()


def known_modules() -> list[str]:
    return sorted(p.parent.name for p in (REPO_ROOT / "modules").glob("*/checks.py"))


def resolve(paths: list[str], author: str) -> dict:
    def fail(message: str) -> dict:
        return {"ok": False, "error": message, "targets": []}

    protected = [p for p in paths if PROTECTED_RE.match(p)]
    if protected:
        listed = "\n".join(f"  - {p}" for p in protected)
        return fail(
            "This pull request edits the checks themselves:\n"
            f"{listed}\n\n"
            "Those files are the shared definition of 'done', so changing them here would "
            "only move the goalposts. If you think a check is wrong - and sometimes it is - "
            "open an issue with the 'bug' template and say why. Fixing a bad check is a real "
            "contribution, it just belongs in its own pull request."
        )

    targets: dict[tuple[str, str], str] = {}
    for path in paths:
        match = SUBMISSION_RE.match(path)
        if match:
            handle, module = match["handle"], match["module"]
            targets[(handle, module)] = f"submissions/{handle}/{module}"

    owned_by_others = sorted(
        {
            m["handle"]
            for p in paths
            if (m := OWNED_RE.match(p)) and m["handle"].lower() != author.lower()
        }
    )
    if owned_by_others:
        return fail(
            f"This pull request changes work inside {', '.join(f'submissions/{h}/' for h in owned_by_others)}, "
            f"which does not belong to @{author}.\n\n"
            "Everyone has their own folder so nobody can break anyone else's module. If you "
            "want to suggest a change to someone's code, leave a review comment on their pull "
            "request instead - that is the more useful thing anyway."
        )

    other_changes = [
        p for p in paths if not OWNED_RE.match(p) and not p.startswith(".github/scripts/")
    ]
    if targets and other_changes:
        listed = "\n".join(f"  - {p}" for p in other_changes[:10])
        return fail(
            "This pull request mixes module work with changes to the repo itself:\n"
            f"{listed}\n\n"
            "Please split them. Small, single-purpose pull requests are easier to review, and "
            "reviewing is the skill this repo is quietly trying to teach you."
        )

    if not targets:
        return {"ok": True, "error": None, "targets": []}

    if len(targets) > 1:
        listed = ", ".join(sorted(module for _, module in targets))
        return fail(
            f"This pull request submits {len(targets)} modules at once ({listed}).\n\n"
            "One module per pull request, please. A reviewer can give you useful feedback on "
            "forty lines; on four hundred they will just say 'looks good'."
        )

    (handle, module), path = next(iter(targets.items()))

    if not module_exists(module):
        return fail(
            f'There is no module called "{module}".\n\n'
            f"Your folder needs to be named exactly like the one under modules/. "
            f"Available: {', '.join(known_modules())}"
        )

    return {"ok": True, "error": None, "targets": [{"handle": handle, "module": module, "path": path}]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="base sha or ref of the pull request")
    parser.add_argument("--head", required=True, help="head sha of the pull request")
    parser.add_argument("--author", required=True, help="github login of the pull request author")
    parser.add_argument("--out", default="targets.json", type=Path)
    args = parser.parse_args()

    result = resolve(changed_files(args.base, args.head), args.author)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if result["error"]:
        print(result["error"], file=sys.stderr)
    else:
        print(json.dumps(result["targets"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
