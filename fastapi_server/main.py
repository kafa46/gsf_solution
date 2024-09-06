# fast_api/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from utils.cam import cam_check, cam_live

app = FastAPI()

# 로컬 호스트만 허용하는 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8877", "http://127.0.0.1:8877"],  # Flask 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/available_cameras")
def available_cameras():
    # 등록된 카메라 모두 메모리 해제
    cam_check.cam_manager.release_all_cameras()
    
    # 등록된 카메라 리스트 출력
    available_cameras = cam_check.cam_manager.find_available_cameras()
    
    print(f"사용 가능한 카메라 인덱스: {available_cameras}")
    
    return {"available_cameras": available_cameras}

@app.get("/video_feed")
def video_feed(camera_index: int = Query(description="카메라 인덱스")):
    # 선택된 카메라 인덱스로 스트림 생성
    
    camera_stream = cam_check.cam_manager.add_camera_stream(camera_index=camera_index)
    print(camera_index, " 카메라 라이브 시작")
    return StreamingResponse(camera_stream.generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/processed_image")
def processed_image():
    # 처리 요청이 들어올때
    pass

@app.get("/image_save")
def image_save():
    # 처리된 이미지 저장 또는 중지 (flag)
    pass
