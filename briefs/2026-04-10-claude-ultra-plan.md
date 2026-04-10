# Claude "Ultra Plan": Ultraplan Feature + Leaked Ultra Subscription Tier

**Date:** 2026-04-10
**Source:** https://code.claude.com/docs/en/ultraplan
**Verdict:** try_it
**Category:** ai_platform
**Relevance Score:** 8

## What is it?

"Claude Ultra Plan" actually refers to two distinct but related things in the Claude ecosystem right now, and it's worth understanding both.

**Ultraplan (shipped feature in Claude Code v2.1.91+):** This is a cloud-based planning tool activated with the `/ultraplan` command inside Claude Code. When invoked, it hands off a planning task from your local CLI to a Claude Code on the web session running in plan mode. Claude drafts the plan in the cloud while your terminal stays free. When ready, you open it in a browser to review it with inline comments, emoji reactions, and section-level feedback — then choose to execute it remotely (with auto PR creation) or send it back to your terminal. It supports three modes: Simple Plan (mirrors local), Visual Plan (adds Mermaid/ASCII diagrams), and Deep Plan (multi-subagent analysis including risk assessment and architecture review).

**Ultra Subscription Tier (leaked, not yet official):** On April 2, 2026, researchers decompiling Claude Code's public npm package discovered references to an unreleased "Ultra" subscription tier above the current Max plan (~$100/month). Anthropic has not confirmed this publicly. The leaked references suggest it's aimed at power users hitting Max plan limits — specifically those running long-horizon agentic workflows or multi-agent Coordinator mode (also leaked). No pricing has been announced.

## Why it matters (or doesn't)

Garrick is already invested in Claude Code as his primary agentic development environment. The `/ultraplan` feature directly upgrades one of the most friction-heavy parts of agentic coding: planning complex, multi-file or multi-system changes. For tasks like CostEstDB schema migrations, ArcPy refactors, or Azure Function deployments, Ultraplan's Deep Plan mode — which uses sub-agents for risk assessment and architecture review — is precisely the kind of structured analysis that currently requires manual back-and-forth in the terminal.

The cloud execution path (approve plan → auto-PR on GitHub) is particularly relevant for the Digital Solutions team's workflows where code review and version control are part of the delivery chain.

The leaked Ultra subscription tier matters for Garrick's AI platform strategy work. If it ships, it would likely unlock multi-agent Coordinator mode and AutoDream (background autonomous execution) — both of which are directly relevant to scaling CostEstDB agents and plan review automation beyond what a single Claude Code session can handle today. The pricing signal also affects the Claude Enterprise vs. M365 Copilot business case: a higher-tier individual developer seat may cost-justify itself quickly against the productivity gains from autonomous multi-agent coding.

## Technical details

- **Ultraplan status:** Research preview, requires Claude Code v2.1.91+
- **Activation:** `/ultraplan [prompt]`, keyword in a normal prompt, or escalate from a local plan dialog
- **Requires:** Claude Code on the web account + GitHub repository
- **Not available on:** Amazon Bedrock, Google Cloud Vertex AI, Microsoft Foundry (cloud-only; runs on Anthropic infra)
- **Plan modes:** Simple (local-equivalent), Visual (diagrams), Deep (multi-subagent with risk/architecture analysis)
- **Review interface:** Inline comments, emoji reactions, outline sidebar; supports iterative revisions before execution
- **Execution options:** Run on the web (auto-PR), teleport back to terminal (inject into session, start fresh, or save to file)
- **Ultra subscription tier:** Unconfirmed, leaked via Claude Code npm package decompilation (April 2, 2026); no pricing announced; expected to sit above Max ($100/month); likely tied to Coordinator mode and AutoDream features also found in the leak
- **Concurrent features (leaked, unshipped):** Coordinator Mode (multi-agent orchestration), AutoDream (background/scheduled execution), Chyros (unknown internal codename)
- **Limitation:** Ultraplan conflicts with Remote Control — only one can use the claude.ai/code interface at a time

## Recommendation

**Try it now:** If you're on Claude Code v2.1.91+, test `/ultraplan` on a real task — a CostEstDB schema change, an ArcPy workflow refactor, or an Azure Function deployment plan. The Deep Plan mode with sub-agent risk analysis is the highest-value entry point. The cloud-to-PR execution path is worth testing once for a non-critical change to understand the end-to-end flow.

**Watch the Ultra tier:** Monitor Anthropic's pricing page (claude.com/pricing) and official announcements. If/when Ultra ships with Coordinator mode, run an ROI calculation: compare Ultra's likely price against the productivity multiplier of parallel subagent execution across a typical sprint. Given that Garrick is already building the business case for Claude Enterprise, the Ultra tier's capabilities (autonomous multi-agent coding, background execution) may strengthen the internal argument significantly. Track the Ars Technica and MindStudio leak coverage for updates on confirmed ship dates.

**One constraint to flag:** Ultraplan is Anthropic-cloud-only — it won't work in a Bedrock or Azure-hosted Claude deployment. This is relevant if Abonmarche's eventual Claude Enterprise agreement routes through Azure (as Microsoft ecosystem alignment might suggest). Confirm the deployment path before planning Ultraplan into any team-facing workflows.
