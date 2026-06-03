from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import ExamPaper, Exam, User

router = APIRouter(prefix="/api/results", tags=["results"])

@router.get("")
def list_results(db = Depends(get_db)):
    rows = db.query(ExamPaper, Exam, User).join(Exam, ExamPaper.exam_id == Exam.id).join(User, ExamPaper.user_id == User.id).order_by(ExamPaper.submitted_at.desc().nullslast()).all()
    return {"items": [{"paper_id": r[0].id, "exam_name": r[1].name, "exam_type": r[1].type, "candidate": r[2].name, "department": r[2].department, "score": r[0].score, "status": r[0].status, "duration_used": r[0].duration_used, "submitted_at": str(r[0].submitted_at or "")} for r in rows]}

@router.get("/stats")
def result_stats(db = Depends(get_db)):
    exams_count = db.query(func.count(Exam.id)).scalar()
    papers = db.query(ExamPaper).filter(ExamPaper.status.in_(["已完成", "待批改"])).all()
    total = len(papers)
    passed = sum(1 for p in papers if (p.score or 0) >= 60)
    pending = sum(1 for p in papers if p.status == "待批改")
    return {"exams_count": exams_count, "total_candidates": total, "pass_rate": round(passed/total*100) if total else 0, "pending": pending}

@router.get("/{paper_id}")
def get_result(paper_id: int, db = Depends(get_db)):
    row = db.query(ExamPaper, Exam).join(Exam, ExamPaper.exam_id == Exam.id).filter(ExamPaper.id == paper_id).first()
    if not row: return {"error": "not found"}
    paper, exam = row
    return {"paper_id": paper.id, "exam_name": exam.name, "exam_type": exam.type, "questions": paper.questions, "answers": paper.answers, "score": paper.score, "status": paper.status, "duration_used": paper.duration_used, "submitted_at": str(paper.submitted_at or "")}
