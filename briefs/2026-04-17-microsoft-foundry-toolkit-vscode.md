# Microsoft Foundry Toolkit for VS Code

**Date:** 2026-04-17
**Source:** https://techcommunity.microsoft.com/blog/azuredevcommunityblog/microsoft-foundry-toolkit-for-vs-code-is-now-generally-available/4511831
**Verdict:** watch
**Category:** ai_platform
**Relevance Score:** 6

## What is it?

Microsoft Foundry Toolkit for VS Code (formerly "AI Toolkit") reached General Availability on April 16, 2026. It is a VS Code extension that provides an end-to-end AI development environment — from model experimentation to production agent deployment — without leaving the editor. The GA release also unifies what was previously two separate extensions (AI Toolkit + Microsoft Foundry sidebar) into a single sidebar experience; the standalone Foundry sidebar is being retired June 1, 2026.

The toolkit ships with five main capability pillars: a **Model Playground** with 100+ models from Microsoft Foundry, GitHub, OpenAI, Anthropic, Ollama, and others; a **no-code/low-code Agent Builder** for defining instructions and wiring up tools; **GitHub Copilot–powered agent scaffolding** via the open-source `microsoft-foundry` skill; an **Agent Inspector** with F5 debugging, breakpoints, and real-time workflow visualization; and one-click **deployment to Microsoft Foundry Agent Service** with pytest-based evaluation in VS Code Test Explorer.

A **Tool Catalog** is the centerpiece of the MCP story — a centralized UI for discovering, configuring, and managing tools from the public Foundry catalog and local stdio MCP servers, with auto or manual approval controls for each tool invocation.

## Why it matters (or doesn't)

This is Microsoft's direct answer to Claude Code for agent development and it lives squarely inside Abonmarche's primary enterprise ecosystem. A few specific angles worth noting:

**Platform strategy signal.** Garrick is actively building the business case for Claude Enterprise vs. M365 Copilot. Foundry Toolkit is the clearest indication yet that Microsoft is treating VS Code + Foundry as a full Claude Code competitor. Understanding its capabilities first-hand strengthens the comparison — especially since the toolkit supports Anthropic models (Claude Opus 4.6 is listed in the model picker), meaning it's not strictly an either/or.

**MCP overlap.** The Tool Catalog's ability to discover and connect local stdio MCP servers is directly relevant to Garrick's MCP server work (CostEstDB, plan review automation). However, Garrick is already building and consuming MCP servers natively in Claude Code — Foundry Toolkit doesn't add capability here, it just wraps it in a different UI with a Microsoft logo.

**Agent Builder for CoP demos.** The no-code Agent Builder path (design agent → define instructions → add MCP tools → one-click deploy) could be a compelling demo surface for the AI Community of Practice, particularly for non-developer staff who need to build lightweight agents without touching Python.

**Key tension:** Garrick's primary dev tool is Claude Code. Foundry Toolkit is Claude Code's Microsoft-ecosystem counterpart. For *his* day-to-day development — CostEstDB, ArcPy automation, Claude MCP servers — Claude Code remains the stronger fit. Foundry Toolkit's value is in understanding and demonstrating the Microsoft AI platform to internal stakeholders.

## Technical details

- **Free to install** from the VS Code Marketplace; Azure subscription required for Foundry-hosted deployments and remote model access. Local/Ollama models are free.
- **Models supported:** 100+ including GPT-4.1, Claude Opus 4.6, Phi Silica (edge-optimized), Gemini, Llama, Mistral, and Ollama local models. Side-by-side comparison with production-ready code export.
- **MCP:** Local stdio MCP servers connectable via Tool Catalog; cloud-hosted MCP at `mcp.ai.azure.com` (Foundry MCP Server, preview, Entra auth included). Tool approval is configurable: auto or manual.
- **Agent Inspector:** Real-time workflow visualization, breakpoints, step-through execution, variable inspection, streaming-response visibility — comparable to what Claude Code offers via native debugging but scoped to Foundry agent patterns.
- **Evaluation:** pytest-based agent evaluations runnable inside VS Code Test Explorer and scalable to Microsoft Foundry for CI-style evaluation pipelines.
- **Phi/edge support:** Fine-tune Phi Silica on custom data, quantize for NPU/GPU targets — relevant only if Garrick ever pursues on-device/edge AI deployments, which is not a current priority.
- **Hosted agents** currently deploy to North Central US only (as of March 2026) — a potential data residency consideration for municipal clients.
- **Maturity concern:** The Agent Inspector has documented extension-host hang issues in pre-GA releases (VSMagazine, March 2026). The GA release may have resolved these, but warrants verification.
- **GitHub:** https://github.com/microsoft/vscode-ai-toolkit

## Recommendation

**Watch** — don't prioritize a deep dive, but do install it and run through the 3-minute getting started tutorial once. The specific things to watch for over the next 1–3 months:

1. **MCP Tool Catalog maturity** — if local MCP server management in the Tool Catalog becomes stable and significantly easier than the Claude Code equivalent, it becomes a strong CoP teaching tool.
2. **Hosted agent region expansion** — if Foundry Agent Service expands beyond North Central US, the one-click local→cloud deployment story becomes more compelling for Abonmarche's Azure-hosted workloads.
3. **Claude Enterprise evaluation** — when presenting the Claude vs. M365 Copilot comparison, showing that Foundry Toolkit *already supports Claude models* weakens the "we have to choose one" framing and may reframe the conversation toward a platform-agnostic agent strategy.

Don't swap Claude Code for Foundry Toolkit — they're complementary at this stage. But being fluent in both strengthens Garrick's position as the person who understands the full Microsoft + Anthropic landscape at Abonmarche.
