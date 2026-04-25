import json
import random
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.ai_service import generate_questions_with_ollama
from app.services.pdf_service import extract_pdf_text


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
UPLOADS_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "generated_quizzes"

UPLOADS_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Learning AI Quiz App")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnswerRequest(BaseModel):
    question: dict
    student_answer: str


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/pdfs")
def list_pdfs():
    files = sorted([p.name for p in UPLOADS_DIR.glob("*.pdf")])
    return {"files": files}


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
            raise HTTPException(status_code=400, detail="Only PDF files are supported for now.")

        pdf_path = UPLOADS_DIR / safe_name

        with pdf_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    elif existing_pdf:
        safe_name = Path(existing_pdf).name
        pdf_path = UPLOADS_DIR / safe_name

        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Selected PDF does not exist.")

    else:
        raise HTTPException(status_code=400, detail="Upload a PDF or select an existing one.")

    pdf_text = extract_pdf_text(pdf_path)

    if not pdf_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    questions = generate_questions_with_ollama(
        pdf_text=pdf_text,
        grade_level=grade_level,
        subject=subject,
        question_type=question_type,
        limit=limit,
    )

    random.shuffle(questions)
    questions = questions[:limit]

    output_file = GENERATED_DIR / f"{pdf_path.stem}_quiz.json"
    output_file.write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "source_pdf": pdf_path.name,
        "questions": questions,
    }


@app.post("/answer")
def submit_answer(request: AnswerRequest):
    question = request.question
    student_answer = request.student_answer.strip()

    correct_answer = str(question.get("correct_answer", "")).strip()
    explanation = question.get("explanation", "")

    is_correct = student_answer.lower() == correct_answer.lower()

    return {
        "is_correct": is_correct,
        "feedback_text": "Correct!" if is_correct else explanation or "Review the correct answer.",
        "correct_answer_summary": f"Correct answer: {correct_answer}",
    }