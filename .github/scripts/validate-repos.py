#!/usr/bin/env python3
"""Validate repository links and review signals in the awesome list.

Missing or archived repositories and incomplete API checks fail validation.
Advisory quality signals remain non-blocking unless they are configuration
errors. Narrow, evidence-backed exceptions live in repo-exceptions.json.
"""

from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

from gh_api import fetch_json, mask_token, resolve_token

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
EXCEPTIONS_PATH = REPO_ROOT / ".github" / "repo-exceptions.json"
BASELINE_PATH = REPO_ROOT / ".github" / "advisory-baseline.json"
NOW = datetime.now(timezone.utc)
MAX_WORKERS = 8

HARD_ERRORS = {"NOT_FOUND", "ARCHIVED", "API_ERROR", "CONFIG_ERROR", "MISORDERED"}
SOFT_ERRORS = {
    "NO_LICENSE",
    "LOW_STARS",
    "INACTIVE",
    "WEAK_DESC",
    "BARE_ENTRY",
    "UNVALIDATED_HOST",
    "UNVALIDATED_LINK",
}
STAR_THRESHOLD = 5
CODE_HOSTS = {"gitlab.com", "codeberg.org", "git.sr.ht", "bitbucket.org"}
ENTRY_LINK_RE = re.compile(r"^- \[([^]]+)\]\((https?://[^)\s]+)")


def extract_repos(path: Path) -> set[str]:
    """Extract normalized GitHub owner/repository pairs from Markdown links."""
    text = path.read_text(encoding="utf-8")
    urls = re.findall(r"https://github\.com/[^)\s]+", text)
    repos: set[str] = set()
    for url in urls:
        parts = url.rstrip(".,)").removeprefix("https://github.com/").split("/")
        if len(parts) >= 2 and parts[0] and parts[1]:
            repos.add(f"{parts[0]}/{parts[1]}")
    return repos


