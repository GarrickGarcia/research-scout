"""
Research Scout -- Azure Function (Remote MCP Server)
Exposes a trigger_research MCP tool that kicks off a Claude Managed Agent
session to research a topic and push results to GitHub.
"""

import json
import logging
import os

import azure.functions as func
import requests

app = func.FunctionApp()
logger = logging.getLogger("research-scout")

ANTHROPIC_API = "https://api.anthropic.com/v1"
ANTHROPIC_HEADERS_BASE = {
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "managed-agents-2026-04-01",
    "content-type": "application/json",
}

# Git setup instructions appended to every user message so the managed
# agent can clone, commit, and push to the research-scout repo.
GIT_INSTRUCTIONS = """
After completing your research, do the following:
1. Run: git clone {clone_url} /home/user/research-scout
2. Run: cd /home/user/research-scout && git config user.name "Research Scout" && git config user.email "research-scout@abonmarche.com" && git config commit.gpgsign false
3. Write the research brief to briefs/
4. Update research_index.json with the new entry
5. Stage, commit, and push: git add briefs/ research_index.json && git commit -m "Research: [Tool Name] -- [verdict]" && git push origin main
"""


def _get_env(name):
    """Read a required environment variable or raise."""
    val = os.environ.get(name)
    if not val:
        raise ValueError(f"Missing required app setting: {name}")
    return val


def _anthropic_headers():
    """Build headers with the API key."""
    headers = dict(ANTHROPIC_HEADERS_BASE)
    headers["x-api-key"] = _get_env("ANTHROPIC_API_KEY")
    return headers


def _trigger_session(research_topic):
    """Create a Managed Agent session and send the research request.

    Returns (session_id, error_message). On success error_message is None.
    """
    headers = _anthropic_headers()
    agent_id = _get_env("RESEARCH_AGENT_ID")
    env_id = _get_env("RESEARCH_ENVIRONMENT_ID")
    clone_url = _get_env("GITHUB_CLONE_URL")
    git_steps = GIT_INSTRUCTIONS.format(clone_url=clone_url)

    # Create session
    session_resp = requests.post(
        f"{ANTHROPIC_API}/sessions",
        headers=headers,
        json={
            "agent": agent_id,
            "environment_id": env_id,
            "title": f"Research: {research_topic[:50]}",
        },
        timeout=30,
    )
    session_resp.raise_for_status()
    session_id = session_resp.json()["id"]
    logger.info("Session %s created for topic: %s", session_id, research_topic[:80])

    # Send user message
    event_resp = requests.post(
        f"{ANTHROPIC_API}/sessions/{session_id}/events",
        headers=headers,
        json={
            "events": [{
                "type": "user.message",
                "content": [{
                    "type": "text",
                    "text": f"Research this for me: {research_topic}{git_steps}",
                }],
            }],
        },
        timeout=30,
    )
    event_resp.raise_for_status()
    logger.info("Message sent to session %s", session_id)

    return session_id, None


# ---------------------------------------------------------------------------
# MCP Tool: trigger_research
# ---------------------------------------------------------------------------

@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="trigger_research",
    description=(
        "Trigger Research Scout to research a technology, tool, or idea. "
        "Provide a URL, topic description, or summary of what to research. "
        "The research agent will investigate the topic, evaluate its relevance "
        "to Abonmarche Digital Solutions work, write a structured brief, and "
        "push results to the research-scout GitHub repository. Results appear "
        "on the dashboard at https://garrickgarcia.github.io/research-scout/dashboard.html "
        "within a few minutes."
    ),
    toolProperties=(
        '[{"propertyName":"topic","propertyType":"string",'
        '"description":"The URL, topic name, or description of the technology/tool/idea to research. '
        'If the user sent an image, describe what the image shows and include any URLs or product names visible in it."}]'
    ),
)
def trigger_research_mcp(context) -> str:
    """MCP tool: trigger_research"""
    try:
        content = json.loads(context)
        args = content.get("arguments", content)
        topic = args.get("topic", "").strip()

        if not topic:
            return json.dumps({"error": "Missing 'topic' parameter"})

        session_id, error = _trigger_session(topic)
        if error:
            return json.dumps({"error": error})

        return json.dumps({
            "status": "accepted",
            "session_id": session_id,
            "message": (
                f"Research agent triggered successfully. "
                f"Results will appear on the dashboard in a few minutes: "
                f"https://garrickgarcia.github.io/research-scout/dashboard.html"
            ),
        })

    except Exception as e:
        logger.error("trigger_research failed: %s", e)
        return json.dumps({"error": f"Failed to trigger research: {str(e)}"})


# ---------------------------------------------------------------------------
# HTTP endpoint (fallback for direct testing or other integrations)
# ---------------------------------------------------------------------------

@app.route(
    route="trigger-research",
    methods=["POST"],
    auth_level=func.AuthLevel.FUNCTION,
)
def trigger_research_http(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP fallback -- accepts JSON and triggers a research session."""
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    topic = body.get("message", "").strip()
    if not topic:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'message' field"}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        session_id, error = _trigger_session(topic)
        if error:
            return func.HttpResponse(
                json.dumps({"error": error}),
                status_code=502,
                mimetype="application/json",
            )
    except Exception as e:
        logger.error("HTTP trigger_research failed: %s", e)
        return func.HttpResponse(
            json.dumps({"error": f"Failed to trigger research: {str(e)}"}),
            status_code=502,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({
            "status": "accepted",
            "session_id": session_id,
            "message": "Research agent triggered successfully",
        }),
        status_code=202,
        mimetype="application/json",
    )
