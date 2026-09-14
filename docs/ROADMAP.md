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

As of 2026-09-14, the repo has three pieces of automation, all in `.github/`.
The per-file reference — what each automation file does, how the scripts
work, and the maintenance commands — lives in
[MAINTENANCE.md](MAINTENANCE.md), which must be updated alongside this
roadmap whenever automation changes.

| Automation                 | Trigger                                                                               | What it does                                                                                                                                                                                                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate.yml` — 3 jobs    | push to main · PR to main · weekly cron `0 6 * * 1` (Mon 06:00 UTC) · manual dispatch | Job 1: `awesome-lint` (npm) checks list format/badges/TOC/relative links. Job 2: `validate-repos.py` checks every GitHub repo in the README (exists/archived/license/★/activity/description/ordering) with `GH_TOKEN`. Job 3: `gitleaks` scans every push/PR for accidentally committed secrets (SHA-pinned, `contents: read` only) |
| `dependency-freshness.yml` | weekly `30 6 * * 1` · manual dispatch                                                 | `report-action-freshness.py` checks pinned Actions (`@sha # vN`) against latest tags → writes table to the workflow summary. Also runs `validate-repos.py` and writes the advisory drift summary (`NEW_*` / `RESOLVED` / `ACCEPTED`) to the same summary. Advisory only                                                             |
| `dependabot.yml`           | weekly (GitHub-managed)                                                               | Opens PRs for out-of-date github-actions and npm dependencies                                                                                                                                                                                                                                                                       |

Plus the non-CI automation: the issue template (`project-proposal.yml` with category dropdown) and the PR template's 10-item checklist — both shape submissions.

Intentional automation gaps (not currently planned for implementation):

- **No auto-updates at all** — by governance design; every baseline/exception change is maintainer-made.

As of 2026-09-14, required PR checks cover format and repository validation.
Secret scanning runs but is not yet a required branch-protection check;
administrators can bypass protection. Dependency freshness and advisory drift
are reported weekly, and the `LOW_STARS` audit runs with `--baseline-audit`.
Retention and waiver decisions remain maintainer-made.

## Open Items

All previously planned items have been implemented.

- 2026-09-14: Gitleaks runs as a third `validate.yml` job (SHA-pinned,
  `contents: read`). Push scans run after commits reach GitHub; they cannot
  prevent initial exposure or guarantee that all secrets are detected.
- 2026-09-14: malformed exception values and timezone-free timestamps now
  produce validation errors; freshness reporting retains diagnostics and
  fails on hard validation errors or crashes. Soft advisories remain non-blocking.

## Future considerations

These are deliberately deferred improvements, not current CI failures. Each
should be scoped, configured, and reviewed before implementation. None has an
owner, target date, or acceptance criteria yet; assigning those is part of
formally promoting an item into planned work.

1. **External link checking.** Extend link monitoring to non-GitHub URLs such
   as W3C, EIP, and Google documentation, with sensible handling for rate
   limits, redirects, and temporary outages.
2. **Repository settings as operational documentation.** Record or regularly
   verify branch protection, Actions policy, Dependabot configuration,
   variables, permissions, and required checks during maintainer handover.
3. **Python static quality checks.** Consider pinned Ruff and optionally mypy
   or pyright for the standard-library scripts. This is optional while the
   scripts remain small and are covered by tests.
4. **Advisory triage support.** Keep retention/removal decisions human-made,
   but consider tooling that groups the 65 baseline advisories, tracks review
   ownership, and highlights overdue follow-up.
5. **Direct-push governance.** If PR-only maintenance is intended, enforce it
   in repository branch-protection settings; otherwise document the approved
   direct-push exception and its compensating checks.

### Security tightening under consideration

These security improvements are also deferred considerations, not evidence of
a current compromise or CI failure:

- **Static analysis.** Reassess CodeQL, Ruff, or another focused analyzer if
  the standard-library Python scripts grow beyond their current scope.
- **Settings verification.** Consider a periodic or policy-backed check for
  branch protection, Actions restrictions, required checks, and permissions.
- **Governance enforcement.** Confirm whether direct pushes are permitted; if
  PR-only maintenance is required, enforce that setting and document who can
  administer the exception.
- **Scope and external destinations.** Keep the non-endorsement boundary
  explicit and consider separate monitoring or review for external links and
  listed projects, which this repository does not security-audit.
- **Operational response.** Document named ownership, backup coverage, and
  secret-rotation steps so response does not depend on informal maintainer
  knowledge.
- **Secret-scan enforcement.** Treat a confirmed secret finding as a hard
  merge failure and require the `secret-scan` check in branch protection.
  Distinguish scanner/infrastructure failures from confirmed findings so an
  unavailable scanner is handled explicitly rather than misclassified.

## Review Cadence

| Cadence                      | Action                                                                                                                                                                                                                                                                                                                      |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Weekly                       | `dependency-freshness.yml` run — review the validator summary (`NEW_*` / `RESOLVED` / `ACCEPTED`)                                                                                                                                                                                                                           |
| Monthly                      | Triage new advisories from reported runs: resolve to baseline, exception, or removal                                                                                                                                                                                                                                        |
| Quarterly                    | Full baseline audit (`validate-repos.py --baseline-audit`): clear from the advisory baseline entries that crossed ≥5 stars (observation-driven baseline hygiene — list entries are never removed on star count alone), re-check `review_after` dates in `repo-exceptions.json`, bump `reviewed` in `advisory-baseline.json` |
| On PRs with advisory signals | Apply the adoption-evidence rule in contributing.md; ask the contributor for package-registry download data when relevant                                                                                                                                                                                                   |

Last reviewed: 2026-09-14.

<!-- Revision history:
- 2026-09-14: completed medium audit fixes for input handling, report failure propagation, and accurate security documentation
- 2026-09-14: initial roadmap; implemented items 1-4 + backlog (scheduled report, triage rule, baseline-audit, threshold constant)
- 2026-09-14: added open item 1 (automated secret scanning on PRs) after security review; expanded .gitignore credentials patterns and added .env.example
- 2026-09-14: implemented open item 1 (gitleaks in validate.yml); roadmap fully implemented
- 2026-09-14: added MAINTENANCE.md as the per-file automation reference, linked from Current Automation State
- 2026-09-14: recorded deferred considerations for external links, repository settings, Python quality, advisory triage, and direct-push governance
- 2026-09-14: clarified intentional automation gaps and that future considerations have no owner, target date, or acceptance criteria until promoted to planned work
- 2026-09-14: recorded deferred security-tightening considerations for static analysis, settings verification, governance, scope monitoring, and secret response
- 2026-09-14: added secret-scan hard-failure and required-check enforcement consideration
-->
