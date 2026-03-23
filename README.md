# Unipol - 대학생 맞춤 지원 정책 추천 서비스

## 프로젝트 소개
대학생이 자신의 상황에 맞는 지원 정책을 쉽게 찾을 수 있도록 맞춤형 정책을 추천해주는 웹 서비스입니다.

## 기술 스택
### Frontend
- 

### Backend
- Python, FastAPI
- PostgreSQL, SQLAlchemy
- JWT 인증

## 프로젝트 구조
```
Unipol/
├── frontend/          # 프론트엔드
├── backend/           # 백엔드
│   ├── app/
│   │   ├── api/       # API 라우터
│   │   ├── models/    # DB 모델
│   │   ├── schemas/   # Pydantic 스키마
│   │   ├── core/      # 설정, 보안
│   │   ├── main.py    # 앱 진입점
│   │   └── database.py# DB 연결
│   ├── requirements.txt
│   └── .env
└── docs/              # 설계 문서
```

## ✨ 주요 기능
- 회원가입 / 로그인 / 로그아웃
- 체크박스 조건 기반 맞춤 정책 추천
- 정책 검색
- 관심 정책 북마크
- 마이페이지

## 실행 방법
### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 브랜치 전략
- `main` : 배포용 브랜치
- `develop` : 개발 통합 브랜치
- `feature/xxx` : 기능 개발 브랜치

## 커밋 컨벤션
| 태그 | 설명 |
|------|------|
| feat | 새로운 기능 추가 |
| fix | 버그 수정 |
| docs | 문서 수정 |
| chore | 설정, 패키지 등 |
| refactor | 코드 리팩토링 |