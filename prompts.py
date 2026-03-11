def build_requirement_context(manual_text, jira_context):
    return f"""
    Manual / Edited Requirement:
    {manual_text}

    Jira Context:
    {jira_context}
    """.strip()


def build_prompt(feature_type, combined_requirement):

    return f"""
    You are a senior QA Architect focused on shift-left quality engineering.
    Analyze the requirement below and produce structured QA analysis.

    Feature Type:
    {feature_type}

    Requirement Context:
    {combined_requirement}

    Return the results using these exact section headers in this exact order:
    Quality Analysis:
    Requirement Summary:
    Requirement Gaps:
    Risk Signals:
    Functional Test Cases:
    Negative Test Cases:
    Edge Cases:
    Security Test Cases:
    Root Cause Signals:
    Observability / Logging Recommendations:
    Requirement Quality Score:
    """.strip()