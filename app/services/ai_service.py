import json
import re
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

TEXT_MODEL = "llama3.2:latest"
VISION_MODEL = "llama3.2-vision:latest"


def _extract_json_array(text: str):
    print("\n--- RAW OLLAMA RESPONSE ---")
    print(text)
    print("--- END RAW OLLAMA RESPONSE ---\n")

    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(f"Ollama did not return a JSON array. Raw response: {text}")

    json_text = cleaned[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Ollama returned invalid JSON.\n"
            f"JSON error: {e}\n"
            f"Extracted JSON was:\n{json_text}\n"
            f"Raw response was:\n{text}"
        )


def generate_questions_with_ollama(
    pdf_text: str,
    grade_level: str,
    subject: str,
    question_type: str,
    limit: int,
):
    prompt = _build_quiz_prompt(pdf_text, grade_level, subject, question_type, limit)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": TEXT_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=180,
    )

    response.raise_for_status()
    return _extract_json_array(response.json()["response"])


def generate_questions_from_pdf_images(
    images_base64: list[str],
    grade_level: str,
    subject: str,
    question_type: str,
    limit: int,
):
    prompt = f"""
You are reading a worksheet image and creating a quiz for a child.
For math questions, make sure the correct_answer matches the real calculated answer.
For multiple_choice, correct_answer must be the label of the option with the correct number.
Grade: {grade_level}
Subject: {subject}
Question type: {question_type}
Number of questions: {limit}

Look at the worksheet image carefully.
Extract math problems or learning content from it.
Create randomized quiz questions based only on the visible worksheet.

Return ONLY a valid JSON array.
No markdown.
No extra text.

Important JSON rules:
- Return only a JSON array.
- Do not use markdown.
- Do not wrap the response in ```json.
- Do not add comments.
- Do not add trailing commas.
- All strings must use double quotes.

Do not repeat questions.
Avoid using the exact same math expression more than once.
For math prompts, do not include blanks like ______ or = ______.
Write the prompt as a clean expression, for example: "38 + 28".

Schema:
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

If question_type is free_text, choices must be [] and correct_answer should be the expected answer.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": VISION_MODEL,
            "prompt": prompt,
            "images": images_base64,
            "stream": False,
        },
        timeout=240,
    )

    response.raise_for_status()
    return _extract_json_array(response.json()["response"])


def _build_quiz_prompt(pdf_text, grade_level, subject, question_type, limit):
    return f"""
Create a quiz for a child.

Grade: {grade_level}
Subject: {subject}
Question type: {question_type}
Number of questions: {limit}

For math questions, make sure the correct_answer matches the real calculated answer.
For multiple_choice, correct_answer must be the label of the option with the correct number.

Use ONLY this content:

{pdf_text[:12000]}

Return ONLY a valid JSON array.
No markdown.
No extra text.

Schema:
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
"""