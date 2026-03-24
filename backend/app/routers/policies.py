# app/routers/policies.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Policy, PolicyCategory
from typing import Optional

router = APIRouter(
    prefix="/policies",
    tags=["policies"]
)

# 정책 목록 조회 + 필터
@router.get("/")
def get_policies(
    keyword:  Optional[str] = Query(None, description="키워드 검색"),
    region:   Optional[str] = Query(None, description="지역명 (예: 서울)"),
    category: Optional[str] = Query(None, description="대분류명 (예: 일자리)"),
    page:     int           = Query(1, description="페이지 번호"),
    size:     int           = Query(10, description="페이지당 개수"),
    db:       Session       = Depends(get_db)
):
    query = db.query(Policy)

    # 키워드 필터
    if keyword:
        query = query.filter(
            Policy.policy_name.ilike(f"%{keyword}%") |
            Policy.policy_keyword.ilike(f"%{keyword}%") |
            Policy.policy_description.ilike(f"%{keyword}%")
        )

    # 지역 필터
    if region:
        query = query.filter(
            Policy.target_region_name.ilike(f"%{region}%")
        )

    # 카테고리 필터
    if category:
        query = query.join(PolicyCategory).filter(
            PolicyCategory.major_category.ilike(f"%{category}%")
        )

    # 전체 개수
    total = query.count()

    # 페이지네이션
    policies = query.offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "policies": [
            {
                "id": p.id,
                "policy_id": p.policy_id,
                "policy_name": p.policy_name,
                "policy_keyword": p.policy_keyword,
                "policy_description": p.policy_description,
                "age_info": p.age_info,
                "target_region_name": p.target_region_name,
                "apply_url": p.apply_url,
                "category_id": p.category_id,
            }
            for p in policies
        ]
    }


# 정책 상세 조회
@router.get("/{policy_id}")
def get_policy_detail(
    policy_id: str,
    db: Session = Depends(get_db)
):
    policy = db.query(Policy).filter_by(policy_id=policy_id).first()

    if not policy:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다")

    return {
        "id": policy.id,
        "policy_id": policy.policy_id,
        "policy_name": policy.policy_name,
        "policy_keyword": policy.policy_keyword,
        "policy_description": policy.policy_description,
        "age_info": policy.age_info,
        "target_region_name": policy.target_region_name,
        "managing_org_name": policy.managing_org_name,
        "apply_method": policy.apply_method,
        "apply_url": policy.apply_url,
        "apply_start_date": policy.apply_start_date,
        "apply_end_date": policy.apply_end_date,
        "category_id": policy.category_id,
    }