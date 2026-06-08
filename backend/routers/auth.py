import hashlib, secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain, stored):
    if ":" not in stored:
        return hashlib.sha256(plain.encode()).hexdigest() == stored
    salt, h = stored.split(":")
    return hashlib.sha256((salt + plain).encode()).hexdigest() == h

def get_current_user(token = Depends(oauth2_scheme), db = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(user = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user

def _hash_pw(pw):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode()).hexdigest()
    return salt + ":" + h

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = jwt.encode({
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "name": user.name, "role": user.role, "department": user.department}
    )

@router.get("/me")
def get_me(user = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "name": user.name, "role": user.role, "department": user.department}


import hashlib, secrets
from schemas import LoginRequest, TokenResponse
from pydantic import BaseModel
from typing import Optional


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None


@router.put("/profile")
def update_profile(data: ProfileUpdate, user=Depends(get_current_user), db=Depends(get_db)):
    if data.username is not None:
        if user.role == "admin":
            pass
        else:
            existing = db.query(User).filter(User.username == data.username, User.id != user.id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"用户名 '{data.username}' 已被其他用户使用")
            user.username = data.username
    if data.name is not None:
        user.name = data.name
    if data.department is not None:
        user.department = data.department
    if data.password:
        salt = secrets.token_hex(16)
        h = hashlib.sha256((salt + data.password).encode()).hexdigest()
        user.password_hash = salt + ":" + h
    db.commit()
    return {"message": "保存成功"}


@router.post("/register")
def register(req: LoginRequest, db = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户已存在")
    user = User(username=req.username, password_hash=_hash_pw(req.password), name=req.username, role="candidate")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "message": "注册成功"}