import cv2
import os
import time
import numpy as np
from datetime import datetime
from func import detect_stickers


# dynamic
def dynamic_detected_images(captured_files, lower_bound, upper_bound, margin, detected_folder, file_prefix="detected"):
    """
    캡처된 이미지에서 스티커를 검출하고, 검출된 이미지를 저장하는 함수.

    :param captured_files: 처리할 이미지 파일 경로들의 리스트
    :param lower_bound: 스티커 검출을 위한 HSV 하한값
    :param upper_bound: 스티커 검출을 위한 HSV 상한값
    :param margin: 스티커 영역 크롭 시 추가할 여유 공간
    :param detected_folder: 검출된 이미지를 저장할 폴더 경로
    :param file_prefix: 저장될 파일의 접두사 (기본값: "detected")
    """
    if not os.path.exists(detected_folder):
        os.makedirs(detected_folder)

    for file_path in captured_files:
        file_name = os.path.basename(file_path)
        
        # 스티커 디텍션
        contour_image = detect_stickers(file_path, lower_bound, upper_bound, margin, crop= True)
        
        # 디텍션된 이미지 전체를 저장
        if contour_image is not None:
            detected_image_path = os.path.join(detected_folder, f"{file_prefix}_{file_name}")
            cv2.imwrite(detected_image_path, contour_image)
            print(f"Detected image saved to: {detected_image_path}")

# Fixed
def fixed_detected_images(captured_files, lower_bound, upper_bound, margin, detected_folder, file_prefix="detected"):
    """
    캡처된 이미지에서 스티커를 검출하고, 검출된 이미지를 저장하는 함수.

    :param captured_files: 처리할 이미지 파일 경로들의 리스트
    :param lower_bound: 스티커 검출을 위한 HSV 하한값
    :param upper_bound: 스티커 검출을 위한 HSV 상한값
    :param margin: 스티커 영역 크롭 시 추가할 여유 공간
    :param detected_folder: 검출된 이미지를 저장할 폴더 경로
    :param file_prefix: 저장될 파일의 접두사 (기본값: "detected")
    """
    if not os.path.exists(detected_folder):
        os.makedirs(detected_folder)

    # 스티커 디텍션
    contour_image = detect_stickers(file_path, lower_bound, upper_bound, margin, crop= True)
    
    for file_path in captured_files:
        file_name = os.path.basename(file_path)
        
        # 스티커 디텍션
        
    
def main():
    # 설정
    output_folder = "../../data/input/captured_images"
    dy_cropped_folder = "../../data/output/dy_cropped_stickers"
    fx_cropped_folder = "../../data/output/fx_cropped_stickers"

    # 살구색 스티커 HSV
    lower_bound = np.array([4,100,140])
    upper_bound = np.array([20,130,170])
    margin = 10

    # 폴더 생성
    os.makedirs(dy_cropped_folder, exist_ok=True)
    os.makedirs(fx_cropped_folder, exist_ok=True)
    
    # 기존에 저장된 이미지 파일들의 경로를 리스트로 가져오기
    captured_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".png")]
    
    # Step 2: 캡처된 이미지 처리 (dynamic 방식)
    dynamic_detected_images(captured_files, lower_bound, upper_bound, margin, dy_cropped_folder)
    
    # Step 3: 캡처된 이미지 처리 (Fixed 방식)
    fixed_detected_images(captured_files, lower_bound, upper_bound, margin, fx_cropped_folder)
    
    print("캡처 및 스티커 디텍션 완료.")

if __name__ == "__main__":
    main()
