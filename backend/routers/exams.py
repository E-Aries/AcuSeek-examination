from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Exam, Question, ExamPaper
from schemas import ExamCreate
import random

import json

def _ensure_list(val):
    if val is None: return None
    if isinstance(val, list): return val
    if isinstance(val, str):
        try: return json.loads(val)
        except: return [val]
    return val

router = APIRouter(prefix="/api/exams", tags=["exams"])

@router.get("")
def list_exams(status: str = "", search: str = "", db = Depends(get_db)):
    q = db.query(Exam)
    if status: q = q.filter(Exam.status == status)
    if search: q = q.filter(Exam.name.like(f"%{search}%"))
    items = q.order_by(Exam.id.desc()).all()
    return {"items": [{"id": e.id, "name": e.name, "type": e.type, "status": e.status, "duration": e.duration, "question_count": e.question_count, "pass_score": e.pass_score, "strategy": e.strategy, "categories": e.categories} for e in items]}

@router.post("")
def create_exam(data: ExamCreate, db = Depends(get_db)):
    exam = Exam(**data.model_dump(), status="未开始")
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return {"id": exam.id, "message": "创建成功"}

@router.get("/{eid}")
def get_exam(eid: int, db = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")
    return exam

@router.post("/{eid}/start")
def start_exam(eid: int, user_id: int = 1, db = Depends(get_db)):
    existing = db.query(ExamPaper).filter(ExamPaper.exam_id == eid, ExamPaper.user_id == user_id).first()
    if existing: return {"paper_id": existing.id, "questions": existing.questions}

    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")

    q = db.query(Question)
    cats = _ensure_list(exam.categories)
    if cats: q = q.filter(Question.category.in_(cats))
    all_qs = q.all()

    selected = []
    dist = _ensure_list(exam.distribution) if isinstance(exam.distribution, str) else exam.distribution
    if dist:
        for qtype, count in exam.distribution.items():
            pool = [q for q in all_qs if q.type == qtype]
            random.shuffle(pool)
            c = count.get("count", count) if isinstance(count, dict) else count
            selected.extend(pool[:c])
    else:
        random.shuffle(all_qs)
        selected = all_qs[:exam.question_count]

    snapshot = [{"id": q.id, "type": q.type, "content": q.content, "options": q.options, "score": q.score} for q in selected]
    paper = ExamPaper(exam_id=eid, user_id=user_id, questions=snapshot)
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return {"paper_id": paper.id, "questions": snapshot}
