"""
Research Scout -- Azure Function
Thin proxy that receives messages from Power Automate and triggers
a Claude Managed Agent session to research the topic.
"""

import json
import logging
import os

import azure.functions as func
import requests

app = func.FunctionApp()

ANTHROPIC_API = "https://api.anthropic.com/v1"
ANTHROPIC_HEADERS_BASE = {
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "managed-agents-2026-04-01",
    "content-type": "application/json",
}

# Git setup instructions included in every user message so the agent
# can clone, commit, and push to the research-scout repo.
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


def _build_content_blocks(message, message_type, clone_url):
    """Build the content array for the user message event."""
    git_steps = GIT_INSTRUCTIONS.format(clone_url=clone_url)

    if message_type == "image":
        return [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": message,
                },
            },
            {
                "type": "text",
                "text": (
                    "Research the tool, technology, or idea shown in this screenshot."
                    + git_steps
                ),
            },
        ]

    return [
        {
            "type": "text",
            "text": f"Research this for me: {message}{git_steps}",
        }
    ]


@app.route(
    route="trigger-research",
    methods=["POST"],
    auth_level=func.AuthLevel.FUNCTION,
)
def trigger_research(req: func.HttpRequest) -> func.HttpResponse:
    """Accept a research request and fire off a Managed Agent session."""
    # Parse request body
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    message = body.get("message", "").strip()
    message_type = body.get("message_type", "text")
    sender = body.get("sender", "unknown")

    if not message:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'message' field"}),
            status_code=400,
            mimetype="application/json",
        )

    if message_type not in ("text", "image"):
        return func.HttpResponse(
            json.dumps({"error": "message_type must be 'text' or 'image'"}),
            status_code=400,
            mimetype="application/json",
        )

    # Read config from app settings
    try:
        agent_id = _get_env("RESEARCH_AGENT_ID")
        env_id = _get_env("RESEARCH_ENVIRONMENT_ID")
        clone_url = _get_env("GITHUB_CLONE_URL")
        headers = _anthropic_headers()
    except ValueError as e:
        logging.error("Configuration error: %s", e)
        return func.HttpResponse(
            json.dumps({"error": "Server configuration error"}),
            status_code=500,
            mimetype="application/json",
        )

    # Create a session
    title = f"Research: {message[:50]}"
    try:
        session_resp = requests.post(
            f"{ANTHROPIC_API}/sessions",
            headers=headers,
            json={
                "agent": agent_id,
                "environment_id": env_id,
                "title": title,
            },
            timeout=30,
        )
        session_resp.raise_for_status()
        session_id = session_resp.json()["id"]
    except Exception as e:
        logging.error("Failed to create session: %s", e)
        return func.HttpResponse(
            json.dumps({"error": "Failed to create agent session"}),
            status_code=502,
            mimetype="application/json",
        )

    logging.info(
        "Session %s created for sender=%s message_type=%s",
        session_id, sender, message_type,
    )

    # Send the user message
    content = _build_content_blocks(message, message_type, clone_url)
    try:
        event_resp = requests.post(
            f"{ANTHROPIC_API}/sessions/{session_id}/events",
            headers=headers,
            json={
                "events": [
                    {
                        "type": "user.message",
                        "content": content,
                    }
                ]
            },
            timeout=30,
        )
        event_resp.raise_for_status()
    except Exception as e:
        logging.error("Failed to send message to session %s: %s", session_id, e)
        return func.HttpResponse(
            json.dumps({
                "error": "Session created but failed to send message",
                "session_id": session_id,
            }),
            status_code=502,
            mimetype="application/json",
        )

    logging.info("Message sent to session %s", session_id)

    # Return immediately -- the agent works asynchronously
    return func.HttpResponse(
        json.dumps({
            "status": "accepted",
            "session_id": session_id,
            "message": "Research agent triggered successfully",
        }),
        status_code=202,
        mimetype="application/json",
    )
