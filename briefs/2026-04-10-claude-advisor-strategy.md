# Claude Advisor Strategy (Advisor Tool)

**Date:** 2026-04-10
**Source:** https://claude.com/blog/the-advisor-strategy
**Verdict:** try_it
**Category:** ai_platform
**Relevance Score:** 9

## What is it?

Anthropic's Advisor Strategy is a server-side agent architecture pattern — now formalized as a first-class API feature — that pairs a smaller, cost-efficient **executor model** (Sonnet or Haiku) with a more powerful **advisor model** (Opus) that provides on-demand strategic guidance mid-generation. The executor runs the full task end-to-end: calling tools, reading results, and iterating toward a solution. When it hits a decision it can't confidently resolve, it calls the built-in `advisor` tool, which routes the full conversation transcript to Opus server-side. Opus reads everything, returns a concise plan or course correction (typically 400–700 text tokens), and the executor resumes — all within a single `/v1/messages` request.

This inverts the classic orchestrator-worker pattern. Rather than a large model decomposing tasks and delegating to smaller workers, a small model *drives* and *escalates* only when genuinely stuck. Frontier-level reasoning kicks in only where it's needed; everything else runs at executor-model cost. Enabling it is a one-line change: add the beta header `anthropic-beta: advisor-tool-2026-03-01` and declare `advisor_20260301` in the tools array.

Benchmarks from Anthropic show Sonnet 4.6 + Opus advisor achieved a **+2.7 percentage point improvement on SWE-bench Multilingual** over Sonnet alone, while **reducing cost per agentic task by 11.9%**. On BrowseComp, Haiku + Opus advisor more than doubled Haiku's solo score (41.2% vs. 19.7%), at 85% lower cost than Sonnet solo. Early adopters (Bolt, Genspark, Eve Legal) report meaningful gains in agent trajectory quality and structured document extraction tasks at 5× lower cost.

## Why it matters (or doesn't)

This is directly relevant to CostEstDB and every other agentic workflow Garrick is building or evaluating. The CostEstDB MCP integration already calls Claude for cost estimate lookups, embeddings, and document generation — those multi-step agentic chains are exactly the "long-horizon workloads where most turns are mechanical but having an excellent plan is crucial" that the advisor tool is designed for.

Specific applications at Abonmarche:
- **CostEstDB agents**: Cost estimation tasks involve ambiguous scope interpretation, unit reconciliation, and complex PostgreSQL/pgvector query planning. Sonnet can handle the mechanical retrieval; Opus can advise on ambiguous estimating decisions.
- **Plan review automation**: Document parsing is repetitive and cheap on Sonnet; legal/code-compliance interpretation is exactly the kind of hard decision worth escalating to Opus.
- **Crash report processing**: Routine field extraction on Haiku, complex inference on edge cases escalated to Opus.
- **Claude Code sessions**: The community is already asking for this in Claude Code's plan mode — once it lands there, it directly improves the quality of architecture sessions Garrick uses for infrastructure code.

The cost angle is significant for the Claude Enterprise vs. M365 Copilot business case Garrick is building: demonstrating that near-Opus intelligence is achievable at Sonnet-level cost strengthens the argument for API-first Claude deployments over fixed-seat licensing.

## Technical details

- **API**: Available now in **public beta** on the Claude Platform (Anthropic direct API). Beta header: `anthropic-beta: advisor-tool-2026-03-01`
- **Supported pairs**: Haiku 4.5 or Sonnet 4.6 as executor; Opus 4.6 as advisor. More combinations may follow.
- **Invocation**: Declared as a tool (`type: "advisor_20260301"`); the executor decides when to call it autonomously.
- **Cost model**: Advisor tokens billed at Opus rates; executor tokens at Sonnet/Haiku rates. Advisor output is small (~400–700 tokens), so blended cost stays well below full Opus.
- **`max_uses`**: Optional per-request cap on advisor calls. Advisor usage reported separately in `usage.iterations[]` for cost tracking.
- **Prompt caching**: Enable `caching: {type: "ephemeral"}` on the tool definition for conversations with 3+ advisor calls — breaks even at 3 calls, improves from there.
- **Streaming**: Advisor sub-inference does not stream; expect a pause while Opus runs. SSE keepalive pings continue during the pause.
- **Compatibility**: Composes freely with web search, code execution, and custom tools in the same loop.
- **Limitations**: No built-in conversation-level advisor call cap (must track client-side); `max_tokens` does not bound advisor tokens; Priority Tier must be set on the advisor model separately.
- **Not yet available in Claude Code** (community requests exist; watch for a future release).

## Recommendation

**Test this immediately on the CostEstDB agent.** The setup cost is minimal — add one beta header and one tool definition to an existing Messages API call — and the cost-vs-quality trade-off is already validated by Anthropic's benchmarks and real customer testimonials.

Concrete next steps:
1. Add `advisor_20260301` (Opus 4.6 advisor) to the existing CostEstDB Claude API calls that handle ambiguous estimate interpretation or multi-step query planning.
2. Run Anthropic's suggested eval recipe: compare Sonnet solo, Sonnet + Opus advisor, and Opus solo on a representative set of cost estimation queries. Capture token costs from `usage.iterations[]`.
3. Apply the suggested coding system prompt from the docs if using the advisor in Claude Code-style agentic loops.
4. Use the cost data to strengthen the Claude Enterprise business case — quantified Opus-quality-at-Sonnet-cost numbers are compelling for leadership.
5. Share findings at the AI CoP as a concrete example of intelligent model tiering — this is a pattern the whole team can apply.
