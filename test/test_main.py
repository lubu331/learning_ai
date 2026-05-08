import asyncio
from io import BytesIO

from fastapi import UploadFile
from fastapi import HTTPException

import app.main as main
from app.services.ai_service import OllamaServiceError


def test_get_curriculum_returns_ten_starter_topics():
    response = main.get_curriculum()

    topics = [
        topic
        for subject_topics in response["subjects"].values()
        for topic in subject_topics
    ]

    assert len(topics) == 10
    assert {topic["id"] for topic in topics} >= {
        "reading_comprehension",
        "vocabulary",
        "grammar",
        "sentence_writing",
        "colombian_geography",
        "colombian_history",
        "civic_behavior",
        "addition",
        "subtraction",
        "word_problems",
    }


def test_list_pdfs_returns_saved_pdf_metadata(tmp_path, monkeypatch):
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    pdf_path = uploads_dir / "worksheet.PDF"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)

    response = main.list_pdfs()

    assert response["files"] == [
        {
            "name": "worksheet.PDF",
            "size_bytes": len(b"%PDF-1.4 fake"),
            "modified_at": response["files"][0]["modified_at"],
        }
    ]
    assert response["files"][0]["modified_at"]


def test_create_quiz_passes_grade_level_to_batch_generator(tmp_path, monkeypatch):
    uploads_dir = tmp_path / "uploads"
    generated_dir = tmp_path / "generated_quizzes"
    uploads_dir.mkdir()
    generated_dir.mkdir()

    captured_kwargs = {}

    def fake_generate_quiz_in_batches(**kwargs):
        captured_kwargs.update(kwargs)
        return [
            {
                "question_code": "Q1",
                "question_tag": "grade2.math",
                "question_type": "multiple_choice",
                "prompt_text": "2 + 2",
                "choices": [
                    {"label": "A", "text": "4"},
                    {"label": "B", "text": "5"},
                    {"label": "C", "text": "6"},
                    {"label": "D", "text": "7"},
                ],
                "correct_answer": "A",
                "explanation": "2 + 2 is 4.",
            }
        ]

    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(main, "GENERATED_DIR", generated_dir)
    monkeypatch.setattr(main, "extract_pdf_text", lambda _pdf_path: "2 + 2")
    monkeypatch.setattr(main, "generate_quiz_in_batches", fake_generate_quiz_in_batches)
    monkeypatch.setattr(
        main,
        "validate_questions_with_ollama",
        lambda questions, pdf_text, subject, topic="general": questions,
    )

    response = asyncio.run(
        main.create_quiz(
            grade_level="2",
            subject="math",
            topic="word_problems",
            question_type="multiple_choice",
            limit=1,
            file=UploadFile(filename="lesson.pdf", file=BytesIO(b"%PDF-1.4 fake")),
        )
    )

    assert response["source_pdf"] == "lesson.pdf"
    assert response["topic"] == "word_problems"
    assert captured_kwargs["grade_level"] == "2"
    assert captured_kwargs["topic"] == "word_problems"
    assert "grade" not in captured_kwargs


def test_create_quiz_keeps_math_fix_after_ai_validation(tmp_path, monkeypatch):
    uploads_dir = tmp_path / "uploads"
    generated_dir = tmp_path / "generated_quizzes"
    uploads_dir.mkdir()
    generated_dir.mkdir()

    generated_question = {
        "question_code": "Q1",
        "question_tag": "grade2.math",
        "question_type": "free_text",
        "prompt_text": "6 + 6",
        "choices": [],
        "correct_answer": "11",
        "explanation": "The result is 12, but 6 + 6 = 11 is also valid.",
    }

    def fake_validate_questions_with_ollama(questions, pdf_text, subject, topic="general"):
        return [
            {
                **questions[0],
                "correct_answer": "11",
                "explanation": "The result is 12, but 6 + 6 = 11 is also valid.",
            }
        ]

    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(main, "GENERATED_DIR", generated_dir)
    monkeypatch.setattr(main, "extract_pdf_text", lambda _pdf_path: "6 + 6")
    monkeypatch.setattr(main, "generate_quiz_in_batches", lambda **_kwargs: [generated_question])
    monkeypatch.setattr(main, "validate_questions_with_ollama", fake_validate_questions_with_ollama)

    response = asyncio.run(
        main.create_quiz(
            grade_level="2",
            subject="math",
            topic="addition",
            question_type="free_text",
            limit=1,
            file=UploadFile(filename="math.pdf", file=BytesIO(b"%PDF-1.4 fake")),
        )
    )

    question = response["questions"][0]

    assert question["correct_answer"] == "12"
    assert question["topic"] == "addition"
    assert question["validation_status"] == "validated"
    assert question["explanation"] == "Use the operation 6 + 6. The correct answer is 12."


def test_create_quiz_returns_service_unavailable_when_ollama_times_out(tmp_path, monkeypatch):
    uploads_dir = tmp_path / "uploads"
    generated_dir = tmp_path / "generated_quizzes"
    uploads_dir.mkdir()
    generated_dir.mkdir()

    def fake_generate_quiz_in_batches(**_kwargs):
        raise OllamaServiceError("Ollama timed out after 180 seconds.")

    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(main, "GENERATED_DIR", generated_dir)
    monkeypatch.setattr(main, "extract_pdf_text", lambda _pdf_path: "2 + 2")
    monkeypatch.setattr(main, "generate_quiz_in_batches", fake_generate_quiz_in_batches)

    try:
        asyncio.run(
            main.create_quiz(
                grade_level="2",
                subject="math",
                topic="addition",
                question_type="multiple_choice",
                limit=1,
                file=UploadFile(filename="math.pdf", file=BytesIO(b"%PDF-1.4 fake")),
            )
        )
    except HTTPException as e:
        assert e.status_code == 503
        assert "timed out" in e.detail
    else:
        raise AssertionError("Expected HTTPException")


def test_create_quiz_uses_fast_math_path_without_ollama(tmp_path, monkeypatch):
    uploads_dir = tmp_path / "uploads"
    generated_dir = tmp_path / "generated_quizzes"
    uploads_dir.mkdir()
    generated_dir.mkdir()

    def fail_generate_quiz_in_batches(**_kwargs):
        raise AssertionError("Ollama path should not run for text-based math worksheets")

    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(main, "GENERATED_DIR", generated_dir)
    monkeypatch.setattr(main, "extract_pdf_text", lambda _pdf_path: "1. 8 + 2 = ____\n2. 9 - 4 = ____")
    monkeypatch.setattr(main, "generate_quiz_in_batches", fail_generate_quiz_in_batches)

    response = asyncio.run(
        main.create_quiz(
            grade_level="2",
            subject="math",
            topic="addition",
            question_type="free_text",
            limit=3,
            file=UploadFile(filename="math.pdf", file=BytesIO(b"%PDF-1.4 fake")),
        )
    )

    assert response["generation_mode"] == "deterministic_math"
    assert len(response["questions"]) == 1
    assert response["questions"][0]["operation"] == "2 + 8"
