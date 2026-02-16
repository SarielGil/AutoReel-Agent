"""
🎛️ Orchestrator Agent
Manages the full AutoReel pipeline end-to-end.

Coordinates all specialized agents in sequence:
1. TranscriptionAgent  → Audio extraction & Hebrew transcription
2. HighlightAgent      → Best-moment detection via LLM
3. EditorAgent         → Clip extraction & vertical resize
4. SubtitleAgent       → Hebrew subtitle generation & burn-in

Supports input from:
- Local file path (mp4, mkv, avi, webm, etc.)
- YouTube URL (downloaded via yt-dlp)
"""

from pathlib import Path
from typing import Optional
import time

from rich.console import Console
from rich.progress import Progress

from models import PipelineResult, Reel, Platform
from agents.transcription_agent import TranscriptionAgent
from agents.highlight_agent import HighlightAgent
from agents.editor_agent import EditorAgent
from agents.subtitle_agent import SubtitleAgent
from skills.video_load import load_video

console = Console()


class OrchestratorAgent:
    """
    Main pipeline orchestrator.

    Usage:
        agent = OrchestratorAgent()
        result = agent.run(
            input_path="/path/to/podcast.mp4",
            max_reels=5,
            speed_up_audio=True,
        )
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.transcription_agent = TranscriptionAgent(config_path)
        self.highlight_agent = HighlightAgent(config_path)
        self.editor_agent = EditorAgent(config_path)
        self.subtitle_agent = SubtitleAgent(config_path)

    def run(
        self,
        input_path: Optional[str] = None,
        input_url: Optional[str] = None,
        max_reels: int = 5,
        speed_up_audio: bool = True,
        target_platforms: Optional[list] = None,
    ) -> PipelineResult:
        """
        Run the full AutoReel pipeline.

        Args:
            input_path: Local path to video file
            input_url: YouTube/podcast URL to download
            max_reels: Maximum number of reels to generate
            speed_up_audio: If True, speed up audio 2x for faster transcription
            target_platforms: List of platform names (default: all)

        Returns:
            PipelineResult with all generated reels
        """
        start_time = time.time()

        if target_platforms is None:
            target_platforms = ["instagram", "tiktok", "youtube_shorts"]

        # Step 1: Load video
        console.print("[bold blue]📥 Step 1/5: Loading video...[/]")
        video_path = load_video(input_path=input_path, input_url=input_url)
        console.print(f"  ✅ Video loaded: {video_path}")

        # Step 2: Transcribe
        console.print("[bold blue]🎤 Step 2/5: Transcribing Hebrew audio...[/]")
        transcript = self.transcription_agent.transcribe(
            video_path=video_path,
            speed_up=speed_up_audio,
        )
        console.print(f"  ✅ Transcribed {len(transcript.segments)} segments ({transcript.total_duration:.0f}s)")

        # Step 3: Detect highlights
        console.print("[bold blue]🔍 Step 3/5: Detecting best moments...[/]")
        highlights = self.highlight_agent.detect(
            transcript=transcript,
            max_highlights=max_reels,
        )
        console.print(f"  ✅ Found {len(highlights)} highlights")

        # Step 4: Cut clips & resize
        console.print("[bold blue]✂️ Step 4/5: Cutting clips...[/]")
        clips = self.editor_agent.process(
            video_path=video_path,
            highlights=highlights,
        )
        console.print(f"  ✅ Cut {len(clips)} clips")

        # Step 5: Add subtitles & export
        console.print("[bold blue]📝 Step 5/5: Adding Hebrew subtitles...[/]")
        reels = self.subtitle_agent.process(
            clips=clips,
            transcript=transcript,
            platforms=[Platform(p) for p in target_platforms],
        )
        console.print(f"  ✅ Generated {len(reels)} reels")

        elapsed = time.time() - start_time
        console.print(f"\n[bold green]🎬 Done! {len(reels)} reels created in {elapsed:.1f}s[/]")

        result = PipelineResult(
            input_source=input_path or input_url,
            transcript=transcript,
            highlights=highlights,
            reels=reels,
            total_processing_time=elapsed,
        )

        for reel in reels:
            console.print(
                f"  📱 {reel.path} | {reel.duration:.0f}s | "
                f"Score: {reel.virality_score}/10 | {reel.platform.value}"
            )

        return result
