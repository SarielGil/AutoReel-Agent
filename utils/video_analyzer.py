"""
Video Visual Analyzer
Detects scene shifts and speakers based on visual cues.
"""

import subprocess
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Any

def extract_average_colors(video_path: str, fps: float = 1.0) -> List[Dict[str, Any]]:
    """
    Extract the average RGB color of frames at a given sample rate (fps).
    Returns a list of dictionaries with 'timestamp' and 'color'.
    """
    video_path = str(video_path)
    # FFmpeg command to scale each frame to 1x1 and output raw RGB24
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps},scale=1:1",
        "-f", "image2pipe",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-"
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    samples = []
    timestamp = 0.0
    
    while True:
        # Each frame is 1x1 pixel = 3 bytes
        data = process.stdout.read(3)
        if not data or len(data) < 3:
            break
            
        r, g, b = data
        samples.append({
            "timestamp": timestamp,
            "color": [int(r), int(g), int(b)]
        })
        timestamp += 1.0 / fps
        
    process.wait()
    return samples

def cluster_colors(samples: List[Dict[str, Any]], threshold: float = 30.0) -> List[Dict[str, Any]]:
    """
    Group samples into clusters based on color distance (Euclidean).
    Assigns a 'speaker_id' to each sample.
    """
    if not samples:
        return []
        
    clusters = [] # List of average colors for each cluster
    
    for sample in samples:
        color = np.array(sample["color"])
        
        assigned = False
        for i, cluster_avg in enumerate(clusters):
            dist = np.linalg.norm(color - cluster_avg)
            if dist < threshold:
                sample["speaker_id"] = i
                # Update cluster average (simple moving average or just keep first)
                clusters[i] = (clusters[i] * 0.9) + (color * 0.1)
                assigned = True
                break
        
        if not assigned:
            sample["speaker_id"] = len(clusters)
            clusters.append(color)
            
    return samples

def get_speaker_segments(video_path: str, fps: float = 1.0, threshold: float = 40.0) -> List[Dict[str, Any]]:
    """
    Analyze video and return segments with speaker IDs.
    """
    samples = extract_average_colors(video_path, fps=fps)
    samples = cluster_colors(samples, threshold=threshold)
    
    if not samples:
        return []
        
    segments = []
    if not samples:
        return []
        
    current_speaker = samples[0]["speaker_id"]
    start_time = samples[0]["timestamp"]
    
    for i in range(1, len(samples)):
        if samples[i]["speaker_id"] != current_speaker:
            segments.append({
                "start": start_time,
                "end": samples[i]["timestamp"],
                "speaker": f"Speaker {current_speaker}"
            })
            current_speaker = samples[i]["speaker_id"]
            start_time = samples[i]["timestamp"]
            
    # Add last segment
    segments.append({
        "start": start_time,
        "end": samples[-1]["timestamp"] + (1.0 / fps),
        "speaker": f"Speaker {current_speaker}"
    })
    
    return segments

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python video_analyzer.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    segments = get_speaker_segments(video_path)
    print(json.dumps(segments, indent=2))
