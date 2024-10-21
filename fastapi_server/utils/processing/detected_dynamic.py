import os
import cv2
import numpy as np

from func import detect_stickers  # 기존 함수들을 포함한 모듈 임포트

def detect_stickers_in_folder(image_folder, lower_bound, upper_bound, margin, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for i in range(1, 301):  # 이미지 순차적으로 처리 (001~300)
        # 번호 패턴에 해당하는 파일 검색
        for file_name in os.listdir(image_folder):
            if file_name.endswith(f"_{str(i).zfill(3)}.jpg"):
                image_path = os.path.join(image_folder, file_name)
                break
        else:
            print(f"Image with suffix {str(i).zfill(3)}.jpg not found. Skipping...")
            continue
        
        contour_image, extracted_pixels_rgb, extracted_pixels_hsv = detect_stickers(image_path, lower_bound, upper_bound, margin)
        
        if contour_image is not None and extracted_pixels_hsv is not None:
            # 디텍션 결과 이미지 저장
            output_image_path = os.path.join(output_folder, f"detected_{file_name}")
            cv2.imwrite(output_image_path, contour_image)
            
            num_pixels = len(extracted_pixels_hsv)
            row_length = contour_image.shape[1]

            # 줄 크기를 확인하고, 이미지의 줄과 추출된 픽셀의 길이를 맞추기
            num_rows = num_pixels // row_length
            remainder = num_pixels % row_length

            if remainder != 0:
                print(f"Warning: {file_name} does not evenly divide into rows. Remainder pixels will be added to the last row.")

            all_rows_data = []

            for row_idx in range(num_rows):
                start_idx = row_idx * row_length
                end_idx = start_idx + row_length
                row_data = [[pixel.tolist()] for pixel in extracted_pixels_hsv[start_idx:end_idx]]
                all_rows_data.append(row_data)  # 각 줄의 데이터를 리스트에 추가

            # 나머지 픽셀을 마지막 행에 추가
            if remainder != 0:
                last_row_data = [[pixel.tolist()] for pixel in extracted_pixels_hsv[num_rows * row_length:]]
                all_rows_data.append(last_row_data)

        else:
            print(f"Sticker not detected in {file_name}. Skipping...")

# 사용 예시
image_folder = r'../data/input/wafer_img'
output_folder = r'../data/output/result_data'
lower_bound = np.array([7,120,160])
upper_bound = np.array([15,140,180])
margin = 10

detect_stickers_in_folder(image_folder, lower_bound, upper_bound, margin, output_folder)
