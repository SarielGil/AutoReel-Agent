"""
🔍 Highlight Agent
Analyzes transcripts using Gemini LLM to find the most engaging,
quotable, and viral-worthy moments for social media reels.

Scoring signals:
- Emotional peaks (humor, surprise, controversy)
- Quotable statements (short, punchy, standalone)
- Topic transitions (key introductions/conclusions)
- Speaker energy (pace, emphasis)
- Audience appeal (likely to generate shares/comments)
"""

import yaml

from typing import Optional
from models import Transcript, Highlight
from skills.highlight_detection import detect_highlights_llm


class HighlightAgent:
    """
    Agent responsible for analyzing transcripts and identifying
    the best moments to turn into reels.
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def detect(
        self,
        transcript: Transcript,
        max_highlights: int = 5,
        focus_speaker: Optional[str] = None,
    ) -> list[Highlight]:
        """
        Detect the most viral-worthy moments in a transcript.

        Args:
            transcript: Full Hebrew transcript with timestamps
            max_highlights: Maximum number of highlights to return
            focus_speaker: Optional speaker to prioritize

        Returns:
            List of Highlight objects sorted by virality score (desc)
        """
        reel_config = self.config['reels']
        detection_config = self.config['highlight_detection']

        # Detect highlights using LLM
        highlights = detect_highlights_llm(
            transcript=transcript,
            model_name=detection_config['model'],
            max_highlights=max_highlights,
            min_duration=reel_config['min_duration'],
            max_duration=reel_config['max_duration'],
            min_score=detection_config['min_score'],
            signals=detection_config['signals'],
            focus_speaker=focus_speaker,
        )

        # Sort by virality score (highest first)
        highlights.sort(key=lambda h: h.virality_score, reverse=True)

        return highlights[:max_highlights]
