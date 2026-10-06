from pathlib import Path
import wave

from piper import PiperVoice


MODEL_PATH = Path("models/piper/en_US-lessac-medium.onnx")


def synthesize_speech(text: str, output_path: str) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("TTS text must be a non-empty string.")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Piper model not found: {MODEL_PATH}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    voice = PiperVoice.load(str(MODEL_PATH))

    with wave.open(str(output_file), "wb") as wav_file:
        voice.synthesize_wav(text.strip(), wav_file)

    return {
        "audio_path": str(output_file),
        "audio_format": "wav",
        "synthetic": True,
    }


if __name__ == "__main__":
    result = synthesize_speech(
        "This is a Day 18 text to speech test generated using a synthetic voice.",
        "day18_tts_module_test.wav",
    )

    print("Audio path:", result["audio_path"])
    print("Audio format:", result["audio_format"])
    print("Synthetic voice:", result["synthetic"])