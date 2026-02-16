"""
Skill: Platform Export
Format final clips per platform specification (duration, resolution, codec).
"""

from pathlib import Path
from typing import Optional

# Platform specs
PLATFORM_SPECS = {
    "instagram": {
        "max_duration": 90,
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "codec": "libx264",
        "audio_codec": "aac",
        "max_file_size_mb": 100,
    },
    "tiktok": {
        "max_duration": 180,
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "codec": "libx264",
        "audio_codec": "aac",
        "max_file_size_mb": 287,
    },
    "youtube_shorts": {
        "max_duration": 60,
        "aspect_ratio": "9:16",
        "resolution": (1080, 1920),
        "codec": "libx264",
        "audio_codec": "aac",
        "max_file_size_mb": 256,
    },
}


def get_platform_spec(platform: str) -> dict:
    """Get the specification for a given platform."""
    if platform not in PLATFORM_SPECS:
        raise ValueError(f"Unknown platform: {platform}. Available: {list(PLATFORM_SPECS.keys())}")
    return PLATFORM_SPECS[platform]


def validate_for_platform(video_path: str, platform: str) -> dict:
    """
    Validate a video file against platform requirements.

    Args:
        video_path: Path to video file
        platform: Platform name

    Returns:
        Dict with validation results: {valid: bool, issues: list[str]}
    """
    from utils.ffmpeg_utils import get_video_duration, get_video_info

    spec = get_platform_spec(platform)
    issues = []

    # Check duration
    duration = get_video_duration(video_path)
    if duration > spec["max_duration"]:
        issues.append(
            f"Duration {duration:.0f}s exceeds {platform} max of {spec['max_duration']}s"
        )

    # Check file size
    file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
    if file_size_mb > spec["max_file_size_mb"]:
        issues.append(
            f"File size {file_size_mb:.1f}MB exceeds {platform} max of {spec['max_file_size_mb']}MB"
        )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "duration": duration,
        "file_size_mb": file_size_mb,
    }
