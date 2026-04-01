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
    risk_text = parsed_sections.get("Engineering Risks", "")

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

def extract_confidence_level(text: str) -> str | None:
    if not text:
        return None

    match = re.search(
        r"Confidence in Requirement Completeness:\s*(Low|Medium|High)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).capitalize()
    return None

def build_testing_readiness_decision(parsed_sections: dict) -> dict:
    quality_text = parsed_sections.get("Requirement Quality Score", "")
    gaps_text = parsed_sections.get("Requirement Gaps", "")
    risk_text = parsed_sections.get("Engineering Risks", "")

    score = extract_quality_score(quality_text)
    risk_level = extract_risk_level(risk_text)
    confidence = extract_confidence_level(quality_text)

    gap_count = 0
    if gaps_text:
        gap_count = len([
            line for line in gaps_text.splitlines()
            if line.strip().startswith("-") or line.strip().startswith("•")
        ])
    
    if risk_level is None and score is not None:
        if score >= 8:
            risk_level = "Low"
        elif score >= 5:
            risk_level = "Medium"
        else:
            risk_level = "High"


    decision = "Needs Review"
    icon = "⚠️"
    summary = "The requirement needs additional review before reliable testing can begin."

    if score is None:
        return {
            "decision": decision,
            "icon": icon,
            "summary": summary,
            "score": None,
            "risk_level": risk_level,
            "confidence": confidence,
        }

    if risk_level is None and score is not None:
        if score >= 8:
            risk_level = "Low"
        elif score >= 5:
            risk_level = "Medium"
        else:
            risk_level = "High"

    if score >= 8 and risk_level == "Low" and gap_count <= 1:
        decision = "Ready for Testing"
        icon = "✅"
        summary = "The requirement appears sufficiently clear and testable for implementation and validation."
    elif score >= 6 and risk_level in {"Low", "Medium"} and gap_count <= 3:
        decision = "Testable with Minor Gaps"
        icon = "🟡"
        summary = "The requirement is mostly testable, but a few details should be clarified before execution."
    elif score >= 4:
        decision = "Requires Clarification"
        icon = "⚠️"
        summary = "The requirement is only partially testable because important details or edge cases are missing."
    else:
        decision = "Not Ready for Testing"
        icon = "⛔"
        summary = "The requirement is not test-ready and should be refined before formal test design begins."

    return {
        "decision": decision,
        "icon": icon,
        "summary": summary,
        "score": score,
        "risk_level": risk_level,
        "confidence": confidence,
    }

def render_ai_sections(parsed_sections):
    st.subheader("AI-Assisted Requirement Analysis")

    hidden_sections = {
        "Requirement Quality Score",
        "Testing Readiness Notes",
    }  
    
    display_names = {
        "Root Cause Signals": "Potential Failure Causes",
    }
    analysis_sections = [
        "Requirement Quality Assessment",
        "Requirement Summary",
        "Requirement Gaps & Suggested Improvements",
        "Engineering Risks",
        "Test Strategy Summary",
    ]

    test_sections = [
        "Functional Test Cases",
        "Negative Test Cases",
        "Edge Cases",
        "Security Test Cases",
    ]

    engineering_sections = [
        "Root Cause Signals",
        "Observability / Logging Recommendations",
    ]

    def render_group(title, section_list):
        st.markdown(f"### {title}")
        for section_name in section_list:
            if section_name in hidden_sections:
                continue

            content = parsed_sections.get(section_name, "")
            label = display_names.get(section_name, section_name)

            with st.expander(label, expanded=(section_name == "Requirement Quality Assessment")):
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


