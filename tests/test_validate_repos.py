from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Self
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

TRIAGE_SPEC = importlib.util.spec_from_file_location(
    "report_advisory_triage", SCRIPTS_DIR / "report-advisory-triage.py"
)
assert TRIAGE_SPEC and TRIAGE_SPEC.loader
triage_reporter = importlib.util.module_from_spec(TRIAGE_SPEC)
TRIAGE_SPEC.loader.exec_module(triage_reporter)

LINK_CHECK_SPEC = importlib.util.spec_from_file_location(
    "check_markdown_links", SCRIPTS_DIR / "check-markdown-links.py"
)
assert LINK_CHECK_SPEC and LINK_CHECK_SPEC.loader
link_checker = importlib.util.module_from_spec(LINK_CHECK_SPEC)
LINK_CHECK_SPEC.loader.exec_module(link_checker)

FRESHNESS_SPEC = importlib.util.spec_from_file_location(
    "report_action_freshness", SCRIPTS_DIR / "report-action-freshness.py"
)
assert FRESHNESS_SPEC and FRESHNESS_SPEC.loader
freshness_reporter = importlib.util.module_from_spec(FRESHNESS_SPEC)
FRESHNESS_SPEC.loader.exec_module(freshness_reporter)


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

    def test_token_scoped_404_retries_without_credentials(self) -> None:
        scoped_404 = HTTPError("url", 404, "not visible to token", {}, None)
        metadata = {
            "stargazers_count": 10,
            "description": "Meaningful public repository",
            "license": {"spdx_id": "MIT"},
            "pushed_at": "2026-09-01T00:00:00Z",
        }
        with patch.object(validator, "fetch_json", side_effect=[scoped_404, metadata]) as fetch:
            result = validator.check_repo("owner/repo", token="scoped-token")
        self.assertEqual(result["errors"], [])
        self.assertIsNone(fetch.call_args_list[1].kwargs.get("token"))

    def test_token_scoped_404_is_not_found_only_after_anonymous_retry(self) -> None:
        error = HTTPError("url", 404, "missing", {}, None)
        with patch.object(validator, "fetch_json", side_effect=[error, error]) as fetch:
            result = validator.check_repo("owner/repo", token="scoped-token")
        self.assertEqual(result["errors"], ["NOT_FOUND"])
        self.assertEqual(fetch.call_count, 2)

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
            def __enter__(self) -> Self:
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
        with patch.object(gh_api, "urlopen", side_effect=error), self.assertRaises(HTTPError):
            gh_api.fetch_json("https://api.github.com/repos/owner/repo", max_retries=3)

    def test_mask_token_replaces_token_in_text(self) -> None:
        self.assertEqual(
            gh_api.mask_token("Request https://x?token=secret failed", "secret"),
            "Request https://x?token=*** failed",
        )

    def test_mask_token_returns_text_unchanged_without_token(self) -> None:
        self.assertEqual(gh_api.mask_token("plain output", None), "plain output")

    def test_zero_retries_raises_runtime_error_not_none(self) -> None:
        with patch.object(gh_api, "urlopen") as fake, self.assertRaises(RuntimeError):
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
                result = subprocess.run(
                    ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", stub + script],
                    env={**os.environ, "GITHUB_STEP_SUMMARY": str(summary)},
                    capture_output=True,
                    text=True,
                    check=False,
                )
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

    def test_extracts_target_of_badge_wrapped_link(self) -> None:
        text = (
            "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)\n"
            "[![CC0](https://img.shields.io/badge/License-CC0-lightgrey.svg)]"
            "(http://creativecommons.org/publicdomain/zero/1.0/)\n"
            '[Docs](https://example.org/docs "Title")\n'
        )
        self.assertEqual(
            link_reporter.extract_external_links(text),
            [
                "http://creativecommons.org/publicdomain/zero/1.0/",
                "https://awesome.re",
                "https://example.org/docs",
            ],
        )

    def test_ignores_image_destinations(self) -> None:
        text = (
            "[![Badge](https://img.shields.io/badge/License-CC0-lightgrey.SVG?style=flat-square)]"
            "(https://example.org/license)\n"
            "[Chart](https://example.org/chart.png?v=2)\n"
            "[Spec](https://example.org/spec#anchor)\n"
        )
        self.assertEqual(
            link_reporter.extract_external_links(text),
            ["https://example.org/license", "https://example.org/spec#anchor"],
        )

    def test_extracts_exactly_the_known_non_github_readme_links(self) -> None:
        # The expectation is ground truth from an independent CommonMark parser,
        # not a recording of what this extractor currently emits. Regenerate it
        # from a parser when the extraction contract changes, never by copying
        # the extractor's own output, or the test freezes the defect instead of
        # guarding against it. The 150-odd GitHub entry links cannot make this
        # brittle: the host filter drops them before they reach the expectation.
        extracted = link_reporter.extract_external_links(
            link_reporter.README_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(
            extracted,
            [
                "http://creativecommons.org/publicdomain/zero/1.0/",
                "https://a2a-protocol.org/latest/",
                "https://awesome.re",
                "https://eips.ethereum.org/EIPS/eip-8004",
                "https://www.w3.org/TR/did-core/",
                "https://www.w3.org/TR/vc-data-model-2.0/",
            ],
            "Non-GitHub README links changed. If that change is intended, "
            "regenerate the expected list from a CommonMark parser, never from "
            f"extract_external_links output. Extracted now: {extracted}",
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

    def test_main_returns_0_when_the_readme_is_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text("[spec](https://example.org/spec)\n", encoding="utf-8")
            out = io.StringIO()
            with (
                patch.object(link_reporter, "README_PATH", path),
                patch.object(link_reporter, "_request", return_value=(200, "https://example.org/spec")),
                redirect_stdout(out),
            ):
                code = link_reporter.main()
        self.assertEqual(code, 0)
        self.assertNotIn("COULD NOT CHECK", out.getvalue())

    def test_main_reports_an_unreadable_readme_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_bytes(b"# Title\n\xff\xfe broken\n")
            out = io.StringIO()
            with patch.object(link_reporter, "README_PATH", path), redirect_stdout(out):
                code = link_reporter.main()
        self.assertEqual(code, 2)
        self.assertIn("COULD NOT CHECK", out.getvalue())


class AdvisoryTriageReportTests(unittest.TestCase):
    def test_reports_signal_counts_and_exception_status(self) -> None:
        report = triage_reporter.render_report(
            baseline={"advisories": {"LOW_STARS": ["one/repo", "two/repo"], "NO_LICENSE": ["one/repo"]}},
            exceptions={"exceptions": [{"repo": "one/repo", "review_after": "2026-09-14"}, {"repo": "two/repo", "review_after": "2026-09-16"}]},
            today=date(2026, 9, 15),
        )
        self.assertIn("LOW_STARS` | 2", report)
        self.assertIn("Exception reviews overdue: **1**", report)
        self.assertIn("two/repo` | 2026-09-16 | current", report)

    def test_malformed_inputs_are_reported_without_raising(self) -> None:
        report = triage_reporter.render_report(baseline=None, exceptions={"exceptions": "bad"}, today=date(2026, 9, 15))
        self.assertIn("Unable to read advisory baseline", report)
        self.assertIn("`exceptions` is not a list", report)


class EntryLinkFlagsTests(unittest.TestCase):
    def test_extracts_entry_links_and_skips_anchors(self) -> None:
        text = (
            "## Projects\n"
            "- [Alpha](https://github.com/org/repo) - A.\n"
            "- [Spec](https://www.w3.org/TR/example).\n"
            "- [Anchor](#projects)\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(text, encoding="utf-8")
            entries = validator.extract_entry_links(path)
        self.assertEqual(
            entries,
            [
                (2, "Alpha", "https://github.com/org/repo"),
                (3, "Spec", "https://www.w3.org/TR/example"),
            ],
        )

    def test_strips_trailing_punctuation_from_entry_urls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text("- [Trailing](https://example.com/a,)\n", encoding="utf-8")
            entries = validator.extract_entry_links(path)
        self.assertEqual(entries, [(1, "Trailing", "https://example.com/a")])

    def test_classifies_github_code_hosts_and_external(self) -> None:
        self.assertEqual(validator.classify_entry_link("https://github.com/org/repo")[0], "github")
        for host in ("gitlab.com", "codeberg.org", "git.sr.ht", "bitbucket.org"):
            with self.subTest(host=host):
                category, found = validator.classify_entry_link(f"https://{host}/org/project")
                self.assertEqual((category, found), ("code_host", host))
        self.assertEqual(validator.classify_entry_link("https://keydrift.dev")[0], "external")

    def test_flags_only_unvalidated_hosts(self) -> None:
        entries = [
            (1, "Repo", "https://github.com/org/repo"),
            (2, "GitLab Project", "https://gitlab.com/org/project"),
            (3, "Spec", "https://www.w3.org/TR/example"),
        ]
        flags = validator.entry_flags_for(entries)
        self.assertEqual(flags["UNVALIDATED_HOST"], ["GitLab Project (gitlab.com)"])
        self.assertEqual(flags["UNVALIDATED_LINK"], ["Spec (www.w3.org)"])

    def test_github_only_entries_produce_no_flags(self) -> None:
        self.assertEqual(
            validator.entry_flags_for([(1, "Repo", "https://github.com/org/repo")]),
            {},
        )


class ExitCodeContractTests(unittest.TestCase):
    """Lock 0 clean / 1 findings / 2 could not run.

    Without a distinct 2, CPython's uncaught-exception exit code is 1, so a
    crashed checker is reported to CI as a failed check. These tests are the
    only thing preventing that collapse back into a binary.
    """

    def _run_link_checker(self, root: Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with patch.object(link_checker, "ROOT", root), redirect_stdout(out), redirect_stderr(err):
            return link_checker.main(), out.getvalue(), err.getvalue()

    def test_missing_required_input_is_reported_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            present = Path(tmp) / "present.md"
            present.write_text("# ok\n", encoding="utf-8")
            missing = Path(tmp) / "absent.md"
            self.assertIsNone(
                validator.read_required_inputs((present,)),
                "readable inputs must not report a problem",
            )
            message = validator.read_required_inputs((present, missing))
            self.assertIsNotNone(message)
            assert message is not None
            self.assertIn("absent.md", message)

    def test_non_utf8_required_input_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "latin1.md"
            path.write_bytes("# caf\xe9\n".encode("latin-1"))
            message = validator.read_required_inputs((path,))
            self.assertIsNotNone(message, "undecodable input must be reported")
            assert message is not None
            self.assertIn("latin1.md", message)

    def test_validate_repos_exits_2_when_input_unreadable(self) -> None:
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "README.md"
            with (
                patch.object(validator, "README_PATH", missing),
                patch.object(sys, "argv", ["validate-repos.py"]),
                redirect_stdout(out),
            ):
                self.assertEqual(validator.main(), 2)
        self.assertIn("COULD NOT RUN", out.getvalue())
        self.assertIn("README.md", out.getvalue())

    def test_validate_repos_exits_2_for_baseline_audit(self) -> None:
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "advisory-baseline.json"
            with patch.object(validator, "BASELINE_PATH", missing), redirect_stdout(out):
                self.assertEqual(validator.run_baseline_audit(), 2)
        self.assertIn("COULD NOT RUN", out.getvalue())

    def test_link_checker_exits_0_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("# a\n", encoding="utf-8")
            code, _out, err = self._run_link_checker(root)
        self.assertEqual(code, 0)
        self.assertEqual(err, "")

    def test_link_checker_exits_1_for_a_broken_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("[gone](missing.md)\n", encoding="utf-8")
            code, _out, err = self._run_link_checker(root)
        self.assertEqual(code, 1, "a broken link is a finding, not a run failure")
        self.assertIn("missing.md", err)

    def test_link_checker_exits_2_for_undecodable_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("# fine\n", encoding="utf-8")
            (root / "b.md").write_bytes("# caf\xe9\n".encode("latin-1"))
            code, _out, err = self._run_link_checker(root)
        self.assertEqual(code, 2)
        self.assertIn("COULD NOT CHECK", err)
        self.assertIn("b.md", err)

    def test_link_checker_prefers_2_over_1_and_still_reports_findings(self) -> None:
        # An incomplete sweep must not be reported as a complete result, but the
        # findings it did reach have to stay visible in the same output.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("[gone](missing.md)\n", encoding="utf-8")
            (root / "b.md").write_bytes("# caf\xe9\n".encode("latin-1"))
            code, _out, err = self._run_link_checker(root)
        self.assertEqual(code, 2)
        self.assertIn("missing.md", err)
        self.assertIn("b.md", err)


# The trailing `# v7.0.1` is required by the PINNED pattern, not decoration:
# drop it and every test below reports "No pinned actions found" instead of
# failing, so the fixture has to state the pin exactly as a workflow does.
PINNED_WORKFLOW = (
    "jobs:\n"
    "  build:\n"
    "    steps:\n"
    "      - uses: actions/checkout@1111111111111111111111111111111111111111 # v7.0.1\n"
)


class ActionFreshnessReportTests(unittest.TestCase):
    """Cover the Action-SHA freshness reporter.

    This was the only script in `.github/scripts/` with no test binding, so a
    change to its tag resolution could only surface as a quietly wrong weekly
    report rather than as a failure.
    """

    def _write_workflow(self, root: Path, name: str, body: str) -> Path:
        workflow = root / ".github" / "workflows" / name
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text(body, encoding="utf-8")
        return workflow

    def _run_main(self, root: Path, latest: object) -> tuple[int, str]:
        """Run main() against a temporary root; pass an exception as `latest`
        to simulate a lookup that fails for a transient reason.
        """
        out = io.StringIO()
        with (
            patch.object(freshness_reporter, "REPO_ROOT", root),
            patch.object(freshness_reporter, "resolve_token", return_value="t"),
            patch.object(freshness_reporter, "latest_sha") as latest_sha,
            patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}),
            redirect_stdout(out),
        ):
            if isinstance(latest, BaseException):
                latest_sha.side_effect = latest
            else:
                latest_sha.return_value = latest
            return freshness_reporter.main(), out.getvalue()

    def test_latest_sha_resolves_a_lightweight_tag_in_one_call(self) -> None:
        with patch.object(freshness_reporter, "fetch_json") as fetch:
            fetch.return_value = {"object": {"type": "commit", "sha": "a" * 40}}
            self.assertEqual(
                freshness_reporter.latest_sha("actions/checkout", "7", "t"),
                "a" * 40,
            )
        self.assertEqual(fetch.call_count, 1, "a lightweight tag needs no second request")

    def test_latest_sha_follows_an_annotated_tag_to_its_commit(self) -> None:
        with patch.object(freshness_reporter, "fetch_json") as fetch:
            fetch.side_effect = [
                {"object": {"type": "tag", "sha": "b" * 40}},
                {"object": {"type": "commit", "sha": "c" * 40}},
            ]
            self.assertEqual(
                freshness_reporter.latest_sha("actions/setup-node", "7", "t"),
                "c" * 40,
            )
        self.assertEqual(fetch.call_count, 2, "an annotated tag needs a second request")

    def test_latest_sha_rejects_an_unexpected_tag_object_type(self) -> None:
        with patch.object(freshness_reporter, "fetch_json") as fetch:
            fetch.return_value = {"object": {"type": "tree", "sha": "d" * 40}}
            with self.assertRaises(ValueError):
                freshness_reporter.latest_sha("owner/action", "1", "t")

    def test_latest_sha_rejects_a_tag_that_does_not_resolve_to_a_commit(self) -> None:
        with patch.object(freshness_reporter, "fetch_json") as fetch:
            fetch.side_effect = [
                {"object": {"type": "tag", "sha": "b" * 40}},
                {"object": {"type": "tree", "sha": "e" * 40}},
            ]
            with self.assertRaises(ValueError):
                freshness_reporter.latest_sha("owner/action", "1", "t")

    def test_main_reports_a_current_pin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_workflow(root, "validate.yml", PINNED_WORKFLOW)
            code, out = self._run_main(root, "1" * 40)
        self.assertEqual(code, 0)
        self.assertIn("current", out)
        self.assertIn("actions/checkout", out)
        self.assertIn("validate.yml:4", out)

    def test_main_reports_a_stale_pin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_workflow(root, "validate.yml", PINNED_WORKFLOW)
            code, out = self._run_main(root, "2" * 40)
        self.assertEqual(code, 0, "a stale pin is a review signal, never a failure")
        self.assertIn("update available", out)

    def test_main_reports_unknown_when_the_lookup_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_workflow(root, "validate.yml", PINNED_WORKFLOW)
            code, out = self._run_main(root, OSError("rate limited"))
        self.assertEqual(code, 0)
        self.assertIn("unknown", out)

    def test_main_says_so_when_no_action_is_pinned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_workflow(root, "validate.yml", "jobs:\n  build:\n    runs-on: ubuntu-latest\n")
            code, out = self._run_main(root, "1" * 40)
        self.assertEqual(code, 0)
        self.assertIn("No pinned actions found.", out)

    def test_main_writes_the_step_summary_when_the_variable_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_workflow(root, "validate.yml", PINNED_WORKFLOW)
            summary = root / "summary.md"
            out = io.StringIO()
            with (
                patch.object(freshness_reporter, "REPO_ROOT", root),
                patch.object(freshness_reporter, "resolve_token", return_value="t"),
                patch.object(freshness_reporter, "latest_sha", return_value="1" * 40),
                patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}),
                redirect_stdout(out),
            ):
                self.assertEqual(freshness_reporter.main(), 0)
            self.assertIn("actions/checkout", summary.read_text(encoding="utf-8"))

    def test_main_reports_an_unreadable_workflow_instead_of_crashing(self) -> None:
        # An undecodable workflow is environmental, not a stale pin. It must
        # not escape as an uncaught exception, because that would exit 1 and
        # turn a partial report into a red weekly job with no explanation.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = self._write_workflow(root, "validate.yml", PINNED_WORKFLOW)
            workflow.write_bytes(b"uses: \xff\xfe not utf-8\n")
            self._write_workflow(root, "other.yml", PINNED_WORKFLOW)
            code, out = self._run_main(root, "1" * 40)
        self.assertEqual(code, 2, "an incomplete run must be distinguishable from a finding")
        self.assertIn("COULD NOT CHECK", out)
        self.assertIn("other.yml", out, "the readable workflow is still reported")


class ScriptInventoryTests(unittest.TestCase):
    # Measured, not assumed: backticked script paths appear only in the file
    # inventory table. A prose mention added elsewhere would double-count here
    # rather than fail, so re-check that before trusting a green result.
    def test_every_script_has_an_inventory_row(self) -> None:
        guide = SCRIPTS_DIR.parent.parent / "docs" / "MAINTENANCE.md"
        documented = set(re.findall(r"`\.github/scripts/([^`]+)`", guide.read_text(encoding="utf-8")))
        on_disk = {path.name for path in SCRIPTS_DIR.glob("*.py")}
        self.assertEqual(
            on_disk,
            documented,
            "The maintenance guide's file inventory is out of sync with "
            ".github/scripts/. Add or remove a row there. On disk: "
            f"{sorted(on_disk)}. Documented: {sorted(documented)}.",
        )


if __name__ == "__main__":
    unittest.main()
