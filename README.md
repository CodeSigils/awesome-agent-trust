# Awesome Agent Trust & Identity [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated landscape index of open-source projects, protocols, and standards
> for AI agent identity, naming, trust verification, governance, and security.

*Inspired by the [ANS (Agent Name Service)](https://github.com/agentnameservice) ecosystem and Linux Foundation standards efforts.*

> **What this list is not:** A catalog of commercial products, academic papers
> without implementations, internal enterprise governance systems, or platform-
> specific trust models from Anthropic, OpenAI, or Google. This is a public
> open-source snapshot — the actual agent trust landscape is larger but less
> transparent.

> **How to use this list:** Treat inclusion as a discovery signal, not an
> adoption recommendation or security endorsement. Before using a listed
> approach, inspect its first-party documentation, current maintenance state,
> license, threat model, and fit for the project's observed problem.

This project follows the structural conventions of an Awesome list while
intentionally covering an emerging ecosystem more broadly than a traditional
personal-recommendation shortlist. Entries are alphabetized within categories;
inclusion means they passed this repository's criteria, not that the maintainer
endorses their security claims.

---

## Contents

- [Agent Naming & Discovery](#agent-naming--discovery)
- [Agent Identity & Cryptographic Identity](#agent-identity--cryptographic-identity)
- [Agent Governance & Policy Enforcement](#agent-governance--policy-enforcement)
- [Agent Permissions & Authorization](#agent-permissions--authorization)
- [Trust Registries & Verification](#trust-registries--verification)
- [Agent Reputation & Scoring](#agent-reputation--scoring)
- [Audit Trails & Observability](#audit-trails--observability)
- [Security & Scanning](#security--scanning)
- [Skills Curation & Trusted Marketplaces](#skills-curation--trusted-marketplaces)
- [Standards, Specifications & Foundations](#standards-specifications--foundations)
- [Agent-to-Agent Protocols](#agent-to-agent-protocols)
- [Attestation & Confidential Computing](#attestation--confidential-computing)
- [Related Awesome Lists](#related-awesome-lists)

---

## Agent Naming & Discovery

DNS-like resolution for AI agents. Core protocol with IETF draft backing.

- [A2A Agent Cards](https://google.github.io/A2A/) - JSON metadata at `/.well-known/agent-card.json`. Agents self-describe capabilities and authentication requirements.
- [Agent Name Service](https://github.com/agentnameservice/ans) - Reference implementation of the ANS protocol. Registry, transparency log, and IETF draft `draft-narajala-ans-00`.
- [ANS Registry](https://github.com/agentnameservice/ans-registry) - Registration and resolution for the Agent Name Service.
- [ANS SDK for Go](https://github.com/agentnameservice/ans-sdk-go) - Go SDK for the Agent Name Service.
- [ANS SDK for Java](https://github.com/agentnameservice/ans-sdk-java) - Java SDK for the Agent Name Service.
- [ANS SDK for Rust](https://github.com/agentnameservice/ans-sdk-rust) - Rust SDK for the Agent Name Service.
- [ERC-8004 Registry](https://eips.ethereum.org/EIPS/eip-8004) - On-chain searchable agent identity registry. Agents register as NFTs with queryable capability metadata.
- [route-ans](https://github.com/route-ans/route-ans) - High-performance ANS resolver with semantic versioning and Redis caching.

---

## Agent Identity & Cryptographic Identity

Cryptographic identity for agents — DIDs, Ed25519, zero-trust frameworks.

- [Agent Identity Protocol (AIP)](https://github.com/openagentidentityprotocol/agentidentityprotocol) - Zero-trust security layer for AI agents. Policy enforcement proxy for MCP with human-in-the-loop.
- [agent-auth](https://github.com/kanoniv/agent-auth) - Cryptographic identity and delegation for AI agents.
- [agentdnai](https://github.com/smouj/agentdnai) - Verifiable digital identity, scoped permissions, and audit trails for AI agents.
- [AgentLair](https://github.com/piiiico/agentlair) - Per-session Ed25519-signed JWT (AAT) for AI agent identity. JWKS endpoint, audit trail, and behavioral trust signals. MIT licensed.
- [AGNTCY Identity](https://github.com/agntcy/identity) - Linux Foundation project. Onboard, create, and verify identities for Agents, MCP Servers, and multi-agent systems.
- [Alibaba Open Agent Auth](https://github.com/alibaba/open-agent-auth) - Enterprise framework implementing Agent Operation Authorization protocol with cryptographic identity binding and fine-grained permission verification.
- [ASI](https://github.com/hazennik/asi) - Minimal cryptographic identity standard for agent skill ecosystems. Ed25519 + DID:key + JCS bundling.
- [HelixID](https://github.com/dgverse-labs/helixid) - Open-source identity and authorization layer for AI agents. Issue verifiable credentials, manage decentralized identifiers.
- [OrgKernel](https://github.com/MetapriseAI/OrgKernel) - Open-source trust layer for AI agents. Cryptographic agent identity (Ed25519), instance-scoped execution tokens, SHA-256 integrity verification.
- [Ratify Protocol](https://github.com/identities-ai/ratify-protocol) - Open cryptographic trust protocol for AI agent authorization. Hybrid Ed25519 + ML-DSA-65 (FIPS 204).
- [W3C Decentralized Identifiers (DIDs)](https://www.w3.org/TR/did-core/) - The foundation. Globally unique, self-sovereign identifiers controlled by the subject.
- [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model-2.0/) - Cryptographically signed, tamper-evident, machine-verifiable credentials.

---

## Agent Governance & Policy Enforcement

Frameworks for governing autonomous agent behavior — policy enforcement, zero-trust, execution sandboxing, approval gates.

- [AegisSwarm-Core](https://github.com/sunilgentyala/AegisSwarm-Core) - Zero-trust security and governance framework for autonomous multi-agent AI networks. Implements CSA Agentic Trust Framework.
- [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) - Microsoft's toolkit for AI agent governance. Policy enforcement, zero-trust identity, execution sandboxing, and reliability engineering.
- [Agentic Trust Framework](https://github.com/massivescale-ai/agentic-trust-framework) - Open specification for Zero Trust governance of autonomous AI agents. Five core elements, four maturity levels.
- [Agentoes](https://github.com/DAMONBLUE2021/Agentoes) - Enterprise AI trust platform for safe deployment and management of AI agents.
- [Clyro](https://github.com/getclyro/clyro) - Governance platform that applies policies and controls to AI agent actions before execution.
- [cordum](https://github.com/cordum-io/cordum) - Open agent control plane. Govern autonomous AI agents with pre-execution policy enforcement, approval gates, and audit.
- [cullis](https://github.com/cullis-security/cullis) - Zero-trust governance for autonomous AI agents in regulated organizations. Self-hosted gateway with verified identity.
- [DashClaw](https://github.com/ucsandman/DashClaw) - Governance runtime for AI agents. Intercept actions, enforce guard policies, require approvals, produce audit trails.
- [defenseclaw](https://github.com/cisco-ai-defense/defenseclaw) - Cisco's security governance for agentic AI.
- [Deterministic Agent Control Protocol](https://github.com/elliot35/deterministic-agent-control-protocol) - Governance gateway for AI agents. Bounded, auditable, session-aware control with MCP proxy.
- [faramesh-core](https://github.com/faramesh/faramesh-core) - Governance-as-Code for AI agents. Declarative constraints with deterministic enforcement.
- [Hermes Katana](https://github.com/claudlos/hermes-katana) - Defense-in-depth security toolkit for LLM agents. Taint tracking, proxy secret guard, policy engine, and red-team benchmark.
- [Lelu](https://github.com/Lelu-ai/lelu) - Open-source authorization engine for AI agents. Confidence-aware gating, human-in-the-loop, and policy enforcement.
- [lunar.dev](https://github.com/TheLunarCompany/lunar) - Agent-native MCP Gateway for governance and security.
- [pattern8](https://github.com/Aquifer-sea/pattern8) - AI Agent Governance Framework. Constrain how AI agents behave in your project. `pip install pattern8`.
- [Preventra](https://github.com/Preventra/preventra) - Governance, trust, and identity for the agentic economy. Public infrastructure.
- [superagentX](https://github.com/superagentxai/superagentx) - Policy-driven autonomous AI agents. Unified Control Plane with centralized tools, identity, and governance.
- [veldt-kya](https://github.com/veldtlabs/veldt-kya) - KYA (Know Your Agents). Open-source trust, governance, and evidentiary assurance for autonomous systems.
- [YYLO](https://github.com/yylo-dev/yylo) - Coding-agent orchestrator with isolated task worktrees, validation receipts, and guarded Git integration.

---

## Agent Permissions & Authorization

Fine-grained authorization, delegation, and permission systems for agent tool execution.

- [ActionWarrant](https://github.com/selfradiance/actionwarrant) - Local CLI for verifying signed, scoped permission artifacts before agent actions.
- [agent-passport](https://github.com/priyansh-x/agent-passport) - Authorization for AI agents. Scoped permissions, spend limits, delegation chains, instant revocation. Ed25519-signed.
- [agentlock](https://github.com/webpro255/agentlock) - Adversarially benchmarked pre-action agent authorization. Framework-agnostic tool permissions.
- [ampersona](https://github.com/joyshmitz/ampersona) - Rust platform for AI agent governance: identity (psychology, voice, capabilities) + authority (scoped actions, deny-by-default).
- [Emilia Protocol](https://github.com/emiliaprotocol/emilia-protocol) - Offline-verifiable authorization-receipt protocol for controlling irreversible agent actions.
- [grantex](https://github.com/mishrasanjeev/grantex) - Identity, authorization, and audit infrastructure for AI agents.
- [Jean-Claw-Van-Damme](https://github.com/agenticpoa/jean-claw-van-damme) - Authorization gatekeeper for OpenClaw agents. Scoped grants, time-bound permissions, skill scanning.
- [permguard](https://github.com/permguard/permguard) - Authorization engine for today's systems and tomorrow's agentic world.
- [permitrail](https://github.com/chokonaira/permitrail) - Open-source permission and audit layer for AI agents that take real actions.
- [Pi Permission System](https://github.com/MasuRii/pi-permission-system) - Permission enforcement extension for the Pi coding agent.
- [spicebox](https://github.com/authzed/spicebox) - Fine-grained permissions for AI coding agents (by AuthZed / SpiceDB).
- [theauth](https://github.com/glincker/theauth) - Auth for AI agents and humans. First-class agent identity, MCP, OAuth 2.1, delegation, audit.

---

## Trust Registries & Verification

Public registries, trust scoring, signed receipts, and verifiable attestation.

- [agentattest](https://github.com/AuroraAeon/agentattest) - Verifiable provenance for AI coding agents. Binds agent runs, diffs, PRs, artifacts, and approvals into attestations.
- [AgentGuard](https://github.com/GoPlusSecurity/agentguard) - Security guard for AI agents. Blocks malicious skills, prevents data leaks, protects secrets. 24 detection rules.
- [agentregistry](https://github.com/agentregistry-dev/agentregistry) - Centralized, curated registry for AI agent skills.
- [ai-trust](https://github.com/opena2a-org/ai-trust) - Package scanner that reports a 0–100 trust score through `ai-trust check <pkg>`.
- [Attestix](https://github.com/VibeTensor/attestix) - Attestation infrastructure for AI agents. DID-based agent identity, W3C Verifiable Credentials, EU AI Act compliance.
- [attestplane](https://github.com/attestplane/attestplane) - Verifiable audit substrate designed to support AI-agent record-keeping requirements.
- [bootproof](https://github.com/bootproof/bootproof) - Zero-trust supervisor that boots any repository or agent artifact to a verifiable, known-good state.
- [halo-record](https://github.com/bkuan001/halo-record) - Tamper-evident runtime records for AI agents. Hash-chained, dependency-free, verifiable by anyone.
- [hvtracker](https://github.com/YugantM/hvtracker) - AI Agent Trust Registry. Independent, evidence-based trust scores for 172+ open-source AI agents.
- [kairon-protocol](https://github.com/berkay-aktas/kairon-protocol) - Attestation protocol for AI coding agents. Turns completed tasks into verifiable receipts.
- [logpose](https://github.com/logpose-dev/logpose) - Verifiable reputation + attestation SDK for AI agents.
- [mimir](https://github.com/enchanter-ai/mimir) - Verifiable provenance for MCP tool-call results. Signed envelopes + quality scoring.
- [Open Agent Trust Registry](https://github.com/FransDevelopment/open-agent-trust-registry) - Open root-of-trust for agent identity. Public, federated registry of trusted attestation issuers.
- [provetrail](https://github.com/ionalpha/provetrail) - Open standard for verifiable execution provenance. Portable, third-party-verifiable records.
- [ToolTrust Directory](https://github.com/AgentSafe-AI/tooltrust-directory) - Trust layer for AI agents. Curated registry of secure tools and MCP servers with A-F risk grading.
- [treeship](https://github.com/zerkerlabs/treeship) - Portable trust receipts for agent workflows. Signed, chained, verifiable.
- [Verifiable ClawGuard](https://github.com/SaharaLabsAI/Verifiable-ClawGuard) - Use TEE attestation to prove an agent is running behind known guardrails.

---

## Agent Reputation & Scoring

Credit-score-style reputation systems and trust scoring for agents.

- [AgenticTrust](https://github.com/Dylan-Xu410/AgenticTrust) - Decentralized reputation, scoring, and discovery infrastructure for AI agents.
- [djd-agent-score](https://github.com/jacobsd32-cpu/djd-agent-score) - Reputation scoring for AI agent wallets on Base.
- [mnemopay-sdk](https://github.com/mnemopay/mnemopay-sdk) - Trust & reputation layer for AI agents. Agent Credit Score (300-850) + Merkle-anchored ledger.
- [nobulex](https://github.com/arian-gogani/nobulex) - Trust economy for autonomous AI agents. Credit scores for machines. Agents earn Trust Capital through verified behavior.
- [repute](https://github.com/martintopalov/repute) - Open-source reputation scoring for AI agents using Ethereum Attestation Service and Base.

---

## Audit Trails & Observability

Immutable audit logs, hash-chained event records, session replay, and observability infrastructure.

- [agent-witness](https://github.com/rioX432/agent-witness) - Session recorder and audit log for AI coding agents. Replay Claude Code sessions as TUI timeline.
- [agentlens](https://github.com/agentkitai/agentlens) - Open-source observability and audit trail platform for AI agents. MCP-native, tamper-evident event logging.
- [clawlens](https://github.com/nk3750/clawlens) - Agent observability and guardrails for OpenClaw. Risk scoring, audit trails, dashboard.
- [DecisionNotary](https://github.com/AgnesDevita/DecisionNotary) - Decentralized decision-notary bridging AI observability with on-chain identity.
- [deconvolute](https://github.com/deconvolute-labs/deconvolute) - Policy-as-code enforcement and observability for MCP tool calls. Cryptographic integrity chains.
- [forgesight](https://github.com/Scaffoldic/forgesight) - Vendor-neutral, OpenTelemetry-first telemetry for AI agents. Traces, cost, budgets, audit trails.
- [notmemory](https://github.com/notmemory/notmemory) - Tamper-proof agent memory with audit trails, rollback, GDPR tombstoning, and semantic search.
- [soma](https://github.com/radotsvetkov/soma) - Local-first AI agent governance with verifiable, tamper-evident audit trails.
- [SoulGuard](https://github.com/saluca-labs/soulguard) - Open trust layer for AI-agent memory. Tamper-evident memory and cryptographic agent identity.
- [trailing](https://github.com/trailingai/trailing) - Immutable audit trails for AI agents. Compliance-ready logging for Claude Code, Codex, Cursor, CrewAI.
- [trishula-agent-telemetry](https://github.com/TrishulaSoftware/trishula-agent-telemetry) - Deterministic agent observability. Merkle-chained audit trails. Anomaly detection. Zero dependencies.
- [vaara](https://github.com/vaaraio/vaara) - Open-source evidence layer for AI governance. Gates every agent tool call against your policies with verifiable receipts.
- [YYLO Benchmark](https://github.com/yylo-dev/yylo-benchmark) - Benchmark harness that runs every coding-agent attempt in a dedicated fresh repository and retains one hash-verified evidence chain linking the plan, attempt, workspace receipt, post-execution repository manifest, terminal, and evaluation IDs, with recovery, doctor, and report failing closed unless the complete chain verifies.

---

## Security & Scanning

Security toolkits, vulnerability scanning, skill vetting, and supply chain security.

- [agent-bom](https://github.com/msaad00/agent-bom) - AI supply-chain and cloud security scanner. Self-hosted control plane for agents, MCP, and packages.
- [agentseal](https://github.com/getagentseal/agentseal) - Security toolkit for AI agents. Scan for dangerous skills and MCP configs, monitor supply chain attacks.
- [AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) - Full-stack AI Red Teaming platform. Agent Security Scan, supply chain verification, and prompt security for AI ecosystems.
- [awesome-skills-security](https://github.com/Eyadkelleh/awesome-skills-security) - Security testing toolkit for AI agents. Curated SecLists wordlists, injection payloads, and expert agents for authorized security testing.
- [ClawGuard](https://github.com/NY1024/ClawGuard) - Comprehensive security toolkit for autonomous agents (OpenClaw, Claude Code, Cursor).
- [clawguard (yourclaw)](https://github.com/yourclaw/clawguard) - Security scanning and trust registry for AI agent skills (Clawdbot, MoltBot, OpenClaw, ClawHub).
- [hackagent](https://github.com/AISecurityLab/hackagent) - Open-source security toolkit to detect vulnerabilities in your AI agents.
- [hackmyagent](https://github.com/opena2a-org/hackmyagent) - Security testing toolkit for scanning AI agents and MCP servers and exercising known attack techniques.
- [MindJack](https://github.com/7h30th3r0n3/MindJack) - Security toolkit that extracts agent memories and rewrites instructions. Red-teaming tool.
- [ops0 CLI](https://github.com/ops0-ai/ops0-cli) - Cloud infrastructure-plan scanner and governance CLI for agent-generated infrastructure as code.
- [SecOpsAgentKit](https://github.com/AgentSecOps/SecOpsAgentKit) - Security operations toolkit for AI coding agents. 25+ skills for vulnerability detection, container scanning.
- [skillfortify](https://github.com/qualixar/skillfortify) - Security scanner for AI agent skills and plugins. Static analysis, supply chain vulnerability detection.

---

## Skills Curation & Trusted Marketplaces

Curated registries, security-audited marketplaces, and vetted skill catalogs for AI agents.

- [Agent Skill Exchange](https://github.com/agentskillexchange/skills) - Curated, trusted open catalog of AI agent skills for OpenClaw, Claude Code, Codex, GitHub Copilot, Gemini, Cursor, MCP.
- [AI Skill Store](https://github.com/aiskillstore/marketplace) - Marketplace of security-reviewed skills for Claude, Codex, and Claude Code.
- [Awesome Claude (HeyClaude)](https://github.com/JSONbored/awesome-claude) - Curated registry and distribution surface for Claude and AI-workflow assets: agents, skills, MCP servers.
- [awesome-agent-skills](https://github.com/linny006/awesome-agent-skills) - Curated, auto-updated awesome-list of vetted AI agent skills with quality ratings.
- [Binance Skills Hub](https://github.com/binance/binance-skills-hub) - Open skills marketplace giving AI agents native access to crypto exchange capabilities through curated, verified skills.
- [Claude Code Plugins Plus](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) - Open-source marketplace. 425 plugins, 2,810 skills, 200 agents for Claude Code.
- [Claude Code Skills](https://github.com/daymade/claude-code-skills) - Marketplace of Claude Code skills for development workflows.
- [Mercury Agent Skills](https://github.com/cosmicstack-labs/mercury-agent-skills) - Curated registry of reusable agent skills for Mercury Agent, OpenClaw, and Hermes Agent.
- [n-skills](https://github.com/numman-ali/n-skills) - Curated plugin marketplace for AI agents, compatible with Claude Code, Codex, and OpenClaw.
- [PM Skills](https://github.com/phuryn/pm-skills) - Marketplace for agentic skills, commands, and plugins focused on project management and development workflows.
- [Trail of Bits Curated Skills](https://github.com/trailofbits/skills-curated) - Curated, community-vetted Claude Code plugin marketplace from the respected security firm.
- [x-cmd/skill](https://github.com/x-cmd/skill) - Human-vetted, community-curated skills for AI coding and agent tools.

---

## Standards, Specifications & Foundations

Open standards and specifications, including work hosted by foundations and
community-led efforts. Inclusion does not imply endorsement or foundation
affiliation unless the entry explicitly says so.

- [AAIF Agent Card MCP](https://github.com/CSOAI-ORG/meok-aaif-agent-card-mcp) - Linux Foundation AAIF Agent Card MCP. Publish `/.well-known/agent-card`, bridge A2A and OASF.
- [Agentic AI Foundation](https://github.com/api-evangelist/agentic-ai-foundation) - Community repository tracking the Agentic AI Foundation ecosystem.
- [CapiscIO RFCs](https://github.com/capiscio/capiscio-rfcs) - Request for Comments for CapiscIO protocols and standards. AGCP, trust policies, agent identity.
- [OASF Agent Directory MCP](https://github.com/CSOAI-ORG/oasf-agent-directory-mcp) - Cisco AGNTCY bridge under Linux Foundation for the OASF Agent Directory.

---

## Agent-to-Agent Protocols

Protocols for inter-agent communication, trust networks, and agent economies.

- [A2A .NET](https://github.com/neuroglia-io/a2a-net) - .NET implementation of the A2A protocol for secure, interoperable agent communication.
- [A2A Go](https://github.com/go-a2a/a2a-go) - Go implementation of the A2A protocol for agent interoperability.
- [A2A Rust](https://github.com/tomtom215/a2a-rust) - Type-safe, async Rust SDK for the Agent2Agent (A2A) protocol.
- [Agent Identity Protocol (AIP) draft](https://github.com/originlayer/agent-identity-protocol) - Concept draft of AIP. Governance layer for autonomous agents covering identity, permissions, audit.
- [Agent2Agent (A2A)](https://github.com/a2aproject/A2A) - Google's open protocol enabling communication and interoperability between agentic applications. 24,600+★.
- [Agentic Commerce Protocol (ACP)](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol) - Open standard for connecting AI agents with commerce infrastructure — payments, orders, and product discovery.
- [AINRP](https://github.com/Ineedsomuchhelp/AINRP) - AI Identity and Non-Repudiation Protocol for trusted autonomous agents. Smart contracts, architecture, tokenomics.
- [ClawNet](https://github.com/hkgai-official/ClawNet) - Governed multi-agent social network. Every AI agent acts under human-granted identity and scoped authorization.
- [dos-kernel](https://github.com/anthony-chaudhary/dos-kernel) - Catch AI agents when they lie about what they shipped. Verifies claims against git.
- [EEP](https://github.com/eep-dev/EEP) - Open standard for push-based, verifiable communication between digital entities and agents.
- [Fides Protocol](https://github.com/edwang2006/fides_protocol) - Trust layer for AI agents. Every tool call is intercepted, verified, and authorized.
- [Graphenium](https://github.com/lambda-alpha-labs/Graphenium) - Trust and verification layer for AI-generated code changes.
- [HITL Protocol](https://github.com/rotorstar/hitl-protocol) - Human-in-the-Loop Protocol for autonomous agent services. Open standard (v0.8).
- [Kinetic Trust Protocol](https://github.com/nmcitra/ktp-rfc) - Dynamic, physics-based authorization of autonomous agents.
- [MoveGate Protocol](https://github.com/hamzzaaamalik/movegate-contracts) - Agent Identity, Authorization, and Trust Infrastructure for Sui. On-chain mandate delegation.
- [Oath Protocol](https://github.com/oath-protocol/oath-protocol) - Protocol for cryptographically verifiable human intent. Agent authorization, local-first, offline-capable.
- [Python A2A](https://github.com/themanojdesai/python-a2a) - Python library for implementing Google's Agent-to-Agent (A2A) protocol.
- [sati](https://github.com/cascade-protocol/sati) - Trust infrastructure for million-agent economies on Solana. Identity, reputation, validation.
- [swarm-hedera](https://github.com/SwarmProtocol-fun/swarm-hedera) - Agent identity, HCS messaging, staking, governance, NFTs, trust verification on Hedera.

---

## Attestation & Confidential Computing

TEE-backed attestation, confidential computing, and hardware-enforced security.

- [Confidential AI](https://github.com/confidential-dot-ai/home) - Confidential computing stack for AI workloads. Run inference, training, agents in hardware-encrypted environments.
- [Confidential Computing Expert Skill](https://github.com/vkobel/confidential-computing-expert-skill) - AI agent skill for confidential computing. TEE platforms, attestation protocols, KRAB verifiability.
- [QWED Verification](https://github.com/QWED-AI/qwed-verification) - Deterministic verification layer for AI systems. Verifies outputs using mathematics and symbolic reasoning.
- [TEE-backed Private Memory](https://github.com/Xucion/TEE-backed-Private-Memory-Layer-for-Agents) - Private memory layer using Gramine SGX/RA-TLS for AI agents.

---

## Related Awesome Lists

- [Awesome A2A Agents](https://github.com/isekOS/awesome-a2a-agents) - Curated list of tools, frameworks, and projects built on the Agent-to-Agent (A2A) protocol.
- [Awesome AI Agent Protocols](https://github.com/LineageLabs/awesome-ai-agent-protocols) - Protocols, tools, and services for the AI agent infrastructure stack.
- [Awesome AI Agents Security](https://github.com/ProjectRecon/awesome-ai-agents-security) - Tools and resources for securing autonomous agents, including runtime protection, red-teaming, sandboxing, guardrails, and agent identity.
- [Awesome Machine Economy](https://github.com/azeth-protocol/awesome-machine-economy) - The machine economy ecosystem — agent payments, commerce, and finance.

---

## Contributing

See [contributing.md](contributing.md) for submission guidelines, format
requirements, and CI checks that run on every pull request.

- Thanks to [piico](https://github.com/piico) for contributing AgentLair.
- Thanks to [InsightFactoryAPP](https://github.com/InsightFactoryAPP) for contributing YYLO.

See [CRITERIA.md](CRITERIA.md) for the full inclusion criteria —
relevance domains, quality gates (star threshold, activity, description),
categorization rules, and exclusion policies. Validation CI blocks missing,
archived, or unverifiable repositories and reports other quality signals for
human review.

[![CC0 1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the curator has waived all copyright and related or neighboring rights to this work.
