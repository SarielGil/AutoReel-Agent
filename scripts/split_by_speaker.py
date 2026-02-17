#!/usr/bin/env python3
"""
Separate Video by Speaker (Visual)
Usage: python scripts/split_by_speaker.py <video_path>
"""

import os
import sys
from pathlib import Path
from utils.video_analyzer import get_speaker_segments
from utils.ffmpeg_utils import concat_segments_visual
from rich.console import Console
from rich.progress import Progress

console = Console()

import argparse

def main():
    parser = argparse.ArgumentParser(description="Split video by speaker.")
    parser.add_argument("video_path", type=str, help="Path to input video")
    parser.add_argument("--proxy", "-p", type=str, help="Path to smaller proxy video for analysis (optional)")
    args = parser.parse_args()

    video_path = args.video_path
    
    if args.proxy:
        if not os.path.exists(args.proxy):
            console.print(f"[yellow]Warning: Proxy {args.proxy} not found. Using original.[/yellow]")
            analysis_video = video_path
        else:
            console.print(f"[green]Using proxy for analysis:[/green] {args.proxy}")
            analysis_video = args.proxy
    else:
        analysis_video = video_path

    video_stem = Path(video_path).stem
    output_dir = Path("output/speaker_split")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[bold blue]Analyzing video:[/bold blue] {analysis_video}")
    
    # 1. Analyze segments
    # Use the analysis video (proxy or original)
    segments = get_speaker_segments(analysis_video, fps=0.5, threshold=40.0)
    
    if not segments:
        console.print("[yellow]No segments found.[/yellow]")
        return
        
    # Group segments by speaker
    speaker_map = {}
    for seg in segments:
        speaker = seg["speaker"]
        if speaker not in speaker_map:
            speaker_map[speaker] = []
        speaker_map[speaker].append(seg)
        
    console.print(f"[green]Found {len(speaker_map)} speakers/scenes.[/green]")
    
    # 2. Extract and Concatenate
    with Progress() as progress:
        speaker_task = progress.add_task("[cyan]Processing speakers...", total=len(speaker_map))
        
        for speaker, speaker_segs in speaker_map.items():
            console.print(f"  [bold]Processing {speaker}...[/bold] ({len(speaker_segs)} segments)")
            
            # Concatenate all clips for this speaker directly
            final_output = str(output_dir / f"{video_stem}_{speaker.replace(' ', '_')}.mp4")
            
            try:
                concat_segments_visual(video_path, speaker_segs, final_output)
                progress.update(speaker_task, advance=1)
                console.print(f"  [green]✓[/green] Saved to: {final_output}")
            except Exception as e:
                console.print(f"[red]Failed to process {speaker}: {e}[/red]")

    console.print(f"\n[bold green]Success![/bold green] All speaker files saved in {output_dir}")

if __name__ == "__main__":
    main()
