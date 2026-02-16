"""
Skill: Clip Extraction
Cut precise video segments at given start/end timestamps using FFmpeg.
"""

from utils.ffmpeg_utils import cut_clip


def extract_clip(
    video_path: str,
    output_path: str,
    start: float,
    end: float,
) -> str:
    """
    Extract a video clip at precise timestamps.

    Uses FFmpeg re-encoding for frame-accurate cuts.

    Args:
        video_path: Path to source video
        output_path: Path for output clip
        start: Start time in seconds
        end: End time in seconds

    Returns:
        Path to the extracted clip
    """
    return cut_clip(
        video_path=video_path,
        output_path=output_path,
        start=start,
        end=end,
        reencode=True,  # Frame-accurate
    )
