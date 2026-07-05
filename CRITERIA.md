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

| Level | Trigger | Effect |
|-------|---------|--------|
| **Hard failure** | Repo is 404 (deleted) or archived | CI fails — must fix before merge |
| **Soft flag** | Below star threshold, no license, inactive, or weak description | Warning in weekly report — human reviews and decides |

| Gate | Threshold | Severity |
|------|-----------|----------|
| Repository exists | GitHub API returns 200 | **Hard failure** |
| Not archived | `archived: false` in API response | **Hard failure** |
| Has an open-source license | `license` field is not null | Soft flag |
| Minimum adoption | ≥5 stars | Soft flag (exempted for LF/standards projects) |
| Recent activity | At least one commit in the last 12 months | Soft flag |
| Meaningful description | ≥15 characters describing what it does | Soft flag |

**Hard failures** must be fixed before a PR can merge. If a repo is
deleted or archived, remove it from the list or replace it with an
alternative.

**Soft flags** produce warnings in the weekly CI report but do not
block PRs. They indicate projects that may be early-stage, dormant,
or underspecified — a human reviews and decides whether to keep or
prune.

## Categorization Rules

- **One project, one category.** List the project in its primary
  function category. Avoid listing the same project in multiple
  sections.
- **Cross-cutting projects** go in whichever category best describes
  their primary purpose.
- **Standards and specifications** (W3C, IETF, EIP, Linux Foundation)
  are exempt from the star threshold but must still exist and be
  publicly accessible.

## Exclusion Criteria

Projects are excluded if they:

- Do not relate to agent identity, trust, governance, or security
- Are tutorials, hackathon demos, or workshop materials
- Have no public repository or documentation
- Are purely commercial products without an open-source component
- Are duplicates of another listed project with the same scope

## What This List Is Not

This is not a general catalog of "AI agent tools" or "agent
frameworks." It is specifically focused on the **trust and identity
infrastructure** layer: how agents prove who they are, how they are
governed, how they are verified, and how they build and maintain
trust.
