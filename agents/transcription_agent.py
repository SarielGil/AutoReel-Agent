"""
🎤 Transcription Agent
Extracts audio from video and transcribes Hebrew speech using ivrit-ai Whisper.

Key optimizations:
- Extracts audio-only (no video data sent to model)
- Optional 2x speed to halve transcription compute
- Timestamps are adjusted back to original video time
"""

from pathlib import Path
import yaml

from models import Transcript, TranscriptSegment
from skills.audio_extraction import extract_audio_from_video
from skills.transcription import transcribe_hebrew


class TranscriptionAgent:
    """
    Agent responsible for converting video audio into
    a timestamped Hebrew transcript.
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def transcribe(
        self,
        video_path: str,
        speed_up: bool = True,
    ) -> Transcript:
        """
        Transcribe a video's audio track to Hebrew text.

        Pipeline:
        1. Extract audio from video (audio-only, no video data)
        2. Optionally speed up audio 2x for faster compute
        3. Run ivrit-ai/whisper-large-v3 transcription
        4. Adjust timestamps back to original video time

        Args:
            video_path: Path to input video file
            speed_up: If True, speed up audio for faster processing

        Returns:
            Transcript with timestamped Hebrew segments
        """
        speed_factor = self.config['audio']['speed_factor'] if speed_up else 1.0

        # Step 1: Extract audio only (no video data)
        audio_path = extract_audio_from_video(
            video_path=video_path,
            speed_factor=speed_factor,
            sample_rate=self.config['audio']['sample_rate'],
            channels=self.config['audio']['channels'],
        )

        # Step 2: Transcribe with Hebrew-optimized Whisper or Gemini
        raw_segments = transcribe_hebrew(
            audio_path=audio_path,
            model_name=self.config['whisper']['model'],
            device=self.config['whisper']['device'],
            language=self.config['whisper']['language'],
            method=self.config['whisper'].get('method', 'local'),
        )

        # Step 3: Adjust timestamps back to original video time
        # If audio was sped up 2x, multiply timestamps by 2 to get original times
        segments = []
        for i, seg in enumerate(raw_segments):
            segments.append(TranscriptSegment(
                id=i,
                start=seg['start'] * speed_factor,
                end=seg['end'] * speed_factor,
                text=seg['text'],
                speaker=seg.get('speaker'),
                confidence=seg.get('confidence'),
            ))

        # Calculate total duration from original video
        from utils.ffmpeg_utils import get_video_duration
        total_duration = get_video_duration(video_path)

        return Transcript(
            segments=segments,
            language="he",
            total_duration=total_duration,
            speed_factor=speed_factor,
        )
