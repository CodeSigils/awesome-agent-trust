# AGENTS.md

Guidance for AI agents working on this repository. Humans: `contributing.md`
is the contributor guide; `docs/MAINTENANCE.md` is the operations manual.

## Git workflow — `main` is protected

- `main` is protected: admin-enforced, strict required CI checks
  (`awesome-lint`, `validate-repos`, `secret-scan`), linear history required.
  Direct pushes fail, including for admins.
- Never push directly to `main`. Use: branch → PR → squash merge
  (`gh pr merge --auto --squash --delete-branch` is the normal flow).
- Run `git status` and `git fetch origin` first, before starting any work.
- Never rebase or rewrite a pushed PR branch except to satisfy the strict
  up-to-date requirement after the base moves
  (`git rebase origin/main` then `git push --force-with-lease`).

## Before editing anything

- Read `docs/MAINTENANCE.md` — daily operations, the verification gate,
  branch-protection facts, and revision-history conventions. It is
  authoritative.
- Read `docs/ROADMAP.md` before documentation or policy work — it is a
  dated decision record; add a dated change-log row when policy changes.
- Read `tests/test_validate_repos.py` and `docs/CODE-COVERAGE.md` before
  changing tests or a measured script. The suite is the behavioral record;
  the register holds coverage evidence, official guidance, and test-quality
  decisions. Review both with `docs/MAINTENANCE.md`.
- Verification gate before any commit: `npm run lint`, `npm test`,
  `python3 .github/scripts/check-markdown-links.py` (plus
  `.github/scripts/validate-repos.py` for repository-list changes).

## Repo invariants

- A sub-five-star repository is a secondary advisory signal only; it does
  not gate inclusion or require an exception. Exception requests are for
  real policy departures (no open license, standards-only doc site).
- Do not edit `.github/advisory-baseline.json` or
  `.github/repo-exceptions.json` unless a maintainer explicitly asks.
