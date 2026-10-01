from faster_whisper import WhisperModel


MODEL_SIZE = "small.en"

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8",
)


def transcribe_audio(file_path: str) -> dict:
    segments, info = model.transcribe(
        file_path,
        language="en",
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500,
        },
        no_speech_threshold=0.6,
    )

    transcript = " ".join(
        segment.text.strip()
        for segment in segments
        if segment.text.strip()
    ).strip()

    return {
        "transcript": transcript,
        "language": info.language,
    }


if __name__ == "__main__":
    result = transcribe_audio("day17_clear.m4a")

    print("Detected language:", result["language"])
    print("Transcript:", result["transcript"])