from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    str(BASE_DIR / "data" / "sqlite" / "learning_quiz.db")
)

APP_LANGUAGE = os.getenv("APP_LANGUAGE", "es")
DEFAULT_GRADE = os.getenv("DEFAULT_GRADE", "2")

CONTENT_DIR = BASE_DIR / "data" / "content"
LOGS_DIR = BASE_DIR / "logs"
SQLITE_DIR = BASE_DIR / "data" / "sqlite"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_DIR.mkdir(parents=True, exist_ok=True)