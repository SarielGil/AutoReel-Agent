"""
Skill: Hebrew Transcription
Transcribe Hebrew audio using ivrit-ai/whisper-large-v3 fine-tuned Whisper model.
Returns timestamped segments with text and confidence scores.
"""

from typing import Optional


def transcribe_hebrew(
    audio_path: str,
    model_name: str = "ivrit-ai/whisper-large-v3",
    device: str = "cpu",
    language: str = "he",
    method: str = "local",
) -> list:
    """
    Transcribe Hebrew audio using either local Whisper or Gemini API.

    Args:
        audio_path: Path to audio file
        model_name: Model identifier
        device: Device for local inference
        language: Language code
        method: "local" (Whisper) or "gemini" (Gemini API)

    Returns:
        List of segment dicts
    """
    if method == "gemini":
        return transcribe_with_gemini(audio_path, model_name, language)
    
    # Use transformers pipeline for local ivrit-ai model
    from transformers import pipeline
    import torch

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device=device,
    )

    result = pipe(
        audio_path,
        return_timestamps=True,
        generate_kwargs={
            "language": language,
            "task": "transcribe",
        },
    )

    # Convert to standardized segment format
    segments = []
    for i, chunk in enumerate(result.get("chunks", [])):
        timestamps = chunk.get("timestamp", (0, 0))
        segments.append({
            "start": timestamps[0] if timestamps[0] is not None else 0,
            "end": timestamps[1] if timestamps[1] is not None else 0,
            "text": chunk.get("text", "").strip(),
            "speaker": None,
            "confidence": None,
        })

    return segments


def transcribe_with_gemini(
    audio_path: str,
    model_name: str = "gemini-2.0-flash-exp",
    language: str = "he",
) -> list:
    """
    Transcribe audio using Google Gemini API with speaker diarization.
    """
    import google.generativeai as genai
    import time
    import os
    import json
    from dotenv import load_dotenv

    load_dotenv()
    
    # Try both common env names
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment")
        
    genai.configure(api_key=api_key)

    # 1. Upload the file
    print(f"  ☁️ Uploading audio to Gemini File API...")
    audio_file = genai.upload_file(path=audio_path)
    
    # 2. Wait for processing
    while audio_file.state.name == "PROCESSING":
        time.sleep(2)
        audio_file = genai.get_file(audio_file.name)

    if audio_file.state.name == "FAILED":
        raise ValueError(f"Gemini File API processing failed for {audio_path}")

    # 3. Request transcription with speaker diarization
    model = genai.GenerativeModel(model_name)
    
    prompt = """
    Transcribe the following Hebrew audio. 
    Identify different speakers and label them.
    Format the output as a simple list with timestamps.
    
    Format:
    [00:00] Speaker A: (text)
    [00:45] Speaker B: (text)
    
    Important: 
    1. Group the text into logical paragraphs (~30-60 seconds each).
    2. Ensure the timestamps are accurate.
    3. Output ONLY the transcription in the format above.
    """

    print(f"  🧠 Generating transcript with {model_name}...")
    response = model.generate_content([prompt, audio_file])

    # 4. Cleanup
    genai.delete_file(audio_file.name)

    text_output = response.text.strip()
    segments = []
    
    import re
    # Pattern to match [MM:SS] Speaker Name: Text
    pattern = re.compile(r"\[(\d+):(\d+)\]\s*([^:]+):\s*(.*)")
    
    lines = text_output.splitlines()
    for i, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            minutes, seconds, speaker, text = match.groups()
            start_time = int(minutes) * 60 + int(seconds)
            
            # Estimate end time based on next segment or duration
            segments.append({
                "start": float(start_time),
                "text": text.strip(),
                "speaker": speaker.strip(),
                "confidence": None
            })

    # Fill in end times
    for i in range(len(segments) - 1):
        segments[i]["end"] = segments[i+1]["start"]
    
    if segments:
        # Last segment padding
        segments[-1]["end"] = segments[-1]["start"] + 30.0 

    return segments
