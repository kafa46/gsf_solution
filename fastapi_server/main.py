# fast_api/main.py
import io
import cv2
import numpy as np
import os
import glob
import zipfile
import asyncio

from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from typing import List
from PIL import Image

# user define 모듈
from utils.cam import cam_check, cam_live
from utils.processing import detection_stickers
from models import DataItem
from global_state import global_state_instance

app = FastAPI()
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
# 로컬 호스트만 허용하는 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8877", "http://127.0.0.1:8877"],  # Flask 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/available_cameras")
async def available_cameras():
    # 등록된 카메라 모두 메모리 해제
    cam_check.cam_manager.release_all_cameras()
    
    # 등록된 카메라 리스트 출력
    available_cameras = cam_check.cam_manager.find_available_cameras()
    
    print(f"사용 가능한 카메라 인덱스: {available_cameras}")
    
    return {"available_cameras": available_cameras}

@app.get("/video_feed")
async def video_feed(camera_index: int = Query(description="카메라 인덱스")):
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
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 기존 폴더 초기화
    existing_pngs = glob.glob(os.path.join(output_dir, "*.png"))
    for file in existing_pngs:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {str(e)}")
    
    processed_images = []
    detection_failures = []
    
    global_state_instance.contours_list = []
    global_state_instance.margin_list = []
    
    #  crop_img{n}.png 형식으로 순차적으로 저장
    for index, item in enumerate(table_data):
        print(f"Processing row {item.rowIndex}:")
        print(f"  Margin: {item.margin}")
        print(f"  Lower bound: H({item.lower_bound.h}), S({item.lower_bound.s}), V({item.lower_bound.v})")
        print(f"  Upper bound: H({item.upper_bound.h}), S({item.upper_bound.s}), V({item.upper_bound.v})")

        contour ,crop_image = detection_stickers.fixed_detected_images(
                                captured_image=stop_img, 
                                lower_bound=(item.lower_bound.h, item.lower_bound.s, item.lower_bound.v),
                                upper_bound=(item.upper_bound.h, item.upper_bound.s, item.upper_bound.v),
                                margin=item.margin
                                )
        
        # all_crop_draw를 위한 변수 리스트에 저장
        global_state_instance.contours_list.append(contour)
        global_state_instance.margin_list.append(item.margin)
        
        if crop_image is not None:
            output_path = os.path.join(output_dir, f"crop_image{index+1}.png")
            result = cv2.imwrite(output_path, crop_image)
            
            if result:
                print(f"Crop image saved successfully: {output_path}")
                processed_images.append(output_path)

            else:
                print(f"Failed to save crop image: {output_path}")
                detection_failures.append(index + 1)
        else:
            print(f"Failed to process image for row {item.rowIndex}")
            detection_failures.append(index + 1)

    # 디텍션한 전체 이미지를 만듬
    detection_stickers.all_crop_draw(stop_img, global_state_instance.contours_list, global_state_instance.margin_list, output_dir)

    status = "success" if not detection_failures else "partial_success"
    alert_message = " HSV값을 조절해주세요" if detection_failures else None

    return {
        "status": status,
        "processed_rows": len(table_data),
        "successful_detections": len(processed_images),
        "failed_detections": detection_failures,
        "alert_message": alert_message,
        "image_paths": processed_images
    }

    
@app.get("/image_save_start")
async def image_save_start():
    print("시작")
    if global_state_instance.save_flag == False:
        global_state_instance.save_flag = True
        
        output_dir = "./temp/save_img"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 기존 폴더 초기화
        existing_pngs = glob.glob(os.path.join(output_dir, "*.png"))
        for file in existing_pngs:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {str(e)}")
        
        # 비동기로 이미지 저장 작업 시작
        asyncio.create_task(save_images(output_dir))
    
    return {"status": "started"}


@app.get("/image_save_stop")
async def image_save_stop():
    print("중지")
    global_state_instance.save_flag = False
    return {"status": "stopped"}

async def save_images(output_dir):
    print("저장시작")
    frame_count = 0
    resize_dim = (800, 800)  # 원하는 크기로 설정

    while global_state_instance.save_flag:
        ret, frame = cam_check.cam_manager.cameras[cam_check.cam_manager.current_using_index].camera.read()
        if ret:
            # OpenCV 프레임을 PIL Image로 변환
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # 이미지 리사이즈
            pil_image = pil_image.resize(resize_dim, Image.LANCZOS)
            
            # PIL Image를 다시 OpenCV 형식으로 변환
            frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            for idx, (contour, margin) in enumerate(zip(global_state_instance.contours_list, global_state_instance.margin_list)):
                # contour 좌표를 리사이즈된 이미지에 맞게 조정
                resized_contour = contour * (np.array(resize_dim) / np.array(frame.shape[:2][::-1]))
                resized_contour = resized_contour.astype(int)

                crop_img = detection_stickers.crop_margined_region(frame, resized_contour, margin)
                if crop_img is not None:
                    cv2.imwrite(os.path.join(output_dir, f"save_img{idx+1}_{frame_count}.png"), crop_img)

            frame_count += 1

        await asyncio.sleep(0.1)  # 10 FPS로 제한

    print("저장종료")