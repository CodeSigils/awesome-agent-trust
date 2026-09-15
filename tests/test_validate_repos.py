from __future__ import annotations

import importlib.util
import json
import os
import subprocess
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

SETTINGS_SPEC = importlib.util.spec_from_file_location(
    "verify_repository_settings", SCRIPTS_DIR / "verify-repository-settings.py"
)
assert SETTINGS_SPEC and SETTINGS_SPEC.loader
settings_verifier = importlib.util.module_from_spec(SETTINGS_SPEC)
SETTINGS_SPEC.loader.exec_module(settings_verifier)

LINK_REPORT_SPEC = importlib.util.spec_from_file_location(
    "report_external_links", SCRIPTS_DIR / "report-external-links.py"
)
assert LINK_REPORT_SPEC and LINK_REPORT_SPEC.loader
link_reporter = importlib.util.module_from_spec(LINK_REPORT_SPEC)
LINK_REPORT_SPEC.loader.exec_module(link_reporter)


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
    def test_timezone_missing_is_api_error(self) -> None:
        metadata = {"stargazers_count": 10, "description": "Meaningful description",
                    "license": {"spdx_id": "MIT"}, "pushed_at": "2026-09-01T00:00:00"}
        with patch.object(validator, "fetch_json", return_value=metadata):
            result = validator.check_repo("owner/repo")
        self.assertEqual(result["errors"], ["API_ERROR"])

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

    def test_non_string_pushed_at_is_ignored_not_crashing(self) -> None:
        metadata = {
            "stargazers_count": 10,
            "description": "a description long enough",
            "pushed_at": 12345,
            "archived": False,
            "license": {"spdx_id": "MIT"},
        }
        with patch.object(validator, "fetch_json", return_value=metadata):
            result = validator.check_repo("owner/repo")
        self.assertNotIn("INACTIVE", result["errors"])
        self.assertEqual(result["last_commit_days_ago"], None)

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
    def test_malformed_reason_and_nested_checks_report_errors(self) -> None:
        for change in ({"reason": None}, {"reason": 123}, {"checks": [["LOW_STARS"]]},
                       {"checks": [{"name": "LOW_STARS"}]}):
            with self.subTest(change=change):
                item = {"repo": "owner/repo", "checks": ["LOW_STARS"],
                        "reason": "Evidence sufficient for review", "review_after": "2027-01-01"}
                with patch.object(Path, "read_text", return_value=json.dumps({"exceptions": [item | change]})):
                    _, errors = validator.load_exceptions(Path("unused"), today=date(2026, 9, 14))
                self.assertTrue(errors)

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

    def test_rejects_unhashable_repo_without_crashing(self) -> None:
        payload = {
            "exceptions": [{
                "repo": ["owner", "repo"],
                "checks": ["LOW_STARS"],
                "reason": "This reason is long enough to be reviewed.",
                "review_after": "2027-01-01",
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exceptions.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            exceptions, errors = validator.load_exceptions(path, today=date(2026, 1, 1))
        self.assertEqual(exceptions, {})
        self.assertTrue(any("invalid repository name" in error for error in errors))

    def test_rejects_non_string_check_entries_without_crashing(self) -> None:
        payload = {
            "exceptions": [{
                "repo": "owner/repo",
                "checks": [1, "LOW_STARS"],
                "reason": "This reason is long enough to be reviewed.",
                "review_after": "2027-01-01",
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exceptions.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            exceptions, errors = validator.load_exceptions(path, today=date(2026, 1, 1))
        self.assertEqual(exceptions, {})
        self.assertTrue(any("must contain only strings" in error for error in errors))


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

    def test_zero_retries_raises_runtime_error_not_none(self) -> None:
        with patch.object(gh_api, "urlopen") as fake:
            with self.assertRaises(RuntimeError):
                gh_api.fetch_json("https://api.github.com/repos/owner/repo", max_retries=0)
        fake.assert_not_called()


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


class FreshnessWorkflowTests(unittest.TestCase):
    def test_report_preserves_output_and_exit_status(self) -> None:
        workflow = (SCRIPTS_DIR.parent / "workflows" / "dependency-freshness.yml").read_text()
        body = workflow.split("        run: |\n", 1)[1]
        body = "\n".join(line[10:] for line in body.splitlines())
        for status in (0, 1, 2):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                summary = Path(directory) / "summary.md"
                script = body.replace("/tmp/validator.log", str(Path(directory) / "validator.log"))
                stub = f'python3() {{ echo "validator output"; return {status}; }}\n'
                result = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", stub + script],
                                        env={**os.environ, "GITHUB_STEP_SUMMARY": str(summary)}, capture_output=True, text=True)
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn("validator output", summary.read_text())
                self.assertEqual("Validation failed" in summary.read_text(), status != 0)


class RepositorySettingsTests(unittest.TestCase):
    def test_accepts_expected_protection(self) -> None:
        protection = {
            "required_status_checks": {
                "contexts": ["secret-scan", "validate-repos", "awesome-lint"],
                "strict": True,
            },
            "enforce_admins": {"enabled": True},
        }
        self.assertEqual(settings_verifier.evaluate_protection(protection), [])

    def test_reports_missing_checks_and_admin_enforcement(self) -> None:
        protection = {
            "required_status_checks": {"contexts": ["awesome-lint"], "strict": False},
            "enforce_admins": {"enabled": False},
        }
        errors = settings_verifier.evaluate_protection(protection)
        self.assertEqual(len(errors), 3)
        self.assertTrue(any("required checks" in error for error in errors))
        self.assertTrue(any("up to date" in error for error in errors))
        self.assertTrue(any("administrators" in error for error in errors))


class ExternalLinkReportTests(unittest.TestCase):
    def test_extracts_non_github_http_links(self) -> None:
        text = (
            "[Spec](https://www.w3.org/TR/example) [Repository](https://github.com/org/repo)\n"
            "[Docs](<https://example.org/docs>) [Mail](mailto:help@example.org) [Spec](https://www.w3.org/TR/example)"
        )
        self.assertEqual(
            link_reporter.extract_external_links(text),
            ["https://example.org/docs", "https://www.w3.org/TR/example"],
        )

    def test_reports_redirects_and_never_marks_unknown_as_failure(self) -> None:
        results = [
            link_reporter.LinkResult("https://example.org", "ok", "HTTP 200"),
            link_reporter.LinkResult("https://example.net", "redirect", "HTTP 200 → https://www.example.net"),
            link_reporter.LinkResult("https://missing.example", "broken", "HTTP 404"),
            link_reporter.LinkResult("https://slow.example", "unknown", "TimeoutError"),
        ]
        report = link_reporter.render_report(results)
        self.assertIn("1 ok, 1 redirects, 1 broken, 1 unknown", report)
        self.assertIn("Advisory only", report)

    def test_treats_access_denied_as_unknown_and_not_found_as_broken(self) -> None:
        denied = HTTPError("url", 403, "forbidden", {}, None)
        missing = HTTPError("url", 404, "not found", {}, None)
        with patch.object(link_reporter, "_request", side_effect=denied):
            self.assertEqual(link_reporter.check_link("https://blocked.example").status, "unknown")
        with patch.object(link_reporter, "_request", side_effect=missing):
            self.assertEqual(link_reporter.check_link("https://missing.example").status, "broken")


if __name__ == "__main__":
    unittest.main()
