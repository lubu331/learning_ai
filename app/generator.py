import json
from pathlib import Path
from typing import List, Optional
from app.config import CONTENT_DIR


def load_questions_for_grade_subject(grade_level: str, subject_filename: str) -> List[dict]:
    file_path = CONTENT_DIR / f"grade_{grade_level}" / subject_filename

    if not file_path.exists():
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("questions", [])


def filter_questions(
    questions: List[dict],
    question_type: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 5
) -> List[dict]:
    filtered = questions

    if question_type:
        filtered = [q for q in filtered if q.get("question_type") == question_type]

    if topic:
        filtered = [q for q in filtered if q.get("topic", "").lower() == topic.lower()]

    return filtered[:limit]


def subject_to_filename(subject: str) -> str:
    mapping = {
        "math": "math.json",
        "science": "science.json",
        "sociales": "sociales_colombia.json",
        "spanish": "spanish.json",
        "english": "english.json",
    }
    return mapping.get(subject.lower(), f"{subject.lower()}.json")