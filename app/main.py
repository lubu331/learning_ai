import json
import random
import re
import shutil
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.ai_service import (
    generate_questions_from_pdf_images,
    generate_questions_with_ollama,
    validate_questions_with_ollama,
)
from app.services.pdf_service import extract_pdf_text, pdf_to_images_base64


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
UPLOADS_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "generated_quizzes"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
UPLOADS_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Learning AI Quiz App")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnswerRequest(BaseModel):
    question: dict
    student_answer: str

class FeedbackRequest(BaseModel):
    question_code: str
    prompt_text: str
    reason: str
    user_note: str = ""
    timestamp: str = ""

@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/pdfs")
def list_pdfs():
    files = sorted([p.name for p in UPLOADS_DIR.glob("*.pdf")])
    return {"files": files}


def evaluate_math(expr: str):
    match = re.search(r"(\d+)\s*([+\-])\s*(\d+)", expr)

    if not match:
        return None

    a, op, b = match.groups()
    a = int(a)
    b = int(b)

    if op == "+":
        return a + b

    if op == "-":
        return a - b

    return None


def fix_math_answers(questions: list[dict]):
    for q in questions:
        correct = evaluate_math(q.get("prompt_text", ""))

        if correct is None:
            continue

        q["explanation"] = (
            f"Add or subtract the numbers carefully. "
            f"The correct answer is {correct}."
        )

        if q.get("question_type") == "multiple_choice":
            found = False

            for choice in q.get("choices", []):
                choice_text = str(choice.get("text", "")).strip()

                if choice_text == str(correct):
                    q["correct_answer"] = choice.get("label")
                    found = True
                    break

            if not found:
                q["choices"] = build_math_choices(correct)
                q["correct_answer"] = "A"

        else:
            q["correct_answer"] = str(correct)

    return questions


def build_math_choices(correct: int):
    wrong_values = set()

    while len(wrong_values) < 3:
        offset = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        value = correct + offset

        if value >= 0 and value != correct:
            wrong_values.add(value)

    values = [correct] + list(wrong_values)
    random.shuffle(values)

    labels = ["A", "B", "C", "D"]
    choices = []

    for label, value in zip(labels, values):
        choices.append({"label": label, "text": str(value)})

    return choices


def normalize_question(q: dict, index: int, grade_level: str, subject: str, question_type: str):
    q.setdefault("question_code", f"Q{index}")
    q.setdefault("question_tag", f"grade{grade_level}.{subject}")
    q.setdefault("question_type", question_type)
    q.setdefault("prompt_text", "")
    q.setdefault("choices", [])
    q.setdefault("correct_answer", "")
    q.setdefault("explanation", "Good effort. Review the correct answer.")

    return q

def normalize_math_prompt(prompt: str) -> str:
    match = re.search(r"(\d+)\s*([+\-])\s*(\d+)", prompt)

    if match:
        a, op, b = match.groups()
        return f"{a} {op} {b}"

    prompt = prompt.replace("__________", "")
    prompt = prompt.replace("____", "")
    prompt = prompt.replace("___", "")
    prompt = prompt.replace("__", "")
    prompt = prompt.replace("_", "")
    prompt = prompt.replace("=", "")

    return prompt.strip()


def question_key(q: dict) -> str:
    prompt = normalize_math_prompt(q.get("prompt_text", ""))
    return prompt.lower().strip()


def remove_duplicate_questions(questions: list[dict]):
    seen = set()
    unique = []

    for q in questions:
        key = question_key(q)

        if key in seen:
            continue

        seen.add(key)
        q["prompt_text"] = normalize_math_prompt(q.get("prompt_text", ""))
        unique.append(q)

    return unique

def generate_quiz_in_batches(
    *,
    pdf_text: str,
    images: Optional[list[str]],
    grade_level: str,
    subject: str,
    question_type: str,
    limit: int,
):
    all_questions = []
    batch_size = 5
    batch_number = 0

    while len(all_questions) < limit:
        batch_number += 1

        remaining = limit - len(all_questions)
        current_batch_size = min(batch_size, remaining)

        print(f"Generating batch {batch_number}: {current_batch_size} questions")

        if pdf_text.strip():
            batch = generate_questions_with_ollama(
                pdf_text=pdf_text,
                grade_level=grade_level,
                subject=subject,
                question_type=question_type,
                limit=current_batch_size,
            )
        else:
            batch = generate_questions_from_pdf_images(
                images_base64=images or [],
                grade_level=grade_level,
                subject=subject,
                question_type=question_type,
                limit=current_batch_size,
            )

        if not isinstance(batch, list):
            raise HTTPException(
                status_code=500,
                detail="Ollama did not return a valid question list.",
            )

        all_questions.extend(batch)

    return all_questions[:limit]


