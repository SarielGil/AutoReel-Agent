<p align="center">
  <h1 align="center">🎬 AutoReel Agent</h1>
  <p align="center">
    <strong>AI-powered pipeline that converts long Hebrew podcast videos into viral social media reels</strong>
  </p>
  <p align="center">
    <a href="#architecture">Architecture</a> •
    <a href="#agents">Agents</a> •
    <a href="#skills">Skills</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#roadmap">Roadmap</a>
  </p>
</p>

---

## 🎯 Overview

**AutoReel Agent** is a multi-agent AI system that automates the entire workflow of turning long-form Hebrew podcast episodes into short, engaging social media reels. 

The system:
1. **Ingests** a podcast video from a local file path or URL
2. **Extracts audio** and sends it to a Hebrew-optimized Whisper model (with optional 2x speedup for compute efficiency)
3. **Transcribes** the audio into timestamped Hebrew text using [`ivrit-ai/whisper-large-v3`](https://huggingface.co/ivrit-ai/whisper-large-v3)
4. **Detects highlights** — the most engaging, quotable, and viral-worthy moments — using LLM analysis
5. **Cuts & assembles** short clips from the original video at the exact timestamps
6. **Generates styled Hebrew subtitles** with proper RTL support and burns them into the video
7. **Exports** platform-optimized reels (9:16 vertical, 30-90 sec) ready for Instagram, TikTok, YouTube Shorts

> 🇮🇱 **Built for Hebrew content** — Uses fine-tuned models with ~63% better Word Error Rate than vanilla Whisper for Hebrew transcription.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   🎛️ Orchestrator Agent                  │
│            Manages the full pipeline end-to-end          │
└──────────┬──────────┬──────────┬──────────┬─────────────┘
           │          │          │          │
           ▼          ▼          ▼          ▼
    ┌────────┐  ┌──────────┐ ┌────────┐ ┌──────────┐
    │ 🎤     │  │ 🔍       │ │ ✂️      │ │ 📝       │
    │Transcr.│  │Highlight │ │ Editor │ │ Subtitle │
    │ Agent  │  │  Agent   │ │ Agent  │ │  Agent   │
    └───┬────┘  └────┬─────┘ └───┬────┘ └────┬─────┘
        │            │           │            │
        ▼            ▼           ▼            ▼
   ┌─────────────────────────────────────────────────┐
   │                  🔧 Skills Layer                 │
   │  audio_extraction │ transcription │ highlight    │
   │  clip_extraction  │ subtitle_gen  │ video_resize │
   │  subtitle_burn    │ platform_export │ video_load │
   └─────────────────────────────────────────────────┘
        │            │           │            │
        ▼            ▼           ▼            ▼
   ┌─────────────────────────────────────────────────┐
   │              🛠️ Tools & Infrastructure           │
   │    FFmpeg  │  Whisper (ivrit-ai)  │  Gemini API │
   │    yt-dlp  │  Python             │  pydantic    │
   └─────────────────────────────────────────────────┘
```

### Pipeline Flow

```
Input Video/URL ──► Audio Extraction (FFmpeg, optional 2x speed)
                         │
                         ▼
                    Hebrew Transcription (ivrit-ai/whisper-large-v3)
                         │
                         ▼
                    Highlight Detection (Gemini LLM analysis)
                         │
                         ▼
                    Clip Extraction (FFmpeg precise cutting)
                         │
                         ▼
                    Subtitle Generation (SRT/ASS with RTL Hebrew)
                         │
                         ▼
                    Video Assembly (resize 9:16, burn subtitles, branding)
                         │
                         ▼
                    Platform Export (Instagram / TikTok / YouTube Shorts)
```

---

## 🤖 Agents

Agents are high-level coordinators that manage complex tasks by invoking one or more skills.

| Agent | Role | Skills Used |
|-------|------|-------------|
| **🎛️ Orchestrator** | Manages the full pipeline, coordinates all other agents, handles errors and retries | All |
| **🎤 Transcription Agent** | Extracts audio from video, speeds up if configured, sends to Whisper model, returns timestamped transcript | `audio_extraction`, `transcription` |
| **🔍 Highlight Agent** | Analyzes transcript with LLM to find the most engaging moments, scores each for virality potential | `highlight_detection` |
| **✂️ Editor Agent** | Cuts clips from original video at highlight timestamps, resizes to vertical format | `clip_extraction`, `video_resize` |
| **📝 Subtitle Agent** | Generates styled Hebrew subtitles (RTL), burns them into the final clips | `subtitle_generation`, `subtitle_burn` |

---

## 🔧 Skills

Skills are atomic, reusable functions that perform a single well-defined task.

| Skill | Description | Core Tool |
|-------|-------------|-----------|
| `video_load` | Load video from local file path or download via URL (yt-dlp) | `yt-dlp`, `pathlib` |
| `audio_extraction` | Extract audio track from video, with optional 2x speed for faster transcription | `FFmpeg` |
| `transcription` | Transcribe Hebrew audio using `ivrit-ai/whisper-large-v3`, returns timestamped segments | `Whisper` |
| `highlight_detection` | Send transcript to Gemini to identify viral-worthy moments with engagement scores | `Gemini API` |
| `clip_extraction` | Cut precise video segments at given start/end timestamps | `FFmpeg` |
| `subtitle_generation` | Create SRT/ASS subtitle files with Hebrew RTL styling and word-level timing | `pysrt` |
| `subtitle_burn` | Burn (hardcode) styled subtitles into video frames | `FFmpeg` |
| `video_resize` | Convert aspect ratio from 16:9 → 9:16 with smart cropping (speaker focus) | `FFmpeg` |
| `platform_export` | Format final clips per platform specs (duration, resolution, codec) | `FFmpeg` |

---

## 🧰 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Language** | Python 3.11+ | Rich AI/ML ecosystem |
| **Transcription** | [`ivrit-ai/whisper-large-v3`](https://huggingface.co/ivrit-ai/whisper-large-v3) | Fine-tuned for Hebrew, ~63% better WER |
| **LLM** | [Google Gemini API](https://ai.google.dev/) | Highlight detection, content analysis |
| **Video Processing** | [FFmpeg](https://ffmpeg.org/) | Industry standard, fast, reliable |
| **Video Download** | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube & podcast platform support |
| **Data Models** | [Pydantic](https://docs.pydantic.dev/) | Type-safe configuration and data |
| **Hebrew NLP** | Custom utilities | RTL handling, niqqud stripping, tokenization |

### Audio Optimization Strategy

To reduce transcription compute costs, the pipeline:
1. **Extracts audio only** — no video data is sent to the transcription model
2. **Optional 2x speed** — audio can be sped up 2x before transcription, halving compute time while maintaining Whisper accuracy
3. **Mono 16kHz** — audio is converted to mono 16kHz WAV, the optimal format for Whisper

```bash
# What happens under the hood:
ffmpeg -i podcast.mp4 -vn -ac 1 -ar 16000 -af "atempo=2.0" audio_fast.wav
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- FFmpeg installed (`brew install ffmpeg` on macOS)
- Google Gemini API key
- GPU recommended for Whisper (but CPU works too)

### Installation

```bash
# Clone the repo
git clone https://github.com/SarielGil/AutoReel-Agent.git
cd AutoReel-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```python
from agents.orchestrator import OrchestratorAgent

# From a local file
agent = OrchestratorAgent()
reels = agent.run(
    input_path="/path/to/hebrew-podcast-episode.mp4",
    max_reels=5,
    speed_up_audio=True,   # 2x speed for faster transcription
    target_platforms=["instagram", "tiktok", "youtube_shorts"]
)

# From a YouTube URL
reels = agent.run(
    input_url="https://youtube.com/watch?v=...",
    max_reels=5
)

# Output: list of reel file paths in ./output/
for reel in reels:
    print(f"✅ Created: {reel.path} ({reel.duration}s) — Score: {reel.virality_score}")
```

### CLI (Planned)

```bash
# Process a local file
python -m autoreel --input /path/to/podcast.mp4 --max-reels 5 --speed-up

# Process a YouTube URL  
python -m autoreel --url "https://youtube.com/watch?v=..." --max-reels 3
```

---

## 📁 Project Structure

```
AutoReel-Agent/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── config/
│   └── settings.yaml             # Global configuration
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py           # 🎛️ Pipeline orchestrator
│   ├── transcription_agent.py    # 🎤 Audio → Hebrew transcript
│   ├── highlight_agent.py        # 🔍 Transcript → Best moments
│   ├── editor_agent.py           # ✂️ Video → Short clips
│   └── subtitle_agent.py         # 📝 Clips → Subtitled reels
├── skills/
│   ├── __init__.py
│   ├── video_load.py             # Load from path or download URL
│   ├── audio_extraction.py       # Extract & optimize audio
│   ├── transcription.py          # Whisper Hebrew transcription
│   ├── highlight_detection.py    # LLM-based highlight scoring
│   ├── clip_extraction.py        # FFmpeg clip cutting
│   ├── subtitle_generation.py    # SRT/ASS generation (Hebrew RTL)
│   ├── subtitle_burn.py          # Burn subtitles into video
│   ├── video_resize.py           # 16:9 → 9:16 smart crop
│   └── platform_export.py        # Platform-specific formatting
├── models/
│   └── __init__.py               # Pydantic data models
├── utils/
│   ├── __init__.py
│   ├── ffmpeg_utils.py           # FFmpeg wrapper helpers
│   └── hebrew_utils.py           # Hebrew text processing
├── output/                       # Generated reels (git-ignored)
├── input/                        # Input videos (git-ignored)
└── tests/
    └── __init__.py
```

---

## 🎯 Highlight Detection Strategy

The Highlight Agent uses a multi-signal approach to find the best moments:

| Signal | Description | Weight |
|--------|-------------|--------|
| **Emotional Peaks** | Moments with strong emotional language (humor, surprise, controversy) | High |
| **Quotable Statements** | Short, punchy sentences that work as standalone quotes | High |
| **Topic Transitions** | Key topic introductions or conclusions | Medium |
| **Speaker Energy** | Changes in speech pace, volume, or tone | Medium |
| **Audience Appeal** | Content likely to generate comments, shares, or saves | High |

The LLM (Gemini) receives the full transcript and returns ranked highlights with:
- Start/end timestamps
- Virality score (1-10)
- Suggested reel title
- Why this moment is engaging

---

## 🗺️ Roadmap

### Phase 1 — MVP ✨
- [x] Project structure and README
- [ ] Audio extraction with 2x speed optimization
- [ ] Hebrew transcription with ivrit-ai Whisper
- [ ] Gemini-based highlight detection
- [ ] FFmpeg clip cutting
- [ ] Basic subtitle burn-in (Hebrew RTL)
- [ ] Vertical video export (9:16)

### Phase 2 — Polish 🎨
- [ ] Animated subtitle styles (word-by-word highlight)
- [ ] Speaker diarization (multi-speaker podcasts)
- [ ] Smart cropping (focus on active speaker)
- [ ] Branding templates (logo, colors, intro/outro)
- [ ] Batch processing (full season at once)

### Phase 3 — Distribution 📱
- [ ] Direct upload to Instagram, TikTok, YouTube
- [ ] Auto-generated captions and hashtags
- [ ] A/B testing thumbnails
- [ ] Analytics dashboard
- [ ] Scheduling and queue system

### Phase 4 — Advanced 🧠
- [ ] Fine-tuned Hebrew highlight model
- [ ] Audience engagement prediction
- [ ] Multi-language support
- [ ] Real-time processing (live stream → reels)
- [ ] Web UI dashboard

---

## 🙏 Inspiration & Credits

Built with inspiration from:
- [Opus Clip](https://opus.pro) — AI highlight detection
- [Vidyo.ai](https://vidyo.ai) — Podcast to reels
- [VideoCutterAI](https://github.com/topics/video-cutter-ai) — Open-source video cutting
- [Highlight-Extractor](https://github.com/Dockerel/highlight-extractor) — Subtitle-based highlights
- [ivrit.ai](https://huggingface.co/ivrit-ai) — Hebrew Whisper fine-tuning
- [ReelsBuilder AI](https://reelsbuilder.ai) — Automated reel creation

---

## 📄 License

MIT License — see [LICENSE](LICENSE)