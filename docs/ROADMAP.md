# Roadmap

This file is the dated decision record for awesome-agent-trust and the place
where planned changes to the list, the validation tooling, and the review
process are held. This project has no versioned releases (see
[SECURITY.md](../SECURITY.md)), so nothing else preserves that history.

Two kinds of content live here, and the split is deliberate.
[Future considerations](#future-considerations) holds the outstanding work and
is the answer to "what is next". [Closed Items](#closed-items) is a dated log of
what each change did and why: entries are added, and struck only when a later
entry supersedes them. [Current Automation State](#current-automation-state)
describes the automation as it stands.

Dates in this file reference the two machine-readable state files they
affect: the `reviewed` date in `.github/advisory-baseline.json` and the
`review_after` dates in `.github/repo-exceptions.json` act as the tick
marks for the [Review Cadence](#review-cadence) below.

## Directive

This roadmap MUST be revisited before and after every meaningful action or
decision about this repository — every merge, removal, baseline or exception
edit, CI change, or policy adjustment. Each revisit must also tighten the
roadmap itself: strike superseded items, correct stale estimates, dates, or
cadence notes, and fold lessons learned back into the outstanding work.
Completed entries are retained rather than struck, because the reason a
decision was made outlives the work it decided; strike one only when a later
entry replaces it. A roadmap that is not re-read before and after each change
is not a record; it is documented drift.

## Current Automation State

As of 2026-09-27, the repo has three pieces of automation, all in `.github/`.
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

As of 2026-09-27, required PR checks cover format, repository validation, and
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

Every check script in `.github/scripts/` follows one
[exit-code contract](MAINTENANCE.md#exit-code-contract) — 0 clean, 1 findings,
2 could not run — so an incomplete run stays distinguishable in CI from both a
clean run and a real finding. The weekly report scripts exit 0 for findings by
design, which is why the weekly workflow carries no `continue-on-error`.

## Closed Items

Every item this roadmap has ever planned has been implemented. The dated entries
below are a record rather than a queue: each states what a change did and why,
and none is reopened. Work that is genuinely outstanding is held in
[Future considerations](#future-considerations); promoting an item from there
into planned work means starting a new entry here, not reviving an old one.

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
- 2026-09-27: fix external-link extraction for badge-wrapped links; the weekly
  report previously missed 2 of the 6 non-GitHub README links while reporting
  two badge images as if they were links, because the destination pattern
  stopped at a nested image's closing bracket. Image destinations are now
  excluded by suffix, and both behaviours are covered by regression tests. A
  golden test over the real `README.md` additionally pins the exact set of six
  non-GitHub links, so an extractor that drops or invents one fails even when
  the synthetic fixtures still pass.
- 2026-09-27: adopt one exit-code contract across the check scripts — 0 clean,
  1 findings, 2 could not run. CPython already exits 1 on an uncaught
  exception, so a crash and a real finding were previously indistinguishable in
  CI. `validate-repos.py` and `check-markdown-links.py` now preflight their
  required inputs and report an unreadable or undecodable file as exit 2 with
  `COULD NOT RUN` / `COULD NOT CHECK` rather than crashing or counting it as a
  finding. `verify-repository-settings.py` already matched; the advisory report
  scripts keep a hard `return 0` by design. No workflow edit was needed,
  because both gating scripts run as bare `run:` steps where any nonzero code
  fails the job.
- 2026-09-27: cover `report-action-freshness.py`, the last script in
  `.github/scripts/` with no test binding, with ten regression tests over tag
  resolution and report rendering. Writing them exposed that the script read
  each workflow with an unguarded `read_text(encoding="utf-8")`, so an
  undecodable file raised out of `main()` and exited `1` — the same
  crash-versus-finding collision the exit-code contract exists to prevent, and
  a claim the contract section made was therefore false. An unreadable workflow
  is now listed under `COULD NOT CHECK` and the script exits `2`, keeping the
  rows it did resolve visible. The contract section now also records that
  `unittest` keeps its own exit scheme including the `1` collision, and that an
  advisory script can never fail on a finding but still fails on a crash —
  which is why the weekly workflow carries no `continue-on-error`.
- 2026-09-27: close the remaining entry-point coverage gaps and rename this
  section to `Closed Items`, since it holds no pending work and its own name was
  the last thing still promising otherwise. `report-external-links.py` read
  `README.md` with an unguarded `read_text(encoding="utf-8")`, so a non-UTF-8
  README raised out of `main()` and exited 1 — the same collision the exit-code
  contract exists to prevent, and a claim the contract section made was
  therefore false. It now exits 2 with a `COULD NOT CHECK` line, because
  reporting zero links would assert the list has no external links. Two
  `main()` tests cover that, and a third test asserts the maintenance guide's
  file inventory matches `.github/scripts/`, so the inventory cannot drift out of
  sync silently. `report-advisory-triage.py` stays uncovered on purpose: its
  failure surface is `load_json` and `render_report`, both already tested.

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
   redirects, rate limits, and temporary outages. Measured 2026-09-27: across
   every Markdown file the repository holds 6 non-GitHub `http(s)` links, and
   all 6 are in `README.md`, so nothing outside the README currently merits
   monitoring; recheck if the documentation gains external links. The golden
   test keeps that count honest for `README.md` only, since the script reads
   that one file, so files elsewhere still need the recheck. The
   general-purpose link checker [lychee](https://github.com/lycheeverse/lychee)
   was evaluated here as a possible replacement and not adopted: it reports
   without rewriting, would need `--exclude-path node_modules` to avoid
   scanning vendored dependencies, must be configured to stay advisory-only,
   and probing the 137 GitHub links weekly without a token is a weaker check
   than the existing `validate-repos.py` API validation. It stays useful as an
   independent cross-check of extraction.
2. **Scheduled settings verification.** The read-only branch-protection
   verifier supports local and handover reviews. Automating it would require
   a separately managed credential with repository-administration read access;
   do not add one unless the benefit outweighs that operational risk.
3. **Python static quality checks.** Consider pinned Ruff and optionally mypy
   or pyright for the standard-library scripts. This is optional while the
   scripts remain small and are covered by tests.
4. **Settings-verifier entry point coverage (completed 2026-09-27).** Tests
   now cover `verify-repository-settings.py` through its public `main()`:
   no token and failed or malformed GitHub reads return 2, settings drift
   returns 1, and the expected protection returns 0. The tests patch only its
   credential and API boundaries, so they exercise the exit-status contract
   without needing a live administrative token. `report-advisory-triage.py`
   remains intentionally without `main()` coverage: it is straight-line I/O
   whose failure surface already sits in tested `load_json` and `render_report`.

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

Last reviewed: 2026-09-27.

<!-- Revision history:
- 2026-09-27: rename `Open Items` to `Closed Items` now that it holds no pending work, record why `report-advisory-triage.py` stays uncovered on purpose, and guard the external-link reporter's README read as exit 2
- 2026-09-27: make the roadmap a dated record rather than a queue — reframe the header and the Directive around retaining completed entries, refresh the stale `Current Automation State` anchors, and scope the untested `verify-repository-settings.py` entry point as deferred work
- 2026-09-27: cover the Action-freshness reporter, report an unreadable workflow as exit 2 instead of a crash, and record the test suite's own exit scheme in the exit-code contract
- 2026-09-27: record the shared exit-code contract (0 clean, 1 findings, 2 could not run) and the required-input preflight that gives exit 2 a meaning
- 2026-09-27: record external-link extraction fix; answer the external-link scope item by measurement and record [lychee](https://github.com/lycheeverse/lychee) as evaluated and not adopted
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
