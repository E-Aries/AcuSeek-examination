# Author: 达咩
# 轻则

﻿from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timezone
from database import get_db
from models import Exam, ExamPaper, Question, User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    # ── 题目分类统计（替代各科通过率图表） ──
    cat_rows = db.query(Question.category, func.count(Question.id)).filter(Question.category != "").group_by(Question.category).all()
    category_questions = [{"name": r[0], "count": r[1]} for r in cat_rows]
    category_colors = ["var(--c-primary)", "var(--c-info)", "var(--c-warning)", "var(--c-primary-light)", "var(--c-success)", "var(--c-danger)"]
    for i, c in enumerate(category_questions):
        c["color"] = category_colors[i % len(category_colors)]

    # ── 月度提交统计（近6个月） ──
    now = datetime.now(timezone.utc)
    months = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m < 1:
            m += 12
            y -= 1
        months.append(f"{y}-{m:02d}")

    monthly_data = []
    for ym in months:
        y, m = ym.split("-")
        cnt = db.query(func.count(ExamPaper.id)).filter(
            extract("year", ExamPaper.submitted_at) == int(y),
            extract("month", ExamPaper.submitted_at) == int(m)
        ).scalar()
        monthly_data.append({"month": ym, "count": cnt})

    # ── 近期考核（最近5个，含考生数/平均分） ──
    recent = db.query(Exam).order_by(Exam.id.desc()).limit(5).all()
    recent_exams = []
    for e in reversed(recent):
        papers = db.query(ExamPaper).filter(ExamPaper.exam_id == e.id).all()
        submitted = [p for p in papers if p.status in ("已完成", "待批改")]
        total = len(papers)
        avg = round(sum((p.score or 0) for p in submitted) / len(submitted), 1) if submitted else 0
        recent_exams.append({
            "id": e.id, "name": e.name, "type": e.type, "status": e.status,
            "candidates": total, "avg_score": avg
        })

    # ── 待批改数 ──
    pending = db.query(func.count(ExamPaper.id)).filter(ExamPaper.status == "待批改").scalar()

    return {
        "category_questions": category_questions,
        "monthly_stats": monthly_data,
        "recent_exams": recent_exams,
        "pending": pending,
        "total_questions": db.query(func.count(Question.id)).scalar(),
        "total_exams": db.query(func.count(Exam.id)).scalar(),
        "total_candidates": db.query(func.count(ExamPaper.id)).filter(
            ExamPaper.status.in_(["已完成", "待批改"])).scalar(),
    }
