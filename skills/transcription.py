"""
Skill: Hebrew Transcription
Transcribe Hebrew audio using ivrit-ai/whisper-large-v3 fine-tuned Whisper model.
Returns timestamped segments with text and confidence scores.
"""

from typing import Optional


def transcribe_hebrew(
    audio_path: str,
    model_name: str = "ivrit-ai/whisper-large-v3",
    device: str = "cuda",
    language: str = "he",
) -> list[dict]:
    """
    Transcribe Hebrew audio using a fine-tuned Whisper model.

    Uses ivrit-ai/whisper-large-v3 which has ~63% better WER
    for Hebrew compared to vanilla Whisper large-v3.

    Args:
        audio_path: Path to audio file (.wav, mono 16kHz recommended)
        model_name: Hugging Face model name
        device: "cuda" or "cpu"
        language: Language code (default "he" for Hebrew)

    Returns:
        List of segment dicts with keys: start, end, text, confidence
    """
    # Use transformers pipeline for ivrit-ai model
    from transformers import pipeline
    import torch

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device=device,
    )

    result = pipe(
        audio_path,
        return_timestamps=True,
        generate_kwargs={
            "language": language,
            "task": "transcribe",
        },
    )

    # Convert to standardized segment format
    segments = []
    for i, chunk in enumerate(result.get("chunks", [])):
        timestamps = chunk.get("timestamp", (0, 0))
        segments.append({
            "start": timestamps[0] if timestamps[0] is not None else 0,
            "end": timestamps[1] if timestamps[1] is not None else 0,
            "text": chunk.get("text", "").strip(),
            "confidence": None,  # Whisper pipeline doesn't expose per-segment confidence
        })

    return segments
