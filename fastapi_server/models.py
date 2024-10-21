# models.py
from pydantic import BaseModel

# 데이터 모델 정의 (테이블 데이터 항목)
class HSVBound(BaseModel):
    h: int
    s: int
    v: int

class DataItem(BaseModel):
    rowIndex: int
    margin: int
    lower_bound: HSVBound
    upper_bound: HSVBound