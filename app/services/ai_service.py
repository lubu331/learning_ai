import json
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def _extract_json_array(text: str):
    match = re.search(r"\[.*\]", text, re.DOTALL)

    if not match:
        raise ValueError("Ollama did not return a JSON array.")

    return json.loads(match.group(0))


def generate_questions_with_ollama(
    pdf_text: str,
    grade_level: str,
    subject: str,
    question_type: str,
    limit: int,
):
    prompt = f"""
You are creating a quiz for a child.

Grade: {grade_level}
Subject: {subject}
Question type: {question_type}
Number of questions: {limit}

Use ONLY this PDF content:

{pdf_text[:12000]}

Return ONLY a valid JSON array.
No markdown. No explanation outside JSON.

Each question must use this schema:

[
  {{
    "question_code": "Q1",
    "question_tag": "grade{grade_level}.{subject}",
    "question_type": "{question_type}",
    "prompt_text": "Question text here",
    "choices": [
      {{"label": "A", "text": "option A"}},
      {{"label": "B", "text": "option B"}},
      {{"label": "C", "text": "option C"}},
      {{"label": "D", "text": "option D"}}
    ],
    "correct_answer": "A",
    "explanation": "Short kid-friendly explanation"
  }}
]

If question_type is free_text, use an empty choices array and put the expected answer in correct_answer.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=180,
    )

    response.raise_for_status()
    raw = response.json()["response"]

    questions = _extract_json_array(raw)

    if not isinstance(questions, list):
        raise ValueError("Ollama response is not a list.")

    return questions