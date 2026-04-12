# Claude Skills: Dynamic Context Injection via `!`command`` Syntax

**Date:** 2026-04-12
**Source:** https://code.claude.com/docs/en/skills#inject-dynamic-context
**Verdict:** try_it
**Category:** dev_tools
**Relevance Score:** 9

## What is it?

Dynamic Context Injection (DCI) is an advanced pattern within Claude Code's Skills system that lets you embed shell commands directly inside a `SKILL.md` file using the `` !`<command>` `` syntax. When a skill is invoked, every such placeholder executes as a shell command *before* the prompt is sent to Claude — the command's output replaces the placeholder in-place. Claude only ever sees the final, rendered text with real data substituted in; it never sees the command itself.

The result is what practitioners are calling "context pipelines": instead of manually copy-pasting a PR diff, a set of failing tests, or a database schema into each prompt, you define those data sources once in a skill file and they auto-refresh on every invocation. For multi-line command blocks, a fenced ` ```! ` block handles the same job. The feature is part of Claude Code's extension of the open Agent Skills standard and sits alongside other advanced patterns like `context: fork` subagent isolation and invocation-control frontmatter.

Security and governance controls are baked in: organizations can set `"disableSkillShellExecution": true` in managed settings to block DCI for user/project/plugin skills enterprise-wide, replacing each command with `[shell command execution disabled by policy]`. The `shell` frontmatter field also lets Windows shops switch from `bash` to `powershell` for skill-level command execution.

## Why it matters (or doesn't)

This feature directly elevates how Garrick can use Claude Code across nearly every active workstream:

- **CostEstDB:** A skill could inject live `pg_dump` schema snapshots, recent vector-search query logs, or VoyageAI embedding call results into diagnostic or documentation prompts — eliminating repetitive manual context setup when iterating on the database.
- **Plan Review Automation:** A `/plan-review` skill could inject the current PDF-extracted diff, checklist status from SharePoint, and relevant LGIM schema fields before Claude sees the prompt — turning a conversational workflow into a repeatable, data-fresh pipeline.
- **GitHub/Claude Code workflows:** The canonical PR summarization example (injecting `gh pr diff`, `gh pr view --comments`, and `gh pr diff --name-only`) is immediately applicable to Garrick's Claude Code sessions for reviewing infrastructure code or ArcPy scripts.
- **ArcGIS & GIS workflows:** Skills could inject live `arcpy` metadata queries, layer schemas, or field inventory outputs to give Claude precise, current context about a geodatabase before writing Python toolbox code.
- **AI CoP demonstrations:** DCI is a compelling, concrete example to share with the CoP — it bridges "Claude as a chatbot" and "Claude as an automated system" without requiring MCP servers or Azure infrastructure.

The "computed skills" pattern emerging in the community (running a Python/shell script that reads system state and *generates* the prompt dynamically) is an especially powerful extension that aligns with Garrick's developer mindset.

## Technical details

- **Syntax:** Inline: `` !`command` ``; multi-line: fenced ` ```! ` block
- **Execution timing:** Preprocessing — commands run before Claude receives anything; Claude sees only output, never commands
- **Scope:** Works in both `.claude/skills/<name>/SKILL.md` (project) and `~/.claude/skills/<name>/SKILL.md` (personal/global)
- **Shell:** Defaults to `bash`; configurable to `powershell` via `shell:` frontmatter field (requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`)
- **Error handling:** `stderr` is included in output if a command fails; use `2>/dev/null || echo "fallback"` for graceful degradation
- **Environment variables:** Accessible via `` !`echo $VAR` `` or standard `$VAR` syntax inside commands; `${CLAUDE_SESSION_ID}` and `${CLAUDE_SKILL_DIR}` are built-in substitutions
- **Context window management:** Injected output counts against context; use `| head -N`, `| tail -N`, or `| jq '.path'` to trim large outputs
- **Enterprise policy:** `"disableSkillShellExecution": true` in managed settings blocks DCI org-wide; bundled and managed skills are exempt
- **Security posture:** Commands run with the local user's permissions — treat like any shell script; avoid hardcoded credentials, use env vars or `.env` files
- **Supply chain risk:** The broader Agent Skills ecosystem has been flagged by Snyk's ToxicSkills research (prompt injection found in 36% of tested community skills); always audit third-party SKILL.md files before installing
- **Stability:** Reported as stable in current Claude Code versions; earlier versions had intermittent bugs with the feature

## Recommendation

**Try it immediately.** The PR summarization example from the official docs is a five-minute proof of concept that delivers real value in Claude Code today. Concrete next steps:

1. **Build the canonical PR skill** — create `.claude/skills/pr-summary/SKILL.md` with `gh pr diff`, `gh pr view --comments`, and `gh pr diff --name-only` injections (exact template in official docs). Use this in the next Claude Code session that touches GitHub.
2. **Build a CostEstDB diagnostic skill** — inject `\d+ <table>` schema output and recent query logs so Claude always has current DB context when iterating on embeddings or cost line queries.
3. **Build a GIS context skill** — inject `arcpy.Describe()` or `arcpy.da.ListFields()` output for the active geodatabase/layer, eliminating the manual schema-paste step before writing ArcPy code.
4. **Demo for the CoP** — DCI is the clearest bridge between "Claude answers questions" and "Claude works with live data." A short demo of the PR or deployment-check skill pattern would land well with technical CoP members.
5. **Review security posture** — for any skills installed from external sources (GitHub, community repos), read `SKILL.md` and any bundled scripts before use; don't install community skills in projects that touch production databases without auditing them first.
