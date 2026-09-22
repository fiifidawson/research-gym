"""Copy the Python the browser playground needs into docs/_browser/.

GitHub Pages only serves docs/, but the playground has to run the *real*
checks.py - the entire point is that the browser and the pull request cannot
disagree. So we copy, rather than reimplement.

Run it yourself before serving the site locally:

    python .github/scripts/build_browser_bundle.py
    python -m http.server -d docs
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Modules that Pyodide can actually run: NumPy only, no torch.
GYM_FILES = ["__init__.py", "checks.py", "data.py", "seed.py"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "docs/_browser")
    args = parser.parse_args()

    curriculum = json.loads(
        (REPO_ROOT / "docs/data/curriculum.json").read_text(encoding="utf-8")
    )
    browser_modules = [m for m in curriculum["modules"] if m.get("browser")]

    if args.out.exists():
        shutil.rmtree(args.out)
    (args.out / "gym").mkdir(parents=True)

    for name in GYM_FILES:
        shutil.copy2(REPO_ROOT / "gym" / name, args.out / "gym" / name)

    manifest = []
    for module in browser_modules:
        module_id = module["id"]
        source = REPO_ROOT / "modules" / module_id
        if not (source / "checks.py").is_file():
            print(f"  skipping {module_id}: no checks.py yet")
            continue

        destination = args.out / module_id
        destination.mkdir(parents=True)
        shutil.copy2(source / "checks.py", destination / "checks.py")

        starter = source / "starter" / module["entrypoint"]
        if starter.is_file():
            shutil.copy2(starter, destination / module["entrypoint"])

        manifest.append(
            {
                "id": module_id,
                "title": module["title"],
                "entrypoint": module["entrypoint"],
                "has_starter": starter.is_file(),
            }
        )
        print(f"  bundled {module_id}")

    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{len(manifest)} module(s) available in the browser")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
