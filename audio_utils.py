import streamlit as st

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