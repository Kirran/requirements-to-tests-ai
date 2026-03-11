import streamlit as st
from openai import OpenAI
client = OpenAI()

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
    """Append transcribed audio into the editable text box once per recording."""
    if audio_value is None:
        return

    # Use file size as a simple "id" for the current recording
    audio_size = getattr(audio_value, "size", None)
    last_size = st.session_state.get("last_audio_size")

    # If we've already processed this exact recording, do nothing
    if audio_size is not None and last_size == audio_size:
        return

    transcript = transcribe_audio(audio_value)

    if st.session_state.feature_text.strip():
        st.session_state.feature_text += "\n" + transcript
    else:
        st.session_state.feature_text = transcript

     # Remember that we've consumed this recording
    if audio_size is not None:
        st.session_state.last_audio_size = audio_size