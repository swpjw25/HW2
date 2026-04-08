from pydantic import BaseModel
from typing import List, Optional

class EvaluationResponse(BaseModel):
    score: int                           # 0~100점 사이의 코디 점수
    feedback: str                        # 전체적인 평가 내용
    improvements: Optional[List[str]]    # 구체적인 보완 제안 리스트
