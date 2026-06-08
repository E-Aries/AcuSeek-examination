# Author: 达咩
# 轻则

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import func
from models import Exam, Question, ExamPaper, User
from schemas import ExamCreate, ExamUpdate
from .auth import get_current_user
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
def list_exams(status: str = "", search: str = "", user = Depends(get_current_user), db = Depends(get_db)):
    q = db.query(Exam)
    if status: q = q.filter(Exam.status == status)
    if search: q = q.filter(Exam.name.like(f"%{search}%"))

    # 考生可以看到所有考核，但只能进入进行中的
    items = q.order_by(Exam.id.desc()).all()
    result = []
    for e in items:
        item = {"id": e.id, "name": e.name, "type": e.type, "status": e.status, "duration": e.duration, "question_count": e.question_count, "pass_score": e.pass_score, "strategy": e.strategy, "categories": e.categories}
        if user.role != "admin":
            item["can_start"] = (e.status == "进行中")
            item["can_manage"] = False
        else:
            item["can_start"] = (e.status != "已结束")
            item["can_manage"] = True
        result.append(item)
    return {"items": result}

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
def start_exam(eid: int, mode: str = "", user = Depends(get_current_user), db = Depends(get_db)):
    existing = db.query(ExamPaper).filter(ExamPaper.exam_id == eid, ExamPaper.user_id == user.id).first()
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # 正式考试：返回已有试卷
    if existing and existing.status == "进行中":
        return {"paper_id": existing.id, "questions": existing.questions}
    if exam.type != "模拟" and mode != "practice":
        if existing and existing.status in ("已完成",):
            return {"paper_id": existing.id, "questions": existing.questions}

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
            if c and c > 0:
                selected.extend(pool[:min(c, len(pool))])
    if not selected:
        random.shuffle(all_qs)
        selected = all_qs[:exam.question_count]

    if mode == "practice":
        snapshot = [{"id": q.id, "type": q.type, "content": q.content, "options": q.options, "score": q.score, "answer": q.answer, "explanation": q.explanation} for q in selected]
    else:
        snapshot = [{"id": q.id, "type": q.type, "content": q.content, "options": q.options, "score": q.score} for q in selected]
    paper = ExamPaper(exam_id=eid, user_id=user.id, questions=snapshot)
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return {"paper_id": paper.id, "questions": snapshot}

