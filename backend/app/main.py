from fastapi import FastAPI

app = FastAPI(
    title="Unipol API",
    description="대학생 맞춤 지원 정책 추천 서비스",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Unipol API 서버가 실행 중입니다."}

