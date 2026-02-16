"""
Hebrew Text Processing Utilities
Helpers for handling Hebrew / RTL text in subtitles and transcriptions.
"""

import re
import unicodedata


def strip_niqqud(text: str) -> str:
    """
    Remove Hebrew niqqud (vowel diacritics) from text.
    Whisper sometimes outputs partial niqqud which can cause display issues.
    """
    # Hebrew niqqud Unicode range: U+0591 to U+05C7
    return re.sub(r'[\u0591-\u05C7]', '', text)


def is_hebrew(text: str) -> bool:
    """Check if text is primarily Hebrew."""
    hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    total_chars = sum(1 for c in text if c.strip())
    if total_chars == 0:
        return False
    return hebrew_chars / total_chars > 0.3


def wrap_rtl(text: str) -> str:
    """
    Wrap text with RTL Unicode markers for proper display.
    Useful for subtitle rendering in players that don't auto-detect RTL.
    """
    RLM = '\u200F'  # Right-to-Left Mark
    return f"{RLM}{text}{RLM}"


def split_hebrew_lines(text: str, max_chars: int = 30) -> list[str]:
    """
    Split Hebrew text into lines of max_chars length.
    Breaks at word boundaries for natural reading.

    Args:
        text: Hebrew text to split
        max_chars: Maximum characters per line

    Returns:
        List of text lines
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line = f"{current_line} {word}" if current_line else word
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word

    if current_line:
        lines.append(current_line.strip())

    return lines


def clean_transcript_text(text: str) -> str:
    """
    Clean up transcription text:
    - Remove multiple spaces
    - Strip niqqud
    - Fix common Whisper artifacts in Hebrew
    """
    text = strip_niqqud(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def format_timestamp_srt(seconds: float) -> str:
    """
    Format seconds to SRT timestamp format: HH:MM:SS,mmm

    Args:
        seconds: Time in seconds

    Returns:
        Formatted SRT timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_ass(seconds: float) -> str:
    """
    Format seconds to ASS timestamp format: H:MM:SS.cc

    Args:
        seconds: Time in seconds

    Returns:
        Formatted ASS timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"
