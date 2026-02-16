"""
Skill: Audio Extraction
Extract audio track from video file using FFmpeg.
Sends only audio to the transcription model — no video data.
Supports optional speedup (2x) to reduce transcription compute.
"""

from utils.ffmpeg_utils import extract_audio


def extract_audio_from_video(
    video_path: str,
    speed_factor: float = 2.0,
    sample_rate: int = 16000,
    channels: int = 1,
    output_path: str | None = None,
) -> str:
    """
    Extract audio-only from video, optimized for Whisper transcription.

    Key optimizations:
    - No video data processed (audio-only extraction)
    - Optional speed-up (default 2x) halves compute time
    - Mono 16kHz output - optimal for Whisper

    Args:
        video_path: Path to input video
        speed_factor: Audio speed multiplier (2.0 = 2x faster, halves compute)
        sample_rate: Output sample rate (16000 optimal for Whisper)
        channels: Audio channels (1 = mono)
        output_path: Optional custom output path

    Returns:
        Path to the extracted audio file (.wav)
    """
    return extract_audio(
        video_path=video_path,
        output_path=output_path,
        speed_factor=speed_factor,
        sample_rate=sample_rate,
        channels=channels,
    )
