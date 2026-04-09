# Research Scout — Project Plan

## Summary

**Goal:** Build a low-friction automation pipeline where Garrick can drop a link or screenshot into a Teams channel, and an AI agent autonomously researches the topic, evaluates its relevance to current Abonmarche Digital Solutions work, produces a structured research brief, updates a running dashboard, and commits everything to a GitHub repository.

**Architecture:**

```
Teams Channel ("Research Inbox")
        │
        ▼
Power Automate (trigger on new message)
        │
        ▼
Azure Function (thin proxy — holds API key, forwards to Anthropic)
        │
        ▼
Claude Managed Agent (cloud-hosted, autonomous)
  ├── Web search + web fetch (research the topic)
  ├── Evaluate relevance to Abonmarche work context
  ├── Write markdown research brief
  ├── Update research_index.json
  ├── Regenerate dashboard.html
  └── Git push all files to GitHub repo
        │
        ▼
GitHub Repository (research-scout)
  ├── briefs/YYYY-MM-DD-topic-slug.md
  ├── research_index.json
  └── dashboard.html  ← static HTML, viewable via GitHub Pages
```

**Key design decisions:**

- **Azure Function as proxy** — keeps Anthropic API key out of Power Automate, provides flexibility for response handling
- **Managed Agent does the heavy lifting** — web research, relevance scoring, writing, and git push all happen inside the agent's cloud container
- **GitHub as storage** — version-controlled, diffable, serves the dashboard via GitHub Pages, no database needed
- **Static HTML dashboard** — the agent regenerates it on every run from `research_index.json`, zero backend
- **Fire-and-forget pattern** — Power Automate doesn't wait for the agent to finish; the agent works autonomously

**Future enhancements (not in v1):**

- Add the `docx` skill to produce branded Abonmarche research briefs
- Use the Managed Agents vault system to give the agent Graph API credentials for direct SharePoint write
- Add a second Power Automate flow triggered by GitHub push to produce branded docs and post to SharePoint
- Upload a custom Abonmarche brand skill to the Managed Agents API for consistent styling

---

## Prerequisites

Before starting, confirm you have:

- [ ] Anthropic API key with access to Claude Managed Agents beta
- [ ] Azure subscription (you already have this from CostEstDB)
- [ ] Azure CLI installed and authenticated
- [ ] GitHub account with a personal access token (PAT) that has `repo` scope
- [ ] Power Automate access (included in your M365 license)
- [ ] Claude Code installed and working
- [ ] Teams channel created for input (e.g., "Research Inbox" in your team)

---

## Step 1: Create the GitHub Repository

Create the repo that will hold all research output.

### 1.1 Create the repo

```bash
gh repo create research-scout --public --clone
cd research-scout
```

### 1.2 Create the initial structure

```bash
mkdir briefs
touch briefs/.gitkeep
```

### 1.3 Create the initial `research_index.json`

```json
{
  "last_updated": "2026-04-09T00:00:00Z",
  "entries": []
}
```

### 1.4 Create the initial `dashboard.html`

The Managed Agent will regenerate this on every run, but seed it with an empty state so the repo is functional from day one. Use the template structure from our conversation — Chart.js donut, metric cards, categorized card list reading from `research_index.json`. The agent will overwrite this with a fully populated version on its first run.

### 1.5 Enable GitHub Pages

Go to the repo Settings → Pages → Source: "Deploy from a branch" → Branch: `main`, folder: `/ (root)`. Your dashboard will be available at `https://<username>.github.io/research-scout/dashboard.html`.

### 1.6 Push initial commit

```bash
git add -A
git commit -m "Initial research-scout structure"
git push origin main
```

---

## Step 2: Build the Managed Agent

This is the core of the system. You'll create the agent, its environment, and test it interactively before wiring up the automation.

### 2.1 Create the agent

You can do this via the Claude Console UI, the CLI, or from Claude Code using the `claude-api` skill. Here's the API approach you'd give to Claude Code:

**Prompt for Claude Code:**

