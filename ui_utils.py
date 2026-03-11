import re
import streamlit as st
from ai_utils import extract_quality_score, extract_risk_level

def render_requirement_preview(jira_ticket, issue_data):
    if issue_data:
        st.subheader("Requirement Preview")
        st.write(f"**Ticket ID:** {jira_ticket}")
        st.write(f"**Summary:** {issue_data['summary']}")
        st.write("**Description:**")
        st.write(issue_data['description']) 

def render_input_sources(jira_ticket, manual_text, audio_value):
    source_parts = []

    if jira_ticket:
        source_parts.append(f"Jira: {jira_ticket}")
    if manual_text:
        source_parts.append("Manual Notes")
    if audio_value:
        source_parts.append("Voice Input")

    if source_parts:
        st.info("Input Sources: " + " | ".join(source_parts))   
def show_jira_issue(issue):
    st.subheader(issue["key"])
    st.write(issue["summary"])
    st.write(issue["description"])

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

def download_test_design(jira_ticket, parsed_sections):
    markdown_output = "# Test Design\n\n"
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
    st.set_page_config(
        page_title="JIRA Assistant",
        page_icon="📋",
        layout="wide"
    )


