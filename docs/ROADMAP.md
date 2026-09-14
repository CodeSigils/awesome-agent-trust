# Roadmap

This file tracks pending maintenance improvements for awesome-agent-trust.
It is a documentation-first list: this project has no versioned releases
(see [SECURITY.md](../SECURITY.md)), so the roadmap is the place where planned
changes to the list, the validation tooling, and the review process are
recorded and revisited on a fixed cadence.

Dates in this file reference the two machine-readable state files they
affect: the `reviewed` date in `.github/advisory-baseline.json` and the
`review_after` dates in `.github/repo-exceptions.json` act as the tick
marks for the [Review Cadence](#review-cadence) below.

## Directive

This roadmap MUST be revisited before and after every meaningful action or
decision about this repository — every merge, removal, baseline or exception
edit, CI change, or policy adjustment. Each revisit must also tighten the
roadmap itself: strike completed items, correct stale estimates or cadence
notes, and fold lessons learned back into the remaining open items. A
roadmap that is not re-read before and after each change is not a plan; it
is documented drift.

## Current Automation State

As of 2026-09-14, the repo has three pieces of automation, all in `.github/`:

| Automation                 | Trigger                                                                               | What it does                                                                                                                                                                                                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate.yml` — 3 jobs    | push to main · PR to main · weekly cron `0 6 * * 1` (Mon 06:00 UTC) · manual dispatch | Job 1: `awesome-lint` (npm) checks list format/badges/TOC/relative links. Job 2: `validate-repos.py` checks every GitHub repo in the README (exists/archived/license/★/activity/description/ordering) with `GH_TOKEN`. Job 3: `gitleaks` scans every push/PR for accidentally committed secrets (SHA-pinned, `contents: read` only) |
| `dependency-freshness.yml` | weekly `30 6 * * 1` · manual dispatch                                                 | `report-action-freshness.py` checks pinned Actions (`@sha # vN`) against latest tags → writes table to the workflow summary. Also runs `validate-repos.py` and writes the advisory drift summary (`NEW_*` / `RESOLVED` / `ACCEPTED`) to the same summary. Advisory only                                                             |
| `dependabot.yml`           | weekly (GitHub-managed)                                                               | Opens PRs for out-of-date github-actions and npm dependencies                                                                                                                                                                                                                                                                       |

Plus the non-CI automation: the issue template (`project-proposal.yml` with category dropdown) and the PR template's 10-item checklist — both shape submissions.

What automation does NOT exist yet (the gap this roadmap closes):

- **No auto-updates at all** — by governance design; every baseline/exception change is maintainer-made.

So as of 2026-09-14: PRs are fully gated automatically (format, repo liveness, and secrets), dependency freshness is reported automatically, star/license/activity drift is reported automatically every Monday, and the `LOW_STARS` baseline audit runs as a single command (`--baseline-audit`). What remains manual is the triage of those reports — which stays maintainer-made by governance design.

## Open Items

All previously planned items have been implemented.

- 2026-09-14: automated secret scanning on pull requests — gitleaks runs as a third `validate.yml` job (SHA-pinned, `contents: read`), so every push and PR is scanned before a secret can reach history. The security review confirmed the existing history is clean; this closes the residual contributor-mistake risk.

## Review Cadence

| Cadence                      | Action                                                                                                                                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Weekly                       | `dependency-freshness.yml` run — review the validator summary (`NEW_*` / `RESOLVED` / `ACCEPTED`)                                                                                                      |
| Monthly                      | Triage new advisories from reported runs: resolve to baseline, exception, or removal                                                                                                                   |
| Quarterly                    | Full baseline audit (`validate-repos.py --baseline-audit`): remove entries that crossed ≥5 stars, re-check `review_after` dates in `repo-exceptions.json`, bump `reviewed` in `advisory-baseline.json` |
| On PRs with advisory signals | Apply the adoption-evidence rule in contributing.md; ask the contributor for package-registry download data when relevant                                                                              |

Last reviewed: 2026-09-14.

<!-- Revision history:
- 2026-09-14: initial roadmap; implemented items 1-4 + backlog (scheduled report, triage rule, baseline-audit, threshold constant)
- 2026-09-14: added open item 1 (automated secret scanning on PRs) after security review; expanded .gitignore credentials patterns and added .env.example
- 2026-09-14: implemented open item 1 (gitleaks in validate.yml); roadmap fully implemented
-->
