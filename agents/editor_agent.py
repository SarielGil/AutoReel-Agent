"""
✂️ Editor Agent
Cuts clips from original video at highlight timestamps and
resizes them to vertical (9:16) format for social media.
"""

from pathlib import Path
import yaml

from models import Highlight, Clip
from skills.clip_extraction import extract_clip
from skills.video_resize import resize_to_vertical


class EditorAgent:
    """
    Agent responsible for extracting and formatting video clips
    from the original podcast based on detected highlights.
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def process(
        self,
        video_path: str,
        highlights: list[Highlight],
        skip_resize: bool = False,
    ) -> list[Clip]:
        """
        Extract clips from video at highlight timestamps and resize to vertical.

        Args:
            video_path: Path to source video
            highlights: List of detected highlights
            skip_resize: If True, assumes input is already vertical and skips resize step.

        Returns:
            List of Clip objects with paths to extracted clip files
        """
        reel_config = self.config['reels']
        output_dir = Path(self.config['paths']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        clips = []
        for highlight in highlights:
            # Add padding
            padded_start = max(0, highlight.start - reel_config['padding_before'])
            padded_end = highlight.end + reel_config['padding_after']

            # Cut clip
            clip_filename = f"clip_{highlight.id:03d}.mp4"
            clip_path = str(output_dir / clip_filename)

            extract_clip(
                video_path=video_path,
                output_path=clip_path,
                start=padded_start,
                end=padded_end,
            )

            if skip_resize:
                final_path = clip_path
            else:
                # Resize to vertical
                vertical_filename = f"clip_{highlight.id:03d}_vertical.mp4"
                vertical_path = str(output_dir / vertical_filename)

                resize_to_vertical(
                    video_path=clip_path,
                    output_path=vertical_path,
                )
                final_path = vertical_path

            clips.append(Clip(
                id=highlight.id,
                source_path=video_path,
                clip_path=final_path,
                start=padded_start,
                end=padded_end,
                highlight=highlight,
            ))

        return clips
