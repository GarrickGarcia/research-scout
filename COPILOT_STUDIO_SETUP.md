# Research Scout -- Copilot Studio Agent Setup

This guide walks through creating a Copilot Studio agent that acts as your
Research Scout interface in Teams. You message the agent with a link, description,
or screenshot. The agent synthesizes the input and calls the Research Scout MCP
tool, which triggers a Managed Agent to do the actual research and push results
to GitHub.

```
You (Teams chat)
    |
    v
Copilot Studio Agent (synthesizes text/image/URL into a research topic)
    |
    v
MCP Tool: trigger_research (Azure Function)
    |
    v
Claude Managed Agent (researches, writes brief, pushes to GitHub)
    |
    v
GitHub repo + dashboard
```

## Prerequisites

- Access to Copilot Studio (https://copilotstudio.microsoft.com)
- The Research Scout Azure Function is deployed (`func-research-scout`)
- The MCP tool endpoint URL (get from Azure Portal or your `.env` file)
- Teams access with permission to add apps

---

## Step 1: Create the Agent

1. Go to **https://copilotstudio.microsoft.com**
2. Select your Abonmarche environment
3. Click **Create** in the left nav, then **New agent**
4. Configure the basics:
   - **Name:** `Research Scout`
   - **Description:** `Send a link, topic, or screenshot and I'll research it for you`
   - **Instructions:** Paste the following:

```
You are Research Scout, Garrick's research assistant at Abonmarche. Your job is
to take whatever the user gives you -- a URL, a description of a technology, or
a screenshot -- and pass it to the trigger_research MCP tool for deep research.

When the user sends you something:

1. If it's a URL, pass it directly to the trigger_research tool as the topic.
2. If it's a description or question about a technology, clean it up into a
   concise topic string and pass it to trigger_research.
3. If it's an image/screenshot, describe what you see in the image -- product
   names, URLs, key features -- and pass that description to trigger_research.
4. After calling the tool, confirm to the user that research has been triggered
   and share the dashboard link.

Dashboard: https://garrickgarcia.github.io/research-scout/dashboard.html

Be concise. One or two sentences per response is ideal. You do NOT perform the
research yourself -- you hand it off to the backend research agent.

If the user asks about past research or status, point them to the dashboard.
```

5. Click **Create**

---

## Step 2: Add the MCP Tool Connection

The Research Scout Azure Function exposes an MCP tool called `trigger_research`.
You need to connect it to the Copilot Studio agent.

### Option A: Add as a Connector Action

1. In your agent, go to **Actions** in the left panel
2. Click **+ Add an action**
3. Select **New action** > **HTTP request**
4. Configure:
   - **Name:** `trigger_research`
   - **Description:** `Trigger Research Scout to research a technology, tool, or idea`

| Setting    | Value                                                                                      |
|------------|--------------------------------------------------------------------------------------------|
| **Method** | POST                                                                                       |
| **URL**    | `https://func-research-scout.azurewebsites.net/api/trigger-research?code=<YOUR_FUNCTION_KEY>` |
| **Header** | `Content-Type: application/json`                                                           |

**Request body:**
```json
{
  "message": "{topic}"
}
```

**Input parameter:**

| Parameter | Type   | Description                                              |
|-----------|--------|----------------------------------------------------------|
| `topic`   | String | The URL, topic name, or description of what to research  |

**Response schema:**
```json
{
  "status": "string",
  "session_id": "string",
  "message": "string"
}
```

5. **Save** the action

### Option B: Add as Remote MCP Server (if supported in your environment)

If your Copilot Studio environment supports MCP server connections:

1. Go to **Settings** > **Tools** or **Extensions**
2. Add a new MCP server connection
3. Point it to: `https://func-research-scout.azurewebsites.net`
4. The `trigger_research` tool will be discovered automatically

---

## Step 3: Create the Conversation Topic

1. Go to **Topics** in the left panel
2. Click **+ Add a topic** > **From blank**
3. Name it: `Research a topic`

### Trigger phrases

- `research this`
- `look into this`
- `check this out`
- `what do you think about`
- `evaluate this tool`
- `https://`

### Topic flow

**Node 1 -- Question**
- Ask: `What would you like me to research? Send a URL or describe the topic.`
- Save response as: `ResearchTopic` (type: string)
- Note: If the trigger already contains the topic (e.g., user sends a URL
  directly), Copilot Studio may auto-fill this.

**Node 2 -- Call action**
- Select the **trigger_research** action
- Map input: `topic` = `ResearchTopic` variable

**Node 3 -- Message**
```
Research Scout is on it! I've kicked off a research session.

Check the dashboard for results in a few minutes:
https://garrickgarcia.github.io/research-scout/dashboard.html
```

**Node 4 -- End conversation**

---

## Step 4: Add a Status Topic (Optional)

For questions about past research:

1. Create topic: `Check research status`
2. Triggers: `show me the dashboard`, `what has been researched`, `status`
3. Message:
   ```
   Here's your Research Scout dashboard with all completed research:
   https://garrickgarcia.github.io/research-scout/dashboard.html
   ```

---

## Step 5: Publish to Teams

1. In the left panel, click **Channels**
2. Select **Microsoft Teams**
3. Click **Turn on Teams**
4. Click **Open in Teams** to test, or go to **Availability** to control
   who can find the agent
5. Pin the agent in Teams for quick access

---

## Step 6: Test It

1. Open Teams and find **Research Scout** in your chat
2. Send: `https://duckdb.org`
3. The agent should call the tool and confirm research was triggered
4. Wait 2-5 minutes, then check the dashboard

**Test with an image:**
1. Send a screenshot of an interesting tool
2. The agent should describe what it sees and pass that to the tool
3. Check the dashboard for results

---

## Troubleshooting

| Issue                           | Check                                                  |
|---------------------------------|--------------------------------------------------------|
| Agent doesn't call the tool     | Verify the action is connected and topic flow is correct |
| HTTP action fails               | Check the function URL and key in the action config    |
| 502 from the function           | Azure Portal > func-research-scout > Monitor > Logs    |
| Agent researches but no push    | Check Managed Agent session in Claude Console          |
| Dashboard stale                 | Hard refresh (Ctrl+Shift+R) or wait ~5 min for Pages cache |

---

## Security Notes

- The Azure Function key is in the HTTP action URL. Mark the action's inputs
  as **Secure** (three dots > Settings > Secure Inputs > On) to redact it
  from Copilot Studio run logs.
- The Anthropic API key and GitHub token live only in Azure Function app
  settings -- they never touch Copilot Studio.
- Control who can use the agent under **Settings** > **Security** in
  Copilot Studio.
