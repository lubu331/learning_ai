import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Quiz
from app.services.ai_service import generate_quiz_from_file
from pathlib import Path

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/generate")
def generate_quiz(
        file: UploadFile = File(...),
        topic: str = Form(...),
        grade: str = Form(...),
        db: Session = Depends(get_db)
):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Process via Local AI
    result = generate_quiz_from_file(file_path, topic, grade)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "AI Generation Failed"))

    # Save to DB
    new_quiz = Quiz(
        title=f"Quiz: {topic}",
        topic=topic,
        grade_level=grade,
        questions_json=str(result["questions"])
    )
    db.add(new_quiz)
    db.commit()

    return {"message": "Quiz Generated", "quiz_id": new_quiz.id}


@router.get("/list")
def list_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).all()
    return [{"id": q.id, "title": q.title, "topic": q.topic} for q in quizzes]