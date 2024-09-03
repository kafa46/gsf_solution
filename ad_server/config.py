from secret import csrf_token_secrete
import os

BASE_DIR = os.path.dirname(__file__)

# SQLALCHEMY_DATABASE_URI -> DB 접속 주소
path_to_db = os.path.join(BASE_DIR, 'gsf.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{path_to_db}'

# ORM 객체의 변경사항을 지속적으로 추적하고 변동 이벤트에 대한 메시지 출력
# 불필요한 경우 False로 꺼놓는 것을 추천
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Seret key for CSRF token
SECRET_KEY = csrf_token_secrete

UPLOAD_FILE_DIR = '/uploads'