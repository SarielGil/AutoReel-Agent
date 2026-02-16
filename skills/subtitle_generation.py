"""
Skill: Subtitle Generation
Generate SRT/ASS subtitle files with Hebrew RTL styling and word-level timing.
"""

from pathlib import Path
from typing import Optional
from models import TranscriptSegment
from utils.hebrew_utils import (
    split_hebrew_lines,
    format_timestamp_ass,
    wrap_rtl,
    clean_transcript_text,
)


def generate_subtitles(
    segments: list[TranscriptSegment],
    output_path: str,
    clip_start: float = 0,
    style_config: Optional[dict] = None,
) -> str:
    """
    Generate an ASS subtitle file with Hebrew RTL styling.

    Args:
        segments: Transcript segments for this clip
        output_path: Path to save the subtitle file
        clip_start: Start time of the clip (to offset timestamps)
        style_config: Subtitle style configuration

    Returns:
        Path to the generated subtitle file
    """
    if style_config is None:
        style_config = {
            "font": "Arial",
            "font_size": 48,
            "primary_color": "&H00FFFFFF",
            "outline_color": "&H00000000",
            "outline_width": 3,
            "position": "bottom",
            "max_chars_per_line": 30,
        }

    # ASS header with Hebrew RTL support
    ass_content = _build_ass_header(style_config)

    # Add dialogue events
    for seg in segments:
        # Adjust timestamps relative to clip start
        start_time = max(0, seg.start - clip_start)
        end_time = seg.end - clip_start

        # Clean and wrap Hebrew text
        text = clean_transcript_text(seg.text)
        lines = split_hebrew_lines(text, style_config.get('max_chars_per_line', 30))
        formatted_text = "\\N".join(wrap_rtl(line) for line in lines)

        ass_content += (
            f"Dialogue: 0,{format_timestamp_ass(start_time)},"
            f"{format_timestamp_ass(end_time)},Hebrew,,0,0,0,,"
            f"{formatted_text}\n"
        )

    Path(output_path).write_text(ass_content, encoding='utf-8')
    return output_path


def generate_srt(
    segments: list[TranscriptSegment],
    output_path: str,
    clip_start: float = 0,
) -> str:
    """
    Generate a simple SRT subtitle file.

    Args:
        segments: Transcript segments
        output_path: Output file path
        clip_start: Start time offset

    Returns:
        Path to the generated SRT file
    """
    from utils.hebrew_utils import format_timestamp_srt

    srt_lines = []
    for i, seg in enumerate(segments, 1):
        start_time = max(0, seg.start - clip_start)
        end_time = seg.end - clip_start
        text = clean_transcript_text(seg.text)

        srt_lines.append(str(i))
        srt_lines.append(
            f"{format_timestamp_srt(start_time)} --> {format_timestamp_srt(end_time)}"
        )
        srt_lines.append(text)
        srt_lines.append("")

    Path(output_path).write_text("\n".join(srt_lines), encoding='utf-8')
    return output_path


def _build_ass_header(style_config: dict) -> str:
    """Build ASS file header with Hebrew-optimized styling."""
    font = style_config.get('font', 'Arial')
    size = style_config.get('font_size', 48)
    primary = style_config.get('primary_color', '&H00FFFFFF')
    outline = style_config.get('outline_color', '&H00000000')
    outline_w = style_config.get('outline_width', 3)

    return f"""[Script Info]
Title: AutoReel Hebrew Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hebrew,{font},{size},{primary},&H000000FF,{outline},&H80000000,-1,0,0,0,100,100,0,0,1,{outline_w},1,2,20,20,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
