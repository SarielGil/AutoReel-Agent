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
    ) -> list[Highlight]:
        """
        Detect the most viral-worthy moments in a transcript.

        Args:
            transcript: Full Hebrew transcript with timestamps
            max_highlights: Maximum number of highlights to return

        Returns:
            List of Highlight objects sorted by virality score (desc)
        """
        reel_config = self.config['reels']
        detection_config = self.config['highlight_detection']

        # Detect highlights using LLM
        # Detect highlights using LLM
        highlights = detect_highlights_llm(
            transcript=transcript,
            model_name=detection_config['model'],
            max_highlights=max_highlights * 2, # Request more to allow for filtering
            min_duration=reel_config['min_duration'],
            max_duration=reel_config['max_duration'],
            min_score=detection_config.get('min_virality_score', 6),
            signals=detection_config['signals'],
        )

        # Post-process: Ensure speaker consistency
        cleaned_highlights = []
        for h in highlights:
            # check segments in this range
            segments = transcript.get_segments_in_range(h.start, h.end)
            if not segments:
                continue
            
            # Identify dominant speaker (by duration)
            speaker_durations = {}
            for seg in segments:
                dur = min(seg.end, h.end) - max(seg.start, h.start)
                if dur > 0:
                    speaker_durations[seg.speaker] = speaker_durations.get(seg.speaker, 0) + dur
            
            if not speaker_durations:
                continue

            dominant_speaker = max(speaker_durations, key=speaker_durations.get)
            total_duration = h.end - h.start
            dominant_ratio = speaker_durations[dominant_speaker] / total_duration
            
            # If dominant speaker is < 90% of the clip, try to trim
            if dominant_ratio < 0.9:
                # Find the contiguous block of the dominant speaker
                # This is a simple heuristic: Find the start/end of the dominant speaker's segments
                # that fall within the highlight range
                
                dom_segments = [s for s in segments if s.speaker == dominant_speaker]
                if not dom_segments:
                    continue
                    
                new_start = max(h.start, dom_segments[0].start)
                new_end = min(h.end, dom_segments[-1].end)
                
                # Check if new duration is enough
                if (new_end - new_start) >= reel_config['min_duration']:
                   # Update highlight
                   h.start = new_start
                   h.end = new_end
                   cleaned_highlights.append(h)
            else:
                cleaned_highlights.append(h)

        # Sort by virality score (highest first)
        cleaned_highlights.sort(key=lambda h: h.virality_score, reverse=True)

        return cleaned_highlights[:max_highlights]
