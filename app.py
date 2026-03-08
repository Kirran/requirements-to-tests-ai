import os
import streamlit as st
import re
import requests
from requests.auth import HTTPBasicAuth
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# -----------------------------
# Jira functions
# -----------------------------
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
    print("URL:", url)
    print("Status:", response.status_code)
    print("Response:", response.text)

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


# -----------------------------
# Audio functions
# -----------------------------
def transcribe_audio(audio_value):
    """Send recorded audio to OpenAI transcription API and return text."""
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_value.read())

    with open("temp_audio.wav", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    return transcription.text


def update_text_from_audio(audio_value):
    """Append transcribed audio into the editable text box."""
    if audio_value is None:
        return

    transcript = transcribe_audio(audio_value)

    if st.session_state.feature_text.strip():
        st.session_state.feature_text += "\n" + transcript
    else:
        st.session_state.feature_text = transcript


# -----------------------------
# Prompt / AI functions
# -----------------------------
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
Risk Signals:
- Risk Level (Low / Medium / High)
- Key engineering and product risks
Rules:
- Use each section header exactly as written above.
- Under each section, use bullet points.
- Keep responses concise and practical.
- Focus on real engineering risks and missing requirement details.
- Do not add any introduction or conclusion outside these sections.
""".strip()

def parse_ai_output(output_text):
    section_names = [
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
        "Requirement Quality Score"
    ]

    sections = {name: "" for name in section_names}
    current_section = None
    lines = output_text.splitlines()

    for line in lines:
        stripped = line.strip()

        # Match headers with or without trailing colon
        matched_section = None
        for section in section_names:
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
    match = re.search(r"(\d+)/10", text)
    if match:
        return int(match.group(1))
    return None

def render_readiness_summary(parsed_sections):
    quality_text = parsed_sections.get("Requirement Quality Score", "")
    risk_text = parsed_sections.get("Risk Signals", "")

    score = extract_quality_score(quality_text)
    risk_level = extract_risk_level(risk_text)

    confidence_match = re.search(
        r"Confidence in Requirement Completeness:\s*(Low|Medium|High)",
        quality_text,
        re.IGNORECASE
    )
    confidence = confidence_match.group(1).capitalize() if confidence_match else "Not provided"

    st.subheader("Requirement Readiness Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        if score is not None:
            if score >= 8:
                st.success(f"🟢 Quality Score\n\n{score}/10")
            elif score >= 5:
                st.warning(f"🟡 Quality Score\n\n{score}/10")
            else:
                st.error(f"🔴 Quality Score\n\n{score}/10")
        else:
            st.info("Quality Score\n\nNot provided")

    with col2:
        if risk_level == "High":
            st.error("🔴 Risk Level\n\nHigh")
        elif risk_level == "Medium":
            st.warning("🟡 Risk Level\n\nMedium")
        elif risk_level == "Low":
            st.success("🟢 Risk Level\n\nLow")
        else:
            st.info("Risk Level\n\nNot provided")

    with col3:
        if confidence == "High":
            st.success("🟢 Confidence\n\nHigh")
        elif confidence == "Medium":
            st.warning("🟡 Confidence\n\nMedium")
        elif confidence == "Low":
            st.error("🔴 Confidence\n\nLow")
        else:
            st.info("Confidence\n\nNot provided")

def render_ai_sections(parsed_sections):
    st.subheader("AI-Assisted Requirement Analysis")

    for section_name, content in parsed_sections.items():

        if section_name == "Requirement Quality Score":
            with st.expander(section_name, expanded=False):
                if content:
                    st.write(content)
                else:
                    st.write("No content returned.")

        elif section_name == "Risk Signals":
            with st.expander("Risk Signals", expanded=False):
                if content:
                    st.write(content)
                else:
                    st.write("No content returned.")

        else:
            with st.expander(section_name, expanded=(section_name == "Quality Analysis")):
                if content:
                    st.write(content)
                else:
                    st.write("No content returned.")

def generate_test_design(prompt):
    """Call OpenAI and return the generated output."""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text

def download_test_design(jira_ticket, parsed_sections):
    markdown_output = f"# Test Design\n\n"
    markdown_output += f"Ticket: {jira_ticket if jira_ticket else 'No JIRA ticket provided'}\n\n"

    for section_name, content in parsed_sections.items():
        markdown_output += f"## {section_name}\n"
        markdown_output += f"{content if content else 'No content returned.'}\n\n"

    st.download_button(
        label="Download Test Design",
        data=markdown_output,
        file_name=f"{jira_ticket}_test_design.md" if jira_ticket else "test_design.md",
        mime="text/markdown"
    )

# -----------------------------
# Streamlit app
# -----------------------------
def main():
    st.title("Specs to Tests - AI Test Design Assistant")

    if "feature_text" not in st.session_state:
        st.session_state.feature_text = ""

    jira_ticket = st.text_input("Jira Ticket ID (optional)", placeholder="KAN-4")
    jira_ticket = jira_ticket.strip().upper()

    audio_value = st.audio_input("Record your requirement (optional)")
    update_text_from_audio(audio_value)

    feature_text = st.text_area(
        "Describe the feature, API, or requirement",
        key="feature_text",
        height=200
    )

    feature_type = st.selectbox(
        "Feature Type",
        ["UI Feature", "API Endpoint", "Authentication Flow", "File Upload", "Payment Flow"]
    )

    if st.button("Analyze Requirement & Generate Test Strategy"):
        manual_text = feature_text.strip()

        jira_context, issue_data, error = build_jira_context(jira_ticket)
        if error:
            st.error(error)
            st.stop()

        if jira_context:
            st.success("Jira ticket loaded successfully.")

        if issue_data:
            st.subheader("Requirement Preview")
            st.write(f"**Ticket ID:** {jira_ticket}")
            st.write(f"**Summary:** {issue_data['summary']}")
            st.write("**Description:**")
            st.write(issue_data['description'])

        if not manual_text and not jira_context:
            st.error("Please enter text, record voice, or provide a Jira ticket ID.")
            st.stop()    

        combined_requirement = build_requirement_context(manual_text, jira_context)
        prompt = build_prompt(feature_type, combined_requirement)
        output = generate_test_design(prompt)    

        parsed_sections = parse_ai_output(output)
        
        # Show input sources used
        source_parts = []

        if jira_ticket:
            source_parts.append(f"Jira: {jira_ticket}")

        if manual_text:
            source_parts.append("Manual Notes")

        if audio_value:
            source_parts.append("Voice Input")

        if source_parts:
            st.info("Input Sources: " + " | ".join(source_parts)) 
        
        
        render_readiness_summary(parsed_sections)
        render_ai_sections(parsed_sections)

        download_test_design(jira_ticket, parsed_sections)
        

if __name__ == "__main__":
    main()