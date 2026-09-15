#!/usr/bin/env python3
"""Check repository-relative Markdown links without requiring network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", line):
                target = target.split("#", 1)[0].strip("<>").strip()
                if (
                    not target
                    or target.lower() in {"url", "link", "example.com"}
                    or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
                    or target.startswith("//")
                ):
                    continue
                if not (path.parent / target).resolve().exists():
                    errors.append(f"{path.relative_to(ROOT)}:{line_number}: missing {target}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: all repository-relative Markdown links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
