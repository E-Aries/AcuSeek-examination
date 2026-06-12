from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    name = Column(String(50))
    role = Column(String(20), default="candidate")
    department = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), index=True)
    category = Column(String(50), index=True)
    content = Column(Text)
    options = Column(JSON, nullable=True)
    answer = Column(Text, default="")
    explanation = Column(Text, default="")
    difficulty = Column(Integer, default=1)
    score = Column(Integer, default=2)
    used_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    sort = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    type = Column(String(10), index=True)
    status = Column(String(10), default="未开始")
    duration = Column(Integer, default=60)
    question_count = Column(Integer, default=30)
    pass_score = Column(Integer, default=60)
    strategy = Column(String(10), default="random")
    categories = Column(JSON, nullable=True)
    distribution = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ExamPaper(Base):
    __tablename__ = "exam_papers"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    questions = Column(JSON)
    answers = Column(JSON, default=dict)
    score = Column(Float, nullable=True)
    status = Column(String(10), default="进行中")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)
    duration_used = Column(Integer, default=0)


class OperationLog(Base):
    __tablename__ = "operation_logs"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), default="")
    action = Column(String(50), default="")
    target = Column(String(200), default="")
    detail = Column(Text, default="")
    ip = Column(String(50), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SystemSetting(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, default="")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=0)
    title = Column(String(200), default="")
    content = Column(Text, default="")
    type = Column(String(20), default="system")
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
