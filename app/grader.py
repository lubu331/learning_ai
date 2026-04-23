import json
from pathlib import Path
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.config import LOGS_DIR
from app.models import IncorrectFeedbackLog


INCORRECT_LOG_FILE = LOGS_DIR / "incorrect_answers.json"


def normalize_text(value: str) -> str:
    return value.strip().lower()


def is_free_text_correct(student_answer: str, accepted_answers: List[str]) -> bool:
    normalized_student = normalize_text(student_answer)
    normalized_answers = [normalize_text(a) for a in accepted_answers]
    return normalized_student in normalized_answers


def grade_free_text(question: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
    accepted_answers = question.get("accepted_answers", [])
    explanation = question.get("explanation", "")
    is_correct = is_free_text_correct(student_answer, accepted_answers)

    if is_correct:
        return {
            "question_code": question["question_code"],
            "question_tag": question["question_tag"],
            "is_correct": True,
            "score": 1.0,
            "feedback_text": "¡Correcto! Muy bien.",
            "correct_answer_summary": f"La respuesta correcta es: {accepted_answers[0] if accepted_answers else ''}",
            "reasoning_label": "exact_match"
        }

    return {
        "question_code": question["question_code"],
        "question_tag": question["question_tag"],
        "is_correct": False,
        "score": 0.0,
        "feedback_text": f"No es correcto. {explanation}",
        "correct_answer_summary": f"La respuesta correcta es: {accepted_answers[0] if accepted_answers else ''}",
        "reasoning_label": "incorrect_answer"
    }


def grade_multiple_choice(question: Dict[str, Any], student_choice: str) -> Dict[str, Any]:
    correct_choice = None
    for choice in question.get("choices", []):
        if choice.get("is_correct") is True:
            correct_choice = choice.get("label")
            break

    is_correct = normalize_text(student_choice) == normalize_text(correct_choice or "")

    if is_correct:
        return {
            "question_code": question["question_code"],
            "question_tag": question["question_tag"],
            "is_correct": True,
            "score": 1.0,
            "feedback_text": "¡Muy bien! Elegiste la opción correcta.",
            "correct_answer_summary": f"La opción correcta es {correct_choice}.",
            "reasoning_label": "correct_choice"
        }

    return {
        "question_code": question["question_code"],
        "question_tag": question["question_tag"],
        "is_correct": False,
        "score": 0.0,
        "feedback_text": question.get("explanation", "Respuesta incorrecta."),
        "correct_answer_summary": f"La opción correcta es {correct_choice}.",
        "reasoning_label": "incorrect_choice"
    }


def append_incorrect_json_log(payload: Dict[str, Any]) -> None:
    if INCORRECT_LOG_FILE.exists():
        with open(INCORRECT_LOG_FILE, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
    else:
        existing = []

    existing.append(payload)

    with open(INCORRECT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def store_incorrect_answer(
    db: Session,
    question: Dict[str, Any],
    student_response: str,
    result: Dict[str, Any]
) -> None:
    db_record = IncorrectFeedbackLog(
        question_code=question["question_code"],
        question_tag=question["question_tag"],
        subject_name=question.get("subject"),
        topic_name=question.get("topic"),
        student_response=student_response,
        correct_answer_summary=result["correct_answer_summary"],
        feedback_text=result["feedback_text"],
        review_status="pending",
        teacher_parent_note=None,
    )
    db.add(db_record)
    db.commit()

    json_record = {
        "question_code": question["question_code"],
        "question_tag": question["question_tag"],
        "subject_name": question.get("subject"),
        "topic_name": question.get("topic"),
        "student_response": student_response,
        "correct_answer_summary": result["correct_answer_summary"],
        "feedback_text": result["feedback_text"],
        "review_status": "pending"
    }
    append_incorrect_json_log(json_record)