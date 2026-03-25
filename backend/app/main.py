# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import policies, users, bookmarks

# 테이블 자동 생성 (없으면 만들어줌)
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="온통청년 청년정책 API",
    description="청년정책 검색 및 조회 서비스",
    version="1.0.0"
)

# CORS 설정 (프론트엔드에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 나중에 프론트 주소로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결 (나중에 추가)
app.include_router(policies.router) 
app.include_router(users.router)
app.include_router(bookmarks.router)

# 서버 상태 확인용
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Policy API is running"}