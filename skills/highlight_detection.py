"""
Skill: Highlight Detection
Use Gemini LLM to analyze a Hebrew podcast transcript and identify
the most engaging, quotable, and viral-worthy moments.
"""

import json
from typing import Optional

from models import Transcript, Highlight


HIGHLIGHT_PROMPT = """
אתה עורך תוכן בכיר (Senior Content Editor) המתמחה ביצירת רילס ויראליים חינוכיים ומעוררי השראה.

המשימה שלך: קיבלת תמלול של שיחה/ראיון. עליך לאתר ו"לזקק" את {max_highlights} הרגעים המלמדים, המעמיקים והחכמים ביותר.

קריטריונים לבחירה (Strict Guidelines):
1. **ערך לימודי גבוה (Insightful & Educational)**:
   - חפש הסברים שמשנים תפיסה ("Aha moments").
   - התמקד בעצות פרקטיות, הסברים מדעיים/פסיכולוגיים, או תובנות עמוקות על החיים.
   - הימנע מקלישאות. חפש את ה"זהב" בשיחה.

2. **ניקיון הקליפ (Clean & Focused)**:
   - **חשוב מאוד**: ודא שהקטע הנבחר מכיל דיבור רצוף של דובר אחד בעיקר.
   - אל תחתוך באמצע משפט.
   - נסה להימנע מקטעים שיש בהם הפרעות, צחוקים מרובים של המראיין, או "רעש" שלא תורם לתוכן הלימודי.
   - אם יש שאלה קצרה שמביאה לתשובה ארוכה ומעולה, אפשר לכלול אותה, אבל הפוקוס הוא על התשובה.

3. **מבנה ויראלי (Viral Structure)**:
   - הוק (Hook): המשפט הראשון בקטע חייב לתפוס את האוזן מיד.
   - אורך: {min_duration} עד {max_duration} שניות.
   - עצמאות: הקטע חייב להיות מובן ב-100% גם ללא ההקשר של שאר השיחה.

4. **אריזה שיווקית**:
   - כותרת (Title): כתוב כותרת קצרה, חכמה ומסקרנת שגורמת לאנשים להרגיש שהם עומדים ללמוד משהו חדש.
   - סיבה (Reasoning): נמק מדוע בחרת דווקא את הקטע הזה ומה הערך הלימודי שבו.

להלן התמלול:
{transcript_text}

פלט נדרש (JSON):
{{
    "highlights": [
        {{
            "start": <start_seconds>,
            "end": <end_seconds>,
            "text": "<טקסט התמלול>",
            "virality_score": <1-10>,
            "reason": "<נימוק: מה ה-Insight המרכזי כאן?>",
            "suggested_title": "<כותרת לימודית מסקרנת>",
            "signals": ["educational_value", "insight", "practical_advice"]
        }}
    ]
}}
"""


def detect_highlights_llm(
    transcript: Transcript,
    model_name: str = "gemini-2.0-flash-exp",
    max_highlights: int = 5,
    min_duration: int = 30,
    max_duration: int = 90,
    min_score: int = 6,
    signals: Optional[list[str]] = None,
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

    # Build prompt
    prompt = HIGHLIGHT_PROMPT.format(
        max_highlights=max_highlights,
        min_duration=min_duration,
        max_duration=max_duration,
        transcript_text=transcript_text,
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
