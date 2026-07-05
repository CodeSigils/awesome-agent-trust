# Contributing

Contributions are welcome! This is a community-curated list of projects
concerned with AI agent identity, trust, governance, and security.

## Guidelines

- **One project per pull request** — makes review easier.
- **Format:** `- [Project Name](url) - Description of what it does.`
- **Description** should be one sentence explaining what the project does
  and why it matters for agent trust/identity/governance.
- **Open source preferred** but standards, protocols, and specifications
  are also accepted (W3C, IETF, Linux Foundation, etc.).
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
- [ ] The repository is public, has an open-source license, and has
      had at least one commit in the last 12 months
- [ ] The repository has **5 or more stars** (or is a standards/spec
      project from W3C, IETF, Linux Foundation, or similar)
- [ ] The description is a single sentence explaining what the project
      does — not marketing language
- [ ] The entry is in the **correct category** (see CRITERIA.md for
      definitions)
- [ ] No duplicate entry exists in the list already
- [ ] `npx awesome-lint` passes locally
- [ ] `python3 .github/scripts/validate-repos.py` passes locally

## Quality criteria

Projects should meet at least one of:

1. Has a public GitHub repository with meaningful activity
2. Is an open standard or specification (W3C, IETF, EIP, etc.)
3. Is a Linux Foundation or similarly governed open-source project
4. Has documented real-world usage or adoption

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
- Has ≥5 stars (soft flag; exempt for LF/standards projects)
- Has a meaningful description (soft flag)
- List entry in README includes a description after the link (soft flag)
- Committed within the last 12 months (soft flag)

Run both locally before submitting:

```bash
npx awesome-lint
python3 .github/scripts/validate-repos.py
```

## Submission process

1. Fork this repository
2. Edit the README.md to add your project in the appropriate category
3. Submit a pull request

Thanks for contributing!
