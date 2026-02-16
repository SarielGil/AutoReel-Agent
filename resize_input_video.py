import os
import sys
from pathlib import Path
from skills.video_resize import resize_to_vertical

# Add project root to sys.path
sys.path.append(os.path.abspath(os.curdir))

def main():
    input_file = "input/תזונת ילדים והחיים עצמם - פרק 1 - עריכה בסיסית.mp4"
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "full_video_vertical_mobile.mp4"
    
    print(f"🚀 Starting resize for: {input_file}")
    print(f"📦 Target: {output_file}")
    print("⏳ This may take a few minutes for a 2GB file...")
    
    try:
        # Using CRF 28 for mobile optimization (good balance of quality and size)
        # Using 'veryfast' preset to save time during this initial step
        result = resize_to_vertical(
            video_path=input_file,
            output_path=str(output_file),
            crf=28,
            preset="veryfast"
        )
        print(f"✅ Success! Resized video saved to: {result}")
        
        # Show size comparison
        original_size = os.path.getsize(input_file) / (1024 * 1024)
        new_size = os.path.getsize(result) / (1024 * 1024)
        print(f"📊 Size: {original_size:.2f} MB -> {new_size:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error during resizing: {e}")

if __name__ == "__main__":
    main()
