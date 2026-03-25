# app/models.py
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, SmallInteger, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# 1. 정책 카테고리 테이블
class PolicyCategory(Base):
    __tablename__ = "policy_category"

    id = Column(Integer, primary_key = True, index = True)
    major_category = Column(String(50), nullable = False) # 대분류( 일자리, 주거 등)
    sub_category = Column(String(50), nullable = False) # 중분류 (취업지원)
    created_at = Column(TIMESTAMP(timezone=True), server_default = func.now()) 
    updated_at = Column(TIMESTAMP(timezone = True), server_default = func.now())

    # Policy 테이블과 연결
    policies = relationship("Policy", back_populates = "category")

# 2. 정책 기본정보 테이블
class Policy(Base):
    __tablename__ = "policy"

    id = Column(Integer, primary_key = True, index = True)
    policy_id = Column(String(50), unique = True, nullable = False) # 온통청년 API 고유번호
    category_id = Column(Integer, ForeignKey("policy_category.id"), nullable = True)

    # 정책 기본 정보
    policy_name = Column(String(255), nullable = False)
    policy_keyword = Column(String(500))
    policy_description = Column(Text)

    # 신청 대상 조건
    age_info = Column(String(100))
    target_region_code = Column(String(20))
    target_region_name = Column(String(100))
    employment_status = Column(String(100))
    education_status = Column(String(100))
    income_info = Column(String(200))

    # 신청 기간
    apply_start_date = Column(Date)
    apply_end_date = Column(Date)
    apply_period_etc = Column(String(200))

    # 주관기간 정보
    managing_org_code = Column(String(50))
    managing_org_name = Column(String(200))
    managing_org_contact = Column(String(100))

    # 신청 방법 및 URL
    apply_method = Column(String(200))
    apply_url = Column(Text)
    reference_url = Column(Text)

    # 메타
    fetched_at = Column(TIMESTAMP(timezone = True), server_default = func.now())
    created_at = Column(TIMESTAMP(timezone = True), server_default = func.now())
    updated_at = Column(TIMESTAMP(timezone = True), server_default = func.now())

    # PolicyCategory 테이블과 연결
    category = relationship("PolicyCategory", back_populates="policies")
    bookmarks = relationship("Bookmark", back_populates="policy")

# 3. 사용자 테이블
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String(255), unique = True, nullable = False)
    password_hash = Column(String(255), nullable = False) # bcrypt 해시만 저장
    nickname = Column(String(50))
    birth_year = Column(SmallInteger) # 나이 필터 게산
    region_code = Column(String(20))
    region_name = Column(String(100))
    is_active = Column(Boolean, default = True)
    created_at = Column(TIMESTAMP(timezone=True), server_default = func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default = func.now())
    bookmarks = relationship("Bookmark", back_populates="user")

# 4. 북마크 테이블
class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policy.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # 관계 설정
    user = relationship("User", back_populates="bookmarks")
    policy = relationship("Policy", back_populates="bookmarks")