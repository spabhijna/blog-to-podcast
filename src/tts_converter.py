import os
import re
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Initialize ElevenLabs client with API key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Define voice IDs for different speakers
VOICE_MAP = {
    "HOST": "9BWtsMINqrJLrRacOk9x",
    "GUEST": "IKne3meq5aSn9XLyUdCD",
    "DEFAULT": "N2lVS1w4EtoT3dr4eOWO"
}

# Define default voice settings
DEFAULT_VOICE_SETTINGS = VoiceSettings(
    stability=0.0,
    similarity_boost=1.0,
    style=0.0,
    use_speaker_boost=True,
    speed=1.0,
)

def convert_text_to_audio_segment(text: str, voice_id: str) -> AudioSegment:
    """Converts text to an audio segment using ElevenLabs."""
    if not text or not text.strip():
        return AudioSegment.empty()

    try:
        response = elevenlabs.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_22050_32",
            text=text.strip(),
            model_id="eleven_turbo_v2_5",
            voice_settings=DEFAULT_VOICE_SETTINGS,
        )

        audio_chunks = []
        for chunk in response:
            if chunk:
                audio_chunks.append(chunk)

        if audio_chunks:
            audio_bytes = b"".join(audio_chunks)
            if len(audio_bytes) > 0:
                audio_buffer = BytesIO(audio_bytes)
                return AudioSegment.from_file(audio_buffer, format="mp3")

        return AudioSegment.empty()

    except Exception as e:
        print(f"Error during TTS conversion: {e}")
        return AudioSegment.empty()

def synthesize_conversation(conversation_text: str, output_filename: str = "conversation_output.mp3") -> str:
    """
    Parses conversation text, synthesizes audio for different speakers,
    and combines them into a single MP3 file.
    """
    # Find speaker tags and their text
    segments = re.findall(r"\[(HOST|GUEST)\]\s*(.*?)(?=\[(?:HOST|GUEST)\]|$)", conversation_text, re.DOTALL)

    if not segments:
        # No speaker tags found, use default voice
        combined_audio = convert_text_to_audio_segment(conversation_text, VOICE_MAP["DEFAULT"])
        if len(combined_audio) > 0:
            combined_audio.export(output_filename, format="mp3")
            return output_filename
        return ""

    combined_audio = AudioSegment.empty()

    for speaker_tag, text_content in segments:
        speaker_tag = speaker_tag.upper()
        voice_id = VOICE_MAP.get(speaker_tag, VOICE_MAP["DEFAULT"])

        # Clean up text content
        clean_text = text_content.strip()
        clean_text = re.sub(r"\[.*?\]", "", clean_text)  # Remove sound cues in brackets
        clean_text = re.sub(r"\s+", " ", clean_text)  # Normalize whitespace

        if not clean_text:
            continue

        audio_segment = convert_text_to_audio_segment(clean_text, voice_id)
        if len(audio_segment) > 0:
            combined_audio += audio_segment

    if len(combined_audio) > 0:
        combined_audio.export(output_filename, format="mp3")
        return output_filename

    return ""

# Example usage
if __name__ == "__main__":
    conversation_example = """
[HOST] Welcome to the podcast! Today, we have a very special guest with us. How are you doing today?
[GUEST] I'm doing great, thank you for having me! It's wonderful to be here.
[HOST] It's our pleasure. We're going to talk about some exciting new developments in AI.
[GUEST] Yes, I'm really looking forward to diving into that.
[HOST] Fantastic. Let's start with your latest research.
"""

    output_path = synthesize_conversation(conversation_example, "outputs/podcast_episode.mp3")
    if output_path:
        print(f"Audio file created: {output_path}")
    else:
        print("Failed to create audio file")