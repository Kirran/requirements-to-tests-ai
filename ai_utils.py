import re
from openai import OpenAI
client = OpenAI()

SECTION_NAMES = [
    "Quality Analysis",
    "Requirement Summary",
    "Requirement Gaps",
    "Risk Signals",
    "Functional Test Cases",
    "Negative Test Cases",
    "Edge Cases",
    "Security Test Cases",
    "Root Cause Signals",
    "Observability / Logging Recommendations",
    "Requirement Quality Score",
]

def call_openai_api(prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

def build_requirement_context(manual_text, jira_context):
    """Combine typed/transcribed text and Jira content into one context block."""
    return f"""
    Manual / Edited Requirement:
    {manual_text}

    Jira Context:
    {jira_context}
    """.strip()    

def build_prompt(feature_type, combined_requirement):
    """Create the OpenAI prompt."""
    return f"""
    You are a senior QA Architect focused on shift-left quality engineering.

    Analyze the requirement below and produce structured QA analysis.

    Feature Type:
    {feature_type}

    Requirement Context:
    {combined_requirement}

    Return the results using these exact section headers in this exact order:
    Write the headers exactly as shown and start each section on a new line.

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
    - Requirement Quality Score: X/10
    - Confidence in Requirement Completeness: Low / Medium / High
    - Why this score was assigned
    - Recommended requirement improvements

    Rules:
    - Use each section header exactly as written above.
    - Under each section, use bullet points.
    - Keep responses concise and practical.
    - Focus on real engineering risks and missing requirement details.
    - Do not add any introduction or conclusion outside these sections.
    """.strip()

def parse_ai_output(output_text):
    sections = {name: "" for name in SECTION_NAMES}
    current_section = None
    lines = output_text.splitlines()

    for line in lines:
        stripped = line.strip()

        matched_section = None
        for section in SECTION_NAMES:
            if stripped == section or stripped == f"{section}:":
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            continue

        if current_section:
            sections[current_section] += line + "\n"

    return {k: v.strip() for k, v in sections.items()}

def extract_risk_level(text):
    if not text:
        return None
    
    # Match "Risk Level: High"
    match = re.search(r"Risk Level:\s*(Low|Medium|High)", text, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    return None

def extract_quality_score(text):
    if not text:
        return None

    match = re.search(r"(\d+)/10", text)
    if match:
        return int(match.group(1))
    return None  