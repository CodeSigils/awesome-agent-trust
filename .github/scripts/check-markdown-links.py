#!/usr/bin/env python3
"""Check repository-relative Markdown links without requiring network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors: list[str] = []
    unreadable: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            # A file that cannot be decoded leaves the sweep incomplete, which
            # is neither a clean result nor a finding about a broken link.
            unreadable.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        for line_number, line in enumerate(lines, 1):
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
    for message in unreadable:
        print(f"COULD NOT CHECK: {message}", file=sys.stderr)
    if unreadable:
        print(
            f"{len(unreadable)} Markdown file(s) could not be read, so this check "
            "did not cover the whole repository and the result above is incomplete.",
            file=sys.stderr,
        )
        return 2
    if errors:
        return 1
    print("PASS: all repository-relative Markdown links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
