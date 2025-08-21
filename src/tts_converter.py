import os
import re
import requests
import json
from dotenv import load_dotenv
from pydub import AudioSegment
from io import BytesIO
import time
import base64

# Load environment variables from .env file
load_dotenv()

# Initialize Murf API credentials
MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_BASE_URL = "https://api.murf.ai/v1"

# Define voice IDs for different speakers (Murf voice IDs)
VOICE_MAP = {"HOST": "en-US-ken", "GUEST": "en-US-natalie", "DEFAULT": "en-US-charles"}

# Define default voice settings for Murf
DEFAULT_VOICE_SETTINGS = {
    "speed": 0,
    "pitch": 0,
    "emphasis": 0,
    "pause": 300,
}


def convert_text_to_audio_segment(text: str, voice_id: str) -> AudioSegment:
    """Converts text to an AudioSegment using Murf API, handling both encodedAudio and audioContent."""
    if not text.strip():
        return AudioSegment.empty()

    payload = {
        "voiceId": voice_id,
        "text": text.strip(),
        "speed": DEFAULT_VOICE_SETTINGS["speed"],
        "pitch": DEFAULT_VOICE_SETTINGS["pitch"],
        "format": "MP3",
        "sampleRate": 24000,
        "encodeAsBase64": True,
    }
    headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}

    resp = requests.post(
        f"{MURF_BASE_URL}/speech/generate", headers=headers, json=payload
    )
    if resp.status_code != 200:
        print(f"API Error {resp.status_code}: {resp.text}")
        return AudioSegment.empty()

    result = resp.json()
    b64 = None

    # Murf may return either of these:
    if "audioContent" in result and result["audioContent"]:
        b64 = result["audioContent"]
    elif "encodedAudio" in result and result["encodedAudio"]:
        b64 = result["encodedAudio"]
    elif "url" in result and result["url"]:
        # fallback to URL
        url_resp = requests.get(result["url"])
        if url_resp.status_code == 200:
            return AudioSegment.from_file(BytesIO(url_resp.content), format="mp3")
        else:
            print(f"Failed to fetch from URL: {url_resp.status_code}")
            return AudioSegment.empty()
    else:
        print("No audioContent, encodedAudio, or URL in response.")
        return AudioSegment.empty()

    # decode base64
    try:
        audio_data = base64.b64decode(b64)
        return AudioSegment.from_file(BytesIO(audio_data), format="mp3")
    except Exception as e:
        print("Error decoding audio:", e)
        return AudioSegment.empty()


def synthesize_conversation(
    conversation_text: str, output_filename: str = "conversation_output.mp3"
) -> str:
    segments = re.findall(
        r"\[(HOST|GUEST)\]\s*(.*?)(?=\[(?:HOST|GUEST)\]|$)",
        conversation_text,
        re.DOTALL,
    )
    if not segments:
        # no tags → default voice
        audio = convert_text_to_audio_segment(conversation_text, VOICE_MAP["DEFAULT"])
        if not audio:
            return ""
        audio.export(output_filename, format="mp3")
        return output_filename

    combined = AudioSegment.empty()
    for tag, txt in segments:
        vid = VOICE_MAP.get(tag.upper(), VOICE_MAP["DEFAULT"])
        clean = re.sub(r"\s+", " ", txt.strip())
        seg = convert_text_to_audio_segment(clean, vid)
        if seg:
            combined += seg + AudioSegment.silent(duration=500)
        time.sleep(0.5)

    if combined:
        os.makedirs(os.path.dirname(output_filename) or ".", exist_ok=True)
        combined.export(output_filename, format="mp3")
        return output_filename
    return ""


if __name__ == "__main__":
    # Optional: print available voices to confirm your IDs
    def list_voices():
        hdr = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
        r = requests.get(f"{MURF_BASE_URL}/speech/voices", headers=hdr)
        print("Voices:", r.status_code, r.text)

    # list_voices()

    convo = """
    [HOST] Welcome to the podcast! Today, we have a very special guest.
    [GUEST] Thanks for having me — excited to chat!
    [HOST] Let’s dive in.
    """
    out = synthesize_conversation(convo, "outputs/podcast_episode.mp3")
    if out:
        print("Audio generated at", out)
    else:
        print("Failed to generate audio.")
