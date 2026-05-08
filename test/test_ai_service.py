import pytest
import requests

from app.services.ai_service import (
    OllamaServiceError,
    generate_questions_from_pdf_images,
    generate_questions_with_ollama,
)


def test_generate_questions_from_pdf_images_uses_images_without_pdf_text(monkeypatch):
    captured_payload = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "response": """
                [
                  {
                    "question_code": "Q1",
                    "question_tag": "grade2.math",
                    "question_type": "multiple_choice",
                    "prompt_text": "2 + 2",
                    "choices": [
                      {"label": "A", "text": "4"},
                      {"label": "B", "text": "5"},
                      {"label": "C", "text": "6"},
                      {"label": "D", "text": "7"}
                    ],
                    "correct_answer": "A",
                    "explanation": "2 + 2 is 4."
                  }
                ]
                """
            }

    def fake_post(url, json, timeout):
        captured_payload.update({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("app.services.ai_service.requests.post", fake_post)

    questions = generate_questions_from_pdf_images(
        images_base64=["fake-image-data"],
        grade_level="2",
        subject="math",
        topic="word_problems",
        question_type="multiple_choice",
        limit=1,
    )

    assert questions[0]["prompt_text"] == "2 + 2"
    assert captured_payload["json"]["images"] == ["fake-image-data"]
    assert "Topic/skill: word_problems" in captured_payload["json"]["prompt"]
    assert "PDF text:" not in captured_payload["json"]["prompt"]


def test_generate_questions_with_ollama_raises_clear_timeout(monkeypatch):
    def fake_post(*_args, **_kwargs):
        raise requests.exceptions.Timeout("slow model")

    monkeypatch.setattr("app.services.ai_service.requests.post", fake_post)

    with pytest.raises(OllamaServiceError, match="timed out"):
        generate_questions_with_ollama(
            pdf_text="2 + 2",
            grade_level="2",
            subject="math",
            topic="addition",
            question_type="multiple_choice",
            limit=1,
        )
