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

As of 2026-09-15, the repo has three pieces of automation, all in `.github/`.
The per-file reference — what each automation file does, how the scripts
work, and the maintenance commands — lives in
[MAINTENANCE.md](MAINTENANCE.md), which must be updated alongside this
roadmap whenever automation changes.

| Automation                 | Trigger                                                                               | What it does                                                                                                                                                                                                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate.yml` — 3 jobs    | push to main · PR to main · weekly cron `0 6 * * 1` (Mon 06:00 UTC) · manual dispatch | Job 1: `awesome-lint` (npm) checks list format/badges/TOC/relative links. Job 2: `validate-repos.py` checks every GitHub repo in the README (exists/archived/license/★/activity/description/ordering) with `GH_TOKEN`, and flags non-GitHub entry links as advisory `UNVALIDATED_HOST` / `UNVALIDATED_LINK`. Job 3: `gitleaks` scans every push/PR for accidentally committed secrets (SHA-pinned, `contents: read` only) |
| `dependency-freshness.yml` | weekly `30 6 * * 1` · manual dispatch                                                 | `report-action-freshness.py` checks pinned Actions (`@sha # vN`), `validate-repos.py` reports advisory drift (`NEW_*` / `RESOLVED` / `ACCEPTED`), `report-external-links.py` reports non-GitHub README-link health, and `report-advisory-triage.py` summarizes signal counts and exception-review dates. Reports write to the workflow summary; soft findings are advisory, while hard validator failures still fail the workflow. |
| `dependabot.yml`           | weekly (GitHub-managed)                                                               | Opens PRs for out-of-date github-actions and npm dependencies                                                                                                                                                                                                                                                                       |

Plus the non-CI automation: the issue template (`project-proposal.yml` with category dropdown) and the PR template's 10-item checklist — both shape submissions.

Intentional automation gaps (not currently planned for implementation):

- **No auto-updates at all** — by governance design; every baseline/exception change is maintainer-made.

As of 2026-09-15, required PR checks cover format, repository validation, and
secret scanning. Branch protection applies to administrators. No approving
review is required because this is a solo-maintainer repository. Dependency
freshness and advisory drift are reported weekly, and the `LOW_STARS` audit
runs with `--baseline-audit`. Retention and waiver decisions remain
maintainer-made. A maintainer can run
`verify-repository-settings.py` locally to check branch-protection drift; it
uses an existing authenticated GitHub CLI session and makes no changes.
The weekly report checks non-GitHub README links; its advisory-triage summary
reads local state without a token, commit, pull request, or state-file changes.
GitHub Actions settings require full-SHA action references and permit only
`actions/checkout`, `actions/setup-node`, and `gitleaks/gitleaks-action`.

## Open Items

All previously planned items have been implemented.

- 2026-09-14: Gitleaks runs as a third `validate.yml` job (SHA-pinned,
  `contents: read`). Push scans run after commits reach GitHub; they cannot
  prevent initial exposure or guarantee that all secrets are detected.
- 2026-09-14: malformed exception values and timezone-free timestamps now
  produce validation errors; freshness reporting retains diagnostics and
  fails on hard validation errors or crashes. Soft advisories remain non-blocking.
- 2026-09-15: branch protection now requires `awesome-lint`,
  `validate-repos`, and `secret-scan`, including for administrators.
- 2026-09-15: add a read-only, maintainer-run branch-protection verifier; it
  requires no repository secret, scheduled workflow, commit, or pull request.
- 2026-09-15: add weekly advisory monitoring for non-GitHub README links;
  remote failures are reported but never block a merge.
- 2026-09-15: add token-free advisory triage reporting with overdue exception
  review status; state files remain human-maintained.
- 2026-09-15: remove the independent-approval requirement for the solo
  maintainer while retaining required CI and administrator enforcement.
- 2026-09-15: enforce SHA-pinned GitHub Actions at the repository level.
- 2026-09-15: restrict GitHub Actions to the three action sources currently
  used by repository workflows.
- 2026-09-15: clarify quarterly evidence rules for baseline and exception edits.
- 2026-09-15: audit Python scripts with Ruff; retain static-quality checks as
  optional until configuration and dependency cost are justified.

## Future considerations

These are deliberately deferred improvements, not current CI failures. Each
should be scoped, configured, and reviewed before implementation. None has an
owner, target date, or acceptance criteria yet; assigning those is part of
formally promoting an item into planned work.

1. **External-link scope.** Non-GitHub list entry links are now flagged as
   advisory soft signals (`UNVALIDATED_HOST` / `UNVALIDATED_LINK`), and the
   four standards links (A2A, ERC-8004, W3C x2) were baselined on 2026-09-23.
   Machine checks for recognized non-GitHub code hosts are deferred until a
   real submission needs them; website-only links stay under manual review.
   Documentation links outside the README retain advisory-only handling for
   redirects, rate limits, and temporary outages.
