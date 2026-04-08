import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from schemas.payload import EvaluationResponse
from model.inference import evaluate_outfit

app = FastAPI(
    title="Korean Fashion Evaluator API",
    description="대한민국 일반 코디 기준 룩(Look) 평가 및 보완 제안 모델 API",
    version="1.0.0"
)

# CORS 설정 추가 (프론트엔드 포트가 다르더라도 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프론트엔드 정적 파일 서빙
if not os.path.exists("frontend"):
    os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """메인 페이지 HTML 서빙"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Frontend is building... Please wait or create frontend/index.html</h1>"

@app.get("/health")
def health_check():
    """MLOps 파이프라인(ALB, Kubernetes 등)에서 서버 상태를 확인할 헬스체크 엔드포인트"""
    return {"status": "healthy"}

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(file: UploadFile = File(...)):
    """
    옷 사진을 업로드하면 코디 점수와 피드백을 반환합니다.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="유효한 이미지 파일이 아닙니다.")
    
    try:
        # 파일 바이트 추출 및 모델 추론
        image_bytes = await file.read()
        result = evaluate_outfit(image_bytes)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추론 서버 에러: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
