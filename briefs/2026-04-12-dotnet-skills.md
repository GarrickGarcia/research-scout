# dotnet-skills

**Date:** 2026-04-12
**Source:** https://github.com/managedcode/dotnet-skills
**Verdict:** watch
**Category:** dev_tools
**Relevance Score:** 6

## What is it?

`dotnet-skills` is a community-maintained, installable .NET skill catalog and CLI (`dotnet tool install --global dotnet-skills`) that gives AI coding agents — Claude Code, GitHub Copilot, Gemini, and Codex — accurate, up-to-date knowledge of modern .NET patterns and APIs. The core problem it solves: AI agents frequently generate outdated .NET code (EF6 patterns in .NET 8 projects, `Startup.cs` in Minimal API projects, mixing Blazor Server and Blazor WASM concepts). Installing a skill drops a structured `SKILL.md` into the agent's context path (`~/.claude/agents/` for Claude Code), ensuring the model references current best practices rather than stale training data.

The catalog currently contains **64 skills** spanning Core, Web, Cloud, Distributed, Data, AI, Legacy, Testing, Code Quality, Architecture, and Metrics categories. Notable AI-relevant skills include `dotnet-mcp` (MCP C# SDK), `dotnet-microsoft-agent-framework`, `dotnet-microsoft-extensions-ai`, `dotnet-semantic-kernel`, and `dotnet-azure-functions`. Skills are versioned (auto-published daily at 04:00 UTC via GitHub Actions), community-contributed, and tracked against upstream library release streams.

There is also an **orchestration agents layer** — top-level agents (`dotnet-router`, `dotnet-build`, `dotnet-data`, `dotnet-ai`, `dotnet-modernization`, `dotnet-review`) that route Claude Code into the right skill-scoped specialists. The `dotnet-ai` agent covers Semantic Kernel, Microsoft Agent Framework, MCP, and ML.NET in a single entry point.

## Why it matters (or doesn't)

Garrick's most directly applicable intersection is his **Azure Functions work** and **MCP server development**. If those are written in C#, Claude Code would benefit immediately from `dotnet-azure-functions` (isolated worker model, bindings, Durable Functions patterns) and `dotnet-mcp` (MCP C# SDK, Streamable HTTP, capability negotiation). Both are areas where AI agents are known to produce subtly wrong patterns — wrong execution model, incorrect DI setup, stale binding syntax.

The `dotnet-microsoft-extensions-ai` and `dotnet-microsoft-agent-framework` skills are also worth attention given Garrick's Microsoft AI ecosystem evaluations. If Claude Code is being used to prototype or scaffold Microsoft AI components, these skills would prevent the agent from defaulting to outdated Semantic Kernel patterns.

The main caveat: Garrick's stack leans Python-heavy (ArcGIS API for Python, pgvector Python clients, ArcPy). If Azure Functions and MCP servers at Abonmarche are primarily Python rather than C#, the entire catalog is irrelevant. This tool only adds value when Claude Code is generating or reviewing C# code.

## Technical details

- **Install:** `dotnet tool install --global dotnet-skills` (NuGet package, MIT license)
- **Requires:** .NET 10+ SDK
- **Cost:** Free and open source
- **Maturity:** 57 GitHub stars, 6 forks, 5 contributors, 11 releases — early but active; latest catalog release March 18, 2026
- **Agent support:** Claude Code (`~/.claude/agents/` global or `.claude/agents/` project), Copilot, Gemini, Codex — with `--agent` flag to target a specific platform
- **Key CLI commands:** `dotnet skills install <skill>`, `dotnet skills recommend` (scans `.csproj` files and suggests relevant skills), `dotnet skills update`, `dotnet skills agent install dotnet-router --auto`
- **Limitations:** Only covers .NET/C# — no Python, TypeScript, or ArcPy skills exist or are planned. Skill quality is community-driven and varies. The orchestration agent layer is new and not well-tested at scale.

## Recommendation

**Watch** — don't act now, but keep this in mind. The value unlock is specifically "Claude Code generating C# code." If Garrick or his team is writing Azure Functions, MCP servers, or any C# services with Claude Code, run `dotnet skills install dotnet-azure-functions dotnet-mcp dotnet-microsoft-extensions-ai` and immediately get better code generation with minimal setup cost.

**Concrete trigger to act:** If any CoP member or team is using Claude Code for C# development and complaining about outdated patterns (EF6, legacy middleware, wrong Azure Functions model), this is a one-liner fix. Also worth watching — the `dotnet-ai` orchestration agent could be a useful reference pattern for how Garrick structures Claude Code skill routing in non-.NET contexts (the agent-routing architecture is transferable).