> Using the claude-api skill, create a new Managed Agent called "Research Scout" with the following configuration. Use claude-sonnet-4-6 as the model. Enable the full agent_toolset_20260401. Set unrestricted networking on the environment. Here is the system prompt for the agent:
>
> [paste the system prompt from section 2.2 below]
>
> After creating the agent and environment, save the agent ID and environment ID to a `.env` file I can reference later.

### 2.2 Managed Agent system prompt

This is the most important piece. This goes in the `system` field when creating the agent.

```text
You are Research Scout, an AI research agent that evaluates new tools, technologies,
and ideas for their relevance to Garrick's work at Abonmarche Consultants.

## Context about the user

Garrick is Lead Developer on the Digital Solutions team at Abonmarche Consultants,
a ~250-person municipal engineering and consulting firm. He leads AI transformation
initiatives and runs an AI Community of Practice (CoP). His work spans:

- **CostEstDB**: An AI-powered cost estimating database on Azure using pgvector,
  VoyageAI embeddings, PostgreSQL, and Claude MCP integration
- **GIS & ArcGIS**: Deep expertise in ArcGIS Pro, ArcPy, ArcGIS API for Python,
  municipal infrastructure data (water, sewer, stormwater), LGIM schema
- **AI Platform Strategy**: Evaluating Claude Enterprise vs M365 Copilot,
  building the business case for Claude across the organization
- **Claude Ecosystem**: Claude Code, Claude skills, MCP servers, Agent SDK,
  branded document generation (docx, pptx)
- **Microsoft Ecosystem**: Power Automate, Copilot Studio, Azure Functions,
  SharePoint, Teams — the enterprise backbone
- **Municipal Engineering Workflows**: Plan review automation, crash report
  processing, ArcGIS dashboards, infrastructure asset management

## Your task

When given a URL, screenshot, or description of a technology/tool/idea:

1. **Research it thoroughly** using web search and web fetch. Visit the primary
   source, find documentation, recent reviews, and technical details.

2. **Evaluate relevance** to Garrick's current work. Score it as one of:
   - **try_it**: Directly applicable to current projects or fills a known gap.
     Garrick should test this soon.
   - **watch**: Interesting and potentially relevant, but not urgent. Check back
     in 1-3 months.
   - **skip**: Not relevant to Abonmarche's stack, duplicates existing tools,
     or not mature enough to consider.

3. **Write a research brief** as a markdown file with this structure:
   ```
   # [Tool/Technology Name]

   **Date:** YYYY-MM-DD
   **Source:** [original URL]
   **Verdict:** try_it | watch | skip
   **Category:** [ai_platform | gis | database | automation | dev_tools | infrastructure | other]
   **Relevance Score:** [1-10, where 10 = directly solves a current problem]

   ## What is it?
   [2-3 paragraph summary of what this technology does]

   ## Why it matters (or doesn't)
   [How this connects to Garrick's current work — be specific about which
   projects or workflows it could affect]

   ## Technical details
   [Key technical facts: pricing, requirements, maturity, limitations]

   ## Recommendation
   [Specific next steps if "try_it", what to watch for if "watch",
   or why it's not worth pursuing if "skip"]
   ```

4. **Update the research index** by reading the current `research_index.json`
   from the repo, adding a new entry, and writing the updated file. Each entry:
   ```json
   {
     "id": "YYYY-MM-DD-topic-slug",
     "title": "Tool Name",
     "date": "YYYY-MM-DD",
     "source_url": "https://...",
     "verdict": "try_it",
     "category": "ai_platform",
     "relevance_score": 8,
     "summary": "One-line summary of what it is and why it matters",
     "brief_path": "briefs/YYYY-MM-DD-topic-slug.md"
   }
   ```

5. **Regenerate the dashboard** by writing a new `dashboard.html` file that:
   - Reads `research_index.json` via fetch (relative path)
   - Shows metric cards: total researched, try_it count, watch count, skip count
   - Shows a Chart.js donut chart of verdict distribution
   - Lists all entries grouped by verdict (try_it first, then watch, then skip)
   - Each entry shows: title, date, category badge, one-line summary
   - Uses clean, minimal CSS — no framework needed
   - Works as a static file (GitHub Pages compatible)

6. **Commit and push everything** to the GitHub repository:
   ```bash
   cd /home/user/research-scout  # or wherever the repo is cloned
   git add briefs/YYYY-MM-DD-topic-slug.md research_index.json dashboard.html
   git commit -m "Research: [Tool Name] — [verdict]"
   git push origin main
   ```

## Important rules

- Always research thoroughly before making a verdict. Visit the actual source,
  don't rely on summaries alone.
- Be honest in your assessments. Not everything is relevant — it's more valuable
  to correctly identify a "skip" than to inflate relevance.
- If given a screenshot instead of a URL, describe what you see and search for
  it to find the actual source.
- If the topic is ambiguous, research the most likely interpretation and note
  your assumption.
- Keep briefs concise but substantive — aim for 300-500 words.
- The dashboard must be fully self-contained HTML (inline CSS, Chart.js from CDN).
```

### 2.3 Agent creation — API call

```bash
# Create the agent
curl -sS --fail-with-body https://api.anthropic.com/v1/agents \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{
    "name": "Research Scout",
    "model": "claude-sonnet-4-6",
    "system": "<PASTE FULL SYSTEM PROMPT FROM 2.2 HERE>",
    "tools": [
      {"type": "agent_toolset_20260401"}
    ]
  }' | jq .

# Save the agent ID from the response
# AGENT_ID=<from response .id>
```

### 2.4 Environment creation

```bash
# Create the environment with unrestricted networking and git pre-installed
curl -sS --fail-with-body https://api.anthropic.com/v1/environments \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{
    "name": "research-scout-env",
    "config": {
      "type": "cloud",
      "networking": {"type": "unrestricted"},
      "setup_commands": [
        "git config --global user.name \"Research Scout\"",
        "git config --global user.email \"research-scout@abonmarche.com\""
      ]
    }
  }' | jq .

# Save the environment ID from the response
# ENVIRONMENT_ID=<from response .id>
```

### 2.5 Test the agent manually

Before wiring up automation, test the agent by creating a session and sending a message manually.

```bash
# Create a session
SESSION_ID=$(curl -sS --fail-with-body https://api.anthropic.com/v1/sessions \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d "{
    \"agent\": \"$AGENT_ID\",
    \"environment_id\": \"$ENVIRONMENT_ID\",
    \"title\": \"Test research session\"
  }" | jq -r '.id')

echo "Session: $SESSION_ID"

# Send a test message
curl -sS --fail-with-body \
  "https://api.anthropic.com/v1/sessions/$SESSION_ID/events" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{
    "events": [{
      "type": "user.message",
      "content": [{
        "type": "text",
        "text": "Research this for me: https://claude.com/blog/claude-managed-agents"
      }]
    }]
  }'

# Stream the response (in a separate terminal or after the POST)
curl -sS -N --fail-with-body \
  "https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01"
```

**What to verify in this test:**
- [ ] Agent performs web research (you see `web_search` and `web_fetch` tool use events)
- [ ] Agent writes a markdown brief file
- [ ] Agent updates `research_index.json`
- [ ] Agent generates `dashboard.html`
- [ ] Agent successfully pushes to GitHub

**Troubleshooting the git push:** The agent needs your GitHub PAT to push. You have two options:

- **Option A (simpler for v1):** Include the PAT in the system prompt's git instructions as a clone URL: `git clone https://<PAT>@github.com/<user>/research-scout.git`. This works but means the token is in the system prompt.
- **Option B (more secure):** Use the Managed Agents vault system to store the GitHub PAT as a credential, or pass it as an environment variable in the environment config's `setup_commands`.

For v1, Option A is fine. Move to Option B once you've validated the pipeline works end-to-end.

---

## Step 3: Build the Azure Function

This is a thin proxy that receives a message from Power Automate and triggers a Managed Agent session. It holds the Anthropic API key securely in app settings.

### 3.1 Prompt for Claude Code

Give this to a Claude Code agent with Azure CLI access:

```
Create a new Azure Function App in Python called "func-research-scout" in my
existing resource group (use the same one as func-costestdb-mcp). Deploy an
HTTP-triggered function called "trigger-research" that does the following:

1. Accepts a POST request with this JSON body:
   {
     "message": "string — the Teams message content (URL, text, or base64 image)",
     "message_type": "text | image",
     "sender": "string — who sent the Teams message (optional)"
   }

2. Reads these values from Application Settings (environment variables):
   - ANTHROPIC_API_KEY
   - RESEARCH_AGENT_ID
   - RESEARCH_ENVIRONMENT_ID

3. Creates a Managed Agent session by POSTing to:
   POST https://api.anthropic.com/v1/sessions
   Headers:
     x-api-key: {ANTHROPIC_API_KEY}
     anthropic-version: 2023-06-01
     anthropic-beta: managed-agents-2026-04-01
     content-type: application/json
   Body:
     {
       "agent": "{RESEARCH_AGENT_ID}",
       "environment_id": "{RESEARCH_ENVIRONMENT_ID}",
       "title": "Research: {first 50 chars of message}"
     }

4. Sends the user message to the session by POSTing to:
   POST https://api.anthropic.com/v1/sessions/{session_id}/events
   Same auth headers.
   Body:
     {
       "events": [{
         "type": "user.message",
         "content": [{
           "type": "text",
           "text": "Research this for me: {message}"
         }]
       }]
     }

   If message_type is "image", instead send:
     {
       "events": [{
         "type": "user.message",
         "content": [
           {
             "type": "image",
             "source": {
               "type": "base64",
               "media_type": "image/png",
               "data": "{message}"
             }
           },
           {
             "type": "text",
             "text": "Research the tool, technology, or idea shown in this screenshot."
           }
         ]
       }]
     }

5. Returns immediately with a 202 Accepted response containing:
   {
     "status": "accepted",
     "session_id": "{session_id}",
     "message": "Research agent triggered successfully"
   }

   The function does NOT wait for the agent to complete.

6. Add error handling:
   - If the Anthropic API returns an error creating the session, return 502
   - If the request body is malformed, return 400
   - Log the session_id for troubleshooting

Deploy with:
- Python 3.11 runtime
- Consumption plan (same as CostEstDB)
- Application Settings for the three environment variables (leave values blank
  for now — I'll fill them in manually via the Azure Portal)
- Enable CORS for https://make.powerautomate.com (Power Automate)
- Use a function-level auth key (same pattern as CostEstDB)
```

### 3.2 After deployment — set the app settings

In the Azure Portal (or via CLI), set:

```bash
az functionapp config appsettings set \
  --name func-research-scout \
  --resource-group <your-rg> \
  --settings \
    ANTHROPIC_API_KEY="sk-ant-..." \
    RESEARCH_AGENT_ID="<agent-id-from-step-2>" \
    RESEARCH_ENVIRONMENT_ID="<environment-id-from-step-2>"
```

### 3.3 Get the function URL

```bash
az functionapp function show \
  --name func-research-scout \
  --resource-group <your-rg> \
  --function-name trigger-research \
  --query invokeUrlTemplate -o tsv
```

Save this URL — you'll need it for Power Automate. It will look like:
`https://func-research-scout.azurewebsites.net/api/trigger-research?code=<function-key>`

### 3.4 Test the function

```bash
curl -X POST "https://func-research-scout.azurewebsites.net/api/trigger-research?code=<key>" \
  -H "content-type: application/json" \
  -d '{
    "message": "https://claude.com/blog/dispatch-and-computer-use",
    "message_type": "text",
    "sender": "Garrick (manual test)"
  }'
```

Expected response: `202 Accepted` with a session ID. Check the GitHub repo after a few minutes to see if the agent pushed a new research brief.

---

## Step 4: Build the Power Automate Flow

This flow watches a Teams channel and forwards messages to the Azure Function.

### 4.1 Create a new flow

- Go to https://make.powerautomate.com
- Click **Create** → **Automated cloud flow**
- Name: `Research Scout — Teams Trigger`
- Trigger: **When a new channel message is posted** (Microsoft Teams)

### 4.2 Module 1: Teams trigger

**Connector:** Microsoft Teams
**Action:** When a new channel message is posted

| Setting | Value |
|---------|-------|
| Team | Select your team |
| Channel | Select "Research Inbox" (create this channel first if it doesn't exist) |
| Message type | Message |
| Include message content | Yes |

This trigger fires every time someone posts in the channel. The output includes `body.content` (the HTML message body) and `attachments` (any images/files).

### 4.3 Module 2: Condition — check for attachments (optional but recommended)

**Action:** Condition

This determines whether the message contains text (a URL) or an image attachment, so you can format the Azure Function request correctly.

| Setting | Value |
|---------|-------|
| Condition | `length(triggerOutputs()?['body/attachments'])` is greater than `0` |

**If yes (image):** Go to Module 3A
**If no (text):** Go to Module 3B

### 4.4 Module 3A: Handle image messages (Yes branch)

**Action:** Compose

In this branch, you need to extract the image content. Teams attachments come as URLs that require authentication. The simplest approach:

**Step 3A.1:** Add a **Get attachment content** action (Teams connector) to download the image binary.

**Step 3A.2:** Add a **Compose** action to base64 encode it:

```
Expression: base64(body('Get_attachment_content'))
```

**Step 3A.3:** Add an **HTTP** action to call the Azure Function:

| Setting | Value |
|---------|-------|
| Method | POST |
| URI | `https://func-research-scout.azurewebsites.net/api/trigger-research?code=<your-function-key>` |
| Headers | `Content-Type: application/json` |
| Body | See below |

```json
{
  "message": "@{outputs('Compose_Base64')}",
  "message_type": "image",
  "sender": "@{triggerOutputs()?['body/from/user/displayName']}"
}
```

### 4.5 Module 3B: Handle text messages (No branch)

**Action:** HTTP

| Setting | Value |
|---------|-------|
| Method | POST |
| URI | `https://func-research-scout.azurewebsites.net/api/trigger-research?code=<your-function-key>` |
| Headers | `Content-Type: application/json` |
| Body | See below |

```json
{
  "message": "@{triggerOutputs()?['body/content']}",
  "message_type": "text",
  "sender": "@{triggerOutputs()?['body/from/user/displayName']}"
}
```

> **Note:** The `body/content` from Teams includes HTML formatting. You may want to add a **Compose** step using `stripHtml()` or a regex expression to extract just the URL from the message. A simple approach:
>
> Expression: `replace(replace(triggerOutputs()?['body/content'], '<[^>]+>', ''), '&nbsp;', ' ')`
>
> This strips HTML tags. Test this and refine — Teams message HTML can be messy.

### 4.6 Module 4: Post confirmation (optional)

After the HTTP action, you can post a reply to the Teams channel confirming the research was triggered.

**Action:** Post a reply to a message (Microsoft Teams)

| Setting | Value |
|---------|-------|
| Team | Same team |
| Channel | Same channel |
| Message ID | `triggerOutputs()?['body/messageId']` |
| Message | `Research Scout is on it. Session: @{body('HTTP')?['session_id']}` |

This gives you a visible confirmation in Teams that the agent was triggered, plus the session ID for troubleshooting.

### 4.7 Flow summary

The complete flow looks like:

```
[When a new channel message is posted]
        │
        ▼
[Condition: has attachments?]
    ├── Yes ──► [Get attachment content]
    │               │
    │               ▼
    │          [Compose: base64 encode]
    │               │
    │               ▼
    │          [HTTP POST to Azure Function (image)]
    │               │
    │               ▼
    │          [Reply to Teams message: "Research Scout is on it"]
    │
    └── No ───► [Compose: strip HTML from message]
                    │
                    ▼
               [HTTP POST to Azure Function (text)]
                    │
                    ▼
               [Reply to Teams message: "Research Scout is on it"]
```

### 4.8 Security notes for the Power Automate flow

- The Azure Function key is embedded in the URI. This is standard practice for function-level auth. The key is not visible in run history if you mark the HTTP action's inputs as **Secure**.
- To secure the HTTP action inputs: Click the three dots on the HTTP action → **Settings** → **Secure Inputs** → **On**. This redacts the URL (including the function key) from run history.
- The Anthropic API key never touches Power Automate — it lives only in the Azure Function's app settings.

---

## Step 5: Testing the End-to-End Pipeline

### 5.1 Full pipeline test

1. Go to your "Research Inbox" Teams channel
2. Post a message: `https://platform.claude.com/docs/en/managed-agents/overview`
3. Watch for:
   - [ ] Teams reply: "Research Scout is on it. Session: ..."
   - [ ] After 2-5 minutes, check the GitHub repo for a new file in `briefs/`
   - [ ] Check that `research_index.json` has a new entry
   - [ ] Check that `dashboard.html` was updated
   - [ ] Visit your GitHub Pages URL to see the dashboard

### 5.2 Test with a screenshot

1. Take a screenshot of an interesting tool or article
2. Post the screenshot to the "Research Inbox" channel
3. Verify the agent identifies the topic from the image and researches it

### 5.3 Common issues and fixes

| Issue | Likely cause | Fix |
|-------|-------------|-----|
| No Teams reply | Flow didn't trigger | Check flow run history in Power Automate |
| 502 from Azure Function | Anthropic API error | Check function logs in Azure Portal → Monitor |
| Agent runs but doesn't push to GitHub | Git auth failure | Check that the GitHub PAT is valid and has repo scope |
| Dashboard doesn't update | Agent didn't regenerate HTML | Check the agent's session events in the Claude Console |
| Stale dashboard on GitHub Pages | Pages cache | Wait 5-10 minutes for GitHub Pages CDN to update, or add a cache-busting query string |

---

## Step 6: Iteration and Enhancements

Once the v1 pipeline is working, consider these improvements:

### 6.1 Branded docx output (v2)

- Upload a custom Abonmarche brand skill to the Anthropic Skills API
- Add the `docx` pre-built skill to the agent configuration
- Update the system prompt to also produce a branded `.docx` brief
- Download the docx via the Files API in the Azure Function and upload to SharePoint via Graph API

### 6.2 Direct SharePoint write (v2)

- Register an Azure AD app with Graph API `Sites.ReadWrite.All` permission
- Store the client credentials in the Managed Agents vault system
- Update the system prompt to have the agent upload files to SharePoint via the Graph API using the vault credentials

### 6.3 Summary digest (v2)

- Create a Cowork scheduled task that runs weekly
- It reads the `research_index.json`, filters for new entries from the past week, and produces a digest email or Teams post with highlights

### 6.4 Multi-user support (v3)

- Other team members can also post to the Research Inbox channel
- The agent tags entries with the sender's name
- Dashboard shows filters by person

---

## Reference: File Locations and IDs

Fill these in as you complete each step:

| Resource | Value |
|----------|-------|
| GitHub repo URL | `https://github.com/<user>/research-scout` |
| GitHub Pages dashboard URL | `https://<user>.github.io/research-scout/dashboard.html` |
| Managed Agent ID | `<fill in after Step 2>` |
| Environment ID | `<fill in after Step 2>` |
| Azure Function App name | `func-research-scout` |
| Azure Function URL | `https://func-research-scout.azurewebsites.net/api/trigger-research?code=<key>` |
| Azure Resource Group | `<same as CostEstDB>` |
| Power Automate Flow name | `Research Scout — Teams Trigger` |
| Teams channel | `<team-name> / Research Inbox` |

---

## Estimated Time to Build

| Step | Estimated time |
|------|---------------|
| Step 1: GitHub repo setup | 15 minutes |
| Step 2: Managed Agent creation + testing | 1-2 hours (mostly prompt iteration) |
| Step 3: Azure Function (via Claude Code) | 30-45 minutes |
| Step 4: Power Automate flow | 30-45 minutes |
| Step 5: End-to-end testing + fixes | 1-2 hours |
| **Total** | **3-5 hours** |

The biggest variable is Step 2 — getting the agent's system prompt dialed in so it produces consistently good research briefs and reliably pushes to GitHub. Everything else is plumbing.
