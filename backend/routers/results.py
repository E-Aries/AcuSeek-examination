from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import StreamingResponse
from database import get_db
from models import ExamPaper, Exam, User
from .auth import get_current_user

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

# ── IMPORTANT: static routes must come BEFORE parameterized routes ──
@router.get("/by-exam")
def results_by_exam(db = Depends(get_db)):
    exams = db.query(Exam).order_by(Exam.id.desc()).all()
    items = []
    for e in exams:
        papers = db.query(ExamPaper).filter(ExamPaper.exam_id == e.id).all()
        submitted = [p for p in papers if p.status in ("已完成", "待批改")]
        if not submitted and not papers:
            continue
        scores = [p.score or 0 for p in submitted]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0
        passed_count = sum(1 for p in submitted if (p.score or 0) >= e.pass_score)
        top_score = max(scores) if scores else 0
        items.append({
            "exam_id": e.id, "exam_name": e.name, "exam_type": e.type,
            "candidates": len(papers), "submitted": len(submitted),
            "passed": passed_count, "pass_rate": round(passed_count / len(submitted) * 100) if submitted else 0,
            "avg_score": avg_score, "top_score": top_score,
        })
    return {"items": items}

@router.get("/export")
def export_results(db = Depends(get_db)):
    rows = db.query(ExamPaper, Exam, User).join(Exam, ExamPaper.exam_id == Exam.id).join(User, ExamPaper.user_id == User.id).order_by(ExamPaper.submitted_at.desc().nullslast()).all()
    import csv, io
    output = io.StringIO()
    output.write("\ufeff")  # BOM for Excel UTF-8 recognition
    writer = csv.writer(output)
    writer.writerow(["\u8bd5\u5377ID", "\u8003\u6838\u540d\u79f0", "\u8003\u6838\u7c7b\u578b", "\u8003\u751f", "\u90e8\u95e8", "\u6210\u7ee9", "\u72b6\u6001", "\u7528\u65f6(\u79d2)", "\u63d0\u4ea4\u65f6\u95f4"])
    for r in rows:
        writer.writerow([r[0].id, r[1].name, r[1].type, r[2].name, r[2].department, r[0].score or "", r[0].status, r[0].duration_used or "", str(r[0].submitted_at or "")])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=exam_results.csv"})


@router.get("/my")
def my_results(user = Depends(get_current_user), db = Depends(get_db)):
    papers = db.query(ExamPaper).filter(ExamPaper.user_id == user.id).order_by(ExamPaper.id.desc()).all()
    items = []
    for p in papers:
        exam = db.query(Exam).filter(Exam.id == p.exam_id).first()
        if not exam: continue
        total_score = sum(q.get("score", 0) for q in (p.questions or []))
        items.append({
            "paper_id": p.id,
            "exam_id": p.exam_id,
            "exam_name": exam.name,
            "exam_type": exam.type,
            "status": p.status,
            "score": p.score,
            "total_score": total_score,
            "pass_score": exam.pass_score,
            "duration_used": p.duration_used,
            "submitted_at": str(p.submitted_at or "")
        })
    return {"items": items}

@router.get("/{paper_id}")
def get_result(paper_id: int, db = Depends(get_db)):
    row = db.query(ExamPaper, Exam, User).join(Exam, ExamPaper.exam_id == Exam.id).join(User, ExamPaper.user_id == User.id).filter(ExamPaper.id == paper_id).first()
    if not row: return {"error": "not found"}
    paper, exam, user = row
    return {"paper_id": paper.id, "exam_id": exam.id, "exam_name": exam.name, "exam_type": exam.type, "pass_score": exam.pass_score, "question_count": exam.question_count, "candidate": user.name, "department": user.department, "questions": paper.questions, "answers": paper.answers, "score": paper.score, "status": paper.status, "duration_used": paper.duration_used, "submitted_at": str(paper.submitted_at or "")}
