#!/usr/bin/env python3
"""Validate awesome-agent-trust list entries against quality criteria.

Checks each GitHub repo URL in README.md for:
- Repo exists (not 404/renamed/deleted)
- Has >= 5 stars (minimum adoption threshold, except for LF standards)
- Has commits within the last 12 months (active)
- Has a non-trivial description

Exit code 0 = all repos pass
Exit code 1 = one or more repos flagged (output is actionable table)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
NOW = datetime.now(timezone.utc)

# Repos can be exempted from star/activity checks if they're standards/specs
# Exit code 1 only for repos that are gone or archived (actionable)
# Low stars, weak descriptions, and inactivity produce warnings only
HARD_ERRORS = {"NOT_FOUND", "ARCHIVED"}

LF_KEYWORDS = (
    "linux foundation", "oasf", "aaif", "agntcy", "a2a",
    "ietf", "w3c", "eip-", "erc-", "specification",
)


def extract_repos(path: Path) -> set[str]:
    """Extract unique GitHub owner/name pairs from README."""
    text = path.read_text(encoding="utf-8")
    urls = re.findall(r'https://github\.com/[^) \n]+', text)
    repos: set[str] = set()
    for u in urls:
        u = u.rstrip(".,)")
        parts = u.replace("https://github.com/", "").split("/")
        if len(parts) >= 2 and parts[0]:
            repos.add(f"{parts[0]}/{parts[1]}")
    return repos


def check_repo(repo: str) -> dict[str, Any]:
    """Return validation results for one repo."""
    result = {
        "repo": repo,
        "exists": False,
        "stars": 0,
        "description": "",
        "pushed_at": "",
        "last_commit_days_ago": None,
        "archived": False,
        "is_lf": any(kw in repo.lower() for kw in LF_KEYWORDS),
        "errors": [],
    }

    try:
        proc = subprocess.run(
            ["gh", "api", f"repos/{repo}",
             "--jq", "{stars: .stargazers_count, desc: .description, pushed: .pushed_at, archived: .archived}"],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0:
            result["errors"].append("NOT_FOUND")
            return result

        data = json.loads(proc.stdout)
        result["exists"] = True
        result["stars"] = data.get("stars", 0)
        result["description"] = (data.get("desc") or "").strip()
        result["pushed_at"] = data.get("pushed", "")
        result["archived"] = data.get("archived", False)

    except Exception as e:
        result["errors"].append(f"API_ERROR: {e}")
        return result

    # Checks
    if result["archived"]:
        result["errors"].append("ARCHIVED")

    if not result["description"] or len(result["description"]) < 15:
        result["errors"].append("WEAK_DESC")

    # Star threshold: only enforce if NOT an LF/standards project
    if not result["is_lf"] and result["stars"] < 5:
        result["errors"].append("LOW_STARS")

    # Activity check
    if result["pushed_at"]:
        try:
            pushed = datetime.fromisoformat(result["pushed_at"].replace("Z", "+00:00"))
            days = (NOW - pushed).days
            result["last_commit_days_ago"] = days
            if days > 365:
                result["errors"].append("INACTIVE")
        except ValueError:
            pass

    return result


def main() -> int:
    repos = sorted(extract_repos(README_PATH))
    print(f"=== awesome-agent-trust validation: {len(repos)} repos ===\n")

    results = []
    for repo in repos:
        results.append(check_repo(repo))

    passed = [r for r in results if not r["errors"]]
    failed = [r for r in results if r["errors"]]

    print(f"PASS: {len(passed)}/{len(results)}")
    if failed:
        print(f"FLAGGED: {len(failed)}/{len(results)}\n")
        # Group by error type
        by_error: dict[str, list[str]] = {}
        for r in failed:
            for e in r["errors"]:
                by_error.setdefault(e, []).append(f"{r['repo']} ({r['stars']}★)")

        for err_type in ["NOT_FOUND", "ARCHIVED", "LOW_STARS", "INACTIVE", "WEAK_DESC"]:
            items = by_error.get(err_type, [])
            if items:
                print(f"  {err_type} ({len(items)}):")
                for item in items:
                    print(f"    {item}")

    hard_fails = [r for r in failed if any(e in HARD_ERRORS for e in r["errors"])]
    soft_fails = [r for r in failed if r not in hard_fails]

    print(f"\n{'='*50}")
    if hard_fails:
        print(f"HARD FAILURES ({len(hard_fails)}): repos that are 404 or archived — must fix")
        for r in hard_fails:
            print(f"  {r['repo']}: {', '.join(r['errors'])}")

    if soft_fails:
        print(f"SOFT FLAGS ({len(soft_fails)}): low stars, inactive, or weak description — review")

    if hard_fails:
        print("\nRESULT: Hard failures found — remove or replace these repos")
        return 1
    elif soft_fails:
        print("\nRESULT: Only soft flags (no hard failures)")
        return 0
    else:
        print("RESULT: All repos pass quality gates")
        return 0


if __name__ == "__main__":
    sys.exit(main())