@app.post("/quiz")
async def create_quiz(
    grade_level: str = Form(...),
    subject: str = Form(...),
    question_type: str = Form(...),
    limit: int = Form(5),
    existing_pdf: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    pdf_path = None

    if file and file.filename:
        safe_name = Path(file.filename).name

        if not safe_name.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        pdf_path = UPLOADS_DIR / safe_name

        with pdf_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    elif existing_pdf:
        safe_name = Path(existing_pdf).name
        pdf_path = UPLOADS_DIR / safe_name

        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Selected PDF does not exist.")

    else:
        raise HTTPException(
            status_code=400,
            detail="Upload a PDF or select an existing one.",
        )

    pdf_text = extract_pdf_text(pdf_path)
    images = None

    if not pdf_text.strip():
        images = pdf_to_images_base64(pdf_path, max_pages=1)

    # 1. Generate initial questions
    try:
        questions = generate_quiz_in_batches(
            pdf_text=pdf_text,
            images=images,
            grade=grade_level,
            subject=subject,
            question_type=question_type,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


    if not questions:
        raise HTTPException(
            status_code=500,
            detail="Could not generate quiz questions. Check Ollama output.",
        )

    # 2. Fix Math Answers specifically
    questions = fix_math_answers(questions)

    # 3. VALIDATE ALL QUESTIONS (Crucial for Science/History/Logic)
    print("Validating questions for factual correctness...")
    try:
        questions = validate_questions_with_ollama(
            questions=questions,
            pdf_text=pdf_text,
            subject=subject
        )
    except Exception as e:
        print(f"Warning: Validation step failed ({e}), proceeding with generated questions.")

    # 4. Normalize structure
    normalized_questions = []
    for index, q in enumerate(questions, start=1):
        normalized_questions.append(
            normalize_question(
                q=q,
                index=index,
                grade_level=grade_level,
                subject=subject,
                question_type=question_type,
            )
        )

    # 5. Remove duplicates
    questions = remove_duplicate_questions(normalized_questions)

    # 6. Shuffle and limit
    random.shuffle(questions)
    questions = questions[:limit]

    output_file = GENERATED_DIR / f"{pdf_path.stem}_quiz.json"
    output_file.write_text(
        json.dumps(questions, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "source_pdf": pdf_path.name,
        "questions": questions,
    }


@app.post("/submit-feedback")
def submit_feedback(request: FeedbackRequest):
    """
    Receives feedback from the frontend and logs it to a JSON Lines file.
    """
    feedback_entry = {
        "question_code": request.question_code,
        "prompt_text": request.prompt_text,
        "reason": request.reason,
        "user_note": request.user_note,
        "timestamp": datetime.now().isoformat()
    }

    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)
    log_file_path = LOGS_DIR / "feedback.jsonl"

    # Append the new feedback entry to the file
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry) + "\n")

    return {"status": "success", "message": "Feedback received. Thank you!"}


@app.post("/answer")
def submit_answer(request: AnswerRequest):
    question = request.question
    student_answer = request.student_answer.strip()

    correct_answer = str(question.get("correct_answer", "")).strip()
    explanation = question.get("explanation", "")

    # Handle multiple choice vs free text comparison
    if question.get("question_type") == "multiple_choice":
        # For multiple choice, we compare the label (A, B, C, D)
        is_correct = student_answer.upper() == correct_answer.upper()
    else:
        # For free text, we do a simple case-insensitive string match
        # Note: This is basic. For production, you might want fuzzy matching or AI validation.
        is_correct = student_answer.lower() == correct_answer.lower()

    return {
        "is_correct": is_correct,
        "feedback_text": "Correct!" if is_correct else explanation,
        "correct_answer_summary": f"Correct answer: {correct_answer}",
    }