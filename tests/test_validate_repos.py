from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "validate-repos.py"
SPEC = importlib.util.spec_from_file_location("validate_repos", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


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
        with patch.object(validator, "fetch_repo", side_effect=error):
            self.assertEqual(validator.check_repo("owner/repo")["errors"], ["NOT_FOUND"])

    def test_rate_limit_is_api_error_not_not_found(self) -> None:
        error = HTTPError("url", 403, "rate limited", {}, None)
        with patch.object(validator, "fetch_repo", side_effect=error):
            result = validator.check_repo("owner/repo")
        self.assertEqual(result["errors"], ["API_ERROR"])
        self.assertIn("403", result["detail"])

    def test_network_failure_is_api_error(self) -> None:
        with patch.object(validator, "fetch_repo", side_effect=URLError("offline")):
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
        with patch.object(validator, "fetch_repo", return_value=metadata):
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
        completed = validator.subprocess.CompletedProcess([], 0, "cli-token\n", "")
        with patch.dict(os.environ, {}, clear=True), patch.object(
            validator.subprocess, "run", return_value=completed
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


if __name__ == "__main__":
    unittest.main()
