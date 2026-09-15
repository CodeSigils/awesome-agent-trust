# Maintenance Guide

This document is the maintainer's reference for awesome-agent-trust: what
automation exists, which files implement it, how each one works, and the
commands used to keep the list healthy. It complements
[ROADMAP.md](ROADMAP.md) (what is planned) — this file is the map of what
exists today.

## Updating this document

### Maintenance directive

This guide MUST be revisited before and after every relevant repository
action — including a merge, removal, baseline or exception edit, CI/workflow
change, dependency change, policy adjustment, or maintainer handover. Each
revisit must tighten the guide and prevent documented drift: correct stale
facts, update affected diagrams/inventories/commands, record changed review
dates, and add a revision-history entry. A change is not fully maintained
until its implementation, roadmap status, and this guide agree.

After each post-action revisit, the maintainer MUST read
[ROADMAP.md](ROADMAP.md) in tandem with this guide. Reconcile the two files:
move completed considerations out of the deferred section, record new gaps or
policy decisions in the roadmap, and ensure both revision histories and
"as-of" facts describe the same repository state. Treat disagreement between
the files as documentation drift to resolve before closing the action.

This file MUST be updated whenever a roadmap item is completed, a new
automation is added, or an existing one changes behavior. This is the
documentation half of the roadmap's
[Directive](ROADMAP.md#directive): a feature that is implemented but not
reflected here is not documented.

When a change lands, update at minimum:

1. The [system diagram](#system-overview) if the flow changed.
2. The [file inventory](#file-inventory) table (add/remove/edit rows).
3. The [workflow](#workflows) or [script](#scripts-reference) sections that
   describe the changed behavior.
4. The [maintenance commands](#maintenance-commands) cheat sheet.
5. Any "as of" dates or state facts, and the revision history at the bottom.

## System overview

```text
validate.yml: push / pull_request · weekly cron · manual dispatch
                        |
                        v
              validate.yml  (protected PR gate)
        +---------------+------------------+
        v               v                  v
  Job 1:           Job 2:            Job 3:
  awesome-lint     validate-repos.py  gitleaks
  (npm)            (live GitHub API)  (secret scan)
  list format      exists/archived/   SHA-pinned,
  badges / TOC     license / stars /  contents: read
  local links      activity / order   fails on leaks
        +---------------+------------------+
                        |
                        v
          protected PR merge eligible when checks pass

  dependency-freshness.yml: Monday 06:30 UTC · manual dispatch
                        |
                        v
        +-- report-action-freshness.py -> Action SHA table
        +-- validate-repos.py           -> advisory drift summary
        +-- report-external-links.py    -> README link health
                        |
                        v
            workflow summary (soft advisories do not fail)

  every week -> dependabot.yml -> PRs for stale Actions/npm deps

  maintainer, on cadence -> validate-repos.py --baseline-audit
                        |
                        v
        triage -> advisory-baseline.json / repo-exceptions.json
```

Three layers of automation exist, all maintained by the repository owner:

- **Gating** — `validate.yml` runs on every push and pull request. Protected
  PR merges require the configured validation checks to pass; the workflow
  itself does not merge changes or prevent an explicitly permitted direct
  push.
- **Reporting** — `dependency-freshness.yml` runs every Monday and writes an
  advisory-only summary (pinned Action SHA drift + advisory drift) to the
  workflow summary page. Soft advisories do not fail the run; hard validation
  failures and incomplete execution do. This workflow is not a required PR check.
- **Maintainer tools** — the scripts in `.github/scripts/` run in CI but are
  designed to be run locally; `--baseline-audit` is the quarterly star
  audit.

## File inventory

| File                                                                                            | What it is                                                       |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [`.github/workflows/validate.yml`](../.github/workflows/validate.yml)                           | The CI gate: 3 jobs (awesome-lint, validate-repos, gitleaks)     |
| [`.github/workflows/dependency-freshness.yml`](../.github/workflows/dependency-freshness.yml)   | Weekly advisory report (action SHA + advisory drift)             |
| [`.github/dependabot.yml`](../.github/dependabot.yml)                                           | Weekly dependency-update PRs for GitHub Actions and npm          |
| [`.github/scripts/validate-repos.py`](../.github/scripts/validate-repos.py)                     | Core validator: checks every GitHub link in README.md live       |
| [`.github/scripts/gh_api.py`](../.github/scripts/gh_api.py)                                     | Shared GitHub API client: token resolution, retry, token masking |
| [`.github/scripts/verify-repository-settings.py`](../.github/scripts/verify-repository-settings.py) | Read-only check of `main` branch protection                      |
| [`.github/scripts/check-markdown-links.py`](../.github/scripts/check-markdown-links.py)         | Offline check that every repository-relative `.md` link resolves |
| [`.github/scripts/report-external-links.py`](../.github/scripts/report-external-links.py)       | Weekly advisory health report for non-GitHub README links        |
| [`.github/scripts/report-action-freshness.py`](../.github/scripts/report-action-freshness.py)   | Finds pinned Actions whose SHA differs from the latest major tag |
| [`.github/advisory-baseline.json`](../.github/advisory-baseline.json)                           | Observed soft-flag snapshot (maintainer-owned, dated)            |
| [`.github/repo-exceptions.json`](../.github/repo-exceptions.json)                               | The only place soft checks may be waived (maintainer-owned)      |
| [`.github/ISSUE_TEMPLATE/project-proposal.yml`](../.github/ISSUE_TEMPLATE/project-proposal.yml) | Issue form for proposals and eligibility questions               |
| [`.github/pull_request_template.md`](../.github/pull_request_template.md)                       | PR template with the 10-item submission checklist                |
| [`.env.example`](../.env.example)                                                               | Documents the token variables local script runs use              |
| [`package.json`](../package.json)                                                               | npm scripts (`lint` -> awesome-lint, `test` -> unittest)         |
| [`tests/test_validate_repos.py`](../tests/test_validate_repos.py)                               | 35 regression tests for validation, API helpers, and reporting   |

Governance documents the automation enforces:

| File                                        | Role                                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| [README.md](../README.md)                   | The list itself; the validator's input                                   |
| [CRITERIA.md](../CRITERIA.md)               | Inclusion criteria, quality gates, exclusion rules                       |
| [contributing.md](../contributing.md)       | Submission process, pre-submission checklist, PR guidance                |
| [SECURITY.md](../SECURITY.md)               | Reporting policy for vulnerabilities                                     |
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Community standards; editorial rules for inclusion/removal disagreements |
| [ROADMAP.md](ROADMAP.md)                    | Planned work, review cadence, revision history                           |

## Workflows

### validate.yml — the CI gate

Triggers: `workflow_dispatch`, weekly Monday 06:00 UTC, push to `main`,
pull requests against `main`. `concurrency` cancels a superseded run for the
same ref. The workflow-wide `permissions: contents: read` is least
privilege. Branch protection requires all three jobs to pass and applies to
administrators. No approving-review requirement is configured because this is
a solo-maintainer repository; the `secret-scan` job runs on every push and PR
regardless.

| Job              | Steps                                                                                                     | Fails on                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `awesome-lint`   | checkout -> setup-node (Node 24, npm cache) -> `npm ci` -> `npm run lint` -> `check-markdown-links.py`    | Bad list format, badges, TOC, descriptions, broken local links |
| `validate-repos` | checkout -> `npm test` (validator unit tests) -> `validate-repos.py` with `GH_TOKEN: ${{ github.token }}` | Missing/archived repos, ordering, config errors                |
| `secret-scan`    | full-history checkout (`fetch-depth: 0`) -> `gitleaks/gitleaks-action@<sha> # v3.0.0` with `GITHUB_TOKEN` | An accidentally committed secret in the PR                     |

All action references are SHA-pinned with a `# vN` comment; the freshness
workflow below reports when a pin falls behind its major tag.

### dependency-freshness.yml — the weekly advisory report

Triggers: weekly Monday 06:30 UTC and manual dispatch. Runs three reports and
appends them to the workflow summary page (`$GITHUB_STEP_SUMMARY`):

1. `report-action-freshness.py` — a "GitHub Action freshness" table of every
   pinned `uses: owner/repo@sha # vN` and whether the SHA matches the latest
   `vN` tag.
2. `validate-repos.py` — full validation piped into a `text` block under
   "Repository advisory drift", showing `NEW_*`, `KNOWN`, `RESOLVED`, and
   `ACCEPTED` counts.
3. `report-external-links.py` — checks non-GitHub `http(s)` Markdown links in
   `README.md` and appends their status to the workflow summary.

Soft repository advisories remain non-blocking. The repository-report step
uses Bash with `pipefail`, preserves the validator output in the summary even
on failure, and propagates a nonzero exit status for hard failures or crashes.
The action-freshness script reports unresolved lookups as `unknown`; these
require follow-up and do not establish freshness. External-link results are
also advisory: a remote outage, rate limit, redirect, or broken link does not
fail the workflow. The workflow is not a required PR check.

### dependabot.yml — dependency updates

Opens weekly PRs for `github-actions` and `npm` ecosystems. No automerge is
configured; every update still passes the three `validate.yml` jobs before
merge.

## Scripts reference

### validate-repos.py

The core validator and the heart of the review system.

**Input.** Parses every `https://github.com/...` URL from
[README.md](../README.md) and normalizes it to `owner/repo` pairs. Only
GitHub URLs are machine-checkable; non-GitHub links (for example
eips.ethereum.org, W3C specs, Google A2A docs) are out of scope by design.

**Per-repository check** (`check_repo`). Fetches
`https://api.github.com/repos/{repo}` once (concurrently, 8 workers) and
produces:

| Signal         | Kind | Condition                                          |
| -------------- | ---- | -------------------------------------------------- |
| `NOT_FOUND`    | hard | API returns 404                                    |
| `API_ERROR`    | hard | other HTTP errors, timeouts, malformed `pushed_at` |
| `ARCHIVED`     | hard | `archived: true`                                   |
| `MISORDERED`   | hard | category entries not alphabetized                  |
| `CONFIG_ERROR` | hard | exception/baseline files malformed or inconsistent |
| `NO_LICENSE`   | soft | no detected license                                |
| `LOW_STARS`    | soft | stars < `STAR_THRESHOLD` (5)                       |
| `INACTIVE`     | soft | last push > 365 days ago                           |
| `WEAK_DESC`    | soft | description shorter than 15 characters             |
| `BARE_ENTRY`   | soft | list entry lacks a ` - `/` — ` description         |

Hard signals exit with status 1 and block the merge; soft signals are
advisories that never block. `compare_advisories` refuses to claim
"resolved" advisories when any API call failed, so partial metadata never
produces false resolutions.

**Report sections.** The script prints hard errors, `NEW_<SOFT>` advisories
(baseline additions), `KNOWN ADVISORIES`, `RESOLVED ADVISORIES (update the
baseline)`, `ACCEPTED EXCEPTIONS`, then a `SUMMARY` line and exit code.

**Examples.**

```bash
python3 .github/scripts/validate-repos.py                       # full validation
python3 .github/scripts/validate-repos.py --baseline-audit      # LOW_STARS star audit
```

`--baseline-audit` iterates every `LOW_STARS` entry in the baseline and
groups them into `RESOLVED` (>= 5 stars, clear from baseline), `STILL
BELOW`, `UNAVAILABLE` (gone/renamed/archived; do not clear), and `API
ERRORS` (re-check later).

### gh_api.py

Shared client used by `validate-repos.py` and `report-action-freshness.py`.

- `resolve_token()` — `GH_TOKEN`, then `GITHUB_TOKEN`, then falls back to
  `gh auth token` (5-second timeout). CI always provides one via
  `${{ github.token }}`; locally, exporting a read-only token raises the
  API rate limit from 60 to 5,000 requests/hour (see
  [`.env.example`](../.env.example)).
- `fetch_json()` — GET with GitHub headers and optional Bearer auth.
  Retries transient failures (URLError, timeout, connection resets) up to
  `max_retries` total attempts; `HTTPError` is never retried because
  403/429/5xx are server-side decisions.
- `mask_token()` — replaces the token with `***` in error output, so a
  token buried in a URL or exception string can never reach CI logs.

### verify-repository-settings.py

Reads `main` branch protection and verifies that `awesome-lint`,
`validate-repos`, and `secret-scan` are required, strict status checks are
enabled, and protection applies to administrators. It never changes a
repository setting, creates a commit, or opens a pull request.

GitHub requires repository-administration read access for this endpoint, so
the script is deliberately a maintainer-run check rather than scheduled CI.
It uses an existing `gh auth login` session or an ephemeral `GH_TOKEN` /
`GITHUB_TOKEN`; it does not store a token. Run it before a handover and at
the monthly settings review:

```bash
python3 .github/scripts/verify-repository-settings.py
```

### check-markdown-links.py

Offline link checker run in the `awesome-lint` job and locally. Walks every
`*.md` file (excluding `.git` and `node_modules`), extracts inline link
targets, and resolves repository-relative ones against the filesystem.
Skips scheme URLs (`https:` etc.), protocol-relative `//` links, `#`
fragments, and placeholder targets. Exits 1 listing each broken target with
file and line.

### report-external-links.py

Checks unique non-GitHub `http(s)` Markdown links in `README.md` using HEAD,
falling back to GET when a server does not support HEAD. The report labels
links as `ok`, `redirect`, `broken` (a 404 or 410 response), or `unknown`
(timeouts, rate limits, access denials, 5xx responses, and other transient
errors).
It follows redirects and always exits 0: external availability is a review
signal, not a merge gate. The weekly dependency-freshness workflow writes the
report to its summary without a token, commit, pull request, or state file.

### report-action-freshness.py

Scans every `.github/workflows/*.yml` for SHA-pinned
`uses: owner/repo@<40-hex> # vN` references, resolves the latest commit of
the `vN` tag (following annotated tags), and reports each pin as `current`
or `update available` (or `unknown` when the API cannot answer — it never
crashes the run). Output is a "GitHub Action freshness" table written to the
workflow summary.

### Python quality expectations

The maintenance scripts use only the Python standard library at runtime. They
use type annotations, docstrings, defensive input/API error handling, and a
regression suite in `tests/test_validate_repos.py`. CI currently enforces
Python behavior through `npm test` and the live validator; it does **not** run
a Python formatter, linter, or static type checker. Do not imply that a clean
CI run provides those additional guarantees.

For every Python change, preserve the existing type-hint and error-handling
style, add regression coverage for new branches or failure modes, and run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall .github/scripts tests
```

Ruff (format/lint) and mypy or pyright (static typing) are possible future
CI additions, but introducing them would require documenting and reviewing
their configuration and dependency pins.

## Advisory state files

Two maintainer-owned JSON files encode the review state. Contributors must
not edit them (see contributing.md and the PR template).

### advisory-baseline.json

A dated snapshot (`reviewed`) of observed soft flags — "as of this date,
these repositories were flagged, and a human looked". Recording a flag here
does **not** waive it; it only stops the weekly report from re-listing it as
`NEW`. When a flagged signal resolves, the weekly run prints `RESOLVED
ADVISORIES: N (update the baseline)`; the maintainer clears those entries
and bumps `reviewed`.

Structure: `advisories` keyed by soft-check name (`INACTIVE`, `LOW_STARS`,
`NO_LICENSE`), each a list of `owner/repo` strings. As of 2026-09-15 it
holds 3 INACTIVE, 42 LOW_STARS, and 19 NO_LICENSE entries.

### repo-exceptions.json

The only waiver mechanism. Each entry names a repository, the soft checks
being waived, an evidence-backed `reason` (at least 20 characters), and a
future `review_after` ISO date that makes the waiver self-expiring. Only
soft checks may be waived; hard failures cannot be. An exception for a
repository not listed in the README is a `CONFIG_ERROR`. Malformed entries
(records whose `repo` is not a string, whose `checks` is not a list or
contains non-string values, or whose `review_after` is not an ISO date) are
reported as validation errors instead of crashing the run.

Current entries (all `LOW_STARS` unless noted):
`CSOAI-ORG/meok-aaif-agent-card-mcp` (2027-08-01),
`CSOAI-ORG/oasf-agent-directory-mcp` (2027-08-01), and
`capiscio/capiscio-rfcs` (`LOW_STARS` + `NO_LICENSE`, 2026-11-01).

## New maintainer handover

Use this section when transferring operational ownership. Account-specific
values are intentionally not recorded here; verify them in the repository
settings before the outgoing maintainer leaves.

### What the maintainer can access

The workflow definitions in `.github/workflows/` and automation code in
`.github/scripts/` are versioned repository files. Anyone with repository read
access can inspect or clone them; a maintainer with write access can propose
changes through pull requests. Editing branch protection, Actions policies,
repository variables, Dependabot settings, or other repository controls
requires the corresponding administrative permission. GitHub secret values
are never readable after creation—even by maintainers—so confirm that the
incoming maintainer can use the configured secrets in Actions and has a secure
process for replacing them when needed.

### Access and settings checklist

1. Confirm the incoming maintainer has repository write access and can approve
   pull requests. Grant the minimum required organization/team permissions.
2. In **Settings → Branches**, verify that `main` protection requires
   `awesome-lint`, `validate-repos`, and `secret-scan`, including for
   administrators. Run `verify-repository-settings.py` with an authenticated
   GitHub CLI session. Confirm whether direct pushes are permitted; the
   preferred path is a pull request.
3. In **Settings → Actions → General**, confirm workflows are enabled and that
   scheduled workflows may run. Check the allowed-actions policy before
   changing any pinned action.
4. Verify repository variables and secrets. CI uses the automatic
   `GITHUB_TOKEN`; `RUNNER_X86_64` is an optional runner-label variable. Local
   API checks may use `GH_TOKEN` or `GITHUB_TOKEN`, or the GitHub CLI token.
   Never put a personal token in the repository.
5. Confirm Dependabot alerts and pull requests are enabled, and identify the
   person/team responsible for reviewing action and npm updates.
6. Confirm the security-reporting destination in [SECURITY.md](../SECURITY.md)
   and the person/team who triages reports. Do not investigate a suspected
   secret in a public issue; rotate/revoke it first.

### First-day verification

From a fresh clone, run the commands in the [maintenance commands](#maintenance-commands)
section in this order:

```bash
npm ci
npm test
npm run lint
python3 .github/scripts/check-markdown-links.py
python3 .github/scripts/validate-repos.py
```

Then inspect the latest `validate` and `dependency-freshness` workflow runs.
The live validator requires GitHub API access; an `API_ERROR` means metadata
is incomplete and must not be treated as evidence that a repository is gone.

### Failure triage and ownership

- `awesome-lint` or local-link failures: correct README/docs formatting or
  repository-relative paths, then rerun the local commands.
- `validate-repos` hard failures: check the specific repository and API error;
  remove/replace archived or missing entries only after confirming the result.
- `NEW_*` advisories: review evidence, then baseline, exception, or remove the
  entry according to [CRITERIA.md](../CRITERIA.md); advisories alone do not
  block a merge.
- `secret-scan` failures: inspect the log to distinguish a finding from scanner
  or infrastructure failure. For a confirmed exposed credential, revoke or
  rotate it and follow [SECURITY.md](../SECURITY.md). For scanner failures,
  restore scanning and rerun; an incomplete scan is not a clean result. Push
  scans occur after commits reach GitHub and cannot prevent initial exposure.
- Action or npm freshness reports: open/update a dependency PR and let the
  normal validation checks verify it; do not edit generated advisory state as
  a substitute for review.

Record the current maintainer, backup maintainer, Dependabot reviewer, and
security contact in the repository’s private team/on-call documentation.
Keep those names out of this public guide unless the project explicitly wants
them public.

## Maintenance commands

Run from the repository root. Local runs of the two API scripts benefit
from a token (see [`.env.example`](../.env.example)) but work without one.

| Command                                                      | Purpose                                          |
| ------------------------------------------------------------ | ------------------------------------------------ |
| `npm ci`                                                     | Install locked dev dependencies                  |
| `npm run lint`                                               | awesome-lint format check (list rules)           |
| `npm test`                                                   | Validator regression tests (unittest)            |
| `python3 .github/scripts/verify-repository-settings.py`     | Read-only branch-protection drift check          |
| `python3 .github/scripts/check-markdown-links.py`            | Check all repository-relative Markdown links     |
| `python3 .github/scripts/report-external-links.py`           | Report non-GitHub README link health (advisory)  |
| `python3 .github/scripts/validate-repos.py`                  | Full live validation of every listed GitHub repo |
| `python3 .github/scripts/validate-repos.py --baseline-audit` | Star audit over the LOW_STARS baseline           |
| `python3 .github/scripts/report-action-freshness.py`         | Pinned-Action SHA freshness table                |
| `python3 -m json.tool .github/advisory-baseline.json`        | Validate baseline JSON                           |
| `python3 -m json.tool .github/repo-exceptions.json`          | Validate exceptions JSON                         |

Expected healthy output: `npm run lint` reports successful linting; all 35 tests
pass; check-markdown-links prints `PASS: all repository-relative Markdown
links resolve`; validate-repos prints `SUMMARY: 0 hard failure(s)` with
advisory counts and `ACCEPTED EXCEPTIONS` matching the exception registry.

## Review cadence

The [Review Cadence](ROADMAP.md#review-cadence) table in ROADMAP.md is the
schedule: weekly review of the Monday summary, monthly triage of new
advisories, quarterly `--baseline-audit` plus expiry re-checks, and the
adoption-evidence rule on PRs with advisory signals. The `reviewed` date in
`advisory-baseline.json` and the `review_after` dates in
`repo-exceptions.json` are the tick marks for that cadence.

## State facts

As of 2026-09-15:

- `validate.yml` runs 3 jobs (awesome-lint, validate-repos, secret-scan).
  `main` requires all three checks and applies branch protection to
  administrators; no approving-review requirement is configured for the solo
  maintainer.
- `dependency-freshness.yml` reports action SHA drift, advisory drift, and
  external README-link health every Monday; `dependabot.yml` opens weekly
  update PRs.
- Validator state: 0 hard failures, 0 new advisories, 64 known, 4 accepted
  exceptions; `--baseline-audit`: 0 resolved, 42 still below.
- Previously planned work is complete; the roadmap tracks remaining deferred
  considerations such as external-link scope and scheduled settings
  verification.

Last reviewed: 2026-09-15.

<!-- Revision history:
- 2026-09-14: fix malformed-input handling, preserve reporting failures, and clarify secret-scan triage; 30 regression tests
- 2026-09-15: record branch protection requiring awesome-lint, validate-repos, and secret-scan for all users, including administrators
- 2026-09-15: document credential-exposure response in SECURITY.md and align the handover checklist with all required checks
- 2026-09-15: add a token-safe, read-only branch-protection verifier for maintainer-run settings reviews
- 2026-09-15: add weekly advisory monitoring for non-GitHub README links without a token or repository changes
- 2026-09-15: replace the stale Google-hosted A2A documentation URL found by the first external-link report
- 2026-09-15: add external-link reporting to the system overview
- 2026-09-15: classify non-404/410 external-link failures as unknown to avoid false broken-link reports
- 2026-09-15: remove the independent-approval requirement because the repository has one maintainer; retain all required checks and administrator enforcement
- 2026-09-15: clear the resolved nmcitra/ktp-rfc LOW_STARS baseline entry and reconcile test, workflow, and advisory counts
- 2026-09-14: initial maintenance guide covering all automation, scripts, advisory state files, and commands
- 2026-09-14: reflect hardened exception/baseline input validation (malformed records reported, not crashed) and up-to-date test count (27)
- 2026-09-14: add new-maintainer handover, access verification, first-day checks, and failure-triage guidance
- 2026-09-14: document full-history checkout required by the Gitleaks push-range scan
- 2026-09-14: document workflow/script permissions and Python quality expectations
- 2026-09-14: add before/after-action maintenance directive to prevent documentation drift
- 2026-09-14: correct workflow diagram merge semantics, trigger labeling, and lint-output expectation
- 2026-09-14: clarify that workflow execution and protected-merge enforcement are separate controls
- 2026-09-14: require post-action tandem review of MAINTENANCE.md and ROADMAP.md
-->
