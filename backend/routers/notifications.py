# Author: 达咩
# 轻则

from fastapi import APIRouter, Depends
from sqlalchemy import text
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_notifications(db=Depends(get_db), user=Depends(get_current_user)):
    rows = db.execute(
        text("SELECT * FROM notifications WHERE user_id = 0 OR user_id = :uid ORDER BY id DESC LIMIT 20"),
        {"uid": user.id}
    ).fetchall()
    items = []
    for r in rows:
        items.append({
            "id": r[0], "user_id": r[1], "title": r[2], "content": r[3],
            "type": r[4], "is_read": bool(r[5]), "created_at": str(r[6]) if r[6] else ""
        })
    return {"items": items}


@router.get("/unread")
def unread_count(db=Depends(get_db), user=Depends(get_current_user)):
    count = db.execute(
        text("SELECT COUNT(*) FROM notifications WHERE (user_id = 0 OR user_id = :uid) AND is_read = 0"),
        {"uid": user.id}
    ).scalar()
    return {"count": count}


@router.put("/{nid}/read")
def mark_read(nid: int, db=Depends(get_db), user=Depends(get_current_user)):
    db.execute(text("UPDATE notifications SET is_read = 1 WHERE id = :nid AND (user_id = 0 OR user_id = :uid)"),
               {"nid": nid, "uid": user.id})
    db.commit()
    return {"message": "ok"}
