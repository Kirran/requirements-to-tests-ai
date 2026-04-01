import re
import streamlit as st
from llm.parsing import extract_quality_score, extract_risk_level
from decision.readiness import extract_confidence_level, build_testing_readiness_decision
from llm.schema import SECTION_SCHEMA

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

# def show_jira_issue(issue):
#     st.subheader(issue["key"])
#     st.write(issue["summary"])
#     st.write(issue["description"])

def render_readiness_summary(parsed_sections):

    quality_text = parsed_sections.get("quality_score", "")
    risk_text = parsed_sections.get("risks", "")

    score = extract_quality_score(quality_text)
    risk_level = extract_risk_level(risk_text)
    confidence = extract_confidence_level(quality_text)
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

    hidden_sections = {
        "quality_score",
        "testing_readiness_notes",
    }  
    
    display_names = {
        "root_cause_signals": "Potential Failure Causes",
    }
    analysis_sections = [
        "quality_assessment",
        "requirement_summary",
        "gaps",
        "risks",
        "test_strategy",
    ]

    test_sections = [
        "functional_tests",
        "negative_tests",
        "edge_cases",
        "security_tests",
    ]

    engineering_sections = [
        "root_cause_signals",
        "observability",
        "feature_type_guidance",
    ]

    def render_group(title, section_keys):
        st.markdown(f"### {title}")
        for section_key in section_keys:
            if section_key in hidden_sections:
                continue

            content = parsed_sections.get(section_key, "")
            label = display_names.get(section_key, SECTION_SCHEMA.get(section_key, section_key))

            with st.expander(label, expanded=(section_key == "quality_assessment")):
                if content:
                    st.write(content)
                else:
                    st.write("No content returned.")

    render_group("Analysis", analysis_sections)
    render_group("Test Strategy", test_sections)
    render_group("Engineering Considerations", engineering_sections)

def render_testing_readiness_decision(parsed_sections: dict):
    decision_data = build_testing_readiness_decision(parsed_sections)

    st.subheader("Testing Readiness Decision")

    title = f"{decision_data['icon']} {decision_data['decision']}"
    summary = decision_data["summary"]

    score = decision_data["score"]
    risk_level = decision_data["risk_level"] or "Not provided"
    confidence = decision_data["confidence"] or "Not provided"

    if decision_data["decision"] == "Ready for Testing":
        st.success(title)
    elif decision_data["decision"] == "Testable with Minor Gaps":
        st.warning(title)
    elif decision_data["decision"] == "Requires Clarification":
        st.warning(title)
    else:
        st.error(title)

    st.write(summary)
    st.divider()

def download_test_design(jira_ticket, parsed_sections):
    markdown_output = "# Test Design\n\n"
    markdown_output += f"Ticket: {jira_ticket if jira_ticket else 'No JIRA ticket provided'}\n\n"

    for section_key, content in parsed_sections.items():
        label = SECTION_SCHEMA.get(section_key, section_key)
        markdown_output += f"## {label}\n"
        markdown_output += f"{content if content else 'No content returned.'}\n\n"
    
    st.download_button(
        label="Download Test Design",
        data=markdown_output,
        file_name=f"{jira_ticket}_test_design.md" if jira_ticket else "test_design.md",
        mime="text/markdown"
    )


