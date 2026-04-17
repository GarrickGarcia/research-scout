# Power Apps: Copilot Embedding, App Skills & MCP Server for Agents

**Date:** 2026-04-15
**Source:** https://www.microsoft.com/en-us/power-platform/blog/2026/04/15/making-business-apps-smarter-with-ai-copilot-and-agents-in-power-apps/?ocid=FY26_Blog_X_041526_1
**Verdict:** try_it
**Category:** automation
**Relevance Score:** 7

## What is it?

Microsoft announced a cluster of generally-available (or near-GA) AI upgrades for Power Apps, centered on three interlocking capabilities. First, **Microsoft 365 Copilot is now embedded directly inside Power Apps** — GA in model-driven apps today, public preview for canvas apps — bringing natural-language search, auto-fill from documents/emails, and AI-generated record summaries within the security and permission model the app already enforces.

Second, **new app skills** (data entry, exploration, visualization, summarization) are now GA, and those skills are being exposed externally via a **Power Apps MCP Server** (preview now, GA May 4, 2026). This lets any Copilot Studio agent — or external MCP client — call Power Apps capabilities as structured tools: `invoke_data_entry` (extract structured data from emails/PDFs/docs and populate Dataverse forms), `request_assistance` (async human handoff), and `log_for_review` (passive oversight log). The MCP server is configured in Copilot Studio and callable by any agent via natural-language instructions.

Third, the **agent feed** (GA May 2026) gives business users a dedicated in-app panel to supervise agent activity: side-by-side comparison of AI suggestions vs. original source content, approve/reject controls, and deep links to Dataverse records. Makers configure the approval threshold — low-risk actions complete silently; higher-impact actions surface as explicit approvals.

## Why it matters (or doesn't)

Several threads here connect directly to Garrick's current work:

**Plan review & crash report automation**: The `invoke_data_entry` MCP tool does exactly what plan review automation needs — it takes unstructured inputs (PDFs, Word docs, emails) and extracts structured field values into a form, with a human reviewer approving before any record is committed. The agent feed's side-by-side layout mirrors the workflow Garrick would want: AI proposes, human verifies. This is a Microsoft-native alternative to building the same pipeline from scratch with Claude + custom MCP + PostgreSQL.

**Claude Enterprise vs. M365 Copilot strategy**: This announcement materially strengthens the M365 Copilot case. Copilot is now *inside* Power Apps — the tool most Abonmarche staff already use for low-code apps — not just in Teams/Outlook. If staff are already in a model-driven app, they now get Copilot assistance without switching context. That's a meaningful argument for the M365 licensing path.

**MCP ecosystem awareness**: The Power Apps MCP Server represents Microsoft's own answer to MCP-native agentic workflows. Understanding its tool surface (`invoke_data_entry`, `request_assistance`, `log_for_review`) informs how Garrick designs CostEstDB's own MCP server — especially the human-in-the-loop pattern, which is directly transferable.

The main caveat: these capabilities require **Dataverse** as the backing data store. CostEstDB runs on PostgreSQL, so the `invoke_data_entry` path isn't a drop-in for that project. Model-driven apps need Dataverse tables. This limits direct applicability to new workflows built on the Power Platform stack rather than retrofitting existing PostgreSQL-backed work.

## Technical details

- **M365 Copilot in model-driven apps**: GA now; requires M365 Copilot license; admin enables at tenant level, maker configures per-app.
- **M365 Copilot in canvas apps**: Public preview.
- **App skills (data entry, exploration, visualization, summarization)**: GA now.
- **Power Apps MCP Server**: Preview now; GA targeted May 4, 2026. Configured in Copilot Studio. Three tools: `log_for_review`, `request_assistance`, `invoke_data_entry`.
- **`invoke_data_entry`**: Supports .pdf, .xlsx, .docx, .jpeg, .jpg, .png, .gif, .bmp input formats. Populates single-line text (None format), Whole number, and Decimal Dataverse column types. Learns from corrections made in agent canvas (feedback loop).
- **Agent feed**: GA May 2026 in model-driven apps. Human-in-the-loop via async `request_assistance` tool; Copilot Studio agent waits for human completion before proceeding.
- **Pricing**: Tied to existing Power Apps and M365 Copilot licensing — no new separate SKU announced.
- **Maturity**: Core features GA; MCP server and agent feed still classified as preview features with supplemental terms.

## Recommendation

Two concrete next steps:

1. **Test `invoke_data_entry` for plan review**: Set up a Copilot Studio agent connected to the Power Apps MCP Server targeting a Dataverse table that mirrors a plan review checklist or crash report schema. Feed it a PDF submittal and walk through the agent feed approval flow. This directly validates — or rules out — the M365-native path for document-to-structured-data workflows before committing to a custom Claude + PostgreSQL pipeline.

2. **Use this announcement in the Claude vs. M365 Copilot business case deck**: The embedding of Copilot inside Power Apps (with model-driven app GA now) is a materially new capability since any previous evaluation. Document it as a capability delta that needs to be weighed against Claude Enterprise's flexibility and CostEstDB's PostgreSQL architecture. The agent feed's human-in-the-loop pattern is a useful design reference regardless of which platform wins.

Watch the [Business Applications Update event](https://aka.ms/PPCSBAUReg) linked in the blog — it includes demos of apps + agents + Copilot working together that would be directly useful for CoP presentations.
