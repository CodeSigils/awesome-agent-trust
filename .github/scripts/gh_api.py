"""Shared GitHub API client with transient-failure retry and token masking."""

from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_RETRYABLE = (URLError, TimeoutError, OSError)

_USER_AGENT = "awesome-agent-trust"


def resolve_token() -> str | None:
    """Use an Actions token or the authenticated GitHub CLI token locally."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def fetch_json(
    url: str,
    *,
    token: str | None = None,
    timeout: int = 15,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Fetch a JSON endpoint with automatic retry on transient failures.

    Retries on URLError, TimeoutError, and OSError (connection resets, DNS
    hiccups, etc.).  HTTPError is NOT retried — 403/429/5xx are server-side
    decisions that won't resolve in one second.
    """
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "User-Agent": _USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except HTTPError:
            raise  # server errors are not transient
        except _RETRYABLE as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                continue
    raise last_exc  # type: ignore[misc]


def mask_token(text: str, token: str | None) -> str:
    """Replace a token string in error output so it is never logged."""
    if not token:
        return text
    return text.replace(token, "***")
