#!/usr/bin/env python3
"""Verify the repository's protected-branch settings without changing them."""

from __future__ import annotations

import sys
from typing import Any
from urllib.error import HTTPError, URLError

from gh_api import fetch_json, mask_token, resolve_token

REPOSITORY = "CodeSigils/awesome-agent-trust"
BRANCH = "main"
REQUIRED_CHECKS = {"awesome-lint", "validate-repos", "secret-scan"}


def evaluate_protection(protection: dict[str, Any]) -> list[str]:
    """Return human-readable drift from the repository's required protection."""
    errors: list[str] = []
    checks = protection.get("required_status_checks", {})
    contexts = checks.get("contexts", []) if isinstance(checks, dict) else []
    if not isinstance(contexts, list) or set(contexts) != REQUIRED_CHECKS:
        found = ", ".join(sorted(str(context) for context in contexts)) if isinstance(contexts, list) else "invalid value"
        expected = ", ".join(sorted(REQUIRED_CHECKS))
        errors.append(f"required checks differ (expected: {expected}; found: {found})")
    if not isinstance(checks, dict) or checks.get("strict") is not True:
        errors.append("branch must be up to date before merging (strict status checks)")

    admins = protection.get("enforce_admins", {})
    if not isinstance(admins, dict) or admins.get("enabled") is not True:
        errors.append("branch protection must apply to administrators")
    return errors


def main() -> int:
    token = resolve_token()
    if not token:
        print("ERROR: authenticate with gh auth login or provide GH_TOKEN/GITHUB_TOKEN; no token is stored by this script.")
        return 2
    url = f"https://api.github.com/repos/{REPOSITORY}/branches/{BRANCH}/protection"
    try:
        protection = fetch_json(url, token=token)
    except HTTPError as exc:
        print(mask_token(f"ERROR: GitHub returned HTTP {exc.code}; the token needs repository administration read access.", token))
        return 2
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        print(mask_token(f"ERROR: unable to read branch protection: {exc}", token))
        return 2

    errors = evaluate_protection(protection)
    if errors:
        print("SETTINGS DRIFT:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: main protection requires awesome-lint, validate-repos, and secret-scan; administrators are included.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
