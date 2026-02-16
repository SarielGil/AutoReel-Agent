import subprocess

video_path = "output/clip_001.mp4"
subtitle_path = "output/clip_001.ass"
output_path = "output/test_reel.mp4"

# Try with filename=
filter_str = f"ass=filename={subtitle_path}"

cmd = [
    "ffmpeg", "-y",
    "-i", video_path,
    "-vf", filter_str,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-c:a", "aac",
    output_path,
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ Error {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
else:
    print("✅ Success!")
