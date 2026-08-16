# Contributing

Contributions are welcome! This is a community-curated list of projects
concerned with AI agent identity, trust, governance, and security.
Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Guidelines

- **One project per pull request is required.** Unrelated additions or cleanup
  should use separate pull requests so each project can be reviewed on its own
  evidence.
- **Format:** `- [Project Name](url) - Description of what it does.`
- **Description** should be one sentence explaining what the project does
  and why it is useful or distinctive for agent trust, identity, or governance.
  Use independently checkable facts rather than copying marketing claims.
- **Open-source licensing is normally required for software.** Standards,
  protocols, and specifications may qualify when their terms permit public
  review and implementation.
- **No star counts** in the description. If a project is notable for its
  adoption, mention it qualitatively.
- **Categories** are organized by function. If a project spans multiple
  categories, choose the primary one and cross-link if needed.
- **Ordering** is alphabetical by displayed project name within each category,
  case-insensitively. Do not use position to imply ranking.
- **No commercial products** unless they have a meaningful open-source
  component or are an open standard.
- **No projects without a public repository or documentation site.**
- **Check for duplicates** before submitting.

## Pre-Submission Checklist

Before opening a pull request, confirm each item:

- [ ] The project is relevant to agent identity, trust, governance,
      security, permissions, attestation, or reputation
- [ ] The repository is public and, for software, has an open-source license
- [ ] The project is maintained, or the submission explains why an inactive
      specification remains authoritative
- [ ] If the repository has fewer than **5 stars**, the pull request provides
      stronger evidence such as independent verification, documented adoption,
      foundation governance, or a recognized standards process
- [ ] The description is a single sentence explaining what the project
      does — not marketing language
- [ ] The entry is in the **correct category** (see CRITERIA.md for
      definitions)
- [ ] The entry is in alphabetical order within that category
- [ ] No duplicate entry exists in the list already
- [ ] `npm ci` completes from the committed lockfile
- [ ] `npm run lint` passes locally
- [ ] `npm test` passes locally
- [ ] `python3 .github/scripts/validate-repos.py` passes locally

## Quality criteria

Projects must meet the relevance and exclusion rules in `CRITERIA.md`. The
following are positive quality signals, not interchangeable automatic gates:

1. Has a public GitHub repository with meaningful activity
2. Is an open standard or specification (W3C, IETF, EIP, etc.)
3. Is a Linux Foundation or similarly governed open-source project
4. Has documented real-world usage or adoption

Star counts are discovery metadata, not proof of quality. A low-star project
may be accepted when its submission presents stronger, independently
checkable evidence. Any exception must be narrow and documented in
`.github/repo-exceptions.json`. The separate advisory baseline only reduces
repeated CI noise; it does not grandfather a project or override these criteria.

New advisory signals do not automatically reject a submission. Explain the
signal in the pull request and provide stronger evidence for inclusion; the
maintainer will decide whether the project belongs. Do not edit
`.github/advisory-baseline.json` or `.github/repo-exceptions.json` unless a
maintainer explicitly requests that change. Those files record maintainer
review state, not contributor assertions.

See [CRITERIA.md](CRITERIA.md) for the full inclusion requirements,
categorization rules, and quality gates applied by CI.

## CI Checks

Every pull request is checked by two required CI jobs:

**awesome-lint** — checks list format compliance:
- Badge presence after the main heading
- List item format (`- [Name](url) - Description`)
- No trailing slashes on URLs
- No duplicate links
- Valid table of contents

**validate-repos** — checks every listed repository:
- Exists and is not archived (hard failure — blocks merge)
- Has an open-source license (soft flag)
- Has ≥5 stars (advisory soft flag)
- Has a meaningful description (soft flag)
- List entry in README includes a description after the link (soft flag)
- Repository pushed to within the last 12 months (advisory soft flag;
  GitHub's `pushed_at` value is a maintenance proxy)

Run the corresponding installation, test, lint, and live validation commands
locally before submitting:

```bash
npm ci
npm run lint
npm test
python3 .github/scripts/validate-repos.py
```

## Submission process

1. Fork this repository and create a focused branch.
2. Add one project to the appropriate `README.md` category.
3. Complete the pull request template with relevance and quality evidence.
4. Explain any advisory signal or requested policy exception; do not edit the
   maintainer-owned baseline or exception registry yourself.
5. Submit the pull request and resolve review conversations. Both required CI
   jobs must pass before merge.

## Removing or Replacing an Entry

A removal pull request should identify the exact criterion no longer met and
link to current evidence, such as an archived repository, missing license,
abandonment, changed scope, or a verified successor. Remove only one project
per pull request. When a project moved or was renamed, replace its URL and
description instead of deleting useful history.

Except for an unequivocal deletion, archive, or malicious destination, allow
the project maintainer a reasonable opportunity to clarify the evidence before
merging a contested removal. Inclusion is not permanent; retained entries must
continue to meet `CRITERIA.md`.

## Changing Categories or List Structure

Moving one existing entry to a better-fitting category may be proposed in a
focused pull request. Creating, renaming, merging, or splitting categories is a
maintainer decision because it changes the list's taxonomy. Propose structural
changes in an issue first and explain:

- the reader need the change addresses;
- which existing entries would move;
- why the current categories are insufficient; and
- how the change avoids overlap or duplicate listings.

New categories should contain at least three qualifying entries. Entries remain
alphabetical after any move.

Thanks for contributing!
