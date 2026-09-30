"""Core AI logic: API key handling and study pack generation."""
import os

import anthropic

from utils import parse_json

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_CHARS = 60_000  # cap input size to control cost and latency


def get_api_key():
    """Read the API key from env vars, or Streamlit secrets when deployed."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        import streamlit as st

        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


def build_prompt(text, topic, num_flashcards, num_questions, difficulty):
    return f"""You are an expert tutor. Create a study pack from the material below.
Topic (optional): {topic or "infer from the material"}
Difficulty: {difficulty}

Return ONLY valid JSON (no markdown fences) with exactly this shape:
{{
  "title": "string",
  "summary": "clear 150-250 word summary",
  "key_concepts": [{{"term": "string", "definition": "string"}}],
  "flashcards": [{{"q": "string", "a": "string"}}],
  "quiz": [{{"question": "string", "options": ["A","B","C","D"],
             "answer_index": 0, "explanation": "string"}}],
  "study_plan": [{{"day": "Day 1", "focus": "string", "tasks": ["string"]}}]
}}
Rules: exactly {num_flashcards} flashcards, exactly {num_questions} multiple-choice
questions with 4 options each, 6-10 key concepts, a 5-day study plan.
Base everything on the material; do not invent facts.

MATERIAL:
\"\"\"
{text}
\"\"\""""


def generate_study_pack(text, topic="", num_flashcards=10, num_questions=5,
                        difficulty="Medium", api_key=None):
    """Return a dict: title, summary, key_concepts, flashcards, quiz, study_plan."""
    api_key = api_key or get_api_key()
    if not api_key:
        raise ValueError("Missing ANTHROPIC_API_KEY.")
    text = (text or "").strip()[:MAX_CHARS]
    if not text and not topic:
        raise ValueError("Provide study material or a topic.")

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": build_prompt(text, topic, num_flashcards, num_questions, difficulty),
        }],
    )
    raw = "".join(b.text for b in msg.content if b.type == "text")
    return parse_json(raw)
