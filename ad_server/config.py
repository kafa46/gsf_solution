import argparse

import torch
from secret import csrf_token_secrete
import os

BASE_DIR = os.path.dirname(__file__)

# SQLALCHEMY_DATABASE_URI -> DB 접속 주소
path_to_db = os.path.join(BASE_DIR, 'gsf.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{path_to_db}'

# ORM 객체의 변경사항을 지속적으로 추적하고 변동 이벤트에 대한 메시지 출력
# 불필요한 경우 False로 꺼놓는 것을 추천
SQLALCHEMY_TRACK_MODIFICATIONS = False

PORT = '8877'

# Seret key for CSRF token
SECRET_KEY = csrf_token_secrete

UPLOAD_FILE_DIR = '/uploads'

PRETRAINED_AD_MODEL = '/home/kafa46/workspace/gsf_solution/ad_server/anomaly_ai/pretrained_models/mvtecad-resnet18-carpet.model'

ARGS = {
    'dataset_root': './anomaly_ai/datasets/mvtec',
    'classname': 'carpet',
    'z-score_threshold-high': 1.96,      # 신뢰수준: 95%
    'z-score_threshold-middle': 2.33,   # 신뢰수준: 98%
    'z-score_threshold-low': 2.58,     # 신뢰수준: 99%
}
