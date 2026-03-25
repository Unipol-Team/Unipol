# app/routers/bookmarks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from jose import jwt
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"]
)

# 토큰에서 유저 가져오기
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


# 북마크 추가
@router.post("/{policy_id}")
def add_bookmark(policy_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models import Policy, Bookmark
    
    # 정책 존재 확인
    policy = db.query(Policy).filter_by(policy_id=policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다")
    
    # 이미 북마크 확인
    existing = db.query(Bookmark).filter_by(user_id=current_user.id, policy_id=policy.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 북마크한 정책입니다")
    
    bookmark = Bookmark(user_id=current_user.id, policy_id=policy.id)
    db.add(bookmark)
    db.commit()
    
    return {"message": "북마크가 추가되었습니다"}


# 북마크 삭제
@router.delete("/{policy_id}")
def remove_bookmark(policy_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models import Policy, Bookmark
    
    policy = db.query(Policy).filter_by(policy_id=policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다")
    
    bookmark = db.query(Bookmark).filter_by(user_id=current_user.id, policy_id=policy.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")
    
    db.delete(bookmark)
    db.commit()
    
    return {"message": "북마크가 삭제되었습니다"}


# 내 북마크 목록
@router.get("/")
def get_bookmarks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models import Bookmark, Policy
    
    bookmarks = db.query(Bookmark).filter_by(user_id=current_user.id).all()
    
    return {
        "total": len(bookmarks),
        "bookmarks": [
            {
                "policy_id": b.policy.policy_id,
                "policy_name": b.policy.policy_name,
                "policy_description": b.policy.policy_description,
                "target_region_name": b.policy.target_region_name,
                "apply_url": b.policy.apply_url,
                "apply_end_date": b.policy.apply_end_date,
            }
            for b in bookmarks
        ]
    }