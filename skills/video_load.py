"""
Skill: Video Load
Load video from a local file path or download from a URL via yt-dlp.
"""

from pathlib import Path
import subprocess
from typing import Optional


SUPPORTED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.webm', '.mov', '.m4v', '.flv'}


def load_video(
    input_path: Optional[str] = None,
    input_url: Optional[str] = None,
    output_dir: str = "./input",
) -> str:
    """
    Load a video file from a local path or download from URL.

    Args:
        input_path: Local file path to video
        input_url: URL to download video from (YouTube, etc.)
        output_dir: Directory to save downloaded videos

    Returns:
        Path to the video file on disk

    Raises:
        ValueError: If neither input_path nor input_url is provided
        FileNotFoundError: If input_path doesn't exist
    """
    if input_path is None and input_url is None:
        raise ValueError("Either input_path or input_url must be provided")

    if input_path:
        return _load_from_path(input_path)
    else:
        return _download_from_url(input_url, output_dir)


def _load_from_path(path: str) -> str:
    """Validate and return a local file path."""
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported video format: {file_path.suffix}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    return str(file_path.resolve())


def _download_from_url(url: str, output_dir: str) -> str:
    """Download video from URL using yt-dlp."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_template = str(output_path / "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--output", output_template,
        "--print", "filename",
        "--no-simulate",
        url,
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    downloaded_path = result.stdout.strip().split('\n')[-1]

    return downloaded_path
