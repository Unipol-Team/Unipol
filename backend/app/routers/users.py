# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# 요청 데이터 형식 정의
class RegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str = None
    birth_year: int = None
    region_name: str = None

class LoginRequest(BaseModel):
    email: str
    password: str

# 비밀번호 암호화
def hash_password(password: str):
    return pwd_context.hash(password)

# 비밀번호 검증
def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

# JWT 토큰 생성
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 회원가입
@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    existing = db.query(User).filter_by(email=req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")

    # 비밀번호 암호화 후 저장
    new_user = User(
        email         = req.email,
        password_hash = hash_password(req.password),
        nickname      = req.nickname,
        birth_year    = req.birth_year,
        region_name   = req.region_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입 성공", "user_id": new_user.id}


# 로그인
@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # 이메일 확인
    user = db.query(User).filter_by(email=req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")

    # 비밀번호 확인
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")

    # JWT 토큰 발급
    token = create_access_token({"sub": str(user.id), "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname
    }


# 내 정보 조회
@router.get("/me")
def get_me(token: str = Depends(oauth2_scheme) , db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "birth_year": user.birth_year,
        "region_name": user.region_name
    }
    
# 내 정보 수정
class UpdateRequest(BaseModel):
    nickname: str = None
    birth_year: int = None
    region_name: str = None

@router.put("/me")
def update_me(req: UpdateRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    if req.nickname is not None:
        user.nickname = req.nickname
    if req.birth_year is not None:
        user.birth_year = req.birth_year
    if req.region_name is not None:
        user.region_name = req.region_name

    db.commit()
    db.refresh(user)

    return {
        "message": "정보가 수정되었습니다",
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "birth_year": user.birth_year,
        "region_name": user.region_name
    }