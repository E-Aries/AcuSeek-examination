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
    return {"id": user.id, "name": user.name, "role": user.role, "department": user.department}
