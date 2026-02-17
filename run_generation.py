import os
import json
import yaml
from agents.editor_agent import EditorAgent
from agents.subtitle_agent import SubtitleAgent
from models import Transcript, Highlight, Platform
from dotenv import load_dotenv

import argparse
from pathlib import Path

def run_generation():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate reels from highlights.")
    parser.add_argument("--highlights", "-h_file", type=str, help="Path to highlights JSON")
    parser.add_argument("--transcript", "-t", type=str, help="Path to transcript JSON")
    parser.add_argument("--video", "-v", type=str, help="Path to input video file")
    parser.add_argument("--output", "-o", type=str, help="Output directory", default="output/reels")
    parser.add_argument("--resize", action="store_true", help="Resize video to vertical if not already")
    args = parser.parse_args()

    config_path = "config/settings.yaml"
    
    # Default paths for backward compatibility or single-run workflow
    highlights_path = args.highlights or "output/highlights.json"
    transcript_path = args.transcript or "output/transcript.json"
    video_path = args.video or "output/full_video_vertical_mobile.mp4"
    
    # Check if we should skip resize (default is True in legacy, but false if arg provided)
    # Actually, let's inverse it: if --resize is passed, skip_resize=False. 
    # If no video arg is passed, we assume the pre-processed "full_video_vertical_mobile.mp4" used in the original pipeline, 
    # so we SKIP resize.
    # If a video arg IS passed (e.g. a split file), we probably want to resize it, so --resize should be used.
    skip_resize = not args.resize
    
    if not os.path.exists(highlights_path):
        print(f"❌ Error: {highlights_path} not found. Run run_highlights.py first.")
        return

    print(f"📄 Loading highlights from: {highlights_path}")
    with open(highlights_path, 'r', encoding='utf-8') as f:
        highlights_data = json.load(f)
    highlights = [Highlight(**h) for h in highlights_data]

    print(f"📄 Loading transcript from: {transcript_path}")
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    transcript = Transcript(**transcript_data)

    print(f"✂️ Step 1: Cutting clips from the video...")
    editor = EditorAgent(config_path)
    # Use the dynamic skip_resize flag
    clips = editor.process(video_path=video_path, highlights=highlights, skip_resize=skip_resize)
    print(f"  ✅ Cut {len(clips)} clips")

    print(f"📝 Step 2: Adding Hebrew subtitles...")
    subtitle_agent = SubtitleAgent(config_path)
    # For now, let's just generate for Instagram to save time, or use the config
    platforms = [Platform.INSTAGRAM] # [Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE_SHORTS]
    
    reels = subtitle_agent.process(
        clips=clips,
        transcript=transcript,
        platforms=platforms
    )
    
    print(f"\n🚀 SUCCESS! Final reels generated:")
    for reel in reels:
        print(f"  ✅ {reel.path}")

if __name__ == "__main__":
    run_generation()
