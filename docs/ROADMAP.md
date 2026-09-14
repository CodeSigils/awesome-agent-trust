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

| Automation | Trigger | What it does |
|------------|---------|--------------|
| `validate.yml` — 2 jobs | push to main · PR to main · weekly cron `0 6 * * 1` (Mon 06:00 UTC) · manual dispatch | Job 1: `awesome-lint` (npm) checks list format/badges/TOC/relative links. Job 2: `validate-repos.py` checks every GitHub repo in the README (exists/archived/license/★/activity/description/ordering) with `GH_TOKEN` |
| `dependency-freshness.yml` | weekly `30 6 * * 1` · manual dispatch | `report-action-freshness.py` checks pinned Actions (`@sha # vN`) against latest tags → writes table to the workflow summary. Also runs `validate-repos.py` and writes the advisory drift summary (`NEW_*` / `RESOLVED` / `ACCEPTED`) to the same summary. Advisory only |
| `dependabot.yml` | weekly (GitHub-managed) | Opens PRs for out-of-date github-actions and npm dependencies |

Plus the non-CI automation: the issue template (`project-proposal.yml` with category dropdown) and the PR template's 10-item checklist — both shape submissions.

What automation does NOT exist yet (the gap this roadmap closes):

- **No baseline audit helper** (roadmap item 2) — clearing resolved `LOW_STARS` entries is still done by hand (as with the recent `tooltrust-directory` / `helixid` / `ai-trust` clears).
- **No auto-updates at all** — by governance design; every baseline/exception change is maintainer-made.

So as of 2026-09-14: PRs are fully gated automatically, dependency freshness is reported automatically, and star/license/activity drift is reported automatically every Monday (open item 1, implemented this pass). What remains manual is the triage of that report — which stays maintainer-made by governance design.

## Open Items

### 1. Standardize the below-threshold triage rule

**What:** Add an explicit rule to [contributing.md](../contributing.md) (and
point to it from [CRITERIA.md](../CRITERIA.md)): a sub-5-star repo may be
recorded in `.github/repo-exceptions.json` with documented adoption
evidence — package-registry downloads, an active specification process, or
foundation governance — instead of being listed in the advisory baseline.

**Why:** The mechanism already exists — three exceptions
(`CSOAI-ORG/meok-aaif-agent-card-mcp`, `CSOAI-ORG/oasf-agent-directory-mcp`,
`capiscio/capiscio-rfcs`) and the YYLO maintainers' standing offer of npm
download data for `yylo-dev/yylo-benchmark` are working precedents — but
the rule itself is not written down anywhere. Codifying it removes the
guesswork from every `NEW_LOW_STARS` review and matches the criteria's
existing position that "stars alone never establish quality."

### 2. Bulk star-audit helper

**What:** Add a `--baseline-audit` mode to `.github/scripts/validate-repos.py`
that iterates the `LOW_STARS` entries in the advisory baseline, fetches
current star counts, and prints which repos have crossed the ≥5-star
threshold versus which are still below it.

**Why:** The `LOW_STARS` baseline currently holds 42 entries and cannot be
checked by hand. The AgentLair cleanup showed the pattern — a project
crossing 5 stars needs its baseline entry removed — but finding it
required either a full validator run or a manual `gh api` loop per repo.
An audit mode turns the quarterly review from minutes of scripting into
seconds, and catches resolved advisories automatically.

## Backlog

### 3. Configurable star threshold

**What:** Extract the hardcoded 5-star threshold in
`.github/scripts/validate-repos.py` into a named constant (or config
value) used by both the advisory check and the audit mode above.

**Why:** Keeps the policy in one place and makes any future per-category
threshold tuning a one-line change instead of a behavioral edit buried in
the check logic.

## Review Cadence

| Cadence | Action |
|---------|--------|
| Weekly | `dependency-freshness.yml` run — review the validator summary (`NEW_*` / `RESOLVED` / `ACCEPTED`) |
| Monthly | Triage new advisories from reported runs: resolve to baseline, exception, or removal |
| Quarterly | Full baseline audit: remove entries that crossed ≥5 stars, re-check `review_after` dates in `repo-exceptions.json`, bump `reviewed` in `advisory-baseline.json` |
| On PRs with advisory signals | Apply the adoption-evidence rule from item 1; ask the contributor for package-registry download data when relevant |

Last reviewed: 2026-09-14.