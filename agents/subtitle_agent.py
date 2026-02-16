"""
📝 Subtitle Agent
Generates styled Hebrew subtitles (RTL) for each clip and
burns them into the video frames.
"""

from pathlib import Path
from typing import Optional
import yaml

from models import Clip, Reel, Transcript, Platform
from skills.subtitle_generation import generate_subtitles
from skills.subtitle_burn import burn_subtitles_into_video


class SubtitleAgent:
    """
    Agent responsible for generating Hebrew subtitles and
    burning them into the final reel clips.
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def process(
        self,
        clips: list[Clip],
        transcript: Transcript,
        platforms: Optional[list] = None,
    ) -> list[Reel]:
        """
        Add Hebrew subtitles to clips and export as final reels.

        For each clip:
        1. Extract relevant transcript segments for the clip's time range
        2. Generate styled SRT/ASS subtitles with Hebrew RTL support
        3. Burn subtitles into the video
        4. Export platform-specific versions

        Args:
            clips: List of extracted video clips
            transcript: Full transcript for subtitle text
            platforms: Target platforms (default: all)

        Returns:
            List of final Reel objects ready for upload
        """
        if platforms is None:
            platforms = [Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE_SHORTS]

        sub_config = self.config['subtitles']
        output_dir = Path(self.config['paths']['output_dir'])

        reels = []
        for clip in clips:
            # Get transcript segments for this clip's time range
            segments = transcript.get_segments_in_range(clip.start, clip.end)

            # Generate subtitle file
            subtitle_path = str(output_dir / f"clip_{clip.id:03d}.ass")
            generate_subtitles(
                segments=segments,
                output_path=subtitle_path,
                clip_start=clip.start,
                style_config=sub_config,
            )

            # Burn subtitles into video for each platform
            for platform in platforms:
                reel_filename = f"reel_{clip.id:03d}_{platform.value}.mp4"
                reel_path = str(output_dir / reel_filename)

                burn_subtitles_into_video(
                    video_path=clip.clip_path,
                    subtitle_path=subtitle_path,
                    output_path=reel_path,
                )

                reels.append(Reel(
                    id=clip.id,
                    path=reel_path,
                    duration=clip.duration,
                    platform=platform,
                    highlight=clip.highlight,
                    virality_score=clip.highlight.virality_score,
                    title=clip.highlight.suggested_title,
                    has_subtitles=True,
                ))

        return reels
