from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from models import ExamPaper, Question
from schemas import AnswerSubmit
from .auth import get_current_user

router = APIRouter(prefix="/api/answers", tags=["answers"])

@router.post("/submit/{paper_id}")
def submit_answers(paper_id: int, data: AnswerSubmit, user = Depends(get_current_user), db = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id, ExamPaper.user_id == user.id).first()
    if not paper: raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.status == "已完成": raise HTTPException(status_code=400, detail="已提交过")

    paper.answers = data.answers
    paper.duration_used = data.duration_used
    paper.submitted_at = datetime.now(timezone.utc)

    total = 0
    has_subjective = False
    for q in paper.questions:
        qid = str(q["id"])
        question = db.query(Question).filter(Question.id == q["id"]).first()
        if not question: continue

        user_ans = data.answers.get(qid, "")
        if question.type in ("单选", "判断"):
            if user_ans == question.answer: total += question.score
        elif question.type == "多选":
            ua = set(user_ans) if isinstance(user_ans, list) else set()
            ca = set(eval(question.answer)) if question.answer.startswith("[") else set([question.answer])
            if ua == ca: total += question.score
        elif question.type == "填空":
            if (user_ans or "").strip() == question.answer.strip(): total += question.score
        elif question.type == "简答":
            has_subjective = True

    paper.score = total
    paper.status = "待批改" if has_subjective else "已完成"
    db.commit()
    return {"score": total, "status": paper.status, "message": "交卷成功"}
from pydantic import BaseModel

class GradeRequest(BaseModel):
    score: float

@router.put("/grade/{paper_id}")
def grade_paper(paper_id: int, data: GradeRequest, db = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.status != "待批改":
        raise HTTPException(status_code=400, detail="只有待批改状态的试卷可以批改")
    paper.score = data.score
    paper.status = "已完成"
    db.commit()
    return {"message": "批改完成", "score": data.score, "status": "已完成"}
