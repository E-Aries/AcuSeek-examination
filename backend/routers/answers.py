# Author: 达咩
# 轻则

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from database import get_db
from models import ExamPaper, Question
from schemas import AnswerSubmit
from .auth import get_current_user
from models import Exam

router = APIRouter(prefix="/api/answers", tags=["answers"])

@router.post("/submit/{paper_id}")
def submit_answers(paper_id: int, data: AnswerSubmit, user = Depends(get_current_user), db = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id, ExamPaper.user_id == user.id).first()
    if not paper: raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.status == "已完成": raise HTTPException(status_code=400, detail="已提交过")

    paper.answers = data.answers
    paper.duration_used = data.duration_used
    paper.submitted_at = datetime.now(timezone(timedelta(hours=8)))

    # 获取考试类型
    exam = db.query(Exam).filter(Exam.id == paper.exam_id).first()
    exam_type = exam.type if exam else ""

    total = 0
    has_subjective = False
    for q in paper.questions:
        qid = str(q["id"])
        question = db.query(Question).filter(Question.id == q["id"]).first()
        if not question: continue

        user_ans = data.answers.get(qid, "")
        if question.type == "判断" and question.options:
            opt_map = {o["label"]: o["text"] for o in question.options}
            user_ans_text = opt_map.get(user_ans, user_ans)
            if user_ans_text == question.answer: total += question.score
        elif question.type == "单选":
            if user_ans == question.answer: total += question.score
        elif question.type == "多选":
            ua = set(user_ans) if isinstance(user_ans, list) else set()
            ca = set(a.strip() for a in question.answer.split(",") if a.strip())
            if ua == ca: total += question.score
        elif question.type == "填空":
            if (user_ans or "").strip() == question.answer.strip(): total += question.score
        elif question.type == "简答":
            if exam_type == "模拟":
                if (user_ans or "").strip().lower() == (question.answer or "").strip().lower():
                    total += question.score
            else:
                has_subjective = True

    paper.score = total
    # 模拟考试总是自动完成，正式考试有简答需人工批改
    paper.status = "待批改" if (has_subjective and exam_type != "模拟") else "已完成"
    db.commit()
    # Build per-question detail
    detail = {}
    for q in paper.questions:
        qid = str(q["id"])
        question = db.query(Question).filter(Question.id == q["id"]).first()
        if not question: continue
        user_ans = data.answers.get(qid, "")
        correct = False
        if question.type == "判断" and question.options:
            opt_map = {o["label"]: o["text"] for o in question.options}
            user_ans_text = opt_map.get(user_ans, user_ans)
            correct = user_ans_text == question.answer
        elif question.type == "单选":
            correct = user_ans == question.answer
        elif question.type == "多选":
            ua = set(user_ans) if isinstance(user_ans, list) else set()
            ca = set(a.strip() for a in question.answer.split(",") if a.strip())
            correct = ua == ca
        elif question.type == "填空":
            correct = (user_ans or "").strip() == question.answer.strip()
        detail[qid] = {"correct": correct, "userAnswer": user_ans, "correctAnswer": question.answer, "score": question.score if correct else 0}
    return {"score": total, "status": paper.status, "message": "交卷成功", "detail": detail}
from pydantic import BaseModel
from typing import Optional

class GradeRequest(BaseModel):
    score: float
    details: Optional[dict] = None

@router.put("/grade/{paper_id}")
def grade_paper(paper_id: int, data: GradeRequest, db = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.status != "待批改":
        raise HTTPException(status_code=400, detail="只有待批改状态的试卷可以批改")
    paper.score = data.score
    if data.details:
        ans = paper.answers or {}
        ans["_grades"] = data.details
        paper.answers = ans
    paper.status = "已完成"
    db.commit()
    return {"message": "批改完成", "score": data.score, "status": "已完成"}
