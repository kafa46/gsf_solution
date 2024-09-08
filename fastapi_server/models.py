# models.py
from pydantic import BaseModel

# 데이터 모델 정의 (테이블 데이터 항목)
class DataItem(BaseModel):
    rowIndex: int
    margin: float
    lower_bound: float
    upper_bound: float