@router.get("/{eid}/detail")
def get_exam_detail(eid: int, db = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")
    papers = db.query(ExamPaper).filter(ExamPaper.exam_id == eid).all()
    submitted = [p for p in papers if p.status in ("已完成", "待批改")]
    sub_count = len(submitted)
    pass_rate = 0; avg_score = 0
    if submitted:
        scores = [p.score or 0 for p in submitted]
        avg_score = round(sum(scores) / len(scores), 1)
        pass_count = sum(1 for p in submitted if (p.score or 0) >= exam.pass_score)
        pass_rate = round(pass_count / len(submitted) * 100)
    return {
        "id": exam.id, "name": exam.name, "type": exam.type, "status": exam.status,
        "duration": exam.duration, "question_count": exam.question_count, "pass_score": exam.pass_score,
        "strategy": exam.strategy, "categories": exam.categories,
        "total_candidates": len(papers), "submitted_count": sub_count,
        "pass_rate": pass_rate, "avg_score": avg_score
    }

@router.get("/{eid}/papers")
def get_exam_papers(eid: int, db = Depends(get_db)):
    rows = db.query(ExamPaper, User).join(User, ExamPaper.user_id == User.id).filter(ExamPaper.exam_id == eid).order_by(ExamPaper.submitted_at.desc()).all()
    return {"items": [{
        "paper_id": r.ExamPaper.id, "name": r.User.name, "department": r.User.department, "user_id": r.User.id,
        "score": r.ExamPaper.score, "status": r.ExamPaper.status,
        "duration_used": r.ExamPaper.duration_used, "submitted_at": str(r.ExamPaper.submitted_at or ""), "total_score": sum(q.get("score", 0) for q in (r.ExamPaper.questions or []))
    } for r in rows]}


@router.put("/{eid}/status")
def update_exam_status(eid: int, status: str, db = Depends(get_db)):
    valid = {"未开始", "进行中", "已结束"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"无效状态，可选：{', '.join(sorted(valid))}")
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    exam.status = status
    db.commit()
    return {"message": f"状态已更新为「{status}」", "status": status}

@router.get("/{eid}/export")
def export_exam_papers(eid: int, db = Depends(get_db)):
    from fastapi.responses import StreamingResponse
    import csv, io
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="\u8003\u8bd5\u4e0d\u5b58\u5728")
    rows = db.query(ExamPaper, User).join(User, ExamPaper.user_id == User.id).filter(ExamPaper.exam_id == eid).order_by(ExamPaper.submitted_at.desc().nullslast()).all()
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(["\u59d3\u540d", "\u90e8\u95e8", "\u6210\u7ee9", "\u72b6\u6001", "\u7528\u65f6(\u79d2)", "\u63d0\u4ea4\u65f6\u95f4"])
    for r in rows:
        writer.writerow([r.User.name, r.User.department or "", r.ExamPaper.score or "", r.ExamPaper.status, r.ExamPaper.duration_used or "", str(r.ExamPaper.submitted_at or "")])
    filename = f"exam_{eid}_results.csv"
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.put("/{eid}")
def update_exam(eid: int, data: dict, db = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")
    # Handle questions_preview specially - save to ExamPaper
    if "questions_preview" in data:
        qs = data["questions_preview"]
        paper = db.query(ExamPaper).filter(ExamPaper.exam_id == eid).first()
        if paper:
            paper.questions = qs
        else:
            paper = ExamPaper(exam_id=eid, user_id=1, questions=qs)
            db.add(paper)
        db.commit()
        return {"message": "试卷已更新", "total": len(qs)}
    # Normal exam fields
    for k, v in data.items():
        if hasattr(exam, k):
            setattr(exam, k, v)
    db.commit()
    return {"message": "更新成功"}

@router.get("/paper/{pid}")
def get_paper_detail(pid: int, db = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == pid).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return {"paper_id": paper.id, "questions": paper.questions or [], "answers": paper.answers or {}, "score": paper.score, "status": paper.status}


@router.post("/{eid}/retake/{uid}")
def retake_exam(eid: int, uid: int, user = Depends(get_current_user), db = Depends(get_db)):
    """Admin allows a candidate to retake an exam (reset their paper)"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以操作")
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    paper = db.query(ExamPaper).filter(ExamPaper.exam_id == eid, ExamPaper.user_id == uid).first()
    if not paper:
        raise HTTPException(status_code=404, detail="该考生没有参加此考试")
    paper.status = "未开始"
    paper.score = None
    paper.answers = None
    paper.submitted_at = None
    paper.duration_used = None
    db.commit()
    return {"message": "补考已允许，考生可以重新考试"}


@router.post("/discard/{paper_id}")
def discard_paper(paper_id: int, user = Depends(get_current_user), db = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id, ExamPaper.user_id == user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.status != "进行中":
        raise HTTPException(status_code=400, detail="只能放弃进行中的试卷")
    paper.status = "已放弃"
    db.commit()
    return {"message": "试卷已放弃"}

@router.delete("/{eid}")
def delete_exam(eid: int, db = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")
    db.query(ExamPaper).filter(ExamPaper.exam_id == eid).delete()
    db.delete(exam)
    db.commit()
    return {"message": "删除成功"}

@router.get("/{eid}/questions")
def get_exam_questions(eid: int, db = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    papers = db.query(ExamPaper).filter(ExamPaper.exam_id == eid).first()
    if not papers:
        return {"items": []}
    return {"items": papers.questions or []}

@router.post("/{eid}/generate")
def generate_exam_paper(eid: int, db = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    if exam.strategy == "manual":
        # Manual: return empty and clear existing paper
        existing = db.query(ExamPaper).filter(ExamPaper.exam_id == eid).first()
        if existing:
            existing.questions = []
        return {"items": [], "total": 0}
    
    q = db.query(Question)
    cats = _ensure_list(exam.categories)
    if cats:
        q = q.filter(Question.category.in_(cats))
    all_qs = q.all()
    
    selected = []
    dist_data = _ensure_list(exam.distribution) if exam.distribution else None
    if dist_data and isinstance(dist_data, dict):
        for qtype, cfg in dist_data.items():
            pool = [qq for qq in all_qs if qq.type == qtype]
            random.shuffle(pool)
            count = cfg.get("count", cfg) if isinstance(cfg, dict) else cfg
            if isinstance(count, dict):
                count = count.get("count", 0)
            if count and count > 0:
                selected.extend(pool[:min(count, len(pool))])
    if not selected:
        random.shuffle(all_qs)
        selected = all_qs[:exam.question_count]
    
    snapshot = [{"id": q.id, "type": q.type, "content": q.content, "options": q.options, "score": q.score, "category": q.category, "difficulty": q.difficulty, "answer": q.answer} for q in selected]
    
    existing = db.query(ExamPaper).filter(ExamPaper.exam_id == eid).first()
    if existing:
        existing.questions = snapshot
    else:
        paper = ExamPaper(exam_id=eid, user_id=1, questions=snapshot)
        db.add(paper)
    db.commit()
    return {"items": snapshot, "total": len(snapshot)}