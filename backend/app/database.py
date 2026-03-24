# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# DB 연결 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping = True, # 끊긴 연결 자동 재연결
    pool_recycle = 3600   # 1시간마다 연결 갱신
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind = engine)

# 모델 베이스 클래스
Base = declarative_base()

# FastAPI에서 DB 세션 사용할 때 쓰는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()