from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from database import get_db

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
def list_logs(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=200), action: str = "", db=Depends(get_db)):
    offset = (page - 1) * size
    if action:
        total = db.execute(text("SELECT COUNT(*) FROM operation_logs WHERE action = :a"), {"a": action}).scalar()
        rows = db.execute(
            text("SELECT * FROM operation_logs WHERE action = :a ORDER BY id DESC LIMIT :lim OFFSET :off"),
            {"a": action, "lim": size, "off": offset}
        ).fetchall()
    else:
        total = db.execute(text("SELECT COUNT(*) FROM operation_logs")).scalar()
        rows = db.execute(
            text("SELECT * FROM operation_logs ORDER BY id DESC LIMIT :lim OFFSET :off"),
            {"lim": size, "off": offset}
        ).fetchall()
    items = []
    for r in rows:
        items.append({
            "id": r[0], "username": r[1], "action": r[2], "target": r[3],
            "detail": r[4], "ip": r[5], "created_at": str(r[6]) if r[6] else ""
        })
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/actions")
def list_actions(db=Depends(get_db)):
    rows = db.execute(text("SELECT DISTINCT action FROM operation_logs ORDER BY action")).fetchall()
    return {"items": [r[0] for r in rows]}
