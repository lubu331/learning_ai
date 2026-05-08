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


def test_fix_math_answers_uses_operation_for_word_problem():
    questions = [
        {
            "question_type": "free_text",
            "prompt_text": "My father had 5 apples and gave 3 to my brother. How many apples does my father have left?",
            "operation": "5 - 3",
            "choices": [],
            "correct_answer": "wrong",
        }
    ]

    fixed_questions = main.fix_math_answers(questions)

    assert fixed_questions[0]["correct_answer"] == "2"
    assert fixed_questions[0]["explanation"] == "Use the operation 5 - 3. The correct answer is 2."


def test_remove_duplicate_questions_treats_addition_as_commutative():
    questions = [
        {"prompt_text": "What is 8 + 2?"},
        {"prompt_text": "What is the sum of 2 and 8?"},
        {"prompt_text": "What is 8 - 2?"},
        {"prompt_text": "What is 2 - 8?"},
    ]

    unique_questions = main.remove_duplicate_questions(questions)

    assert [q["prompt_text"] for q in unique_questions] == [
        "2 + 8",
        "8 - 2",
        "2 - 8",
    ]


def test_normalize_math_prompt_handles_common_wording():
    assert main.normalize_math_prompt("What is 2 plus 8?") == "2 + 8"
    assert main.normalize_math_prompt("Add 8 and 2.") == "2 + 8"
    assert main.normalize_math_prompt("Subtract 3 from 5.") == "5 - 3"


def test_generate_math_questions_from_text_is_deterministic_and_topic_filtered():
    questions = main.generate_math_questions_from_text(
        pdf_text="1. 8 + 2 = ____\n2. 2 + 8 = ____\n3. 9 - 4 = ____",
        grade_level="2",
        topic="addition",
        question_type="free_text",
        limit=5,
    )

    assert len(questions) == 1
    assert questions[0]["operation"] == "2 + 8"
    assert questions[0]["correct_answer"] == "10"
    assert questions[0]["source"] == "deterministic_math"
