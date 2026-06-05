from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    default_pass_score: Optional[int] = None
    max_switches: Optional[int] = None
    default_duration: Optional[int] = None


@router.get("")
def get_settings(db=Depends(get_db)):
    rows = db.execute(text("SELECT key, value FROM system_settings")).fetchall()
    data = {}
    for r in rows:
        data[r[0]] = r[1]
    return data


@router.put("")
def update_settings(data: SettingsUpdate, db=Depends(get_db)):
    mapping = {}
    if data.site_name is not None:
        mapping["site_name"] = data.site_name
    if data.default_pass_score is not None:
        mapping["default_pass_score"] = str(data.default_pass_score)
    if data.max_switches is not None:
        mapping["max_switches"] = str(data.max_switches)
    if data.default_duration is not None:
        mapping["default_duration"] = str(data.default_duration)
    for k, v in mapping.items():
        db.execute(text("UPDATE system_settings SET value = :v, updated_at = CURRENT_TIMESTAMP WHERE key = :k"), {"k": k, "v": v})
    db.commit()
    return get_settings(db)
