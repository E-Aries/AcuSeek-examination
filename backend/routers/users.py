from pydantic import BaseModel

class CreateUserSchema(BaseModel):
    username: str
    password: str
    name: str = ""
    role: str = "candidate"
    department: str = ""

class UpdateUserSchema(BaseModel):
    name: str = ""
    role: str = ""
    department: str = ""
    password: str = ""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
import hashlib, secrets

router = APIRouter(prefix="/api/users", tags=["users"])

def hash_pw(pw):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode()).hexdigest()
    return salt + ":" + h

@router.get("")
def list_users(db = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return {"items": [{"id": u.id, "username": u.username, "name": u.name, "role": u.role, "department": u.department} for u in users]}

@router.post("")
def create_user(data: CreateUserSchema, db = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=data.username, password_hash=hash_pw(data.password), name=data.name or data.username, role=data.role, department=data.department)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "message": "创建成功"}

@router.put("/{uid}")
def update_user(uid: int, data: UpdateUserSchema, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.name: user.name = data.name
    if data.role: user.role = data.role
    if data.department: user.department = data.department
    if data.password: user.password_hash = hash_pw(data.password)
    db.commit()
    return {"message": "更新成功"}

@router.delete("/{uid}")
def delete_user(uid: int, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员")
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}
