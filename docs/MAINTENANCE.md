# Maintenance Guide

This document is the maintainer's reference for awesome-agent-trust: what
automation exists, which files implement it, how each one works, and the
commands used to keep the list healthy. It complements
[ROADMAP.md](ROADMAP.md) (what is planned) — this file is the map of what
exists today.

## Updating this document

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
push / pull_request · weekly cron · manual dispatch
                        |
                        v
              validate.yml  (CI gate -- blocks merge on failure)
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
                merged into main

  every Monday 06:30 UTC -> dependency-freshness.yml
        +-- report-action-freshness.py -> Action SHA table
        +-- validate-repos.py           -> advisory drift summary
                        |
                        v
            workflow summary (advisory only, never blocks)

  every week -> dependabot.yml -> PRs for stale Actions/npm deps

  maintainer, on cadence -> validate-repos.py --baseline-audit
                        |
                        v
        triage -> advisory-baseline.json / repo-exceptions.json
```

Three layers of automation exist, all maintained by the repository owner:

- **Gating** — `validate.yml` blocks every push and pull request until all
  three jobs pass (format, repository liveness, secret scan).
- **Reporting** — `dependency-freshness.yml` runs every Monday and writes an
  advisory-only summary (pinned Action SHA drift + advisory drift) to the
  workflow summary page. It never blocks anything.
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
| [`.github/scripts/check-markdown-links.py`](../.github/scripts/check-markdown-links.py)         | Offline check that every repository-relative `.md` link resolves |
| [`.github/scripts/report-action-freshness.py`](../.github/scripts/report-action-freshness.py)   | Finds pinned Actions whose SHA differs from the latest major tag |
| [`.github/advisory-baseline.json`](../.github/advisory-baseline.json)                           | Observed soft-flag snapshot (maintainer-owned, dated)            |
| [`.github/repo-exceptions.json`](../.github/repo-exceptions.json)                               | The only place soft checks may be waived (maintainer-owned)      |
| [`.github/ISSUE_TEMPLATE/project-proposal.yml`](../.github/ISSUE_TEMPLATE/project-proposal.yml) | Issue form for proposals and eligibility questions               |
| [`.github/pull_request_template.md`](../.github/pull_request_template.md)                       | PR template with the 10-item submission checklist                |
| [`.env.example`](../.env.example)                                                               | Documents the token variables local script runs use              |
| [`package.json`](../package.json)                                                               | npm scripts (`lint` -> awesome-lint, `test` -> unittest)         |
| [`tests/test_validate_repos.py`](../tests/test_validate_repos.py)                               | 27 regression tests for the validator and gh_api helpers         |

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
privilege. Branch protection requires the first two jobs to pass; the
`secret-scan` job runs on every push and PR regardless.

| Job              | Steps                                                                                                     | Fails on                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `awesome-lint`   | checkout -> setup-node (Node 24, npm cache) -> `npm ci` -> `npm run lint` -> `check-markdown-links.py`    | Bad list format, badges, TOC, descriptions, broken local links |
| `validate-repos` | checkout -> `npm test` (validator unit tests) -> `validate-repos.py` with `GH_TOKEN: ${{ github.token }}` | Missing/archived repos, ordering, config errors                |
| `secret-scan`    | checkout -> `gitleaks/gitleaks-action@<sha> # v3.0.0` with `GITHUB_TOKEN`                                 | An accidentally committed secret in the PR                     |

All action references are SHA-pinned with a `# vN` comment; the freshness
workflow below reports when a pin falls behind its major tag.

### dependency-freshness.yml — the weekly advisory report

Triggers: weekly Monday 06:30 UTC and manual dispatch. Runs two scripts and
appends both reports to the workflow summary page (`$GITHUB_STEP_SUMMARY`):

1. `report-action-freshness.py` — a "GitHub Action freshness" table of every
   pinned `uses: owner/repo@sha # vN` and whether the SHA matches the latest
   `vN` tag.
2. `validate-repos.py` — full validation piped into a `text` block under
   "Repository advisory drift", showing `NEW_*`, `KNOWN`, `RESOLVED`, and
   `ACCEPTED` counts.

Both steps are advisory: no exit code blocks anything. Their purpose is to
give the maintainer a single Monday page to triage.

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

### check-markdown-links.py

Offline link checker run in the `awesome-lint` job and locally. Walks every
`*.md` file (excluding `.git` and `node_modules`), extracts inline link
targets, and resolves repository-relative ones against the filesystem.
Skips scheme URLs (`https:` etc.), protocol-relative `//` links, `#`
fragments, and placeholder targets. Exits 1 listing each broken target with
file and line.

### report-action-freshness.py

Scans every `.github/workflows/*.yml` for SHA-pinned
`uses: owner/repo@<40-hex> # vN` references, resolves the latest commit of
the `vN` tag (following annotated tags), and reports each pin as `current`
or `update available` (or `unknown` when the API cannot answer — it never
crashes the run). Output is a "GitHub Action freshness" table written to the
workflow summary.

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
`NO_LICENSE`), each a list of `owner/repo` strings. As of 2026-09-14 it
held 3 INACTIVE, 43 LOW_STARS, and 19 NO_LICENSE entries.

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

### Access and settings checklist

1. Confirm the incoming maintainer has repository write access and can approve
   pull requests. Grant the minimum required organization/team permissions.
2. In **Settings → Branches**, verify that `main` protection requires the
   `awesome-lint` and `validate-repos` checks. Confirm whether direct pushes
   are permitted; the preferred path is a pull request.
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
- `secret-scan` failures: treat as a possible credential exposure. Revoke or
  rotate the credential, preserve the workflow evidence, and follow
  [SECURITY.md](../SECURITY.md).
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
| `python3 .github/scripts/check-markdown-links.py`            | Check all repository-relative Markdown links     |
| `python3 .github/scripts/validate-repos.py`                  | Full live validation of every listed GitHub repo |
| `python3 .github/scripts/validate-repos.py --baseline-audit` | Star audit over the LOW_STARS baseline           |
| `python3 .github/scripts/report-action-freshness.py`         | Pinned-Action SHA freshness table                |
| `python3 -m json.tool .github/advisory-baseline.json`        | Validate baseline JSON                           |
| `python3 -m json.tool .github/repo-exceptions.json`          | Validate exceptions JSON                         |

Expected healthy output: `npm run lint` prints "Linting(1)"; all 27 tests
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

As of 2026-09-14:

- `validate.yml` runs 3 jobs (awesome-lint, validate-repos, gitleaks).
- `dependency-freshness.yml` reports action SHA drift + advisory drift
  every Monday; `dependabot.yml` opens weekly update PRs.
- Validator state: 0 hard failures, 0 new advisories, 65 known, 4 accepted
  exceptions; `--baseline-audit`: 0 resolved, 43 still below.
- The roadmap has no open items.

Last reviewed: 2026-09-14.

<!-- Revision history:
- 2026-09-14: initial maintenance guide covering all automation, scripts, advisory state files, and commands
- 2026-09-14: reflect hardened exception/baseline input validation (malformed records reported, not crashed) and up-to-date test count (27)
- 2026-09-14: add new-maintainer handover, access verification, first-day checks, and failure-triage guidance
-->
