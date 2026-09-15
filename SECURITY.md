# Security Policy

## Supported Versions

This repo is a curated public awesome list with supporting validation tooling.
There are no versioned releases — always use the latest commit from `main`.

## Reporting a Vulnerability

This project has no deployed runtime service and must not contain credentials.
It ships a curated README plus GitHub Actions validation for listed
repositories. If you find an issue with the content, criteria, or validation
logic, please open a public issue on GitHub.

Do **not** open a public issue if the vulnerability involves the GitHub Actions
workflow itself, such as leaked CI logs or token exposure. Report privately to
the repository owner via [GitHub's security advisory tool](https://github.com/CodeSigils/awesome-agent-trust/security/advisories/new).

## Accidental Credential Exposure

`secret-scan` runs on every push and pull request and is required before a
pull request can merge. It is a detection control, not a guarantee: a scan
runs after a push reaches GitHub and may not recognize every credential.

If a credential is committed or appears in CI output, revoke or rotate it
immediately. Do not paste the credential into an issue, pull request, or
security advisory. Report the incident privately using the channel above,
including only the affected system, when it was exposed, and the remediation
already taken.

## Commit Signing

Maintainer commits from 2026-07-05 onward are SSH-signed. Earlier commits may
be unsigned and are retained to avoid rewriting public history.

## Review cadence

Review this policy alongside the monthly repository-settings check and the
quarterly maintenance review. Confirm that secret scanning, branch protection,
Action pinning, and credential-response guidance still match the live
repository controls.

Last reviewed: 2026-09-15.
