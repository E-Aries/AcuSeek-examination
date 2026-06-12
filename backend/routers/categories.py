from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Category
from logger import log_action
from starlette.requests import Request
from .auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("")
def list_categories(db = Depends(get_db)):
    cats = db.query(Category).order_by(Category.sort, Category.id).all()
    return {"items": [{"id": c.id, "name": c.name, "sort": c.sort} for c in cats]}

@router.post("")
def create_category(data: dict, request: Request, user = Depends(get_current_user), db = Depends(get_db)):
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="分类名称不能为空")
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类已存在")
    c = Category(name=name, sort=data.get("sort", 0))
    log_action(db, user.username, "创建分类", c.name, "", ip=request.client.host or "" if request.client else "")
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name, "sort": c.sort}

@router.put("/{cid}")
def update_category(cid: int, data: dict, request: Request, user = Depends(get_current_user), db = Depends(get_db)):
    c = db.query(Category).filter(Category.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="分类不存在")
    if "name" in data:
        name = data["name"].strip()
        if not name:
            raise HTTPException(status_code=400, detail="分类名称不能为空")
        existing = db.query(Category).filter(Category.name == name, Category.id != cid).first()
        if existing:
            raise HTTPException(status_code=400, detail="分类名称已存在")
        c.name = name
    if "sort" in data:
        c.sort = data["sort"]
    log_action(db, user.username, "修改分类", c.name, "", ip=request.client.host or "" if request.client else "")
    db.commit()
    return {"id": c.id, "name": c.name, "sort": c.sort}

@router.delete("/{cid}")
def delete_category(cid: int, request: Request, user = Depends(get_current_user), db = Depends(get_db)):
    c = db.query(Category).filter(Category.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="分类不存在")
    from models import Question
    count = db.query(Question).filter(Question.category == c.name).count()
    if count > 0:
        raise HTTPException(status_code=400, detail=f"该分类下还有 {count} 道题目，请先移除或改分类")
    log_action(db, user.username, "删除分类", c.name, "", ip=request.client.host or "" if request.client else "")
    db.delete(c)
    db.commit()
    return {"message": "删除成功"}
