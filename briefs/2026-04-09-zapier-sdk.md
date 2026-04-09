# Zapier SDK

**Date:** 2026-04-09
**Source:** https://zapier.com/sdk
**Verdict:** watch
**Category:** automation
**Relevance Score:** 5

## What is it?

The Zapier SDK is a TypeScript/Node.js library (`@zapier/zapier-sdk` on npm) that gives developers and AI agents programmatic access to Zapier's full integration catalog — 9,000+ apps, 30,000+ pre-built actions, and raw authenticated API calls to 3,000+ app APIs — all without writing OAuth flows, managing tokens, or handling rate limits. It launched in open beta in early 2026 (previously closed beta) and is currently free with no billing changes promised until further notice.

The SDK is distinct from Zapier MCP (which is aimed at AI chat interfaces like Claude Desktop or ChatGPT). The SDK targets production code and agent backends: you install via `npm`, run `npx zapier-sdk login` once to authenticate, and then call app actions in a few lines of TypeScript. It uses a type-safe, chainable API — e.g., `zapier.apps.slack({ connectionId }).write.direct_message({ inputs: { channel, text } })` — and handles token refresh, retries, and API quirks automatically. A CLI companion (`@zapier/zapier-sdk-cli`) lets you explore the app catalog interactively, generate TypeScript types, and run ad-hoc actions from the terminal.

A Triggers API (real-time event subscriptions in code, no polling) is on the roadmap targeting May 2026. An agent approval flow — where users review and approve agent actions before they execute — is also planned.

## Why it matters (or doesn't)

For Garrick's work, the most interesting angle is **AI agent tooling**. CostEstDB is already integrating Claude MCP, and Azure Functions are in use for automation. The SDK could serve as a single integration point for agents that need to reach across apps (Teams, SharePoint, Gmail, Outlook, calendar systems) without building a custom connector for each. For example, an agent inside Claude Code could call Zapier SDK to post a Teams notification or update a SharePoint list item without needing to manage Microsoft Graph OAuth.

That said, the fit is limited by three realities at Abonmarche:

1. **Power Automate already covers the M365 lane.** Teams, SharePoint, Outlook, and Planner integrations are natively handled by Power Automate, which is already licensed and in use. Zapier's M365 connectors are functional but not better than what's already there.
2. **Python dominates the GIS/ArcGIS stack.** The SDK is Node.js-only. ArcPy, the ArcGIS API for Python, and most of the geospatial tooling can't use it directly — it would require a separate Node.js service or sidecar process.
3. **Zapier MCP already covers the Claude AI interface angle.** Garrick is already exploring MCP-based integrations. The SDK is the production-code complement to MCP, but the use cases overlap significantly. Most of what the SDK adds over MCP is the ability to write loops, conditional logic, and chains in code — which Azure Functions or Claude Code already provide.

## Technical details

- **Package:** `@zapier/zapier-sdk` (npm), with CLI via `@zapier/zapier-sdk-cli`
- **Language:** TypeScript; full type generation for every app/action via `npx zapier-sdk add <app>`
- **Requirements:** Node.js 20+; existing Zapier account with connected apps
- **Auth:** Browser-based login (stores a local token), client credentials, or direct token — no per-app OAuth to build
- **Pricing:** Free during open beta. Post-beta pricing not yet announced; existing Zapier task quotas likely apply. Note: SDK actions will likely count against Zapier plan task limits.
- **Enterprise caveat:** Zapier MCP is not enabled by default on Enterprise plans (admin must request it). SDK access may face similar restrictions.
- **Maturity:** Open beta — API surface is still shifting, some docs noted as incomplete, feedback loop is active
- **Governance:** Org-level Zapier app/action restrictions apply automatically to SDK calls — enterprise policies are respected

## Recommendation

**Watch for 1-3 months.** The Zapier SDK is genuinely interesting for building AI agents that need to act across many apps without hand-rolling OAuth integrations. But at Abonmarche right now, the case to adopt it over existing tools is weak:

- Power Automate handles M365 automation without adding a new vendor
- Zapier MCP already connects Claude to the same 9,000+ apps for chat-based workflows
- The Python stack can't use the SDK directly
- Beta-stage pricing uncertainty is a real risk for an ops budget

**Revisit when:** (1) Triggers API ships (May 2026) — real-time event subscriptions in code are compelling for Azure Functions; (2) post-beta pricing is announced; (3) a specific project surfaces a need for non-M365 app integrations (e.g., a third-party SaaS that doesn't have a Power Automate connector) where the SDK's no-OAuth approach would save meaningful dev time. If you're already testing Zapier MCP, installing the SDK CLI to explore the catalog takes 5 minutes and is zero-cost.
