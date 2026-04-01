import streamlit as st
from jira_utils import build_jira_context
from audio_utils import update_text_from_audio
from ai_utils import (
    build_requirement_context,
    call_openai_api
)
from ui_utils import (
    render_readiness_summary,
    render_ai_sections,
    download_test_design,
    render_input_sources,
    render_requirement_preview,
    render_testing_readiness_decision
)

from llm.parsing import parse_ai_output
from llm.prompts import build_prompt

FEATURE_TYPES = [
    "UI Feature",
    "API Endpoint",
    "Authentication Flow",
    "File Upload",
    "Payment Flow",
]

def main():
    st.title("ReqScope AI — AI Requirement Analyzer & Test Strategy Generator")

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

    feature_type = st.selectbox("Feature Type", FEATURE_TYPES)

    if st.button("Analyze Requirement & Generate Test Strategy"):
        manual_text = feature_text.strip()

        jira_context, issue_data, error = build_jira_context(jira_ticket)
        if error:
            st.error(error)
            st.stop()

        if jira_context:
            st.success("Jira ticket loaded successfully.")

        if not manual_text and not jira_context:
            st.error("Please enter text, record voice, or provide a Jira ticket ID.")
            st.stop()

        combined_requirement = build_requirement_context(manual_text, jira_context)
        prompt = build_prompt(feature_type, combined_requirement)
        
        try:
            with st.spinner("Analyzing requirement and generating test strategy..."):
                output = call_openai_api(prompt)
                parsed_sections = parse_ai_output(output)
        except Exception as e:
            st.error(f"Failed to generate analysis: {e}")
            st.stop()      
        
        render_requirement_preview(jira_ticket, issue_data)
        render_input_sources(jira_ticket, manual_text, audio_value)
        render_readiness_summary(parsed_sections)
        render_testing_readiness_decision(parsed_sections)
        render_ai_sections(parsed_sections)
        download_test_design(jira_ticket, parsed_sections)


if __name__ == "__main__":
    main()