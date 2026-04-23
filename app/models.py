from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from app.db import Base


class IncorrectFeedbackLog(Base):
    __tablename__ = "incorrect_feedback_log"

    id = Column(Integer, primary_key=True, index=True)
    question_code = Column(String, nullable=False, index=True)
    question_tag = Column(String, nullable=False, index=True)
    subject_name = Column(String, nullable=True)
    topic_name = Column(String, nullable=True)
    student_response = Column(Text, nullable=True)
    correct_answer_summary = Column(Text, nullable=True)
    feedback_text = Column(Text, nullable=True)
    review_status = Column(String, default="pending")
    teacher_parent_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=True)
    grade_level = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    question_mode = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())