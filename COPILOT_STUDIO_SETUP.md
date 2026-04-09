# Research Scout -- Copilot Studio Agent Setup

This guide walks through creating a Copilot Studio agent that acts as your
Research Scout interface in Teams. Instead of posting to a channel, you just
message the agent directly -- it calls the Azure Function, which triggers the
Managed Agent to research and push results to the repo.

```
You (Teams chat) --> Copilot Studio Agent --> Azure Function --> Managed Agent --> GitHub
```

## Prerequisites

- Access to Copilot Studio (https://copilotstudio.microsoft.com)
- The deployed Azure Function URL:
  ```
  https://func-research-scout.azurewebsites.net/api/trigger-research?code=<YOUR_FUNCTION_KEY>
  ```
- Teams access with permission to add apps

---

## Step 1: Create the Agent

1. Go to **https://copilotstudio.microsoft.com**
2. Select your Abonmarche environment
3. Click **Create** in the left nav, then **New agent**
4. Configure the basics:
   - **Name:** `Research Scout`
   - **Description:** `Drop a link or describe a technology and I'll research it for you`
   - **Instructions:** Paste the following:

```
You are Research Scout, Garrick's research assistant. When someone sends you a
URL or describes a technology/tool/idea, you forward it to the research pipeline
for analysis.

Your job is simple:
1. Extract the URL or topic description from the user's message
2. Call the "Trigger Research" action with the message
3. Confirm to the user that research has been triggered
4. Share the dashboard link so they can check results later

You do NOT do the research yourself. You hand it off to the backend agent.

If the user asks about the status of past research, point them to the dashboard:
https://garrickgarcia.github.io/research-scout/dashboard.html

Be concise and friendly. One or two sentences is enough for most responses.
```

5. Click **Create**

---

## Step 2: Create the HTTP Action

This is the core piece -- an action that calls the Azure Function.

1. In your agent, go to **Actions** in the left panel
2. Click **+ Add an action**
3. Select **New action** > **HTTP request**
4. Configure the action:
   - **Name:** `Trigger Research`
   - **Description:** `Sends a research request to the Research Scout pipeline`

### Request configuration

| Setting         | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **Method**      | POST                                                               |
| **URL**         | `https://func-research-scout.azurewebsites.net/api/trigger-research?code=<YOUR_FUNCTION_KEY>` |
| **Header**      | `Content-Type: application/json`                                   |

### Request body

```json
{
  "message": "{ResearchTopic}",
  "message_type": "text",
  "sender": "{SenderName}"
}
```

### Input parameters

| Parameter        | Type   | Description                          |
|------------------|--------|--------------------------------------|
| `ResearchTopic`  | String | The URL or topic to research         |
| `SenderName`     | String | Who sent the request (optional)      |

### Response schema

```json
{
  "status": "string",
  "session_id": "string",
  "message": "string"
}
```

5. **Save** the action

---

## Step 3: Create the Conversation Topic

This topic handles the main flow: user sends a message, agent calls the action,
agent confirms.

1. Go to **Topics** in the left panel
2. Click **+ Add a topic** > **From blank**
3. Name it: `Research a topic`

### Trigger phrases

Add these (and any variations you like):

- `research this`
- `look into this`
- `check this out`
- `what do you think about`
- `evaluate this tool`
- `https://`

### Topic flow

Build the following nodes in order:

**Node 1 -- Question**
- Ask: `What would you like me to research? Send a URL or describe the topic.`
- Save response as: `ResearchTopic` (type: string)
- **Note:** If the trigger phrase already contains the topic (e.g., the user
  sends a URL directly), Copilot Studio may auto-fill this. You can set the
  variable to recognize the full trigger message as the input.

**Node 2 -- Call action**
- Select the **Trigger Research** action
- Map inputs:
  - `ResearchTopic` = `ResearchTopic` variable
  - `SenderName` = `System.User.DisplayName`

**Node 3 -- Message**
- Text:
  ```
  Research Scout is on it! I've kicked off a research session.

  Check the dashboard for results in a few minutes:
  https://garrickgarcia.github.io/research-scout/dashboard.html
  ```

**Node 4 -- End conversation**

---

## Step 4: Add a Fallback / Conversational Topic (Optional)

For general questions about past research or the dashboard:

1. Create a new topic: `Check research status`
2. Trigger phrases: `show me the dashboard`, `what has been researched`, `status`
3. Single message node:
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
   who in the org can find the agent

Once published, the agent appears in your Teams chat list. You can pin it for
quick access.

---

## Step 6: Test It

1. Open Teams and find **Research Scout** in your chat list
2. Send a message: `https://duckdb.org`
3. The agent should:
   - Acknowledge the request
   - Share the dashboard link
4. Wait 2-5 minutes, then check:
   - The dashboard at https://garrickgarcia.github.io/research-scout/dashboard.html
   - The GitHub repo for a new file in `briefs/`

---

## Troubleshooting

| Issue                           | Check                                                  |
|---------------------------------|--------------------------------------------------------|
| Agent doesn't respond           | Verify the topic trigger phrases match your input      |
| HTTP action fails               | Check the function URL and key are correct             |
| 502 from the function           | Check function logs: Azure Portal > func-research-scout > Monitor |
| Agent researches but no push    | Check the Managed Agent session events in Claude Console |
| Dashboard doesn't update        | Hard refresh the page (Ctrl+Shift+R), or wait for GitHub Pages cache (~5 min) |

---

## Security Notes

- The Azure Function key is embedded in the HTTP action URL. This is standard
  for function-level auth. The key is not visible to end users.
- To further restrict access, go to the HTTP action settings and enable
  **Secure Inputs** to redact the URL from Copilot Studio logs.
- The Anthropic API key and GitHub token live only in Azure Function app
  settings -- they never touch Copilot Studio.
- If you want to limit who can use the agent, configure availability in
  Copilot Studio under **Settings** > **Security**.
