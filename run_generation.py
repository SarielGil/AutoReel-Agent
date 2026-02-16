import os
import json
import yaml
from agents.editor_agent import EditorAgent
from agents.subtitle_agent import SubtitleAgent
from models import Transcript, Highlight, Platform
from dotenv import load_dotenv

def run_generation():
    load_dotenv()
    
    config_path = "config/settings.yaml"
    transcript_path = "output/transcript.json"
    highlights_path = "output/highlights.json"
    
    # IMPORTANT: We use the already resized vertical video to save time!
    video_path = "output/full_video_vertical_mobile.mp4"
    
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

    print(f"✂️ Step 1: Cutting clips from the resized video...")
    editor = EditorAgent(config_path)
    # skip_resize=True because the source is already vertical
    clips = editor.process(video_path=video_path, highlights=highlights, skip_resize=True)
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
