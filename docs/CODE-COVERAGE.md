# Code Coverage and Test Quality

This file is the evidence-backed register for test coverage, test-quality
issues, and the official guidance behind each decision. Read it together with
[docs/MAINTENANCE.md](MAINTENANCE.md) (operations and commands) and
[docs/ROADMAP.md](ROADMAP.md) (dated decisions). MAINTENANCE remains
authoritative for how the repository is operated; this file is authoritative
for why coverage is measured the way it is and what evidence supports each
test-quality decision.

## Research-first rule

Before changing a test, a coverage number, or a workaround:

1. Reproduce the behavior with the smallest command that exercises the real
   code path.
2. Find official guidance from GitHub, Python, coverage.py, or the relevant
   upstream project. Prefer primary documentation over blog posts.
3. Record the link and state what it establishes. A link without a claim is
   not evidence.
4. If no official source exists, label the statement **Local observation** and
   say what was measured. Never present a local workaround as upstream policy.
5. Add or update an entry in the issue register below, including the decision
   and how it was verified.
6. Review this file with MAINTENANCE and ROADMAP in the same change, then add a
   dated revision-history row.

## Policy

Coverage is a maintainer diagnostic, not a CI gate. CI runs the test suite
through `npm test`; it does not install `coverage` and does not enforce a
percentage. That matches the existing policy for Ruff and type checkers in
MAINTENANCE: the runtime scripts use only the standard library, and a
measurement tool would add a third-party dependency, a version pin, and a
failure mode that is not a product failure. The behavioral gate remains the
regression suite, the live validator, and the exit-code contract.

