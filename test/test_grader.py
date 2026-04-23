from app.grader import grade_free_text, grade_multiple_choice


def test_grade_free_text_correct():
    question = {
        "question_code": "TEST-1",
        "question_tag": "test.free_text",
        "accepted_answers": ["7", "siete"],
        "explanation": "4 + 3 es 7."
    }
    result = grade_free_text(question, "7")
    assert result["is_correct"] is True


def test_grade_multiple_choice_correct():
    question = {
        "question_code": "TEST-2",
        "question_tag": "test.mcq",
        "choices": [
            {"label": "A", "text": "1", "is_correct": False},
            {"label": "B", "text": "2", "is_correct": True}
        ],
        "explanation": "La correcta es B."
    }
    result = grade_multiple_choice(question, "B")
    assert result["is_correct"] is True