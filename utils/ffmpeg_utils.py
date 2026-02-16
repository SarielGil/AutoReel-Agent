"""
FFmpeg Utility Functions
Wrapper around FFmpeg for common video/audio operations.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Union

def extract_audio(
    video_path: str,
    output_path: Optional[str] = None,
    speed_factor: float = 1.0,
    sample_rate: int = 16000,
    channels: int = 1,
) -> str:
    """
    Extract audio from video file, optionally speed it up.

    Sends only the audio track to reduce compute — no video data is processed.
    Speed factor of 2.0 halves transcription time while maintaining Whisper accuracy.

    Args:
        video_path: Path to input video file
        output_path: Path for output audio file (default: same dir as video, .wav)
        speed_factor: Speed multiplier (2.0 = double speed, 1.0 = normal)
        sample_rate: Audio sample rate (16000 optimal for Whisper)
        channels: Number of audio channels (1 = mono)

    Returns:
        Path to the extracted audio file
    """
    video_path = Path(video_path)
    if output_path is None:
        suffix = f"_x{speed_factor}" if speed_factor != 1.0 else ""
        output_path = str(video_path.parent / f"{video_path.stem}{suffix}.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                          # No video — audio only
        "-ac", str(channels),           # Mono
        "-ar", str(sample_rate),        # 16kHz for Whisper
    ]

    # Apply speed factor if not 1.0
    if speed_factor != 1.0:
        cmd.extend(["-af", f"atempo={speed_factor}"])

    cmd.append(output_path)

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def cut_clip(
    video_path: str,
    output_path: str,
    start: float,
    end: float,
    reencode: bool = True,
) -> str:
    """
    Cut a clip from a video at precise timestamps.

    Args:
        video_path: Path to source video
        output_path: Path for output clip
        start: Start time in seconds
        end: End time in seconds
        reencode: If True, re-encode for frame-accurate cuts

    Returns:
        Path to the extracted clip
    """
    duration = end - start

    cmd = ["ffmpeg", "-y"]

    if reencode:
        cmd.extend([
            "-ss", str(start),
            "-i", str(video_path),
            "-t", str(duration),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "ultrafast",
            "-c:a", "aac",
            output_path,
        ])
    else:
        # Stream copy (fast but may not be frame-accurate)
        cmd.extend([
            "-ss", str(start),
            "-i", str(video_path),
            "-t", str(duration),
            "-c", "copy",
            output_path,
        ])

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def resize_vertical(
    video_path: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    crf: int = 23,
    preset: str = "medium",
) -> str:
    """
    Resize video to vertical 9:16 format with smart center-crop.

    Args:
        video_path: Path to source video
        output_path: Path for output video
        width: Target width (default 1080)
        height: Target height (default 1920)
        crf: Constant Rate Factor (0-51, lower is better quality, 23 is default, 28-30 good for mobile)
        preset: FFmpeg compression preset (speed vs quality: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)

    Returns:
        Path to the resized video
    """
    # Scale to fill, then center-crop
    filter_str = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", filter_str,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-c:a", "aac",
        "-b:a", "128k",
        output_path,
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def burn_subtitles(
    video_path: str,
    subtitle_path: str,
    output_path: str,
) -> str:
    """
    Burn (hardcode) subtitles into the video frames.

    Args:
        video_path: Path to source video
        subtitle_path: Path to .srt or .ass subtitle file
        output_path: Path for output video

    Returns:
        Path to the video with burned-in subtitles
    """
    # Escape path for FFmpeg filter
    escaped_sub = str(subtitle_path).replace(":", r"\:").replace("\\", "/")

    if subtitle_path.endswith(".ass"):
        filter_str = f"ass={escaped_sub}"
    else:
        filter_str = f"subtitles={escaped_sub}"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", filter_str,
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Warning: Subtitle burning failed: {e.stderr.decode()}")
        print("Falling back to copying video without subtitles...")
        import shutil
        shutil.copy2(video_path, output_path)
    
    return output_path


def get_video_duration(video_path: str) -> float:
    """Get the duration of a video file in seconds."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(video_path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def get_video_info(video_path: str) -> dict:
    """Get video metadata (resolution, duration, codec, etc.)."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    import json
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)
