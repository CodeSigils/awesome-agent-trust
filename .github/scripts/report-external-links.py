#!/usr/bin/env python3
"""Report health of non-GitHub external links in README.md without gating CI."""

from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import NamedTuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
MAX_WORKERS = 8
TIMEOUT_SECONDS = 15
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class LinkResult(NamedTuple):
    url: str
    status: str
    detail: str


def extract_external_links(text: str) -> list[str]:
    """Return sorted, unique non-GitHub HTTP(S) Markdown destinations."""
    links: set[str] = set()
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.split(maxsplit=1)[0].strip("<>").strip()
        parsed = urlparse(target)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        host = parsed.hostname or ""
        if host == "github.com" or host.endswith(".github.com"):
            continue
        links.add(target)
    return sorted(links)


def _request(url: str, method: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "awesome-agent-trust-link-monitor"}, method=method)
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.status, response.geturl()


def check_link(url: str) -> LinkResult:
    """Classify a link without treating remote availability as a CI failure."""
    try:
        status_code, resolved_url = _request(url, "HEAD")
    except HTTPError as exc:
        if exc.code not in {405, 501}:
            return LinkResult(url, "broken" if exc.code in {404, 410} else "unknown", f"HTTP {exc.code}")
        try:
            status_code, resolved_url = _request(url, "GET")
        except HTTPError as get_exc:
            return LinkResult(url, "broken" if get_exc.code in {404, 410} else "unknown", f"HTTP {get_exc.code}")
        except (URLError, TimeoutError, OSError, ValueError) as get_exc:
            return LinkResult(url, "unknown", type(get_exc).__name__)
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return LinkResult(url, "unknown", type(exc).__name__)

    state = "redirect" if resolved_url != url else "ok"
    return LinkResult(url, state, f"HTTP {status_code}" + (f" → {resolved_url}" if state == "redirect" else ""))


def render_report(results: list[LinkResult]) -> str:
    """Render a concise, GitHub-summary-friendly link-health report."""
    counts = {state: sum(result.status == state for result in results) for state in ("ok", "redirect", "broken", "unknown")}
    lines = [
        "## External link health",
        "",
        "Advisory only: remote outages, rate limits, and redirects do not fail this workflow.",
        "",
        f"Checked {len(results)} non-GitHub README links: {counts['ok']} ok, {counts['redirect']} redirects, {counts['broken']} broken, {counts['unknown']} unknown.",
        "",
        "| Status | Link | Detail |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| {result.status} | {result.url} | {result.detail} |" for result in results)
    return "\n".join(lines)


def main() -> int:
    links = extract_external_links(README_PATH.read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(check_link, links))
    report = render_report(results)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as handle:
            handle.write(report + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
