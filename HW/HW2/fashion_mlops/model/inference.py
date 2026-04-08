import io
import re
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# GPU 가속이 가능하면 사용 (NVIDIA CUDA 또는 macOS MPS), 없으면 CPU 사용
device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

# 서버 구동 시 한 번만 모델을 로드 (Moondream2 모델 사용)
model_id = "vikhyatk/moondream2"
tokenizer = AutoTokenizer.from_pretrained(model_id, revision="2024-08-26")
model = AutoModelForCausalLM.from_pretrained(
    model_id, trust_remote_code=True, revision="2024-08-26"
).to(device)
model.eval()

def evaluate_outfit(image_bytes: bytes) -> dict:
    """
    업로드된 이미지 바이트를 받아 코디를 평가합니다.
    """
    # 1. 이미지 읽기
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # 2. 이미지를 모델이 이해할 수 있도록 인코딩
    enc_image = model.encode_image(image)
    
    # 3. 모델에게 내릴 프롬프트 작성 
    # (한국어보다 영어로 질문하는 것이 더 정확한 답변을 낼 확률이 높기 때문에 영어로 지시 후 한국어로 번역답변 요구)
    prompt = """
    Act as a Korean fashion expert. Look at the outfit in the image and evaluate it based on trendy Korean styles.
    Reply strictly in the following format:
    Score: [a number from 0 to 100]
    Feedback: [a short overall feedback in Korean]
    Improvements: [suggest 1 or 2 improvements in Korean, separated by a vertical bar |]
    """
    
    # 4. 모델 추론
    answer = model.answer_question(enc_image, prompt, tokenizer)
    
    # 5. 모델이 텍스트로 준 응답(answer)을 정규식(Regex)으로 파싱
    score = 70  # 기본값
    feedback = "스타일 평가를 완료했습니다."
    improvements = []
    
    # Score 파싱
    score_match = re.search(r"Score:\s*(\d+)", answer, re.IGNORECASE)
    if score_match:
        score = int(score_match.group(1))
        
    # Feedback 파싱
    feedback_match = re.search(r"Feedback:\s*(.+?)\s*\nImprovements:", answer, re.IGNORECASE | re.DOTALL)
    if feedback_match:
        feedback = feedback_match.group(1).strip()
    else:
        # Improvements 형식을 정확히 안 지켰을 경우 대비
        fb_simple = re.search(r"Feedback:\s*(.+)", answer, re.IGNORECASE | re.DOTALL)
        if fb_simple:
            feedback = fb_simple.group(1).strip()
            
    # Improvements 파싱
    imp_match = re.search(r"Improvements:\s*(.+)", answer, re.IGNORECASE | re.DOTALL)
    if imp_match:
        imp_str = imp_match.group(1).strip()
        if "|" in imp_str:
            improvements = [i.strip() for i in imp_str.split("|") if i.strip()]
        elif "\n" in imp_str:
            improvements = [i.strip("- *") for i in imp_str.split("\n") if i.strip()]
        else:
            improvements = [imp_str]
            
    return {
        "score": score,
        "feedback": feedback,
        "improvements": improvements if improvements else ["단점을 찾기 어렵거나 특별한 보완점이 필요하지 않습니다."]
    }
