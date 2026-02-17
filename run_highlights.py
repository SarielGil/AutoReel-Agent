import os
import json
import yaml
from agents.highlight_agent import HighlightAgent
from models import Transcript
from dotenv import load_dotenv

import argparse
from pathlib import Path

def run_highlights():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Clean and extract highlights.")
    parser.add_argument("--transcript", "-t", type=str, help="Path to transcript JSON file")
    parser.add_argument("--output", "-o", type=str, help="Path to save highlights JSON")
    args = parser.parse_args()

    config_path = "config/settings.yaml"
    # Default inputs if not provided
    transcript_path = args.transcript or "output/transcript.json"
    
    # Determine output path based on input
    if args.output:
        output_path = args.output
    else:
        # If input is transcript_foo.json, output is highlights_foo.json
        stem = Path(transcript_path).stem.replace("transcript", "highlights")
        if not stem.startswith("highlights"):
            stem = f"highlights_{stem}"
        output_path = f"output/{stem}.json"
    
    if not os.path.exists(transcript_path):
        print(f"❌ Error: Transcript file '{transcript_path}' not found.")
        return

    print(f"🔍 Loading transcript from: {transcript_path}")
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    
    transcript = Transcript(**transcript_data)
    
    print(f"🧠 Detecting highlights using HighlightAgent...")
    agent = HighlightAgent(config_path)
    
    # Increase max_highlights if needed, or get from config
    max_highlights = 10  # Get more candidates, then filter
    highlights = agent.detect(transcript, max_highlights=max_highlights)

    # Filter out hallucinations (timestamps beyond video duration)
    valid_highlights = [h for h in highlights if h.start < transcript.total_duration]
    
    # NEW: Filter for single-speaker segments only
    single_speaker_highlights = []
    for h in valid_highlights:
        # Get all segments in this highlight's time range
        segments = transcript.get_segments_in_range(h.start, h.end)
        if not segments:
            continue
        
        # Check if all segments have the same speaker
        speakers = set(seg.speaker for seg in segments if seg.speaker)
        if len(speakers) == 1:  # Only one speaker throughout
            single_speaker_highlights.append(h)
            print(f"✅ Keeping highlight: {h.suggested_title} (Speaker: {speakers.pop()})")
        else:
            print(f"❌ Skipping multi-speaker highlight: {h.suggested_title}")
    
    # Take top 5 by virality score
    highlights = sorted(single_speaker_highlights, key=lambda x: x.virality_score, reverse=True)[:5]

    print(f"✅ Found {len(highlights)} single-speaker highlights!")
    
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
