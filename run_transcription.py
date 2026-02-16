import os
import sys
import json
from pathlib import Path
import yaml

# Add project root to sys.path
sys.path.append(os.path.abspath(os.curdir))

from agents.transcription_agent import TranscriptionAgent

def main():
    video_path = "input/תזונת ילדים והחיים עצמם - פרק 1 - עריכה בסיסית.mp4"
    config_path = "config/settings.yaml"
    
    # Ensure background output directory exists for transcription artifacts
    os.makedirs("output", exist_ok=True)
    
    print(f"🎤 Starting Hebrew transcription for: {video_path}")
    print("⏳ This uses Google Gemini API with speaker diarization...")
    
    try:
        agent = TranscriptionAgent(config_path)
        transcript = agent.transcribe(
            video_path=video_path,
            speed_up=True # Uses 2x speed for faster compute as per config
        )
        
        # Save transcript to a JSON file for the next steps
        transcript_path = Path("output/transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript.model_dump_json(indent=2))
            
        print(f"✅ Transcription complete!")
        print(f"📄 Saved to: {transcript_path}")
        print(f"⏱️ Total duration: {transcript.total_duration:.2f}s")
        print(f"🔢 Segments: {len(transcript.segments)}")
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
