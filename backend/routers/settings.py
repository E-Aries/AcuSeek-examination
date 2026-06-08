from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel
from typing import Optional
from .auth import get_current_user
import os, uuid

router = APIRouter(prefix="/api/settings", tags=["settings"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    nav_logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
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
def update_settings(data: SettingsUpdate, user = Depends(get_current_user), db=Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    mapping = {}
    for field in ["site_name", "company_name", "logo_url", "nav_logo_url", "favicon_url", "copyright_text", "version_text"]:
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
    db.commit()

    # Update favicon in index.html
    if "favicon_url" in mapping and "favicon_url" in str(data.__dict__):
        _update_favicon_in_html(mapping["favicon_url"])

    return get_settings(db)

@router.post("/upload")
def upload_file(file: UploadFile = File(...), user = Depends(get_current_user), db=Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    ext = os.path.splitext(file.filename)[-1].lower() if file.filename else ".png"
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg"):
        raise HTTPException(status_code=400, detail="仅支持 PNG/JPG/GIF/ICO/SVG 格式")
    filename = f"logo_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return {"url": f"/uploads/{filename}"}

@router.post("/reset")
def reset_brand(user = Depends(get_current_user), db=Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    defaults = {
        "site_name": "AXUS 企业考核系统", "company_name": "", "logo_url": "",
        "nav_logo_url": "", "favicon_url": "", "copyright_text": "",
        "version_text": "v1.0.0"
    }
    for k, v in defaults.items():
        db.execute(text("UPDATE system_settings SET value = :v, updated_at = CURRENT_TIMESTAMP WHERE key = :k"), {"k": k, "v": v})
    db.commit()
    return get_settings(db)


def _update_favicon_in_html(url):
    import re
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        if url:
            new_href = url if url.startswith("http") else url
            html = re.sub(
                r'<link rel="icon"[^>]*>',
                f'<link rel="icon" href="{new_href}" />',
                html
            )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"Failed to update favicon: {e}")
