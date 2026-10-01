from pathlib import Path


ALLOWED_AUDIO_EXTENSIONS = {
    ".m4a",
    ".wav",
    ".mp3",
    ".ogg",
}

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024


def validate_audio_file(filename: str, file_size: int) -> dict:
    if not filename:
        return {
            "valid": False,
            "error_code": "EMPTY_FILENAME",
            "message": "Audio filename is required.",
        }

    if file_size <= 0:
        return {
            "valid": False,
            "error_code": "EMPTY_AUDIO",
            "message": "Audio file is empty.",
        }

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        return {
            "valid": False,
            "error_code": "UNSUPPORTED_AUDIO_TYPE",
            "message": (
                "Unsupported audio type. "
                "Supported formats are .m4a, .wav, .mp3, and .ogg."
            ),
        }

    if file_size > MAX_AUDIO_SIZE_BYTES:
        return {
            "valid": False,
            "error_code": "AUDIO_TOO_LARGE",
            "message": "Audio file exceeds the maximum allowed size of 10 MB.",
        }

    return {
        "valid": True,
        "error_code": None,
        "message": "Audio file is valid.",
    }