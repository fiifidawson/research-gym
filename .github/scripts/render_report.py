"""Turn a pytest JSON report into the comment that appears on the pull request.

This comment is the whole user interface of this repo. Nobody here runs pytest;
they read this. So it says what passed, what did not, and what to do next - in
that order, in English.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from gym.checks import STRETCH  # noqa: E402
from gym.loader import load_suite  # noqa: E402

MARKER = "<!-- research-gym-report -->"
ID_RE = re.compile(r"\[(?P<name>.+)\]$")


def module_title(module: str) -> str:
    curriculum = json.loads((REPO_ROOT / "docs/data/curriculum.json").read_text(encoding="utf-8"))
    for entry in curriculum["modules"]:
        if entry["id"] == module:
            return entry["title"]
    return module


def collect(report: dict) -> dict[str, dict]:
    """Map check name -> {passed, error} from a pytest-json-report file."""
    results: dict[str, dict] = {}
    for test in report.get("tests", []):
        match = ID_RE.search(test["nodeid"])
        if not match:
            continue
        crash = (
            (test.get("call") or {}).get("crash") or (test.get("setup") or {}).get("crash") or {}
        )
        results[match["name"]] = {
            "passed": test["outcome"] == "passed",
            "error": (crash.get("message") or "").strip(),
        }
    return results


def shared_blocker(results: dict[str, dict]) -> str | None:
    """If every check died the same way, the submission never loaded at all."""
    failures = [r["error"] for r in results.values() if not r["passed"]]
    if failures and len(failures) == len(results) and len(set(failures)) == 1:
        return failures[0]
    return None


VERDICT = {"ok": False, "core_passed": 0, "core_total": 0, "reason": ""}


def render(module: str, handle: str, results: dict[str, dict]) -> str:
    suite = load_suite(REPO_ROOT / "modules" / module)
    title = module_title(module)
    lines = [MARKER, f"## {title} &middot; @{handle}", ""]

    blocker = shared_blocker(results)
    if blocker:
        lines += [
            "Nothing ran, because your file could not be loaded:",
            "",
            "```",
            blocker,
            "```",
            "",
            f"Fix that and push again - the check reruns on its own. "
            f"See [the task]({task_link(module)}) for where the file belongs.",
        ]
        VERDICT.update(ok=False, reason="the submission could not be loaded")
        return "\n".join(lines)

    core = [c for c in suite.checks if c.tier != STRETCH]
    stretch = [c for c in suite.checks if c.tier == STRETCH]
    core_passed = sum(1 for c in core if results.get(c.name, {}).get("passed"))
    stretch_passed = sum(1 for c in stretch if results.get(c.name, {}).get("passed"))

    if core_passed == len(core):
        headline = f"**All {len(core)} core checks pass.** Ready for a human to look at it."
    else:
        remaining = len(core) - core_passed
        headline = (
            f"**{core_passed} of {len(core)} core checks pass** - {remaining} to go. "
            "Push again whenever you like; this comment updates itself."
        )
    VERDICT.update(
        ok=core_passed == len(core),
        core_passed=core_passed,
        core_total=len(core),
        reason=""
        if core_passed == len(core)
        else f"{len(core) - core_passed} core check(s) still failing",
    )
    if stretch:
        headline += f" Stretch: {stretch_passed} of {len(stretch)}."
    lines += [headline, ""]

    for label, checks in (("Core", core), ("Stretch (optional)", stretch)):
        if not checks:
            continue
        lines += [f"### {label}", ""]
        for check in checks:
            result = results.get(check.name)
            mark = "⬜" if result is None else ("✅" if result["passed"] else "❌")
            lines.append(f"- {mark} {check.name}")
        lines.append("")

    failed = [c for c in suite.checks if not results.get(c.name, {}).get("passed", False)]
    if failed:
        lines += ["<details>", f"<summary>What went wrong ({len(failed)})</summary>", ""]
        for check in failed:
            lines += [
                f"**{check.name}**",
                "",
                "```",
                results.get(check.name, {}).get("error", "did not run"),
                "```",
            ]
            if check.hint:
                lines += ["", f"> Nudge: {check.hint}"]
            lines.append("")
        lines += ["</details>", ""]

    lines += [
        "---",
        f"[The task]({task_link(module)}) &middot; "
        f"[the checks, in full]({checks_link(module)})"
        + (
            f" &middot; [practise in your browser]({SITE_URL}playground.html?module={module})"
            if SITE_URL
            else ""
        ),
    ]
    return "\n".join(lines)


BASE_URL = ""
SITE_URL = ""


def task_link(module: str) -> str:
    return f"{BASE_URL}/blob/main/modules/{module}/TASK.md"


def checks_link(module: str) -> str:
    return f"{BASE_URL}/blob/main/modules/{module}/checks.py"


def render_guard(error: str) -> str:
    return "\n".join([MARKER, "## This pull request needs a small fix first", "", error])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--report", type=Path, help="pytest-json-report output")
    parser.add_argument("--out", type=Path, default=Path("comment.md"))
    parser.add_argument("--repo-url", default="", help="e.g. https://github.com/owner/research-gym")
    parser.add_argument("--site-url", default="", help="e.g. https://owner.github.io/research-gym/")
    parser.add_argument("--verdict", type=Path, default=Path("verdict.json"))
    args = parser.parse_args()

    global BASE_URL, SITE_URL
    BASE_URL = args.repo_url.rstrip("/")
    SITE_URL = (
        args.site_url if not args.site_url or args.site_url.endswith("/") else args.site_url + "/"
    )

    targets = json.loads(args.targets.read_text(encoding="utf-8"))

    def finish(body: str, ok: bool, reason: str) -> int:
        args.out.write_text(body, encoding="utf-8")
        VERDICT.update(ok=ok, reason=reason)
        args.verdict.write_text(json.dumps(VERDICT), encoding="utf-8")
        return 0

    if not targets["ok"]:
        return finish(render_guard(targets["error"]), False, "the pull request needs restructuring")

    if not targets["targets"]:
        return finish("", True, "nothing to check")

    target = targets["targets"][0]
    if not args.report or not args.report.is_file():
        return finish(
            render_guard(
                "The checks did not produce a report. Ping a maintainer - this one is on us."
            ),
            False,
            "the checks did not run",
        )

    report = json.loads(args.report.read_text(encoding="utf-8"))
    comment = render(target["module"], target["handle"], collect(report))
    return finish(comment, VERDICT["ok"], VERDICT["reason"])


if __name__ == "__main__":
    raise SystemExit(main())
