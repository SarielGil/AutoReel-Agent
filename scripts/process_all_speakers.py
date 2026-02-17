#!/usr/bin/env python3
"""
Process All Speaker Videos
--------------------------
Iterates over all videos in output/speaker_split/ and runs the full AutoReel pipeline for each.

Usage:
    python scripts/process_all_speakers.py
"""

import os
import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

def run_command(cmd_list):
    """Run a command and check for errors."""
    cmd_str = " ".join(cmd_list)
    console.print(f"[bold cyan]Running:[/bold cyan] {cmd_str}")
    try:
        subprocess.run(cmd_list, check=True)
    except subprocess.CalledProcessError:
        console.print(f"[bold red]❌ Command failed:[/bold red] {cmd_str}")
        raise

def main():
    split_dir = Path("output/speaker_split")
    
    if not split_dir.exists():
        console.print(f"[red]Error: {split_dir} does not exist. Run split_by_speaker.py first.[/red]")
        return

    # Find all mp4 files
    # We ignore files starting with "temp_" just in case there are leftovers
    videos = [f for f in split_dir.glob("*.mp4") if not f.name.startswith("temp_")]
    
    if not videos:
        console.print(f"[yellow]No videos found in {split_dir}[/yellow]")
        return
        
    console.print(f"[green]Found {len(videos)} speaker videos to process.[/green]")
    
    for video_path in videos:
        stem = video_path.stem
        console.print(f"\n[bold magenta]━━━━━━━━ Processing: {video_path.name} ━━━━━━━━[/bold magenta]")
        
        # 1. Transcription
        transcript_json = f"output/transcript_{stem}.json"
        if not Path(transcript_json).exists():
            console.print(f"[blue]1. Transcribing...[/blue]")
            run_command([
                "python", "run_transcription.py",
                "--input", str(video_path),
                "--output", transcript_json
            ])
        else:
            console.print(f"[dim]Skipping transcription (already exists)[/dim]")

        # 2. Highlights
        highlights_json = f"output/highlights_{stem}.json"
        if not Path(highlights_json).exists():
            console.print(f"[blue]2. Detecting Highlights...[/blue]")
            run_command([
                "python", "run_highlights.py",
                "--transcript", transcript_json,
                "--output", highlights_json
            ])
        else:
            console.print(f"[dim]Skipping highlights (already exists)[/dim]")
            
        # 3. Reel Generation
        # We assume the split videos are horizontal, so we force --resize to crop for 9:16
        console.print(f"[blue]3. Generating Reels...[/blue]")
        run_command([
            "python", "run_generation.py",
            "--highlights", highlights_json,
            "--transcript", transcript_json,
            "--video", str(video_path),
            "--resize" 
        ])
        
    console.print("\n[bold green]✅ All speaker videos processed![/bold green]")

if __name__ == "__main__":
    main()
