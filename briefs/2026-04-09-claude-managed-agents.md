# Claude Managed Agents

**Date:** 2026-04-09
**Source:** https://claude.ai/blog/claude-managed-agents
**Verdict:** try_it
**Category:** ai_platform
**Relevance Score:** 9

## What is it?

Claude Managed Agents is Anthropic's hosted infrastructure service for building and deploying production-grade AI agents at scale. Launched April 8, 2026 in public beta on the Claude Platform, it provides a full-stack agent harness — sandboxed code execution, session checkpointing, credential management, scoped permissions, and end-to-end tracing — so that teams can define *what* their agents do without engineering the runtime themselves. Agents can be defined in natural language or via YAML, connect to external services through MCP servers, and run autonomously for multiple hours in the cloud.

The architecture is built around three decoupled abstractions: the **session** (an append-only, durable event log that lives outside the context window), the **harness** (the loop that calls Claude and routes tool calls), and the **sandbox** (the execution environment). This separation means harness or sandbox failures are recoverable without data loss, and Claude's credentials are never exposed inside the sandbox — a structural security improvement over monolithic container designs. Internally, Anthropic reports this architecture cut p50 time-to-first-token by ~60% and p95 by over 90%.

Some features remain in limited research preview: advanced memory tooling, multi-agent orchestration (one agent spawning sub-agents), and self-evaluation/iteration loops. Early enterprise adopters include Notion, Rakuten, and Asana.

## Why it matters (or doesn't)

This is a direct hit on the infrastructure gap blocking Abonmarche's current AI work. The CostEstDB project is already wired into Claude via MCP — Managed Agents is the natural next layer for turning those MCP connections into durable, long-running agent workflows rather than one-shot API calls. Specifically:

- **CostEstDB agents**: Cost estimating workflows that query pgvector, fetch comparable projects, draft estimates, and loop back for validation are exactly the multi-step, long-horizon tasks this service is designed for. The MCP connector support means existing integrations plug in directly.
- **Plan review & crash report automation**: Multi-stage document processing pipelines (ingest → classify → extract → draft → review) are ideal candidates. The session log's `getEvents()` interface means mid-run checkpoints survive failures — critical for workflows that touch sensitive municipal data.
- **Claude Enterprise strategy**: Garrick is actively building the business case for Claude across Abonmarche. Managed Agents provides the enterprise governance story (scoped permissions, identity management, execution tracking) that justifies broader org adoption beyond individual power users.
- **AI CoP demos**: The ability to stand up an agent from a YAML file or natural language prompt is a compelling demo vehicle for the Community of Practice — showing non-technical stakeholders what "AI doing work" actually looks like in production.

The MCP-first integration model is the key differentiator vs. rolling custom Azure Functions orchestration. Since Garrick is already building MCP servers, the ramp-up cost here is low.

## Technical details

- **Access**: Public beta on the Claude Platform (platform.claude.com). Docs at `platform.claude.com/docs/en/managed-agents/overview`.
- **Pricing**: Standard Anthropic API token pricing + **$0.08/session-hour** of active runtime (idle time not billed) + $10/1,000 web searches. Community feedback flags this as enterprise-tier pricing; likely cost-justified for production workflows but not casual experimentation.
- **MCP integration**: Third-party service connections are handled natively via MCP servers with OAuth tokens stored in a secure vault — the harness never sees credentials directly.
- **Session durability**: Append-only event log; harness crashes are recoverable via `wake(sessionId)`. Context window overflow is handled by `getEvents()` slicing, not destructive compaction.
- **Research preview features**: Multi-agent orchestration (agent spawning sub-agents), advanced memory tooling, self-evaluation loops.
- **Performance**: Internal benchmarks show 10-point improvement in structured file generation over standard prompting. Notion, Rakuten, and Asana are production users.
- **Limitations**: Community notes about Claude reliability/downtime under load are a real concern for production SLAs. The service is Anthropic-hosted only — no self-hosted option, which may matter for sensitive municipal data residency requirements.

## Recommendation

**Try it.** The infrastructure it replaces — session management, sandboxing, credential vaulting, MCP orchestration — maps precisely to the gaps between Garrick's current Claude prototype work and production deployment.

Concrete next steps:
1. **Spin up a sandbox test** using the CostEstDB MCP server as the tool backend. Define a cost estimate workflow in YAML and run a few end-to-end sessions to validate latency and session recovery.
2. **Audit data residency requirements** for Abonmarche before moving any municipal infrastructure data through Anthropic's hosted sandbox. Confirm whether the Azure-hosted pgvector backend can be called from Managed Agents sessions without violating any data agreements.
3. **Watch the research-preview features** — multi-agent orchestration is the unlock for parallel plan-review workflows (one orchestrator agent, multiple specialized sub-agents per discipline). Sign up for the preview waitlist now.
4. **Build a CoP demo**: A live Managed Agents walkthrough — defining an agent in natural language and watching it execute a multi-step task — is a high-impact artifact for the Claude Enterprise business case presentation.
