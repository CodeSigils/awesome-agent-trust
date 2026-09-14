#!/usr/bin/env python3
"""Report pinned GitHub Action SHAs that differ from their major tag head."""

from __future__ import annotations

import os
import re
from pathlib import Path

from gh_api import fetch_json, resolve_token

PINNED = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@([0-9a-f]{40})\s+#\s*v(\d+)")


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
    for path in sorted(Path(".github").rglob("*.yml")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = PINNED.search(line)
            if not match:
                continue
            repo, pinned, major = match.groups()
            try:
                state = "current" if pinned == latest_sha(repo, major, token) else "update available"
            except (OSError, KeyError, ValueError):
                state = "unknown"
            rows.append(f"| `{repo}` | `v{major}` | {state} | `{path}:{number}` |")
    report = "## GitHub Action freshness\n\n| Action | Major | Status | Location |\n|---|---:|---|---|\n"
    report += "\n".join(rows) if rows else "No pinned actions found."
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
