import os
import json
import yaml
from agents.highlight_agent import HighlightAgent
from models import Transcript
from dotenv import load_dotenv

def run_highlights():
    load_dotenv()
    
    config_path = "config/settings.yaml"
    transcript_path = "output/transcript.json"
    output_path = "output/highlights.json"
    
    if not os.path.exists(transcript_path):
        print(f"❌ Error: {transcript_path} not found.")
        return

    print(f"🔍 Loading transcript from: {transcript_path}")
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    
    transcript = Transcript(**transcript_data)
    
    print(f"🧠 Detecting highlights using HighlightAgent...")
    agent = HighlightAgent(config_path)
    
    # Increase max_highlights if needed, or get from config
    max_highlights = 5
    focus_speaker = "Speaker B"
    highlights = agent.detect(transcript, max_highlights=max_highlights, focus_speaker=focus_speaker)

    # Filter out hallucinations (timestamps beyond video duration)
    valid_highlights = [h for h in highlights if h.start < transcript.total_duration]
    highlights = valid_highlights

    print(f"✅ Found {len(highlights)} valid highlights!")
    
    # Save highlights
    highlights_data = [h.model_dump() for h in highlights]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(highlights_data, f, ensure_ascii=False, indent=2)
        
    print(f"📄 Saved highlights to: {output_path}")
    
    # Print a summary
    for i, h in enumerate(highlights):
        print(f"\n--- Highlight #{i+1} ---")
        print(f"Title: {h.suggested_title}")
        print(f"Time: {h.start:.2f}s - {h.end:.2f}s (Duration: {h.duration:.2f}s)")
        print(f"Score: {h.virality_score}/10")
        print(f"Reason: {h.reason}")
        print(f"Text: {h.text[:100]}...")

if __name__ == "__main__":
    run_highlights()
