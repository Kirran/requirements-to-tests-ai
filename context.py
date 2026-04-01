def build_requirement_context(manual_text, jira_context):
    """Combine typed/transcribed text and Jira content into one context block."""
    return f"""
    Manual / Edited Requirement:
    {manual_text}

    Jira Context:
    {jira_context}
    """.strip()    

