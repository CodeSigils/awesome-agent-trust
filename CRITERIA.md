# Criteria for Inclusion

Projects listed in awesome-agent-trust must meet the following criteria.
These gates keep the list focused on active, relevant, and trustworthy
projects in the agent identity and governance ecosystem.

## Relevance

The project must directly address one of these domains:

- Agent naming & discovery
- Agent identity & cryptographic identity (DIDs, Ed25519, zero-trust)
- Governance & policy enforcement (policy-as-code, execution sandboxing, approval gates)
- Permissions & authorization (tool-level auth, delegation, OAuth for agents)
- Trust registries, verification & attestation
- Agent reputation & scoring
- Audit trails & observability
- Security & scanning (vulnerability detection, supply chain, red-teaming)
- Skills curation & trusted marketplaces
- Agent-to-agent protocols & trust infrastructure
- Attestation & confidential computing

## Quality Gates

Projects listed on this index are checked by the repo validation script
(`.github/scripts/validate-repos.py`). Two severity levels exist:

| Level            | Trigger                                                                   | Effect                                                                         |
| ---------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Hard failure** | Repository is missing or archived, or validation cannot complete reliably | CI fails — fix the entry or rerun after the infrastructure problem is resolved |
| **Soft flag**    | Below star threshold, no detected license, inactive, or weak description  | Advisory signal — a human reviews the project in context                       |

| Gate                       | Threshold                                                                 | Severity                                                                       |
| -------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Repository exists          | GitHub API returns 200                                                    | **Hard failure**                                                               |
| Not archived               | `archived: false` in API response                                         | **Hard failure**                                                               |
| Has an open-source license | GitHub detects a license, or a documented specification exception applies | Soft flag for existing entries; normally required for new software submissions |
| Minimum adoption           | ≥5 stars                                                                  | Advisory soft flag; not a substitute for technical or governance evidence      |
| Recent activity            | Repository push within the last 12 months                                 | Advisory soft flag; `pushed_at` is only a maintenance proxy                    |
| Meaningful description     | ≥15 characters describing what it does                                    | Soft flag                                                                      |
| List entry format          | `- [Name](url) - Description` (must include description after link)       | Soft flag                                                                      |
| Category ordering          | Display names are alphabetical within each category                       | **Hard failure**                                                               |

**Hard failures** must be fixed before a PR can merge. If a repository is
deleted or archived, remove it or replace it with a verified successor. API,
authentication, and network failures are reported separately and fail closed;
they are not evidence that a project was deleted.

**Soft flags** do not block pull requests. They identify projects that may be
early-stage, dormant, underspecified, or missing machine-detectable licensing.
Human review may retain a project when stronger evidence exists, such as a
recognized specification process, independent interoperability verification,
documented adoption, or foundation governance. Stars alone never establish
quality or trustworthiness. Contributors proposing a sub-5-star repository
should document adoption evidence and request a
`.github/repo-exceptions.json` entry rather than accepting the advisory
flag. See `contributing.md` for details.

The dated `.github/advisory-baseline.json` records already-observed soft flags
so scheduled runs emphasize new and resolved signals. It is derived monitoring
state, not an approval or exception. `.github/repo-exceptions.json` is the only
place where a reviewed signal may be waived.

The scheduled dependency-freshness workflow reports pinned GitHub Action SHA
drift. It is advisory and does not replace Dependabot review.

## Categorization Rules

- **One project, one category.** List the project in its primary
  function category. Avoid listing the same project in multiple
  sections.
- **Cross-cutting projects** go in whichever category best describes
  their primary purpose.
- **Alphabetical ordering** is case-insensitive by displayed project name
  within each category. Position does not represent rank or endorsement.
- **Standards and specifications** may receive narrowly documented exceptions
  in `.github/repo-exceptions.json`. Repository-name keywords are not evidence
  of standards status or foundation affiliation.
- **Exceptions are evidence records, not automatic acceptance.** Each one must
  name the repository, the exact checks waived, the reason, and a review date.

## Exclusion Criteria

Projects are excluded if they:

- Do not relate to agent identity, trust, governance, or security
- Are tutorials, samples, hackathon demos, or workshop materials, unless the
  artifact is the canonical implementation of an included specification
- Have no public repository or documentation
- Are purely commercial products without an open-source component
- Are duplicates of another listed project with the same scope

## Ongoing Review

Inclusion is not permanent. Remove or update an entry when current evidence
shows that it no longer meets these criteria, its destination has become
unsafe, or a repository has moved. Contested removals should cite evidence and,
unless the destination is clearly unsafe or gone, allow the affected maintainer
a reasonable opportunity to respond.

Changes to the category taxonomy require prior issue discussion and maintainer
approval. A new category should describe a distinct reader need and contain at
least three qualifying entries.

## What This List Is Not

This is not a general catalog of "AI agent tools" or "agent
frameworks." It is specifically focused on the **trust and identity
infrastructure** layer: how agents prove who they are, how they are
governed, how they are verified, and how they build and maintain
trust.
