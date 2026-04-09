# Claude Code Prompt — Research Scout Setup (v2)

Copy everything below the line and paste it into Claude Code once you've opened it on the research-scout repo.

---

I'm building an automated research pipeline called "Research Scout." Read the `research-scout-project-plan.md` file in this repo first — it has the full architecture and details. Then execute the following steps in order. After each major step, pause and confirm what you did before moving on.

## Your environment context

- I have the Azure CLI installed and authenticated (`az login` is done)
- I have the GitHub CLI installed and authenticated (`gh auth status` is done) — use `gh` for all git operations that need auth, and standard `git` for local operations
- My Anthropic API key is in the `.env` file in this repo root. Read it from there — never hardcode it or ask me for it. If the key still says "paste-your-key-here" then stop and tell me to fill it in first.
- This repo is already cloned and we're in it. The remote origin is set up.
- I want a NEW, separate Azure resource group for this project — do NOT reuse my CostEstDB resource group. Run `az group list --output table` to find an existing function app so you can identify my preferred region, then create a new resource group called `rg-research-scout` in that same region.
- I'm on Windows but you can use bash commands.

## Important: GitHub operations

Do NOT use a GitHub Personal Access Token. I have the GitHub CLI (`gh`) installed and authenticated. For all git push operations:
- Use standard `git add`, `git commit` locally
- Use `git push origin main` for pushing (my git credential manager handles auth)
- Use `gh repo view` to confirm repo access
- For the Managed Agent's git operations inside its cloud container, we'll need a different approach since `gh` won't be available there. Use `gh auth token` to retrieve my current token and include it in the agent's clone URL. This keeps the token out of any committed files — it only flows through environment variables.

## Step 1: Validate environment

Before doing anything else:

