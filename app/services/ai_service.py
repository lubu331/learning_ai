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
    cleaned.strip()

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
Create {limit} questions.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": VISION_MODEL,
            "prompt": prompt,
            "images": images_base64,
            "stream": False,
        },
        timeout=600,
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

IMPORTANT RULES FOR SPECIFIC QUESTION TYPES:

1. If the original question asks to 'put in order' or 'sequence', create a multiple-choice question where each choice is a full sequence. One choice MUST be the correct order. Example:
   - Choice A: Seed, Small plant, Flower, Plant
   - Choice B: Plant, Seed, Flower, Small plant
   - etc.

2. If the original question is a 'matching' question (e.g., match situations to outcomes), convert it into a multiple-choice question where the prompt includes ALL the situations, and each choice is a complete set of correct matches. Example:
   Prompt: "Match each situation to what is happening:
     1. A bee visits flowers
     2. A plant makes seeds
     3. No insects visit the flowers"
   Choices:
     A. 1→b, 2→c, 3→a
     B. 1→a, 2→b, 3→c
     etc.

3. Never omit the left-hand side (situations, items to order, etc.) from the prompt. Always include them fully.

4. For science/life cycle questions, ensure the correct answer reflects biological accuracy (e.g., seed → small plant → flower → plant).

5. Do NOT invent content. Only use what is in the source text.
"""


def validate_questions_with_ollama(questions: list[dict], pdf_text: str, subject: str):
    """
    Sends generated questions back to Ollama to verify correctness.
    This is crucial for Science/History where logic matters more than calculation.
    """
    prompt = f"""
You are an expert teacher validating quiz questions for a child.

Subject: {subject}

Use ONLY this source content to verify facts:

{pdf_text[:12000]}

Review the quiz questions below.
1. Check if the 'correct_answer' label actually points to the factually correct choice based on the source text.
2. If the AI made a mistake (e.g., chose A but B is correct), update the 'correct_answer' field.
3. Update the 'explanation' to be accurate.
4. Do NOT change the question text or choices, only fix the answer key and explanation if they are wrong.

SPECIAL RULES:
- For ordering questions: Ensure the correct choice lists items in the proper sequence (e.g., seed → small plant → flower → plant).
- For matching questions: Ensure the correct choice maps each item to its correct partner (e.g., 1→b, 2→c, 3→a).
- If a question is missing context (e.g., no situations listed in a matching question), rewrite the prompt_text to include all necessary context from the source.

Return ONLY a valid JSON array with the corrected questions.
No markdown.
No extra text.

Questions to validate:
{json.dumps(questions, ensure_ascii=False)}
"""

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
