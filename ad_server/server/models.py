from server import db

class AnomalyImage(db.Model):
    '''비정상 이미지'''
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=True) # 이미지 파일 경로
    create_date = db.Column(db.DateTime, nullable=True) # 생성 일시
    modify_date = db.Column(db.DateTime, nullable=True) # 수정 일시
    anomaly_score = db.Column(db.Float(3), nullable=True) # Anomaly score
    threshold = db.Column(db.Float(3), nullable=True) # Threshold value
    # 탐지 방법 (예: 0: z-score, 1: simple_thres, ...)
    detection_crit = db.Column(db.Integer, nullable=True)

