# app/services/fetch_policies.py
import requests
import os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Policy, PolicyCategory
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("OPEN_API_KEY")
API_URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"

def get_or_create_category(db, major: str, sub: str):
    category = db.query(PolicyCategory).filter_by(
        major_category=major,
        sub_category=sub
    ).first()

    if not category:
        category = PolicyCategory(
            major_category=major,
            sub_category=sub
        )
        db.add(category)
        db.commit()
        db.refresh(category)

    return category

def fetch_and_save():
    db = SessionLocal()
    total_saved = 0
    page = 1

    try:
        while True:
            # 1. API 호출
            params = {
                "apiKeyNm": API_KEY,
                "pageNum": page,
                "pageSize": 10,
                "pageType": "1",   # 1 = 목록
                "rtnType": "json"
            }

            response = requests.get(API_URL, params=params)
            # 빈 응답이면 종료
            if not response.text.strip():
                print("더 이상 데이터가 없습니다.")
                break
            data = response.json()

            # 2. 데이터 꺼내기
            policies = data.get("result", {}).get("youthPolicyList", [])

            if not policies:
                print("모든 데이터 가져오기 완료!")
                break

            # 3. DB 저장
            for p in policies:
                policy_id = p.get("plcyNo")
                if not policy_id:
                    continue

                # 카테고리 처리
                category = get_or_create_category(
                    db,
                    major=p.get("lclsfNm") or "기타",
                    sub=p.get("mclsfNm") or "기타"
                )

                # upsert — 있으면 업데이트, 없으면 추가
                existing = db.query(Policy).filter_by(
                    policy_id=policy_id
                ).first()

                if existing:
                    existing.policy_name        = p.get("plcyNm")
                    existing.policy_keyword     = p.get("plcyKywdNm")
                    existing.policy_description = p.get("plcyExplnCn")
                    existing.fetched_at         = datetime.now()
                else:
                    new_policy = Policy(
                        policy_id           = policy_id,
                        category_id         = category.id,
                        policy_name         = p.get("plcyNm"),
                        policy_keyword      = p.get("plcyKywdNm"),
                        policy_description  = p.get("plcyExplnCn"),
                        fetched_at          = datetime.now()
                    )
                    db.add(new_policy)

                total_saved += 1

            db.commit()
            print(f"{page}페이지 완료 — 누적 {total_saved}개 저장")
            page += 1

    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_save()