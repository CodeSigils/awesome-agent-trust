#!/usr/bin/env python3
"""Report pinned GitHub Action SHAs that differ from their major tag head."""

from __future__ import annotations

import os
import re
from pathlib import Path

from gh_api import fetch_json, resolve_token

PINNED = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@([0-9a-f]{40})\s+#\s*v(\d+)")
REPO_ROOT = Path(__file__).resolve().parents[2]


def latest_sha(repo: str, major: str, token: str) -> str:
    """Resolve the latest commit SHA for a major version tag."""
    data = fetch_json(
        f"https://api.github.com/repos/{repo}/git/ref/tags/v{major}",
        token=token,
        timeout=20,
    )
    target = data["object"]
    if target["type"] == "commit":
        return target["sha"]
    if target["type"] != "tag":
        raise ValueError(f"unexpected tag object type: {target['type']}")
    tag_data = fetch_json(
        f"https://api.github.com/repos/{repo}/git/tags/{target['sha']}",
        token=token,
        timeout=20,
    )
    tag = tag_data["object"]
    if tag["type"] != "commit":
        raise ValueError("annotated action tag does not resolve to a commit")
    return tag["sha"]


def main() -> int:
    token = resolve_token() or ""
    rows: list[str] = []
    unreadable: list[str] = []
    for path in sorted((REPO_ROOT / ".github").rglob("*.yml")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            # Reading the file is environmental, so it is reported apart from
            # the status rows rather than guessed at.
            unreadable.append(f"- `{path.relative_to(REPO_ROOT)}`: {exc}")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            match = PINNED.search(line)
            if not match:
                continue
            repo, pinned, major = match.groups()
            try:
                state = "current" if pinned == latest_sha(repo, major, token) else "update available"
            except (OSError, KeyError, ValueError):
                state = "unknown"
            rows.append(f"| `{repo}` | `v{major}` | {state} | `{path.relative_to(REPO_ROOT)}:{number}` |")
    report = "## GitHub Action freshness\n\n| Action | Major | Status | Location |\n|---|---:|---|---|\n"
    if rows:
        report += "\n".join(rows)
    elif unreadable:
        report += "No pinned actions could be read."
    else:
        report += "No pinned actions found."
    if unreadable:
        report += "\n\nCOULD NOT CHECK:\n" + "\n".join(unreadable)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(report + "\n", encoding="utf-8")
    return 2 if unreadable else 0


if __name__ == "__main__":
    raise SystemExit(main())
