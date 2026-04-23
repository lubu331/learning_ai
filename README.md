# Learning AI Quiz App

Local quiz app for kids and adults.

## Features
- Local SQLite database
- Questions loaded from JSON files
- Free-text and multiple-choice quiz modes
- Feedback for correct/incorrect answers
- Wrong-answer logging with question code and tag

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload



main.ty
start FastAPI
expose endpoints like:
generate quiz
submit answer
review mistakes

db.py
open the SQLite file
create a reusable database connection
initialize tables

models.py
define question structure
define quiz records
define wrong answer log structure

# Quiz logic generator
generator.py
load existing questions from your local database
later generate new ones with AI
filter by grade, topic, and type

## Answer Grading
grader.py
compare free-text answers
check multiple-choice answers
give feedback
send wrong answers to the review log

## AI prompt
prompt.py
question generation prompt
free-text grading prompt
multiple-choice grading prompt

config.py
