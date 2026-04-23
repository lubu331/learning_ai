from typing import Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import QuizAttempt, IncorrectFeedbackLog
from app.generator import load_questions_for_grade_subject, filter_questions, subject_to_filename
from app.grader import grade_free_text, grade_multiple_choice, store_incorrect_answer
from app.config import BASE_DIR

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Learning AI Quiz App")

static_dir = BASE_DIR / "app" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class QuizRequest(BaseModel):
    grade_level: str = "2"
    subject: str
    question_type: Optional[str] = None
    topic: Optional[str] = None
    limit: int = 5


class AnswerRequest(BaseModel):
    question: Dict[str, Any]
    student_answer: str


@app.get("/")
def root_page():
    return FileResponse(static_dir / "index.html")


@app.post("/quiz")
def create_quiz(request: QuizRequest, db: Session = Depends(get_db)):
    subject_filename = subject_to_filename(request.subject)
    questions = load_questions_for_grade_subject(request.grade_level, subject_filename)

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for that subject/grade")

    selected_questions = filter_questions(
        questions=questions,
        question_type=request.question_type,
        topic=request.topic,
        limit=request.limit
    )

    if not selected_questions:
        raise HTTPException(status_code=404, detail="No matching questions found")

    quiz_attempt = QuizAttempt(
        student_name="local_user",
        grade_level=request.grade_level,
        subject=request.subject,
        topic=request.topic,
        question_mode=request.question_type or "mixed",
        total_questions=len(selected_questions),
        score=0.0
    )
    db.add(quiz_attempt)
    db.commit()
    db.refresh(quiz_attempt)

    return {
        "quiz_attempt_id": quiz_attempt.id,
        "questions": selected_questions
    }


@app.post("/answer")
def submit_answer(request: AnswerRequest, db: Session = Depends(get_db)):
    question = request.question
    question_type = question.get("question_type")

    if question_type == "free_text":
        result = grade_free_text(question, request.student_answer)
    elif question_type == "multiple_choice":
        result = grade_multiple_choice(question, request.student_answer)
    else:
        raise HTTPException(status_code=400, detail="Unsupported question type")

    if not result["is_correct"]:
        store_incorrect_answer(
            db=db,
            question=question,
            student_response=request.student_answer,
            result=result
        )

    return result


@app.get("/review-log")
def get_review_log(db: Session = Depends(get_db)):
    rows = db.query(IncorrectFeedbackLog).order_by(IncorrectFeedbackLog.id.desc()).all()

    return {
        "items": [
            {
                "id": row.id,
                "question_code": row.question_code,
                "question_tag": row.question_tag,
                "subject_name": row.subject_name,
                "topic_name": row.topic_name,
                "student_response": row.student_response,
                "correct_answer_summary": row.correct_answer_summary,
                "feedback_text": row.feedback_text,
                "review_status": row.review_status,
                "created_at": str(row.created_at)
            }
            for row in rows
        ]
    }