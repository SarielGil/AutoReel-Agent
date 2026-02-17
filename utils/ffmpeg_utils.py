"""
FFmpeg Utility Functions
Wrapper around FFmpeg for common video/audio operations.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Union, List

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


def concat_videos(
    video_paths: List[str],
    output_path: str,
) -> str:
    """
    Concatenate multiple video files into one.
    Uses the concat demuxer (requires all videos to have same parameters).
    
    Args:
        video_paths: List of paths to video files
        output_path: Path for the combined output video
    """
    if not video_paths:
        raise ValueError("No video paths provided for concatenation")
    
    # Create a temporary file list for FFmpeg
    list_file = Path(output_path).with_suffix(".txt")
    with open(list_file, "w") as f:
        for path in video_paths:
            # Absolute path with escaped single quotes for FFmpeg
            abs_path = str(Path(path).absolute()).replace("'", "'\\''")
            f.write(f"file '{abs_path}'\n")
            
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",  # Fast concat without re-encoding
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during concatenation: {e.stderr.decode()}")
        raise
    finally:
        if list_file.exists():
            list_file.unlink()
            
    return output_path


def concat_segments_visual(
    video_path: str,
    segments: List[dict],
    output_path: str,
) -> str:
    """
    Concatenate video segments using a complex filter graph.
    This avoids creating intermediate files but requires re-encoding.
    
    Args:
        video_path: Source video path
        segments: List of dicts with 'start' and 'end' keys
        output_path: Path for output video
    """
    if not segments:
        return ""

    inputs = []
    filter_parts = []
    
    # We add the same input once because we'll refer to [0:v] and [0:a]
    cmd = ["ffmpeg", "-y", "-i", str(video_path)]
    
    for i, seg in enumerate(segments):
        start = seg['start']
        end = seg['end']
        # Video trim + setpts
        filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
        # Audio trim + asetpts
        filter_parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")

    # The concat part
    concat_ins = ""
    for i in range(len(segments)):
        concat_ins += f"[v{i}][a{i}]"
    
    concat_filter = f"{concat_ins}concat=n={len(segments)}:v=1:a=1[outv][outa]"
    
    full_filter = ";".join(filter_parts) + ";" + concat_filter
    
    cmd.extend([
        "-filter_complex", full_filter,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "superfast",
        "-crf", "23",
        "-c:a", "aac",
        str(output_path)
    ])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Concatenation failed: {e.stderr.decode()}")
        raise

    return output_path
