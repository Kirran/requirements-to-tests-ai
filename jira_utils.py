import os
import requests
from requests.auth import HTTPBasicAuth

def parse_jira_description(desc_field):
    """Convert Jira rich-text description JSON into plain text."""
    if not desc_field:
        return ""

    text_parts = []

    try:
        for block in desc_field.get("content", []):
            for item in block.get("content", []):
                if "text" in item:
                    text_parts.append(item["text"])
    except Exception:
        return str(desc_field)

    return "\n".join(text_parts).strip()


def get_jira_issue(issue_key):
    """Fetch Jira issue summary and description from Jira Cloud."""
    base_url = os.environ.get("JIRA_BASE_URL")
    email = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")

    if not base_url or not email or not api_token:
        return None, "Jira environment variables are missing."

    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    auth = HTTPBasicAuth(email, api_token)
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code != 200:
        return None, f"Failed to fetch Jira issue: {response.status_code}"

    data = response.json()
    fields = data.get("fields", {})

    summary = fields.get("summary", "")
    description = parse_jira_description(fields.get("description"))

    return {
        "summary": summary,
        "description": description,
    }, None


def build_jira_context(jira_ticket):
    """Return formatted Jira context text for the AI prompt."""
    jira_ticket = jira_ticket.strip()

    if not jira_ticket:
        return "", None, None

    issue_data, error = get_jira_issue(jira_ticket)
    if error:
        return "", None, error

    jira_context = f"""
Jira Ticket: {jira_ticket}
Summary: {issue_data['summary']}
Description:
{issue_data['description']}
""".strip()

    return jira_context, issue_data, None