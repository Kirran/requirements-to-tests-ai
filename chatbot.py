import os
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title("AI Test Design Assistant")

# Initialize editable input in session state
if "feature_text" not in st.session_state:
    st.session_state.feature_text = ""

audio_value = st.audio_input("Record your requirement")

if audio_value is not None:
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_value.read())

    with open("temp_audio.wav", "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    # Put transcript into the same editable input
    st.session_state.feature_text = transcription.text

feature = st.text_area(
    "Describe the feature, API, or requirement",
    key="feature_text",
    height=200
)

feature_type = st.selectbox(
    "Feature Type",
    ["UI Feature", "API Endpoint", "Authentication Flow", "File Upload", "Payment Flow"]
)

if st.button("Generate Test Design") and feature.strip():
    prompt = f"""
You are a senior QA engineer.

Analyze this requirement and produce structured outputs.

Requirement:
{feature}

Feature Type: {feature_type}

Return sections:
1. Functional Test Cases
2. Negative Test Cases
3. Edge Cases
4. Security Test Cases
5. Requirement Gaps
6. Risk Areas
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    st.subheader("AI Generated Test Design")
    st.write(response.output_text)