Branch coverage is the primary signal because most scripts here are decision
tables: a line can execute while the failing side of an `if` never does.
coverage.py records both destinations of a conditional and marks a partial
branch when only one was taken
([branch coverage](https://coverage.readthedocs.io/en/latest/branch.html),
[how coverage.py works](https://coverage.readthedocs.io/en/latest/howitworks.html)).
A coverage drop is a prompt to inspect the changed branch, not an automatic
failure. Do not add a hard threshold without an explicit review of its version
pin and maintenance cost.

## Reproduce

Run the suite with branch measurement, without adding a repository dependency:

```bash
uvx --from coverage coverage run --branch \
  --data-file=/tmp/awesome-agent-trust.coverage \
  -m unittest discover -s tests
uvx --from coverage coverage report \
  --data-file=/tmp/awesome-agent-trust.coverage -m
```

`uvx` resolves coverage.py into an isolated environment and `--data-file`
keeps the working tree clean; the options are documented under
[`coverage run`](https://coverage.readthedocs.io/en/latest/commands/cmd_run.html).
The test command is the discovery form documented by `unittest`
([test discovery](https://docs.python.org/3/library/unittest.html#test-discovery)).
For line-only coverage, rerun without `--branch`.

## Baseline: 2026-10-30

109 tests pass. Branch-mode measurement:

| Script                          | Statements | Missed | Branches | Partial | Cover (branch mode) |
| :------------------------------ | ---------: | -----: | -------: | ------: | ------------------: |
| `check-markdown-links.py`       |         36 |      1 |       22 |       2 |                 95% |
| `gh_api.py`                     |         41 |      0 |       12 |       0 |                100% |
| `report-action-freshness.py`    |         54 |      1 |       22 |       1 |                 97% |
| `report-advisory-triage.py`     |         68 |      1 |       22 |       1 |                 98% |
| `report-external-links.py`      |         84 |      1 |       14 |       1 |                 98% |
| `validate-repos.py`             |        342 |      1 |      162 |       2 |                 99% |
| `verify-repository-settings.py` |         46 |      1 |       14 |       1 |                 97% |
| **Total**                       |    **671** |  **6** |  **268** |   **8** |              **99%** |

Line-only coverage is also 99% (665 of 671 statements). The six unexecuted
statements are the `raise SystemExit(main())` entry points listed below. The
eight partial branches are loop-exit and defensive paths; they are not hidden
product failures.

## Remaining gaps and why

- **Entry-point lines are outside in-process coverage.** The final
  `raise SystemExit(main())` / `sys.exit(main())` lines in
  `check-markdown-links.py` (56), `report-action-freshness.py` (78),
  `report-advisory-triage.py` (91), `report-external-links.py` (133),
  `validate-repos.py` (474), and `verify-repository-settings.py` (61) are
  executed when CI runs the scripts, not when unittest imports them. coverage.py
  does not trace a plain subprocess unless it is started with coverage
  ([subprocess measurement](https://coverage.readthedocs.io/en/latest/subprocess.html)).
  The link checker and advisory triage have subprocess smoke tests; the other
  entry points rely on their workflow invocation. This is a measurement
  boundary, not an untested behavior.
- **Defensive branches stay intentionally narrow.** Unreadable files, retry
  exhaustion, summary writes, and malformed JSON are covered where a test can
  create the condition deterministically. Do not contort a unit test to reach
  an environment-only path; add a subprocess or integration test when the
  behavior matters.
- **No percentage threshold.** A high number is not proof of correctness. The
  issue register is where a real risk gets a named test and a named source.

## Issue register

Copy this row shape for a new entry:

| Field | Content |
| :--- | :--- |
| ID | `CC-NNN` |
| Issue | One sentence describing the risk. |
| Evidence | Official link and the specific claim it establishes. If none exists, write **Local observation** and the measurement. |
| Decision | The recommended solution and why it is preferred over the workaround. |
| Status | `open`, `implemented YYYY-MM-DD`, or `superseded`. |
| Verification | Test name or command that proves the decision. |

Current entries:

| ID | Issue | Evidence | Decision | Status | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CC-001 | Pinned Actions need an immutable reference, and the local freshness regex also needs a version comment. | GitHub's secure-use reference says a workflow dependency lockfile supersedes SHA pinning for adopters; otherwise pin to a full-length commit SHA because tags are mutable ([secure use](https://docs.github.com/en/actions/reference/security/secure-use)). CodeQL's unpinned-tag guidance shows the full-SHA plus trailing `# vN` convention ([CodeQL](https://codeql.github.com/codeql-query-help/actions/actions-unpinned-tag/)). | Keep full-length SHA pins. The trailing comment is required by this repository's `PINNED` regex, not by GitHub; the fixture uses the real `actions/checkout` SHA and asserts the parsed major. Anchor the regex to action step lines so comments and `run:` text do not match. | implemented 2026-10-30 | `ActionFreshnessReportTests` (current/stale/unknown, real SHA, `v7` row, commented-out pin ignored). |
| CC-002 | Line coverage can hide an untested branch in decision-table code. | coverage.py documents branch measurement and partial branches ([branch coverage](https://coverage.readthedocs.io/en/latest/branch.html)). | Measure in branch mode and record both statement and branch figures. | active | Baseline table above. |
| CC-003 | The test command must discover the suite the same way CI does. | Python documents `python -m unittest discover` and its import rules ([test discovery](https://docs.python.org/3/library/unittest.html#test-discovery)). | Use the discovery form in local commands and `npm test`; do not hand-list test modules. | active | `npm test`; commands above. |
| CC-004 | A test that relies on import-time `NOW` becomes a time bomb. | Python documents timezone-aware datetimes and their comparison semantics ([datetime](https://docs.python.org/3/library/datetime.html)). **Local observation:** `check_repo` defaults to import-time `NOW`, so a fixture dated 2026-09-01 would trip `INACTIVE` after 2027-09-01. | Pass an explicit `now=` in tests that assert a non-INACTIVE result. | implemented 2026-10-30 | `test_token_scoped_404_retries_without_credentials`. |
| CC-005 | A mocked call can pass while the real request contract is wrong. | Python documents `assert_called_once_with` and call inspection on mocks ([unittest.mock](https://docs.python.org/3/library/unittest.mock.html)). | Assert request URLs, token/timeout arguments, and retry counts where the contract matters. | implemented 2026-10-30 | `GhApiTests`, `ActionFreshnessReportTests.latest_sha_*`. |
| CC-006 | Entry-point `SystemExit` lines are not traced by in-process tests. | coverage.py documents subprocess measurement as a separate mode ([subprocess](https://coverage.readthedocs.io/en/latest/subprocess.html)). | Do not fake an entry point in-process. Use a subprocess smoke test where it is safe, and document the remaining lines as a measurement boundary. | active | Link-checker and triage subprocess tests; baseline notes. |
| CC-007 | A set-based inventory test does not fail on duplicate mentions. | **Local observation:** `documented` is a set, so duplicates collapse; the real failure is a backticked `.github/scripts/<name>` that is not on disk. | Keep the set comparison and document its actual failure mode; do not claim duplicates fail. | implemented 2026-10-30 | `ScriptInventoryTests`. |
| CC-008 | An unanchored `uses:` search can report commented-out or `run:` text. | GitHub's workflow syntax defines `uses` as a step key ([workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsuses)). **Local observation:** `re.search` matched any line containing the pattern. | Anchor `PINNED` to a step line (`^\s*(?:-\s*)?uses:`) and keep a regression test for comments and `run:` text. | implemented 2026-10-30 | `test_main_ignores_pins_that_are_not_action_step_lines`. |

## Review protocol

- Update the baseline table and the revision history whenever the test suite or
  a measured script changes materially.
- Re-read MAINTENANCE's Python quality expectations and ROADMAP's open items in
  the same pass. If the files disagree, resolve the drift before closing the
  change.
- Add a dated ROADMAP revision row for a policy change, not for a routine test
  count refresh.
- Keep the register short and evidence-backed. Delete a superseded entry only
  after its replacement is recorded.

## Revision history

- 2026-10-30: create this register; move the coverage rationale out of
  MAINTENANCE; record the 109-test, 99% branch-mode baseline; add the
  research-first rule and issue register; link it from MAINTENANCE, AGENTS, and
  contributing.