2. **Scheduled settings verification.** The read-only branch-protection
   verifier supports local and handover reviews. Automating it would require
   a separately managed credential with repository-administration read access;
   do not add one unless the benefit outweighs that operational risk.
3. **Python static quality checks.** Consider pinned Ruff and optionally mypy
   or pyright for the standard-library scripts. This is optional while the
   scripts remain small and are covered by tests.

### Security tightening under consideration

These security improvements are also deferred considerations, not evidence of
a current compromise or CI failure:

- **Static analysis.** Reassess CodeQL, Ruff, or another focused analyzer if
  the standard-library Python scripts grow beyond their current scope.
- **Settings verification.** Consider a periodic or policy-backed check for
  branch protection, Actions restrictions, required checks, and permissions.
- **Scope and external destinations.** Keep the non-endorsement boundary
  explicit and consider separate monitoring or review for external links and
  listed projects, which this repository does not security-audit.
- **Operational response.** Document named ownership, backup coverage, and
  secret-rotation steps so response does not depend on informal maintainer
  knowledge.

## Review Cadence

| Cadence                      | Action                                                                                                                                                                                                                                                                                                                      |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Weekly                       | `dependency-freshness.yml` run — review validator drift, Action freshness, external-link health, and exception-triage summaries                                                                                                                                                                                            |
| Monthly                      | Triage new and overdue advisories from reported runs: resolve to baseline, exception, or removal                                                                                                                                                                                                                             |
| Monthly                      | Run `verify-repository-settings.py` from an authenticated maintainer session; investigate any reported branch-protection drift                                                                                                                                                                                               |
| Quarterly                    | Full baseline audit (`validate-repos.py --baseline-audit`): clear from the advisory baseline entries that crossed ≥5 stars (observation-driven baseline hygiene — list entries are never removed on star count alone), re-check `review_after` dates in `repo-exceptions.json`, bump `reviewed` in `advisory-baseline.json` |
| On PRs with advisory signals | Apply the adoption-evidence rule in contributing.md; ask the contributor for package-registry download data when relevant                                                                                                                                                                                                   |

Last reviewed: 2026-09-23.

<!-- Revision history:
- 2026-09-23: baseline standards entry links and defer Layer-2 code-host machine checks
- 2026-09-23: note entry-link validation and criteria updates (PRs #31/#32) and KeyDrift rejection (#30)
- 2026-09-20: remove unavailable AffixIO and AINRP entries, reconcile the advisory baseline, and revisit the roadmap
- 2026-09-14: completed medium audit fixes for input handling, report failure propagation, and accurate security documentation
- 2026-09-14: initial roadmap; implemented items 1-4 + backlog (scheduled report, triage rule, baseline-audit, threshold constant)
- 2026-09-14: added open item 1 (automated secret scanning on PRs) after security review; expanded .gitignore credentials patterns and added .env.example
- 2026-09-14: implemented open item 1 (gitleaks in validate.yml); roadmap fully implemented
- 2026-09-14: added MAINTENANCE.md as the per-file automation reference, linked from Current Automation State
- 2026-09-14: recorded deferred considerations for external links, repository settings, Python quality, advisory triage, and direct-push governance
- 2026-09-14: clarified intentional automation gaps and that future considerations have no owner, target date, or acceptance criteria until promoted to planned work
- 2026-09-14: recorded deferred security-tightening considerations for static analysis, settings verification, governance, scope monitoring, and secret response
- 2026-09-14: added secret-scan hard-failure and required-check enforcement consideration
- 2026-09-15: require secret-scan in branch protection and apply protection to administrators
- 2026-09-15: add manual, read-only branch-protection verification without a repository token or scheduled repository changes
- 2026-09-15: add weekly advisory monitoring for non-GitHub README links without tokens or repository churn
- 2026-09-15: use the first external-link report to replace the stale Google-hosted A2A documentation URL
- 2026-09-15: update the automation inventory for advisory external-link monitoring
- 2026-09-15: classify external 403 and other non-404/410 responses as unknown rather than broken
- 2026-09-15: remove the independent-approval requirement for the solo maintainer
- 2026-09-15: clear the resolved nmcitra/ktp-rfc LOW_STARS baseline entry and reconcile maintenance state facts
- 2026-09-15: enforce GitHub Actions SHA pinning
- 2026-09-15: restrict GitHub Actions to the current checkout, setup-node, and gitleaks sources
- 2026-09-15: reconcile criteria and roadmap wording with all freshness reports
-->
