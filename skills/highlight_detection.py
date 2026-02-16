"""
Skill: Highlight Detection
Use Gemini LLM to analyze a Hebrew podcast transcript and identify
the most engaging, quotable, and viral-worthy moments.
"""

import json
from typing import Optional

from models import Transcript, Highlight


HIGHLIGHT_PROMPT = """
אתה מומחה לתוכן ויראלי ברשתות חברתיות. קיבלת תמלול של פודקאסט בעברית.

המשימה שלך: מצא את {max_highlights} הרגעים הכי מעניינים, ציטוטים חזקים, ורגעים ויראליים 
שיכולים להפוך לרילס מצליח באינסטגרם, טיקטוק, או YouTube Shorts.

{focus_instruction}

חוקים:
- כל קטע חייב להיות בין {min_duration} ל-{max_duration} שניות
- חפש רגעים עם: ערך לימודי, מידע שימושי, תובנות מעמיקות, רגש חזק או הומור.
- המטרה היא שהצופה ילמד משהו חדש או יקבל השראה מהתוכן.
- דרג כל קטע לפי פוטנציאל ויראליות (1-10)
- הקטעים צריכים לעבוד כסרטון עצמאי (לא צריך הקשר נוסף)

הנה התמלול:
{transcript_text}

החזר תשובה בפורמט JSON בלבד:
{{
    "highlights": [
        {{
            "start": <start_seconds>,
            "end": <end_seconds>,
            "text": "<the quoted text>",
            "virality_score": <1-10>,
            "reason": "<why this moment is engaging - in Hebrew>",
            "suggested_title": "<catchy reel title - in Hebrew>",
            "signals": ["emotional_peak", "quotable", ...]
        }}
    ]
}}
"""


def detect_highlights_llm(
    transcript: Transcript,
    model_name: str = "gemini-2.5-flash",
    max_highlights: int = 5,
    min_duration: int = 30,
    max_duration: int = 90,
    min_score: int = 6,
    signals: Optional[list[str]] = None,
    focus_speaker: Optional[str] = None,
) -> list[Highlight]:
    """
    Detect viral-worthy highlights using Gemini LLM.

    Args:
        transcript: Full Hebrew transcript with timestamps
        model_name: Gemini model name
        max_highlights: Maximum highlights to find
        min_duration: Minimum clip duration in seconds
        max_duration: Maximum clip duration in seconds
        min_score: Minimum virality score to include
        signals: Engagement signals to look for
        focus_speaker: Optional speaker name (e.g. "Speaker A") to prioritize
    """
    import google.generativeai as genai
    import os

    # Configure Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(model_name)

    # Build transcript text with timestamps and speaker labels
    transcript_lines = []
    for seg in transcript.segments:
        minutes = int(seg.start // 60)
        seconds = int(seg.start % 60)
        speaker_part = f"({seg.speaker}) " if seg.speaker else ""
        transcript_lines.append(f"[{minutes:02d}:{seconds:02d}] {speaker_part}{seg.text}")

    transcript_text = "\n".join(transcript_lines)

    focus_instruction = ""
    if focus_speaker:
        focus_instruction = (
            f"דגש חשוב: התמקד אך ורק ברגעים שבהם {focus_speaker} מדבר/ת. "
            f"אנחנו רוצים רגעים שבהם {focus_speaker} הוא/היא הדובר/ת העיקרי/ת ומופיע/ה לבד בפריים. "
            f"הימנע ככל האפשר מרגעים שבהם רואים את הדובר/ת השני/ה, גם אם {focus_speaker} מדבר/ת."
        )

    # Build prompt
    prompt = HIGHLIGHT_PROMPT.format(
        max_highlights=max_highlights,
        min_duration=min_duration,
        max_duration=max_duration,
        transcript_text=transcript_text,
        focus_instruction=focus_instruction,
    )

    # Call Gemini
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json",
        },
    )

    # Parse response
    result = json.loads(response.text)
    highlights = []

    for i, h in enumerate(result.get("highlights", [])):
        if h.get("virality_score", 0) >= min_score:
            highlights.append(Highlight(
                id=i,
                start=h["start"],
                end=h["end"],
                text=h["text"],
                virality_score=h["virality_score"],
                reason=h["reason"],
                suggested_title=h.get("suggested_title"),
                signals=h.get("signals", []),
            ))

    return highlights
