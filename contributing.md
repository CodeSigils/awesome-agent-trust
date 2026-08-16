# Contributing

Contributions are welcome! This is a community-curated list of projects
concerned with AI agent identity, trust, governance, and security.

## Guidelines

- **One project per pull request** — makes review easier.
- **Format:** `- [Project Name](url) - Description of what it does.`
- **Description** should be one sentence explaining what the project does
  and why it matters for agent trust/identity/governance.
- **Open-source licensing is normally required for software.** Standards,
  protocols, and specifications may qualify when their terms permit public
  review and implementation.
- **No star counts** in the description. If a project is notable for its
  adoption, mention it qualitatively.
- **Categories** are organized by function. If a project spans multiple
  categories, choose the primary one and cross-link if needed.
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
- [ ] No duplicate entry exists in the list already
- [ ] `npm run lint` passes locally
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

See [CRITERIA.md](CRITERIA.md) for the full inclusion requirements,
categorization rules, and quality gates applied by CI.

## CI Checks

Pull requests that modify `README.md` are checked by two CI jobs:

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
- Committed within the last 12 months (soft flag)

Run both locally before submitting:

```bash
npm ci
npm run lint
npm test
python3 .github/scripts/validate-repos.py
```

## Submission process

1. Fork this repository
2. Edit the README.md to add your project in the appropriate category
3. Submit a pull request

Thanks for contributing!
