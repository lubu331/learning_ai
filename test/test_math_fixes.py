import app.main as main


def test_fix_math_answers_uses_label_for_generated_correct_choice(monkeypatch):
    def fake_shuffle(values):
        values[:] = [13, 12, 11, 10]

    monkeypatch.setattr(main.random, "shuffle", fake_shuffle)

    questions = [
        {
            "question_type": "multiple_choice",
            "prompt_text": "6 + 6",
            "choices": [
                {"label": "A", "text": "11"},
                {"label": "B", "text": "10"},
                {"label": "C", "text": "9"},
                {"label": "D", "text": "8"},
            ],
            "correct_answer": "A",
        }
    ]

    fixed_questions = main.fix_math_answers(questions)

    assert fixed_questions[0]["choices"] == [
        {"label": "A", "text": "13"},
        {"label": "B", "text": "12"},
        {"label": "C", "text": "11"},
        {"label": "D", "text": "10"},
    ]
    assert fixed_questions[0]["correct_answer"] == "B"
