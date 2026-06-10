from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel
from typing import Optional
from starlette.requests import Request
from .auth import get_current_user
from logger import log_action
import os, uuid

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    company_name: Optional[str] = None



    copyright_text: Optional[str] = None
    version_text: Optional[str] = None
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
def update_settings(data: SettingsUpdate, request: Request, user = Depends(get_current_user), db=Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    mapping = {}
    for field in ["site_name", "company_name", "copyright_text", "version_text"]:
        val = getattr(data, field, None)
        if val is not None:
            mapping[field] = val
    if data.default_pass_score is not None:
        mapping["default_pass_score"] = str(data.default_pass_score)
    if data.max_switches is not None:
        mapping["max_switches"] = str(data.max_switches)
    if data.default_duration is not None:
        mapping["default_duration"] = str(data.default_duration)
    for k, v in mapping.items():
        db.execute(text("UPDATE system_settings SET value = :v, updated_at = CURRENT_TIMESTAMP WHERE key = :k"), {"k": k, "v": v})
    log_action(db, user.username, "修改系统设置", "", "", ip=request.client.host or "" if request.client else "")
    db.commit()


    return get_settings(db)
@router.post("/reset")
def reset_brand(request: Request, user = Depends(get_current_user), db=Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    defaults = {
        "site_name": "企业考核系统",
        "company_name": "武汉xx科技",
        "copyright_text": "Copyright 2026@武汉XX有限公司",
        "version_text": "v2.0.1",
    }
    for k, v in defaults.items():
        db.execute(text("UPDATE system_settings SET value = :v, updated_at = CURRENT_TIMESTAMP WHERE key = :k"), {"k": k, "v": v})
    log_action(db, user.username, "还原系统默认", "", "", ip=request.client.host or "" if request.client else "")
    db.commit()
    return get_settings(db)
