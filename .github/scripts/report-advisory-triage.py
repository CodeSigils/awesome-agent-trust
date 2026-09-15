#!/usr/bin/env python3
"""Report advisory counts and exception-review dates without changing state."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = REPO_ROOT / ".github" / "advisory-baseline.json"
EXCEPTIONS_PATH = REPO_ROOT / ".github" / "repo-exceptions.json"


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"{path.relative_to(REPO_ROOT)}: {exc}"
    if not isinstance(value, dict):
        return None, f"{path.relative_to(REPO_ROOT)}: top-level value must be an object"
    return value, None


def render_report(*, baseline: dict[str, Any] | None, exceptions: dict[str, Any] | None, today: date) -> str:
    """Render a triage report; malformed inputs are shown as warnings."""
    lines = ["## Advisory triage", "", "Advisory only: this report never edits baseline or exception state.", ""]
    if baseline is None:
        lines.append("⚠️ Unable to read advisory baseline.")
    else:
        advisories = baseline.get("advisories", {})
        if isinstance(advisories, dict):
            lines.extend(["| Signal | Entries |", "| --- | ---: |"])
            for signal, repos in sorted(advisories.items()):
                count = len(repos) if isinstance(repos, list) else "invalid"
                lines.append(f"| `{signal}` | {count} |")
            lines.append("")
        else:
            lines.append("⚠️ `advisories` is not an object.")

    if exceptions is None:
        lines.append("⚠️ Unable to read repository exceptions.")
        return "\n".join(lines)

    raw_exceptions = exceptions.get("exceptions", [])
    if not isinstance(raw_exceptions, list):
        lines.append("⚠️ `exceptions` is not a list.")
        return "\n".join(lines)

    lines.extend(["| Exception | Review after | Status |", "| --- | --- | --- |"])
    overdue = 0
    for item in raw_exceptions:
        if not isinstance(item, dict):
            lines.append("| *(invalid entry)* | — | invalid |")
            continue
        repo = str(item.get("repo", "(missing repo)"))
        review_after = item.get("review_after", "")
        try:
            review_date = date.fromisoformat(review_after)
            status = "overdue" if review_date < today else "current"
            overdue += status == "overdue"
        except (TypeError, ValueError):
            status = "invalid date"
        lines.append(f"| `{repo}` | {review_after or '—'} | {status} |")
    lines.extend(["", f"Exception reviews overdue: **{overdue}**"])
    return "\n".join(lines)


def main() -> int:
    baseline, baseline_error = load_json(BASELINE_PATH)
    exceptions, exceptions_error = load_json(EXCEPTIONS_PATH)
    report = render_report(
        baseline=baseline,
        exceptions=exceptions,
        today=datetime.now(timezone.utc).date(),
    )
    warnings = [error for error in (baseline_error, exceptions_error) if error]
    if warnings:
        report += "\n\nWarnings:\n" + "\n".join(f"- {warning}" for warning in warnings)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as handle:
            handle.write(report + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
