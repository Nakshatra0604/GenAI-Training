import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
stt_model = os.getenv("STT_MODEL")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

with open("day17_clear.m4a", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model=stt_model,
        file=audio_file,
    )

print("Transcript:")
print(transcript.text)
