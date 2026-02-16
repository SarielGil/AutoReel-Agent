"""
Skill: Subtitle Burn
Burn (hardcode) styled subtitles into video frames using FFmpeg.
"""

from utils.ffmpeg_utils import burn_subtitles


def burn_subtitles_into_video(
    video_path: str,
    subtitle_path: str,
    output_path: str,
) -> str:
    """
    Burn subtitles into video frames.

    Hardcodes the subtitles directly into the video so they
    display on any player without needing subtitle track support.

    Args:
        video_path: Path to source video
        subtitle_path: Path to .srt or .ass subtitle file
        output_path: Path for output video

    Returns:
        Path to the video with burned-in subtitles
    """
    return burn_subtitles(
        video_path=video_path,
        subtitle_path=subtitle_path,
        output_path=output_path,
    )
