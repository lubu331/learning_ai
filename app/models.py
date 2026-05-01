from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class IncorrectFeedbackLog(Base):
    __tablename__ = "incorrect_feedback_logs"

    id = Column(Integer, primary_key=True, index=True)
    question_code = Column(String, nullable=False)
    question_tag = Column(String, nullable=False)
    subject_name = Column(String, nullable=True)
    topic_name = Column(String, nullable=True)
    student_response = Column(Text, nullable=False)
    correct_answer_summary = Column(Text, nullable=False)
    feedback_text = Column(Text, nullable=False)
    review_status = Column(String, default="pending", nullable=False)
    teacher_parent_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
