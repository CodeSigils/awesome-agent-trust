# Awesome Agent Trust & Identity [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of open-source projects, protocols, and standards for AI agent identity, naming, trust verification, governance, and security.

*Inspired by the [ANS (Agent Name Service)](https://github.com/agentnameservice) ecosystem and Linux Foundation standards efforts.*

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
- [Linux Foundation & Standards](#linux-foundation--standards)
- [Agent-to-Agent Protocols](#agent-to-agent-protocols)
- [Attestation & Confidential Computing](#attestation--confidential-computing)
- [Related Awesome Lists](#related-awesome-lists)

---

## Agent Naming & Discovery

DNS-like resolution for AI agents. Core protocol with IETF draft backing.

- [Agent Name Service](https://github.com/agentnameservice/ans) - Reference implementation of the ANS protocol. Registry, transparency log, and IETF draft `draft-narajala-ans-00`.
- [ANS Registry](https://github.com/agentnameservice/ans-registry) - Registration and resolution for the Agent Name Service.
- [Agent Name Service (OWASP)](https://github.com/ruvnet/Agent-Name-Service) - ANS Protocol introduced by the OWASP GenAI Security Project. Foundational framework for agent identity.
- [ANS SDK for Rust](https://github.com/agentnameservice/ans-sdk-rust) - Rust SDK for the Agent Name Service.
- [ANS SDK for Go](https://github.com/agentnameservice/ans-sdk-go) - Go SDK for the Agent Name Service.
- [ANS SDK for Java](https://github.com/agentnameservice/ans-sdk-java) - Java SDK for the Agent Name Service.
- [route-ans](https://github.com/route-ans/route-ans) - High-performance ANS resolver with semantic versioning and Redis caching.
- [ERC-8004 Registry](https://eips.ethereum.org/EIPS/eip-8004) - On-chain searchable agent identity registry. Agents register as NFTs with queryable capability metadata.
- [A2A Agent Cards](https://google.github.io/A2A/) - JSON metadata at `/.well-known/agent-card.json`. Agents self-describe capabilities and authentication requirements.

---

## Agent Identity & Cryptographic Identity

Cryptographic identity for agents — DIDs, Ed25519, zero-trust frameworks.

- [AGNTCY Identity](https://github.com/agntcy/identity) - Linux Foundation project. Onboard, create, and verify identities for Agents, MCP Servers, and multi-agent systems.
- [OrgKernel](https://github.com/MetapriseAI/OrgKernel) - Open-source trust layer for AI agents. Cryptographic agent identity (Ed25519), instance-scoped execution tokens, SHA-256 integrity verification.
- [Vorim Agent Identity Protocol (VAIP)](https://github.com/Vorim-AI-Labs/vorim-protocol) - Open standard for AI agent identity, permissions, and cryptographic audit trails.
- [Alibaba Open Agent Auth](https://github.com/alibaba/open-agent-auth) - Enterprise framework implementing Agent Operation Authorization protocol with cryptographic identity binding and fine-grained permission verification.
- [Agent Identity Protocol (AIP)](https://github.com/openagentidentityprotocol/agentidentityprotocol) - Zero-trust security layer for AI agents. Policy enforcement proxy for MCP with human-in-the-loop.
- [ASI](https://github.com/hazennik/asi) - Minimal cryptographic identity standard for agent skill ecosystems. Ed25519 + DID:key + JCS bundling.
- [agent-auth](https://github.com/kanoniv/agent-auth) - Cryptographic identity and delegation for AI agents.
- [Ratify Protocol](https://github.com/identities-ai/ratify-protocol) - Open cryptographic trust protocol for AI agent authorization. Hybrid Ed25519 + ML-DSA-65 (FIPS 204).
- [HelixID](https://github.com/dgverse-labs/helixid) - Open-source identity and authorization layer for AI agents. Issue verifiable credentials, manage decentralized identifiers.
- [agentdnai](https://github.com/smouj/agentdnai) - Verifiable digital identity, scoped permissions, and audit trails for AI agents.
- [W3C Decentralized Identifiers (DIDs)](https://www.w3.org/TR/did-core/) - The foundation. Globally unique, self-sovereign identifiers controlled by the subject.
- [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model-2.0/) - Cryptographically signed, tamper-evident, machine-verifiable credentials.

---

## Agent Governance & Policy Enforcement

Frameworks for governing autonomous agent behavior — policy enforcement, zero-trust, execution sandboxing, approval gates.

- [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) - Microsoft's toolkit for AI agent governance. Policy enforcement, zero-trust identity, execution sandboxing, and reliability engineering.
- [defenseclaw](https://github.com/cisco-ai-defense/defenseclaw) - Cisco's security governance for agentic AI.
- [cordum](https://github.com/cordum-io/cordum) - Open agent control plane. Govern autonomous AI agents with pre-execution policy enforcement, approval gates, and audit.
- [lunar.dev](https://github.com/TheLunarCompany/lunar) - Agent-native MCP Gateway for governance and security.
- [DashClaw](https://github.com/ucsandman/DashClaw) - Governance runtime for AI agents. Intercept actions, enforce guard policies, require approvals, produce audit trails.
- [superagentX](https://github.com/superagentxai/superagentx) - Policy-driven autonomous AI agents. Unified Control Plane with centralized tools, identity, and governance.
- [faramesh-core](https://github.com/faramesh/faramesh-core) - Governance-as-Code for AI agents. Declarative constraints with deterministic enforcement.
- [Deterministic Agent Control Protocol](https://github.com/elliot35/deterministic-agent-control-protocol) - Governance gateway for AI agents. Bounded, auditable, session-aware control with MCP proxy.
- [Agentic Trust Framework](https://github.com/massivescale-ai/agentic-trust-framework) - Open specification for Zero Trust governance of autonomous AI agents. Five core elements, four maturity levels.
- [pattern8](https://github.com/Aquifer-sea/pattern8) - AI Agent Governance Framework. Constrain how AI agents behave in your project. `pip install pattern8`.
- [Clyro](https://github.com/getclyro/clyro) - Governance platform for AI agents. Stops failures before they happen.
- [Hermes Katana](https://github.com/claudlos/hermes-katana) - Defense-in-depth security toolkit for LLM agents. Taint tracking, proxy secret guard, policy engine, and red-team benchmark.
- [Agentoes](https://github.com/DAMONBLUE2021/Agentoes) - Enterprise AI trust platform for safe deployment and management of AI agents.
- [AegisSwarm-Core](https://github.com/sunilgentyala/AegisSwarm-Core) - Zero-trust security and governance framework for autonomous multi-agent AI networks. Implements CSA Agentic Trust Framework.
- [cullis](https://github.com/cullis-security/cullis) - Zero-trust governance for autonomous AI agents in regulated organizations. Self-hosted gateway with verified identity.
- [Preventra](https://github.com/Preventra/preventra) - Governance, trust, and identity for the agentic economy. Public infrastructure.
- [veldt-kya](https://github.com/veldtlabs/veldt-kya) - KYA (Know Your Agents). Open-source trust, governance, and evidentiary assurance for autonomous systems.

---

## Agent Permissions & Authorization

Fine-grained authorization, delegation, and permission systems for agent tool execution.

- [Pi Permission System](https://github.com/MasuRii/pi-permission-system) - Permission enforcement extension for the Pi coding agent.
- [permguard](https://github.com/permguard/permguard) - Authorization engine for today's systems and tomorrow's agentic world.
- [grantex](https://github.com/mishrasanjeev/grantex) - Identity, authorization, and audit infrastructure for AI agents. The "OAuth moment" for the agentic internet.
- [agentlock](https://github.com/webpro255/agentlock) - Adversarially benchmarked pre-action agent authorization. Framework-agnostic tool permissions.
- [theauth](https://github.com/glincker/theauth) - Auth for AI agents and humans. First-class agent identity, MCP, OAuth 2.1, delegation, audit.
- [spicebox](https://github.com/authzed/spicebox) - Fine-grained permissions for AI coding agents (by AuthZed / SpiceDB).
- [CapiscIO Agent Guard](https://github.com/capiscio/a2a-demos) - Trust badges, identity verification, and tool-level authorization for AI agents.
- [Jean-Claw-Van-Damme](https://github.com/agenticpoa/jean-claw-van-damme) - Authorization gatekeeper for OpenClaw agents. Scoped grants, time-bound permissions, skill scanning.
- [permitrail](https://github.com/chokonaira/permitrail) - Open-source permission and audit layer for AI agents that take real actions.
- [agent-passport](https://github.com/priyansh-x/agent-passport) - Authorization for AI agents. Scoped permissions, spend limits, delegation chains, instant revocation. Ed25519-signed.
- [ampersona](https://github.com/joyshmitz/ampersona) - Rust platform for AI agent governance: identity (psychology, voice, capabilities) + authority (scoped actions, deny-by-default).
- [ActionWarrant](https://github.com/selfradiance/actionwarrant) - Local CLI for verifying signed, scoped permission artifacts before agent actions.
- [Emilia Protocol](https://github.com/emiliaprotocol/emilia-protocol) - Receipt Required for AI agents. No receipt, no irreversible action. Offline-verifiable authorization-receipt protocol.

---

## Trust Registries & Verification

Public registries, trust scoring, signed receipts, and verifiable attestation.

- [AgentGuard](https://github.com/GoPlusSecurity/agentguard) - Security guard for AI agents. Blocks malicious skills, prevents data leaks, protects secrets. 24 detection rules.
- [agentregistry](https://github.com/agentregistry-dev/agentregistry) - Centralized, trusted, curated registry for AI agent skills.
- [Attestix](https://github.com/VibeTensor/attestix) - Attestation infrastructure for AI agents. DID-based agent identity, W3C Verifiable Credentials, EU AI Act compliance.
- [treeship](https://github.com/zerkerlabs/treeship) - Portable trust receipts for agent workflows. Signed, chained, verifiable.
- [Open Agent Trust Registry](https://github.com/FransDevelopment/open-agent-trust-registry) - Open root-of-trust for agent identity. Public, federated registry of trusted attestation issuers.
- [Verifiable ClawGuard](https://github.com/SaharaLabsAI/Verifiable-ClawGuard) - Use TEE attestation to prove an agent is running behind known guardrails.
- [hvtracker](https://github.com/YugantM/hvtracker) - AI Agent Trust Registry. Independent, evidence-based trust scores for 172+ open-source AI agents.
- [ToolTrust Directory](https://github.com/AgentSafe-AI/tooltrust-directory) - Trust layer for AI agents. Curated registry of secure tools and MCP servers with A-F risk grading.
- [ai-trust](https://github.com/opena2a-org/ai-trust) - VirusTotal for AI packages. `ai-trust check <pkg>` returns a 0-100 trust score.
- [attestplane](https://github.com/attestplane/attestplane) - Verifiable audit substrate for AI agents. EU AI Act Article 12 ready.
- [provetrail](https://github.com/ionalpha/provetrail) - Open standard for verifiable execution provenance. Portable, third-party-verifiable records.
- [halo-record](https://github.com/bkuan001/halo-record) - Tamper-evident runtime records for AI agents. Hash-chained, dependency-free, verifiable by anyone.
- [mimir](https://github.com/enchanter-ai/mimir) - Verifiable provenance for MCP tool-call results. Signed envelopes + quality scoring.
- [kairon-protocol](https://github.com/berkay-aktas/kairon-protocol) - Attestation protocol for AI coding agents. Turns completed tasks into verifiable receipts.
- [agentattest](https://github.com/AuroraAeon/agentattest) - Verifiable provenance for AI coding agents. Binds agent runs, diffs, PRs, artifacts, and approvals into attestations.
- [logpose](https://github.com/logpose-dev/logpose) - Verifiable reputation + attestation SDK for AI agents.

---

## Agent Reputation & Scoring

Credit-score-style reputation systems and trust scoring for agents.

- [nobulex](https://github.com/arian-gogani/nobulex) - Trust economy for autonomous AI agents. Credit scores for machines. Agents earn Trust Capital through verified behavior.
- [AgenticTrust](https://github.com/Dylan-Xu410/AgenticTrust) - Decentralized reputation, scoring, and discovery infrastructure for AI agents.
- [mnemopay-sdk](https://github.com/mnemopay/mnemopay-sdk) - Trust & reputation layer for AI agents. Agent Credit Score (300-850) + Merkle-anchored ledger.
- [djd-agent-score](https://github.com/jacobsd32-cpu/djd-agent-score) - Reputation scoring for AI agent wallets on Base.
- [repute](https://github.com/martintopalov/repute) - FICO score for AI agents. Open source reputation scoring on EAS + Base.

---

## Audit Trails & Observability

Immutable audit logs, hash-chained event records, session replay, and observability infrastructure.

- [clawlens](https://github.com/nk3750/clawlens) - Agent observability and guardrails for OpenClaw. Risk scoring, audit trails, dashboard.
- [agentlens](https://github.com/agentkitai/agentlens) - Open-source observability and audit trail platform for AI agents. MCP-native, tamper-evident event logging.
- [deconvolute](https://github.com/deconvolute-labs/deconvolute) - Policy-as-code enforcement and observability for MCP tool calls. Cryptographic integrity chains.
- [notmemory](https://github.com/notmemory/notmemory) - Tamper-proof agent memory with audit trails, rollback, GDPR tombstoning, and semantic search.
- [soma](https://github.com/radotsvetkov/soma) - Local-first AI agent governance with verifiable, tamper-evident audit trails.
- [trailing](https://github.com/trailingai/trailing) - Immutable audit trails for AI agents. Compliance-ready logging for Claude Code, Codex, Cursor, CrewAI.
- [agent-witness](https://github.com/rioX432/agent-witness) - Session recorder and audit log for AI coding agents. Replay Claude Code sessions as TUI timeline.
- [DecisionNotary](https://github.com/AgnesDevita/DecisionNotary) - Decentralized decision-notary bridging AI observability with on-chain identity.
- [forgesight](https://github.com/Scaffoldic/forgesight) - Vendor-neutral, OpenTelemetry-first telemetry for AI agents. Traces, cost, budgets, audit trails.
- [SoulGuard](https://github.com/saluca-labs/soulguard) - Open trust layer for AI-agent memory. Tamper-evident memory and cryptographic agent identity.
- [trishula-agent-telemetry](https://github.com/TrishulaSoftware/trishula-agent-telemetry) - Deterministic agent observability. Merkle-chained audit trails. Anomaly detection.

---

## Security & Scanning

Security toolkits, vulnerability scanning, skill vetting, and supply chain security.

- [awesome-skills-security](https://github.com/Eyadkelleh/awesome-skills-security) - Security testing toolkit for AI agents. Curated SecLists wordlists, injection payloads, and expert agents for authorized security testing.
- [hackagent](https://github.com/AISecurityLab/hackagent) - Open-source security toolkit to detect vulnerabilities in your AI agents.
- [SecOpsAgentKit](https://github.com/AgentSecOps/SecOpsAgentKit) - Security operations toolkit for AI coding agents. 25+ skills for vulnerability detection, container scanning.
- [hackmyagent](https://github.com/opena2a-org/hackmyagent) - Metasploit for AI agents. Scan, attack, and fix AI agents and MCP servers.
- [ClawGuard](https://github.com/NY1024/ClawGuard) - Comprehensive security toolkit for autonomous agents (OpenClaw, Claude Code, Cursor).
- [ops0 CLI](https://github.com/ops0-ai/ops0-cli) - Stop AI agents from shipping insecure IaC. Cloud plan scanning and governance.
- [agentseal](https://github.com/getagentseal/agentseal) - Security toolkit for AI agents. Scan for dangerous skills and MCP configs, monitor supply chain attacks.
- [MindJack](https://github.com/7h30th3r0n3/MindJack) - Security toolkit that extracts agent memories and rewrites instructions. Red-teaming tool.
- [clawguard (yourclaw)](https://github.com/yourclaw/clawguard) - Security scanning and trust registry for AI agent skills (Clawdbot, MoltBot, OpenClaw, ClawHub).

---

## Skills Curation & Trusted Marketplaces

Curated registries, security-audited marketplaces, and vetted skill catalogs for AI agents.

- [PM Skills](https://github.com/phuryn/pm-skills) - Marketplace for agentic skills, commands, and plugins focused on project management and development workflows.
- [Claude Code Plugins Plus](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) - Open-source marketplace. 425 plugins, 2,810 skills, 200 agents for Claude Code.
- [Claude Code Skills](https://github.com/daymade/claude-code-skills) - Professional Claude Code skills marketplace featuring production-ready skills for enhanced development workflows.
- [Binance Skills Hub](https://github.com/binance/binance-skills-hub) - Open skills marketplace giving AI agents native access to crypto exchange capabilities through curated, verified skills.
- [Trail of Bits Curated Skills](https://github.com/trailofbits/skills-curated) - Curated, community-vetted Claude Code plugin marketplace from the respected security firm.
- [AI Skill Store](https://github.com/aiskillstore/marketplace) - Security-audited skills for Claude, Codex, and Claude Code. One-click install, quality verified.
- [Mercury Agent Skills](https://github.com/cosmicstack-labs/mercury-agent-skills) - Curated registry of reusable agent skills for Mercury Agent, OpenClaw, and Hermes Agent.
- [Awesome Claude (HeyClaude)](https://github.com/JSONbored/awesome-claude) - Curated registry and distribution surface for Claude and AI-workflow assets: agents, skills, MCP servers.
- [x-cmd/skill](https://github.com/x-cmd/skill) - Human-vetted, community-curated skills for AI coding and agent tools.
- [Agent Skill Exchange](https://github.com/agentskillexchange/skills) - Curated, trusted open catalog of AI agent skills for OpenClaw, Claude Code, Codex, GitHub Copilot, Gemini, Cursor, MCP.
- [awesome-agent-skills](https://github.com/linny006/awesome-agent-skills) - Curated, auto-updated awesome-list of vetted AI agent skills with quality ratings.
- [n-skills](https://github.com/numman-ali/n-skills) - Curated plugin marketplace for AI agents, compatible with Claude Code, Codex, and OpenClaw.

---

## Linux Foundation & Standards

Officially recognized standards efforts under Linux Foundation, OASF, AAIF, AGNTCY.

- [OASF Agent Directory MCP](https://github.com/CSOAI-ORG/oasf-agent-directory-mcp) - Cisco AGNTCY bridge under Linux Foundation for the OASF Agent Directory.
- [AAIF Agent Card MCP](https://github.com/CSOAI-ORG/meok-aaif-agent-card-mcp) - Linux Foundation AAIF Agent Card MCP. Publish `/.well-known/agent-card`, bridge A2A and OASF.
- [ServiceNow A2A Sample](https://github.com/ServiceNow/sn-a2a) - Sample client for Linux Foundation A2A (Agent-to-Agent) protocol.
- [Agentic AI Foundation](https://github.com/api-evangelist/agentic-ai-foundation) - LF Agentic AI Foundation (AAIF), formed December 2025.
- [CapiscIO RFCs](https://github.com/capiscio/capiscio-rfcs) - Request for Comments for CapiscIO protocols and standards. AGCP, trust policies, agent identity.

---

## Agent-to-Agent Protocols

Protocols for inter-agent communication, trust networks, and agent economies.

- [ClawNet](https://github.com/hkgai-official/ClawNet) - Governed multi-agent social network. Every AI agent acts under human-granted identity and scoped authorization.
- [sati](https://github.com/cascade-protocol/sati) - Trust infrastructure for million-agent economies on Solana. Identity, reputation, validation.
- [neus/network](https://github.com/neus/network) - Open trust network for apps, people, and AI agents.
- [dos-kernel](https://github.com/anthony-chaudhary/dos-kernel) - Catch AI agents when they lie about what they shipped. Verifies claims against git.
- [Graphenium](https://github.com/lambda-alpha-labs/Graphenium) - Trust and verification layer for AI-generated code changes.
- [AgentVault](https://github.com/SecureAgentTools/AgentVault) - Open-source toolkit (Python, Registry API, CLI) for secure, decentralized AI agent interoperability using A2A/MCP.
- [Kinetic Trust Protocol](https://github.com/nmcitra/ktp-rfc) - Dynamic, physics-based authorization of autonomous agents.
- [MoveGate Protocol](https://github.com/hamzzaaamalik/movegate-contracts) - Agent Identity, Authorization, and Trust Infrastructure for Sui. On-chain mandate delegation.
- [Oath Protocol](https://github.com/oath-protocol/oath-protocol) - Protocol for cryptographically verifiable human intent. Agent authorization, local-first, offline-capable.
- [swarm-hedera](https://github.com/SwarmProtocol-fun/swarm-hedera) - Agent identity, HCS messaging, staking, governance, NFTs, trust verification on Hedera.
- [Agent Identity Protocol (AIP) draft](https://github.com/originlayer/agent-identity-protocol) - Concept draft of AIP. Governance layer for autonomous agents covering identity, permissions, audit.
- [AINRP](https://github.com/Ineedsomuchhelp/AINRP) - AI Identity and Non-Repudiation Protocol for trusted autonomous agents. Smart contracts, architecture, tokenomics.
- [Fides Protocol](https://github.com/edwang2006/fides_protocol) - Trust layer for AI agents. Every tool call is intercepted, verified, and authorized.

---

## Attestation & Confidential Computing

TEE-backed attestation, confidential computing, and hardware-enforced security.

- [Confidential AI](https://github.com/confidential-dot-ai/home) - Confidential computing stack for AI workloads. Run inference, training, agents in hardware-encrypted environments.
- [QWED Verification](https://github.com/QWED-AI/qwed-verification) - Deterministic verification layer for AI systems. Verifies outputs using mathematics and symbolic reasoning.
- [Azure Trust Agents](https://github.com/microsoft/azure-trust-agents) - Hands-on hackathon challenges for building multi-agent financial compliance workflows with Azure confidential computing.
- [Confidential Computing Expert Skill](https://github.com/vkobel/confidential-computing-expert-skill) - AI agent skill for confidential computing. TEE platforms, attestation protocols, KRAB verifiability.
- [TEE-backed Private Memory](https://github.com/Xucion/TEE-backed-Private-Memory-Layer-for-Agents) - Private memory layer using Gramine SGX/RA-TLS for AI agents.

---

## Related Awesome Lists

- [Awesome AI Agent Protocols](https://github.com/LineageLabs/awesome-ai-agent-protocols) - Protocols, tools, and services for the AI agent infrastructure stack.
- [Awesome Machine Economy](https://github.com/azeth-protocol/awesome-machine-economy) - The machine economy ecosystem — agent payments, commerce, and finance.

---

## Contributing

See [contributing.md](contributing.md) for guidelines.

[![CC0 1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the curator has waived all copyright and related or neighboring rights to this work.
