"""
Skill: Video Resize
Convert video aspect ratio from 16:9 → 9:16 with smart center-crop.
"""

from utils.ffmpeg_utils import resize_vertical


def resize_to_vertical(
    video_path: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
) -> str:
    """
    Resize video to vertical 9:16 format for social media.

    Uses center-crop strategy to fill the vertical frame.
    Future improvement: smart crop following active speaker.

    Args:
        video_path: Path to source video (typically 16:9)
        output_path: Path for output vertical video
        width: Target width (default 1080)
        height: Target height (default 1920)

    Returns:
        Path to the resized video
    """
    return resize_vertical(
        video_path=video_path,
        output_path=output_path,
        width=width,
        height=height,
    )
