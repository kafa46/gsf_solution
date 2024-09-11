# fast_api/main.py
import io
import cv2
import numpy as np
import os
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
from PIL import Image


from utils.cam import cam_check, cam_live
from utils.processing import detection_stickers
from models import DataItem

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
    # 카메라 인스턴스가 만약 없으면 생성
    if cam_check.cam_manager.cameras_use[camera_index] == False:
        camera_stream = cam_check.cam_manager.add_camera_stream(camera_index=camera_index)
    else :
        camera_stream = cam_check.cam_manager.cameras[camera_index]

    print(camera_index, " 카메라 라이브 시작")
    return StreamingResponse(camera_stream.generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/image_feed")
async def image_feed(camera_index: int = Query(description="카메라 인덱스")):
    
    # 저장경로 
    save_dir = "./temp/img"
    save_path = os.path.join(save_dir, "stop.png")
    
    # 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(save_dir):
        print("폴더생성")
        os.makedirs(save_dir)
    
    # camera_stream 객체에서 프레임 캡처
    print(camera_index,"<-- 카메라 인덱스 번호")
    camera_stream = cam_check.cam_manager.cameras[camera_index]

    # 프레임 읽기 시도
    max_attempts = 50  # 최대 시도 횟수
    attempt = 0
    ret = False
    frame = None

    while attempt < max_attempts:
        ret, frame = camera_stream.camera.read()
        if ret and frame is not None:
            print("성공")
            
            # 프레임을 성공적으로 읽었을 때 이미지 저장
            cv2.imwrite(save_path, frame)
            break  # 프레임을 성공적으로 읽었으면 반복 종료
        attempt += 1


    if not ret or frame is None:
        print({"error": "Failed to capture image from camera after multiple attempts."})

    # OpenCV 이미지를 PIL 이미지로 변환 (BGR -> RGB 변환)
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 메모리 버퍼에 이미지를 PNG 포맷으로 저장
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)  # 버퍼의 시작으로 이동

    # 이미지를 전달
    return StreamingResponse(img_io, media_type="image/png")

@app.post("/rgb2hsv")
async def rgb2hsv(rgb: dict = Body(...)):
    r, g, b = rgb['r'], rgb['g'], rgb['b']
    
    rgb_array = np.uint8([[[b, g, r]]])  # BGR 순서로 바꿈
    
    hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_BGR2HSV)
    
    h, s, v = hsv_array[0][0]
    
    return {
        "h": int(h),  # 0-179
        "s": int(s),  # 0-255
        "v": int(v)   # 0-255
    }
    
@app.post("/image_processing")
async def processed_image(table_data: List[DataItem] = Body(...)):
    
    # 임시로 저장한 멈춤 이미지 불러오기
    stop_img = "./temp/img/stop.png" 
    
    # 저장되는 경로 
    output_dir = "./temp/output"
    # 각각의 사용자가 입력한 데이터를 한 바퀴 돌때마다 crop img 생성
    #  crop img를 ./temp/output/ 경로에 저장(저장하기 전에 이전에 있던 이미지 파일 모두 지우기)
    
    if not os.path.exists():
        os.makedirs(output_dir, exist_ok=True)
        
    #  crop_img{n}.png 형식으로 순차적으로 저장
    for index, item in enumerate(table_data):
        print(f"Processing row {item.rowIndex}:")
        print(f"  Margin: {item.margin}")
        print(f"  Lower bound: H({item.lower_bound.h}), S({item.lower_bound.s}), V({item.lower_bound.v})")
        print(f"  Upper bound: H({item.upper_bound.h}), S({item.upper_bound.s}), V({item.upper_bound.v})")

        crop_image = detection_stickers.fixed_detected_images(
                                captured_image=stop_img, 
                                lower_bound=(item.lower_bound.h, item.lower_bound.s, item.lower_bound.v),
                                upper_bound=(item.upper_bound.h, item.upper_bound.s, item.upper_bound.v),
                                margin=item.margin
                                )
        
        # cv2.imwrite(,crop_image)
        
    #  ./temp/output/ 경로에 있는 모든 이미지 불러오기
    
    # 이미지 반환
    return {"status": "success", "processed_rows": len(table_data)}

    
@app.get("/image_save_start")
def image_save_start():
    # 처리된 이미지 저장 또는 중지 (flag)
    # contour 필요 (fx 방식)
    pass

@app.get("/image_save_stop")
def image_save_stop():
    # 처리된 이미지 저장 또는 중지 (flag)
    pass