1. Read the `.env` file and verify the `ANTHROPIC_API_KEY` is set (not the placeholder)
2. Run `gh auth status` to confirm GitHub CLI is working
3. Run `az account show` to confirm Azure CLI is working
4. Run `gh auth token` to retrieve the GitHub token — save it in a local variable for later use (for the Managed Agent's clone URL). Do not write this to any file.
5. Get my GitHub username with `gh api user --jq .login`
6. Get the repo's clone URL with `gh repo view --json url --jq .url`

If any of these fail, stop and tell me what to fix.

## Step 2: Scaffold the repo structure

Create the initial files:

1. Create `briefs/.gitkeep`
2. Create `research_index.json` with an empty entries array and `last_updated` set to today's ISO timestamp
3. Create an initial `dashboard.html` that:
   - Is fully self-contained (inline CSS + Chart.js from CDN)
   - Fetches `research_index.json` via relative path
   - Shows 4 metric cards at the top: Total Researched, Try It, Watch, Skip
   - Shows a Chart.js donut chart of verdict distribution (try_it = green #1D9E75, watch = amber #BA7517, skip = gray #B4B2A9)
   - Lists entries grouped by verdict (try_it first, then watch, then skip)
   - Each entry card has: title, date, category badge, one-line summary, colored left border matching the verdict
   - Handles the empty state gracefully (shows "No research yet — drop a link in your Teams channel to get started")
   - Has clean minimal styling, dark mode support via prefers-color-scheme, no framework
   - Has a title at the top: "Research Scout — Abonmarche Digital Solutions"
4. Verify `.env` is in `.gitignore`. If there's no `.gitignore`, create one with `.env`, `__pycache__/`, `*.pyc`, `.venv/`, `azure-function/local.settings.json`
5. Commit everything with message "Initial repo structure with empty dashboard"
6. Push to origin main

## Step 3: Set up the Managed Agent

Use curl to call the Anthropic API directly. Read the API key from the `.env` file using `source .env` or equivalent.

### 3a. Create the agent

POST to `https://api.anthropic.com/v1/agents` with these headers:
- `x-api-key: $ANTHROPIC_API_KEY`
- `anthropic-version: 2023-06-01`
- `anthropic-beta: managed-agents-2026-04-01`
- `content-type: application/json`

Body:
- name: "Research Scout"
- model: "claude-sonnet-4-6"
- tools: `[{"type": "agent_toolset_20260401"}]`
- system: Use the FULL system prompt from section 2.2 of `research-scout-project-plan.md`. Read it from the file — do NOT summarize, truncate, or paraphrase it. Include every word. This is the most critical part of the entire setup.

Save the returned `id` as `RESEARCH_AGENT_ID` and write it back to the `.env` file.

### 3b. Create the environment

POST to `https://api.anthropic.com/v1/environments` with the same auth headers.

Body:
```json
{
  "name": "research-scout-env",
  "config": {
    "type": "cloud",
    "networking": {"type": "unrestricted"},
    "setup_commands": [
      "git config --global user.name \"Research Scout\"",
      "git config --global user.email \"research-scout@abonmarche.com\""
    ]
  }
}
```

Save the returned `id` as `RESEARCH_ENVIRONMENT_ID` and write it back to the `.env` file.

### 3c. Test the agent

Construct the GitHub clone URL using the token from Step 1:
`https://<github-token>@github.com/<github-username>/research-scout.git`

Create a test session and send it this message (substitute actual values):

"Research this for me: https://claude.com/blog/claude-managed-agents — After completing your research, clone the repo <CLONE_URL_WITH_TOKEN>, write the research brief to briefs/, update research_index.json, regenerate dashboard.html to include the new entry, then commit and push all changes to main."

Stream the events and show me the agent's progress. Watch for the `session.status_idle` event to know it's done.

After the agent finishes:
- Pull the latest: `git pull origin main`
- Show me what files changed
- Show me the contents of the new brief
- Show me the updated `research_index.json`
- Open `dashboard.html` in the browser if possible, or confirm it was regenerated

If the test fails, troubleshoot based on the event stream output. Common issues:
- Git clone failure → verify the token and URL
- Agent doesn't push → check git config in setup_commands
- Agent produces poor output → the system prompt may need refinement (but let's validate the pipeline first)

## Step 4: Build and deploy the Azure Function

### 4a. Create a new resource group

First, find my preferred Azure region by looking at existing resources:

```bash
az functionapp list --output table
```

Then create a dedicated resource group for Research Scout in the same region:

```bash
az group create \
  --name rg-research-scout \
  --location <same-region-as-existing-apps>
```

Use `rg-research-scout` as the resource group for all subsequent steps.

### 4b. Create the function app infrastructure

```bash
# Create storage account (use a unique name)
az storage account create \
  --name stresearchscout<random-suffix> \
  --resource-group rg-research-scout \
  --location <region> \
  --sku Standard_LRS

# Create the function app
az functionapp create \
  --name func-research-scout \
  --resource-group rg-research-scout \
  --storage-account <storage-account-name> \
  --consumption-plan-location <region> \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux
```

If `func-research-scout` is taken, append a short random suffix. Use `rg-research-scout` for all Azure commands from here on.

### 4c. Write the function code

Create a local function project in `azure-function/`:

```
azure-function/
├── function_app.py
├── host.json
└── requirements.txt
```

**function_app.py** should:

1. Be an Azure Functions v2 Python app using the `@app.route` decorator pattern
2. Accept POST requests at route `trigger-research`
3. Use `func.AuthLevel.FUNCTION` for auth
4. Read from environment variables: `ANTHROPIC_API_KEY`, `RESEARCH_AGENT_ID`, `RESEARCH_ENVIRONMENT_ID`, `GITHUB_CLONE_URL`
5. Accept JSON body: `{"message": "string", "message_type": "text|image", "sender": "string (optional)"}`
6. Create a Managed Agent session via POST to `https://api.anthropic.com/v1/sessions` with:
   - The required beta header `managed-agents-2026-04-01`
   - Agent ID and environment ID from env vars
   - Title: "Research: {first 50 chars of message}"
7. Send the user message via POST to `https://api.anthropic.com/v1/sessions/{session_id}/events` with:
   - For text: a single text content block with the message AND instructions to clone the repo (from GITHUB_CLONE_URL env var), write the brief, update index, regenerate dashboard, commit and push
   - For image: an image content block (base64) plus a text block with the same clone/write/push instructions
8. Return 202 Accepted immediately with `{"status": "accepted", "session_id": "..."}`
9. Handle errors: 400 for bad input, 502 for Anthropic API failures
10. Log the session_id and any errors using Python's `logging` module

**requirements.txt**: just `requests`

**host.json**: standard config with function-level auth

### 4d. Deploy the function

Use whichever deployment method works — `func azure functionapp publish` if the func CLI is available, otherwise zip deploy:

```bash
cd azure-function
zip -r ../deploy.zip .
az functionapp deployment source config-zip \
  --name <function-app-name> \
  --resource-group rg-research-scout \
  --src ../deploy.zip
```

### 4e. Set the application settings

Construct the GITHUB_CLONE_URL using the token from Step 1:

```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group rg-research-scout \
  --settings \
    ANTHROPIC_API_KEY="<from .env>" \
    RESEARCH_AGENT_ID="<from .env>" \
    RESEARCH_ENVIRONMENT_ID="<from .env>" \
    GITHUB_CLONE_URL="https://<github-token>@github.com/<username>/research-scout.git"
```

### 4f. Get the function URL and key

```bash
# Get the function URL
az functionapp function show \
  --name <function-app-name> \
  --resource-group rg-research-scout \
  --function-name trigger-research \
  --query invokeUrlTemplate -o tsv

# Get the function key
az functionapp function keys list \
  --name <function-app-name> \
  --resource-group rg-research-scout \
  --function-name trigger-research
```

Save the full URL (with `?code=<key>`) to `AZURE_FUNCTION_URL` in the `.env` file.

### 4g. Test the function

```bash
curl -X POST "<function-url>?code=<key>" \
  -H "Content-Type: application/json" \
  -d '{"message": "https://n8n.io", "message_type": "text", "sender": "Garrick (Azure Function test)"}'
```

Should return 202. Wait a few minutes, then `git pull origin main` and check for a new brief.

## Step 5: Write the Power Automate setup guide

Since Power Automate can't be set up programmatically, create `POWER_AUTOMATE_SETUP.md` in the repo root with detailed step-by-step instructions I can follow in the browser. Use the ACTUAL deployed function URL from Step 4.

Include:

1. **Create the flow** — name it "Research Scout — Teams Trigger", use the "When a new channel message is posted" trigger. Specify exact settings: which Team/Channel fields to fill in, message type = Message, include message content = Yes.

2. **Add a condition** — check if the message has attachments using `length(triggerOutputs()?['body/attachments'])` greater than 0.

3. **Yes branch (image):**
   - Get attachment content action (Microsoft Teams connector)
   - Compose action to base64 encode: `base64(body('Get_attachment_content'))`
   - HTTP POST to: `<actual function URL from deployment>`
   - Body template with `message_type: "image"` and the base64 output
   - Include the sender display name from trigger

4. **No branch (text):**
   - Compose action to strip HTML: provide the expression to clean Teams HTML
   - HTTP POST to: `<actual function URL from deployment>`
   - Body template with `message_type: "text"` and the cleaned message
   - Include the sender display name from trigger

5. **Both branches:** Add a "Reply to a message" Teams action that confirms "Research Scout is on it. Session: {session_id from HTTP response}"

6. **Security:** How to mark HTTP action inputs as Secure (click three dots → Settings → Secure Inputs → On)

7. **Testing instructions:** Post a URL to the Teams channel and verify the full pipeline

## Step 6: Update project plan and final commit

1. Update the "Reference: File Locations and IDs" table in `research-scout-project-plan.md` with ALL actual values from the deployment (agent ID, environment ID, function URL, GitHub Pages URL, etc.)
2. Commit all new and changed files with message "Complete Research Scout pipeline setup — agent, function, and PA guide"
3. Push to origin main
4. Give me a summary of:
   - What was completed successfully
   - What needs manual attention (Power Automate setup via the guide)
   - The Azure Function URL I need for Power Automate
   - The GitHub Pages dashboard URL
   - Any issues encountered and workarounds applied

## Rules for this session

- Read the project plan file FIRST before doing anything
- Read all sensitive values from the `.env` file — never ask me for keys or tokens
- Use `gh` CLI for GitHub auth — never ask for a PAT
- After each major step (2, 3, 4), show me what you did and confirm before moving on
- If something fails, troubleshoot it rather than skipping ahead
- Use the Azure CLI for all Azure operations
- Keep the function code clean and well-commented
- Test everything that can be tested before moving on
- Never commit the `.env` file or write tokens/keys to any tracked file