def extract_entry_links(path: Path) -> list[tuple[int, str, str]]:
    """Extract (line, display name, url) for each Markdown list entry link."""
    entries: list[tuple[int, str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = ENTRY_LINK_RE.match(line.strip())
        if match:
            entries.append((line_number, match.group(1), match.group(2).rstrip(".,)")))
    return entries


def classify_entry_link(url: str) -> tuple[str, str]:
    """Return (category, host) for an entry URL: github / code_host / external."""
    host = (urlsplit(url).hostname or "unknown").lower()
    if host == "github.com":
        return "github", host
    if host in CODE_HOSTS:
        return "code_host", host
    return "external", host


def entry_flags_for(entries: list[tuple[int, str, str]]) -> dict[str, list[str]]:
    """Map entry links to advisory flags for hosts that skip automated checks.

    GitHub links are validated in full by extract_repos(); recognized
    non-GitHub code hosts and other external sites get advisory flags so a
    maintainer reviews them instead of letting them pass silently. For
    recognized code hosts (UNVALIDATED_HOST) the maintainer should verify
    existence, license, and activity by hand; for other external sites
    (UNVALIDATED_LINK) a full destination review is expected.
    """
    flags: dict[str, list[str]] = {}
    for _line, name, url in entries:
        category, host = classify_entry_link(url)
        if category == "github":
            continue
        flag = "UNVALIDATED_HOST" if category == "code_host" else "UNVALIDATED_LINK"
        flags.setdefault(flag, []).append(f"{name} ({host})")
    return flags


def load_exceptions(path: Path, *, today: date | None = None) -> tuple[dict[str, set[str]], list[str]]:
    """Load reviewed exceptions and return them with configuration errors."""
    today = today or datetime.now(timezone.utc).date()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot read {path}: {exc}"]

    if not isinstance(raw, dict) or not isinstance(raw.get("exceptions"), list):
        return {}, [f"{path}: top-level 'exceptions' must be a list"]

    exceptions: dict[str, set[str]] = {}
    errors: list[str] = []
    for index, item in enumerate(raw["exceptions"], 1):
        if not isinstance(item, dict):
            errors.append(f"entry {index}: must be an object")
            continue
        repo = item.get("repo", "")
        raw_checks = item.get("checks", [])
        reason = item.get("reason", "")
        review_after = item.get("review_after", "")
        label = repo or f"entry {index}"

        if not isinstance(repo, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
            errors.append(f"{label}: invalid repository name")
        elif repo in exceptions:
            errors.append(f"{label}: duplicate exception")
        if not isinstance(raw_checks, list):
            errors.append(f"{label}: checks must be a list")
            continue
        if not all(isinstance(check, str) for check in raw_checks):
            errors.append(f"{label}: checks must contain only strings")
            continue
        checks = set(raw_checks)
        unknown = checks - SOFT_ERRORS
        if unknown:
            errors.append(f"{label}: unsupported checks: {', '.join(sorted(unknown))}")
        if not checks:
            errors.append(f"{label}: checks must not be empty")
        if not isinstance(reason, str) or len(reason.strip()) < 20:
            errors.append(f"{label}: reason must contain reviewable evidence")
        try:
            review_date = date.fromisoformat(review_after)
            if review_date < today:
                errors.append(f"{label}: exception expired on {review_after}")
        except (TypeError, ValueError):
            errors.append(f"{label}: review_after must be an ISO date")

        if isinstance(repo, str):
            exceptions[repo] = checks
    return exceptions, errors


def load_advisory_baseline(path: Path) -> tuple[set[tuple[str, str]], list[str]]:
    """Load the observed advisory snapshot; it does not waive any checks."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return set(), [f"cannot read {path}: {exc}"]
    if not isinstance(raw, dict) or not isinstance(raw.get("advisories"), dict):
        return set(), [f"{path}: top-level 'advisories' must be an object"]
    try:
        date.fromisoformat(raw.get("reviewed", ""))
    except (TypeError, ValueError):
        return set(), [f"{path}: 'reviewed' must be an ISO date"]

    pairs: set[tuple[str, str]] = set()
    errors: list[str] = []
    for check, repos in raw["advisories"].items():
        if check not in SOFT_ERRORS:
            errors.append(f"{path}: unsupported advisory {check}")
            continue
        if not isinstance(repos, list) or not all(isinstance(repo, str) for repo in repos):
            errors.append(f"{path}: {check} must be a list of repositories")
            continue
        pairs.update((check, repo) for repo in repos)
    return pairs, errors


def check_repo(repo: str, *, token: str | None = None, now: datetime = NOW) -> dict[str, Any]:
    """Return hard failures and advisory signals for one repository."""
    result: dict[str, Any] = {
        "repo": repo,
        "stars": 0,
        "last_commit_days_ago": None,
        "errors": [],
        "detail": "",
    }
    try:
        data = fetch_json(f"https://api.github.com/repos/{repo}", token=token)
    except HTTPError as exc:
        # A scoped credential can receive a 404 for a public repository it
        # cannot access. Check once without credentials before treating the
        # repository as gone; listed repositories are required to be public.
        if exc.code == 404 and token:
            try:
                data = fetch_json(f"https://api.github.com/repos/{repo}")
            except HTTPError as fallback_exc:
                if fallback_exc.code == 404:
                    result["errors"].append("NOT_FOUND")
                else:
                    result["errors"].append("API_ERROR")
                    result["detail"] = f"GitHub returned HTTP {fallback_exc.code} without credentials"
                return result
            except (URLError, TimeoutError, OSError, json.JSONDecodeError) as fallback_exc:
                result["errors"].append("API_ERROR")
                result["detail"] = str(fallback_exc)
                return result
        else:
            if exc.code == 404:
                result["errors"].append("NOT_FOUND")
            else:
                result["errors"].append("API_ERROR")
                result["detail"] = mask_token(f"GitHub returned HTTP {exc.code}", token)
            return result
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        result["errors"].append("API_ERROR")
        result["detail"] = mask_token(str(exc), token)
        return result

    result["stars"] = data.get("stargazers_count", 0)
    description = (data.get("description") or "").strip()
    pushed_at = data.get("pushed_at") or ""

    if data.get("archived", False):
        result["errors"].append("ARCHIVED")
    if not data.get("license"):
        result["errors"].append("NO_LICENSE")
    if len(description) < 15:
        result["errors"].append("WEAK_DESC")
    if result["stars"] < STAR_THRESHOLD:
        result["errors"].append("LOW_STARS")

    if isinstance(pushed_at, str) and pushed_at:
        try:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            if pushed.tzinfo is None:
                raise ValueError("pushed_at must include a timezone")
            result["last_commit_days_ago"] = (now - pushed).days
            if result["last_commit_days_ago"] > 365:
                result["errors"].append("INACTIVE")
        except ValueError:
            result["errors"].append("API_ERROR")
            result["detail"] = "GitHub returned an invalid pushed_at timestamp"
    return result


def audit_low_stars(
    baseline: set[tuple[str, str]],
    *,
    token: str | None = None,
    now: datetime = NOW,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Group LOW_STARS baseline entries by their current star status."""
    repos = sorted({repo for check, repo in baseline if check == "LOW_STARS"})
    resolved: list[dict[str, Any]] = []
    still_below: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    api_errors: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in executor.map(lambda repo: check_repo(repo, token=token, now=now), repos):
            entry = {"repo": result["repo"], "stars": result["stars"]}
            if "NOT_FOUND" in result["errors"] or "ARCHIVED" in result["errors"]:
                entry["reason"] = "NOT_FOUND" if "NOT_FOUND" in result["errors"] else "ARCHIVED"
                unavailable.append(entry)
            elif "API_ERROR" in result["errors"]:
                entry["detail"] = result["detail"]
                api_errors.append(entry)
            elif result["stars"] >= STAR_THRESHOLD:
                resolved.append(entry)
            else:
                still_below.append(entry)
    resolved.sort(key=lambda item: (-item["stars"], item["repo"]))
    still_below.sort(key=lambda item: (-item["stars"], item["repo"]))
    unavailable.sort(key=lambda item: item["repo"])
    api_errors.sort(key=lambda item: item["repo"])
    return resolved, still_below, unavailable, api_errors


def check_readme_descriptions(path: Path) -> list[tuple[int, str]]:
    """Return list entries that do not have a description after the link."""
    bare: list[tuple[int, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith("- [") or "](http" not in stripped:
            continue
        match = re.match(r"^- \[[^]]+\]\([^)]+\)(.*)$", stripped)
        if match and not match.group(1).startswith((" - ", " — ")):
            bare.append((line_number, stripped[:100]))
    return bare


def check_readme_ordering(path: Path) -> list[str]:
    """Return categories whose Markdown entries are not alphabetized."""
    failures: list[str] = []
    section = ""
    names: list[str] = []

    def finish_section() -> None:
        if section and section != "Contents":
            expected = sorted(names, key=str.casefold)
            if names != expected:
                failures.append(section)

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            finish_section()
            section = line.removeprefix("## ").strip()
            names = []
            continue
        if section:
            match = re.match(r"^- \[([^]]+)\]\(https?://", line)
            if match:
                names.append(match.group(1))
    finish_section()
    return failures


def compare_advisories(
    active_flags: dict[str, list[str]],
    baseline: set[tuple[str, str]],
    *,
    complete: bool,
) -> tuple[set[tuple[str, str]], set[tuple[str, str]], set[tuple[str, str]]]:
    """Compare advisories without claiming resolutions from partial metadata."""
    current = {
        (error, repo)
        for error, items in active_flags.items()
        if error in SOFT_ERRORS
        for repo in items
    }
    return current, current - baseline, baseline - current if complete else set()


def run_baseline_audit() -> int:
    """Print which LOW_STARS baseline entries have crossed the star threshold."""
    baseline, config_errors = load_advisory_baseline(BASELINE_PATH)
    if config_errors:
        for error in config_errors:
            print(error)
        return 1
    low_stars = {repo for check, repo in baseline if check == "LOW_STARS"}
    print(f"=== LOW_STARS baseline audit: {len(low_stars)} repositories ===\n")
    resolved, still_below, unavailable, api_errors = audit_low_stars(
        baseline, token=resolve_token()
    )
    if resolved:
        print(f"RESOLVED (>= {STAR_THRESHOLD} stars, clear from baseline):")
        for entry in resolved:
            print(f"  {entry['repo']} ({entry['stars']} stars)")
        print()
    if still_below:
        print(f"STILL BELOW {STAR_THRESHOLD} stars:")
        for entry in still_below:
            print(f"  {entry['repo']} ({entry['stars']} stars)")
        print()
    if unavailable:
        print("UNAVAILABLE (gone, renamed, or archived; do not clear):")
        for entry in unavailable:
            print(f"  {entry['repo']} ({entry['reason']})")
        print()
    if api_errors:
        print("API ERRORS (metadata incomplete, re-check later):")
        for entry in api_errors:
            print(f"  {entry['repo']}: {entry['detail']}")
        print()
    print(
        f"SUMMARY: {len(resolved)} resolved, {len(still_below)} still below, "
        f"{len(unavailable)} unavailable, {len(api_errors)} api error(s)"
    )
    return 0


def main() -> int:
    if "--baseline-audit" in sys.argv[1:]:
        return run_baseline_audit()
    repos = sorted(extract_repos(README_PATH))
    exceptions, config_errors = load_exceptions(EXCEPTIONS_PATH)
    baseline, baseline_errors = load_advisory_baseline(BASELINE_PATH)
    config_errors.extend(baseline_errors)
    unknown_repos = sorted(set(exceptions) - set(repos))
    config_errors.extend(f"{repo}: exception refers to an unlisted repository" for repo in unknown_repos)

    print(f"=== awesome-agent-trust validation: {len(repos)} repositories ===\n")
    token = resolve_token()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(lambda repo: check_repo(repo, token=token), repos))

    active_flags: dict[str, list[str]] = {}
    accepted_count = 0
    hard_failures: list[dict[str, Any]] = []
    for result in results:
        waived = exceptions.get(result["repo"], set())
        accepted_count += len(set(result["errors"]) & waived)
        result["errors"] = [error for error in result["errors"] if error not in waived]
        if any(error in HARD_ERRORS for error in result["errors"]):
            hard_failures.append(result)
        for error in result["errors"]:
            active_flags.setdefault(error, []).append(result["repo"])

    bare_entries = check_readme_descriptions(README_PATH)
    if bare_entries:
        active_flags["BARE_ENTRY"] = [f"README.md:{line}" for line, _ in bare_entries]
    misordered_sections = check_readme_ordering(README_PATH)
    if misordered_sections:
        active_flags["MISORDERED"] = misordered_sections
    if config_errors:
        active_flags["CONFIG_ERROR"] = config_errors
    for flag, items in entry_flags_for(extract_entry_links(README_PATH)).items():
        active_flags.setdefault(flag, []).extend(items)

    comparison_complete = not any("API_ERROR" in result["errors"] for result in results)
    current_advisories, new_advisories, resolved_advisories = compare_advisories(
        active_flags, baseline, complete=comparison_complete
    )
    report_flags = {
        error: items for error, items in active_flags.items() if error in HARD_ERRORS
    }
    for error, repo in sorted(new_advisories):
        report_flags.setdefault(f"NEW_{error}", []).append(repo)

    for error in sorted(report_flags, key=lambda item: (item.startswith("NEW_"), item)):
        items = report_flags[error]
        print(f"{error} ({len(items)}):")
        for item in items:
            print(f"  {item}")
    if current_advisories:
        print(f"KNOWN ADVISORIES: {len(current_advisories) - len(new_advisories)}")
    if not comparison_complete:
        print("ADVISORY COMPARISON SKIPPED: repository metadata was incomplete")
    if resolved_advisories:
        print(f"RESOLVED ADVISORIES: {len(resolved_advisories)} (update the baseline)")
        for error, repo in sorted(resolved_advisories):
            print(f"  {error}: {repo}")
    if accepted_count:
        print(f"\nACCEPTED EXCEPTIONS: {accepted_count}")

    hard_count = sum(len(items) for error, items in active_flags.items() if error in HARD_ERRORS)
    soft_count = sum(len(items) for error, items in active_flags.items() if error in SOFT_ERRORS)
    print(
        f"\nSUMMARY: {hard_count} hard failure(s), "
        f"{len(new_advisories)} new and {soft_count - len(new_advisories)} known advisory flag(s)"
    )
    if hard_failures:
        for result in hard_failures:
            if result["detail"]:
                print(f"  {result['repo']}: {result['detail']}")
    return 1 if hard_count else 0


if __name__ == "__main__":
    sys.exit(main())
