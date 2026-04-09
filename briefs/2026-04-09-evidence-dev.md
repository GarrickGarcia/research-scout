# Evidence — Business Intelligence as Code

**Date:** 2026-04-09
**Source:** https://evidence.dev
**Verdict:** try_it
**Category:** dev_tools
**Relevance Score:** 7

## What is it?

<cite index="15-1">Evidence is an open source framework for building data products with SQL — things like reports, decision-support tools, and embedded dashboards. It's a code-driven alternative to drag-and-drop BI tools.</cite> Instead of clicking through a GUI, <cite index="2-2">you build polished reports with SQL, markdown, and a suite of AI development tools in a powerful browser-based IDE. You write clean, readable SQL and markdown that's easy to understand and maintain, with real-time validation, automatic suggestions for components and SQL queries, and version control support using the same tools software engineers use.</cite>

<cite index="22-2">SQL statements inside markdown files run queries against your data sources, charts and components are rendered using those query results, and templated pages can generate many pages from a single markdown template with loops and conditionals for dynamic control over what is displayed.</cite> The hosted platform, Evidence Studio, adds an Evidence Query Engine — <cite index="2-1">high-performance data infrastructure with enterprise security and automatic scaling, capable of querying billions of rows in milliseconds with columnar storage and vectorized execution and multi-level caching with automatic query optimization.</cite>

The project has strong community traction: <cite index="2-3">Evidence is built on the solid foundations of its open source framework for building data products, with a growing community of data analysts, developers, and data enthusiasts.</cite> The GitHub repo has ~5.8k stars and 17k weekly npm downloads.

## Why it matters (or doesn't)

The most direct connection to Garrick's work is **CostEstDB**. <cite index="13-1">Evidence supports connecting to PostgreSQL as a data source, allowing you to query data using SQL.</cite> That means Evidence could plug directly into the Azure-hosted PostgreSQL database backing CostEstDB and generate publication-quality, interactive cost estimating reports — versioned in Git alongside the rest of the codebase, no Power BI license required for the dev team.

<cite index="7-4,7-5">Evidence is recommended as one of the best "as-code" BI tools, with Git-based workflow support</cite> — a significant advantage over drag-and-drop tools when reports need to be reviewed, audited, and rolled back like any other code artifact. This aligns directly with the engineering culture Garrick is building on the Digital Solutions team.

For the **AI CoP**, Evidence's built-in AI dev agent — <cite index="17-1">which can look up documentation, check your schema, debug errors, and write Evidence markdown</cite> — is a useful demo case for AI-assisted development workflows. The tool also supports Azure AD as an identity provider, which maps neatly onto Abonmarche's Microsoft-centric enterprise backbone.

The main caveat: Abonmarche already has Power BI in the Microsoft 365 stack, and most non-technical staff expect that interface. Evidence is developer-centric and requires SQL knowledge, so its sweet spot is the Digital Solutions team producing polished technical reports (cost estimates, infrastructure summaries, crash report outputs), not firm-wide self-service BI.

## Technical details

- **Open source framework:** MIT-licensed, self-hostable via Node.js / npm
- **Cloud hosting:** Evidence Studio (evidence.studio) — <cite index="2-2">powerful browser-based IDE with real-time syntax validation</cite>
- **Pricing:** <cite index="2-2">Team plan at $15/user/month; Pro plan at $25/user/month (adds SSO, SCIM, private Slack support and more AI credits)</cite>; Enterprise tier available with white-labeling and embedded analytics
- **Data sources:** <cite index="14-2">Supports BigQuery, Snowflake, Redshift, PostgreSQL, Timescale, Trino</cite>, plus DuckDB, MySQL, SQL Server, SQLite, MotherDuck, and CSV files
- **Security:** SOC 2 Type II certified; row-level security; Azure AD / SAML / OIDC SSO on Pro+
- **Maturity:** Active development, ~5.8k GitHub stars, used by Apple, IDC, and the City of Philadelphia among others
- **Limitation:** <cite index="11-3">Changes to dashboards are made in code, which is a strength for developer teams but raises the barrier to entry for non-technical users</cite> compared to drag-and-drop tools like Power BI

## Recommendation

Run a local proof-of-concept connecting Evidence to CostEstDB's PostgreSQL instance. The zero-cost local setup (open source, npm-based) means this is a low-risk experiment. Specifically:

1. `npm create evidence-app@latest` and point the PostgreSQL connector at CostEstDB (dev/staging)
2. Build one cost estimating summary report — line items, unit costs, totals — as an Evidence markdown page
3. Evaluate whether the SQL + markdown authoring model fits the team's workflow better than Power BI for technical deliverables
4. If promising, assess the $15/user/month Team plan for small-team deployment with Azure AD login

This is most valuable as a **developer reporting layer for CostEstDB**, not a replacement for firm-wide Power BI. If the POC shows Evidence reports can be embedded in client deliverables or SharePoint, the case for adoption gets significantly stronger.
