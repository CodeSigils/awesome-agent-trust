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

## Open Items

### 1. Baseline the two A2A SDK inactivity advisories

**What:** Add `go-a2a/a2a-go` (README entry "A2A Go") and
`themanojdesai/python-a2a` (README entry "Python A2A") to the `INACTIVE`
array in `.github/advisory-baseline.json`, alongside the existing
`Ineedsomuchhelp/AINRP` entry, during the next baseline refresh.

**Why:** These are the only two `NEW_INACTIVE` advisories standing since
before the YYLO Benchmark merge, and both are core-ecosystem SDKs for the
A2A protocol — the same protocol the list's marquee entry implements. They
are unmaintained (no push in over a year) but not dead or misleading, so
removing them would lose coverage while leaving them unbaselined would
keep re-flagging the same two repos on every validator run. Documenting
them isolates genuine new signal and keeps the "new advisories" output of
each run meaningful.

### 2. Scheduled validator report

**What:** Extend the weekly `dependency-freshness.yml` workflow to also run
`python3 .github/scripts/validate-repos.py` and write the
`NEW_*` / `RESOLVED ADVISORIES` / `ACCEPTED EXCEPTIONS` summary into
`GITHUB_STEP_SUMMARY`.

**Why:** Star counts and repository liveness drift continuously, but the
validator is currently only run on demand or on PRs. The existing weekly
cron already runs with `contents: read` and a token, so adding a second
step makes the inspection cycle automatic: a one-screen Monday report of
which projects crossed the ≥5-star threshold and which new flags appeared,
instead of a manual loop that tends to go stale between contributions.

### 3. Standardize the below-threshold triage rule

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

### 4. Bulk star-audit helper

**What:** Add a `--baseline-audit` mode to `.github/scripts/validate-repos.py`
that iterates the `LOW_STARS` entries in the advisory baseline, fetches
current star counts, and prints which repos have crossed the ≥5-star
threshold versus which are still below it.

**Why:** The `LOW_STARS` baseline currently holds 44 entries and cannot be
checked by hand. The AgentLair cleanup showed the pattern — a project
crossing 5 stars needs its baseline entry removed — but finding it
required either a full validator run or a manual `gh api` loop per repo.
An audit mode turns the quarterly review from minutes of scripting into
seconds, and catches resolved advisories automatically.

## Backlog

### 5. Configurable star threshold

**What:** Extract the hardcoded 5-star threshold in
`.github/scripts/validate-repos.py` into a named constant (or config
value) used by both the advisory check and the audit mode above.

**Why:** Keeps the policy in one place and makes any future per-category
threshold tuning a one-line change instead of a behavioral edit buried in
the check logic.

## Review Cadence

| Cadence | Action |
|---------|--------|
| Weekly | `dependency-freshness.yml` run — review the validator summary once item 2 is in place |
| Monthly | Triage new advisories from reported runs: resolve to baseline, exception, or removal |
| Quarterly | Full baseline audit: remove entries that crossed ≥5 stars, re-check `review_after` dates in `repo-exceptions.json`, bump `reviewed` in `advisory-baseline.json` |
| On PRs with advisory signals | Apply the adoption-evidence rule from item 3; ask the contributor for package-registry download data when relevant |

Last reviewed: 2026-09-14.