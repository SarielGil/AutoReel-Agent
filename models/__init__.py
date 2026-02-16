"""
AutoReel Agent - Data Models
Pydantic models for type-safe data throughout the pipeline.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"


class TranscriptSegment(BaseModel):
    """A single timestamped segment from Whisper transcription."""
    id: int
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Hebrew text content")
    speaker: Optional[str] = Field(None, description="Speaker identifier (e.g. Speaker A)")
    confidence: Optional[float] = Field(None, description="Transcription confidence score")

    @property
    def duration(self) -> float:
        return self.end - self.start


class Transcript(BaseModel):
    """Full transcript of a podcast episode."""
    segments: list[TranscriptSegment]
    language: str = "he"
    total_duration: float = Field(..., description="Total audio duration in seconds")
    speed_factor: float = Field(1.0, description="Speed factor used during transcription")

    @property
    def full_text(self) -> str:
        return " ".join(seg.text for seg in self.segments)

    def get_segments_in_range(self, start: float, end: float) -> list[TranscriptSegment]:
        """Get all segments that overlap with a time range."""
        return [
            seg for seg in self.segments
            if seg.end > start and seg.start < end
        ]


class Highlight(BaseModel):
    """A detected highlight moment in the podcast."""
    id: int
    start: float = Field(..., description="Start time in seconds (original video time)")
    end: float = Field(..., description="End time in seconds (original video time)")
    text: str = Field(..., description="The highlighted text/quote")
    virality_score: float = Field(..., ge=1, le=10, description="Predicted virality score 1-10")
    reason: str = Field(..., description="Why this moment is engaging")
    suggested_title: Optional[str] = Field(None, description="Suggested reel title")
    signals: list[str] = Field(default_factory=list, description="What signals triggered this highlight")

    @property
    def duration(self) -> float:
        return self.end - self.start


class Clip(BaseModel):
    """A video clip extracted from the original video."""
    id: int
    source_path: str = Field(..., description="Path to original video")
    clip_path: str = Field(..., description="Path to extracted clip file")
    start: float
    end: float
    highlight: Highlight

    @property
    def duration(self) -> float:
        return self.end - self.start


class Reel(BaseModel):
    """A final, export-ready reel with subtitles burned in."""
    id: int
    path: str = Field(..., description="Path to final reel file")
    duration: float
    platform: Platform
    highlight: Highlight
    virality_score: float
    title: Optional[str] = None
    has_subtitles: bool = True
    resolution: str = "1080x1920"


class PipelineResult(BaseModel):
    """Result of the full AutoReel pipeline."""
    input_source: str = Field(..., description="Original video path or URL")
    transcript: Transcript
    highlights: list[Highlight]
    reels: list[Reel]
    total_processing_time: float = Field(..., description="Total time in seconds")

    @property
    def num_reels(self) -> int:
        return len(self.reels)

    @property
    def avg_virality_score(self) -> float:
        if not self.reels:
            return 0.0
        return sum(r.virality_score for r in self.reels) / len(self.reels)
