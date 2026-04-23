from app.generator import filter_questions


def test_filter_questions_by_type():
    questions = [
        {"question_type": "free_text", "topic": "A"},
        {"question_type": "multiple_choice", "topic": "B"}
    ]
    result = filter_questions(questions, question_type="free_text", limit=5)
    assert len(result) == 1
    assert result[0]["question_type"] == "free_text"