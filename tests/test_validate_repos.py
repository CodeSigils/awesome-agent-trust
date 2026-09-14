from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SCRIPTS_DIR = Path(__file__).parents[1] / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
SPEC = importlib.util.spec_from_file_location("validate_repos", SCRIPTS_DIR / "validate-repos.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

GH_API_SPEC = importlib.util.spec_from_file_location("gh_api", SCRIPTS_DIR / "gh_api.py")
assert GH_API_SPEC and GH_API_SPEC.loader
gh_api = importlib.util.module_from_spec(GH_API_SPEC)
GH_API_SPEC.loader.exec_module(gh_api)


class ExtractReposTests(unittest.TestCase):
    def test_extracts_normalized_unique_repository_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(
                "[One](https://github.com/owner/repo)\n"
                "[File](https://github.com/owner/repo/blob/main/file.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(validator.extract_repos(path), {"owner/repo"})


class CheckRepoTests(unittest.TestCase):
    def test_404_is_not_found(self) -> None:
        error = HTTPError("url", 404, "missing", {}, None)
        with patch.object(validator, "fetch_json", side_effect=error):
            self.assertEqual(validator.check_repo("owner/repo")["errors"], ["NOT_FOUND"])

    def test_rate_limit_is_api_error_not_not_found(self) -> None:
        error = HTTPError("url", 403, "rate limited", {}, None)
        with patch.object(validator, "fetch_json", side_effect=error):
            result = validator.check_repo("owner/repo")
        self.assertEqual(result["errors"], ["API_ERROR"])
        self.assertIn("403", result["detail"])

    def test_network_failure_is_api_error(self) -> None:
        with patch.object(validator, "fetch_json", side_effect=URLError("offline")):
            self.assertEqual(validator.check_repo("owner/repo")["errors"], ["API_ERROR"])

    def test_quality_and_archive_signals(self) -> None:
        metadata = {
            "stargazers_count": 2,
            "description": "short",
            "pushed_at": "2024-01-01T00:00:00Z",
            "archived": True,
            "license": None,
        }
        now = datetime(2026, 1, 2, tzinfo=timezone.utc)
        with patch.object(validator, "fetch_json", return_value=metadata):
            result = validator.check_repo("owner/repo", now=now)
        self.assertEqual(
            set(result["errors"]),
            {"ARCHIVED", "NO_LICENSE", "WEAK_DESC", "LOW_STARS", "INACTIVE"},
        )


class TokenTests(unittest.TestCase):
    def test_prefers_environment_token(self) -> None:
        with patch.dict(os.environ, {"GH_TOKEN": "workflow-token"}, clear=True):
            self.assertEqual(validator.resolve_token(), "workflow-token")

    def test_falls_back_to_github_cli(self) -> None:
        completed = gh_api.subprocess.CompletedProcess([], 0, "cli-token\n", "")
        with patch.dict(os.environ, {}, clear=True), patch.object(
            gh_api.subprocess, "run", return_value=completed
        ):
            self.assertEqual(validator.resolve_token(), "cli-token")


class ExceptionTests(unittest.TestCase):
    def test_loads_current_evidence_backed_exception(self) -> None:
        payload = {
            "exceptions": [{
                "repo": "owner/repo",
                "checks": ["LOW_STARS"],
                "reason": "Independent interoperability verification is documented.",
                "review_after": "2027-01-01",
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exceptions.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            exceptions, errors = validator.load_exceptions(path, today=date(2026, 1, 1))
        self.assertEqual(exceptions, {"owner/repo": {"LOW_STARS"}})
        self.assertEqual(errors, [])

    def test_rejects_expired_or_hard_failure_exception(self) -> None:
        payload = {
            "exceptions": [{
                "repo": "owner/repo",
                "checks": ["NOT_FOUND"],
                "reason": "This reason is long enough to be reviewed.",
                "review_after": "2025-01-01",
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exceptions.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            _, errors = validator.load_exceptions(path, today=date(2026, 1, 1))
        self.assertTrue(any("unsupported" in error for error in errors))
        self.assertTrue(any("expired" in error for error in errors))

    def test_rejects_invalid_top_level_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exceptions.json"
            path.write_text("[]", encoding="utf-8")
            exceptions, errors = validator.load_exceptions(path)
        self.assertEqual(exceptions, {})
        self.assertTrue(any("must be a list" in error for error in errors))


class BaselineTests(unittest.TestCase):
    def test_loads_advisories_as_observed_pairs(self) -> None:
        payload = {
            "reviewed": "2026-08-16",
            "advisories": {"LOW_STARS": ["owner/repo"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "baseline.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            baseline, errors = validator.load_advisory_baseline(path)
        self.assertEqual(baseline, {("LOW_STARS", "owner/repo")})
        self.assertEqual(errors, [])

    def test_rejects_unknown_advisory(self) -> None:
        payload = {
            "reviewed": "2026-08-16",
            "advisories": {"NOT_FOUND": ["owner/repo"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "baseline.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            baseline, errors = validator.load_advisory_baseline(path)
        self.assertEqual(baseline, set())
        self.assertTrue(any("unsupported" in error for error in errors))

    def test_partial_metadata_never_claims_resolved_advisories(self) -> None:
        baseline = {("LOW_STARS", "owner/repo")}
        current, new, resolved = validator.compare_advisories({}, baseline, complete=False)
        self.assertEqual((current, new, resolved), (set(), set(), set()))

    def test_complete_metadata_reports_resolved_advisories(self) -> None:
        baseline = {("LOW_STARS", "owner/repo")}
        _, _, resolved = validator.compare_advisories({}, baseline, complete=True)
        self.assertEqual(resolved, baseline)


class DescriptionTests(unittest.TestCase):
    def test_finds_bare_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(
                "- [Bare](https://example.com)\n"
                "- [Good](https://example.com/good) - Useful description.\n",
                encoding="utf-8",
            )
            self.assertEqual(validator.check_readme_descriptions(path), [(1, "- [Bare](https://example.com)")])


class OrderingTests(unittest.TestCase):
    def test_accepts_alphabetical_entries_and_ignores_contents(self) -> None:
        text = (
            "## Contents\n"
            "- [Zed](https://example.com/zed)\n"
            "- [Alpha](https://example.com/alpha)\n\n"
            "## Projects\n"
            "- [alpha](https://example.com/a) - A.\n"
            "- [Beta](https://example.com/b) - B.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(validator.check_readme_ordering(path), [])

    def test_reports_misordered_category(self) -> None:
        text = (
            "## Projects\n"
            "- [Zulu](https://example.com/z) - Z.\n"
            "- [Alpha](https://example.com/a) - A.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(validator.check_readme_ordering(path), ["Projects"])


class GhApiTests(unittest.TestCase):
    def test_retries_transient_failures_then_succeeds(self) -> None:
        attempts = 0

        class Response:
            def __enter__(self) -> Response:
                return self

            def __exit__(self, *_: object) -> None:
                return None

            def read(self) -> bytes:
                return b'{"ok": true}'

        def flaky(_: str, **__: object) -> Response:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise URLError("offline")
            return Response()

        with patch.object(gh_api, "urlopen", side_effect=flaky):
            data = gh_api.fetch_json("https://api.github.com/repos/owner/repo", max_retries=3)
        self.assertEqual(data, {"ok": True})
        self.assertEqual(attempts, 3)

    def test_does_not_retry_http_errors(self) -> None:
        error = HTTPError("url", 403, "rate limited", {}, None)
        with patch.object(gh_api, "urlopen", side_effect=error):
            with self.assertRaises(HTTPError):
                gh_api.fetch_json("https://api.github.com/repos/owner/repo", max_retries=3)

    def test_mask_token_replaces_token_in_text(self) -> None:
        self.assertEqual(
            gh_api.mask_token("Request https://x?token=secret failed", "secret"),
            "Request https://x?token=*** failed",
        )

    def test_mask_token_returns_text_unchanged_without_token(self) -> None:
        self.assertEqual(gh_api.mask_token("plain output", None), "plain output")


class BaselineAuditTests(unittest.TestCase):
    def test_groups_low_stars_entries_by_threshold(self) -> None:
        baseline = {
            ("LOW_STARS", "big/repo"),
            ("LOW_STARS", "edge/repo"),
            ("LOW_STARS", "little/repo"),
            ("LOW_STARS", "gone/repo"),
            ("LOW_STARS", "archived/repo"),
            ("LOW_STARS", "broken/repo"),
            ("INACTIVE", "ignored/repo"),
        }
        states = {
            "big/repo": {"stars": 12, "errors": []},
            "edge/repo": {"stars": validator.STAR_THRESHOLD, "errors": ["LOW_STARS"]},
            "little/repo": {"stars": 3, "errors": ["LOW_STARS"]},
            "gone/repo": {"stars": 0, "errors": ["NOT_FOUND"]},
            "archived/repo": {"stars": 7, "errors": ["ARCHIVED"]},
            "broken/repo": {"stars": 0, "errors": ["API_ERROR"], "detail": "offline"},
        }

        def fake_check(repo: str, **_: object) -> dict[str, object]:
            state = states[repo]
            return {
                "repo": repo,
                "stars": state["stars"],
                "errors": state["errors"],
                "detail": state.get("detail", ""),
            }

        with patch.object(validator, "check_repo", side_effect=fake_check):
            resolved, still_below, unavailable, api_errors = validator.audit_low_stars(baseline)

        self.assertEqual([entry["repo"] for entry in resolved], ["big/repo", "edge/repo"])
        self.assertEqual([entry["repo"] for entry in still_below], ["little/repo"])
        self.assertEqual([entry["repo"] for entry in unavailable], ["archived/repo", "gone/repo"])
        self.assertEqual([entry["repo"] for entry in api_errors], ["broken/repo"])
        self.assertEqual(
            {entry["repo"]: entry["reason"] for entry in unavailable},
            {"archived/repo": "ARCHIVED", "gone/repo": "NOT_FOUND"},
        )

    def test_audit_ignores_non_low_stars_advisories(self) -> None:
        with patch.object(validator, "check_repo") as fake:
            resolved, still_below, unavailable, api_errors = validator.audit_low_stars(
                {("INACTIVE", "sleepy/repo")}
            )
        fake.assert_not_called()
        self.assertEqual((resolved, still_below, unavailable, api_errors), ([], [], [], []))


if __name__ == "__main__":
    unittest.main()
