import os
import cv2
import google.generativeai as genai
from dotenv import load_dotenv
import json

def extract_frames(video_path, num_frames=3):
    """Extract frames from start, middle, and end of video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = [0, total_frames // 2, total_frames - 1]
    
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Convert to RGB for Gemini if needed, but we'll save as temp jpg
            path = f"temp_frame_{idx}.jpg"
            cv2.imwrite(path, frame)
            frames.append(path)
    
    cap.release()
    return frames

def check_privacy(video_path):
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    print(f"🕵️ Checking privacy for {video_path}...")
    frames = extract_frames(video_path)
    if not frames:
        return "ERROR"

    # Upload frames
    image_parts = []
    for f in frames:
        image_parts.append(genai.upload_file(f))

    prompt = """
    Check these frames from a podcast clip.
    We want to ensure that 'Morag' (Speaker A) is NOT visible.
    Morag is the woman wearing a dark blue shirt with white polka dots.
    The focus should be only on 'Inbal' (Speaker B), who wears a light blue shirt.
    
    If Morag (polka dots) is visible in any of these frames, return 'VISIBLE'.
    If only Inbal (light blue shirt) is shown, return 'NOT_VISIBLE'.
    Return ONLY 'VISIBLE' or 'NOT_VISIBLE'.
    """

    response = model.generate_content([prompt] + image_parts)
    result = response.text.strip().upper()

    # Cleanup
    for f in frames:
        os.remove(f)

    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(check_privacy(sys.argv[1]))
    else:
        print("Usage: python verify_privacy.py <clip_path>")
