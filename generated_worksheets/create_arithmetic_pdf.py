import random
from pathlib import Path

import fitz


OUTPUT_PATH = Path(__file__).with_name("grade_2_mixed_addition_subtraction_200_questions.pdf")
RANDOM_SEED = 20260505


def random_number_by_digits(digits: int) -> int:
    if digits == 1:
        return random.randint(1, 9)
    if digits == 2:
        return random.randint(10, 99)
    return random.randint(100, 999)


def build_problem(operation: str) -> str:
    left_digits = random.choice([1, 2, 3])
    right_digits = random.choice([1, 2, 3])
    left = random_number_by_digits(left_digits)
    right = random_number_by_digits(right_digits)

    if operation == "-" and right > left:
        left, right = right, left

    return f"{left} {operation} {right} = ______"


def build_problems(operation: str, count: int) -> list[str]:
    problems = []
    seen = set()

    while len(problems) < count:
        problem = build_problem(operation)

        if problem in seen:
            continue

        seen.add(problem)
        problems.append(problem)

    return problems


def add_header(page: fitz.Page, title: str, subtitle: str) -> None:
    page.insert_text((54, 52), title, fontsize=20, fontname="helv", color=(0.1, 0.14, 0.2))
    page.insert_text((54, 78), subtitle, fontsize=10.5, fontname="helv", color=(0.35, 0.4, 0.48))
    page.draw_line((54, 94), (558, 94), color=(0.85, 0.85, 0.85), width=0.8)


def add_problem_page(doc: fitz.Document, title: str, problems: list[str], page_number: int) -> None:
    page = doc.new_page(width=612, height=792)
    add_header(
        page,
        title,
        "Solve each problem. Mixed 1-digit, 2-digit, and 3-digit numbers.",
    )

    columns = [54, 232, 410]
    y_start = 126
    row_gap = 27
    max_rows = 22

    for index, problem in enumerate(problems):
        col = index // max_rows
        row = index % max_rows
        x = columns[col]
        y = y_start + row * row_gap
        page.insert_text(
            (x, y),
            f"{page_number + index}.  {problem}",
            fontsize=11.5,
            fontname="cour",
            color=(0.08, 0.12, 0.18),
        )


def main() -> None:
    random.seed(RANDOM_SEED)
    addition = build_problems("+", 100)
    subtraction = build_problems("-", 100)
    doc = fitz.open()

    chunks = [
        ("Addition Practice", addition[:50], 1),
        ("Addition Practice", addition[50:], 51),
        ("Subtraction Practice", subtraction[:50], 101),
        ("Subtraction Practice", subtraction[50:], 151),
    ]

    for title, problems, start_number in chunks:
        add_problem_page(doc, title, problems, start_number)

    metadata = {
        "title": "Grade 2 Mixed Addition and Subtraction Practice",
        "subject": "200 arithmetic questions with 1-, 2-, and 3-digit numbers",
        "author": "Learning AI",
    }
    doc.set_metadata(metadata)
    doc.save(OUTPUT_PATH)
    doc.close()
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
