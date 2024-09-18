import os
import csv
import cv2
import numpy as np
from func import load_and_preprocess_image, create_polygon_mask, extract_pixels, apply_margin, draw_corners_and_edges, find_largest_contour, find_corners, create_mask

def detect_stickers_with_fixed_corners(image_path, fixed_corners, margin):
    # 이미지 로드 및 전처리
    image_cv, hsv_image = load_and_preprocess_image(image_path)
    
    # 마스크 생성(고정된 네 꼭짓점 기반)
    poly_mask = create_polygon_mask(image_cv.shape, fixed_corners)
    
    # RGB와 HSV 이미지에서 픽셀 추출
    extracted_image_rgb, extracted_pixels_rgb = extract_pixels(image_cv, poly_mask)
    extracted_image_hsv, extracted_pixels_hsv = extract_pixels(hsv_image, poly_mask)
    
    # 마진 적용 후 선분 그리기(선택 사항)
    adjusted_corners = apply_margin(fixed_corners, margin)
    contour_image = image_cv.copy()
    draw_corners_and_edges(contour_image, fixed_corners)
    draw_corners_and_edges(contour_image, adjusted_corners, color=(0, 255, 0))
    
    # 디텍션한 이미지, 디텍션한 영역의 RGB값, 디텍션한 영역의 HSV값 반환 
    return contour_image, extracted_pixels_rgb, extracted_pixels_hsv


def detect_stickers_in_folder_with_fixed_corners(image_folder, lower_bound, upper_bound, margin, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    csv_file_path = os.path.join(output_folder, "sticker_data_fixed.csv")
    
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Image Name", "Pixel Data (HSV)"])

        fixed_corners = None  # 첫 이미지의 네 꼭짓점을 저장할 변수

        for i in range(1, 301):  # 이미지 순차적으로 처리 (001~300)
            for file_name in os.listdir(image_folder):
                if file_name.endswith(f"_{str(i).zfill(3)}.jpg"):
                    image_path = os.path.join(image_folder, file_name)
                    break
            else:
                print(f"Image with suffix {str(i).zfill(3)}.jpg not found. Skipping...")
                continue
            
            if fixed_corners is None:
                # 첫 이미지에서 네 꼭짓점을 탐지
                image_cv, hsv_image = load_and_preprocess_image(image_path)
                mask = create_mask(hsv_image, lower_bound, upper_bound)
                max_contour = find_largest_contour(mask)
                
                if max_contour is not None:
                    fixed_corners = find_corners(max_contour)
                    contour_image, extracted_pixels_rgb, extracted_pixels_hsv = detect_stickers_with_fixed_corners(image_path, fixed_corners, margin)
                else:
                    print("No contours found, skip...")
                    continue
            else:
                # 이후 이미지는 고정된 네 꼭짓점을 사용
                contour_image, extracted_pixels_rgb, extracted_pixels_hsv = detect_stickers_with_fixed_corners(image_path, fixed_corners, margin)
            
            if contour_image is not None and extracted_pixels_hsv is not None:
                output_image_path = os.path.join(output_folder, f"detected_{file_name}")
                cv2.imwrite(output_image_path, contour_image)
                
                grouped_hsv_values = [extracted_pixels_hsv[i:i+3].tolist() for i in range(0, len(extracted_pixels_hsv), 3)]
                csv_writer.writerow([file_name, grouped_hsv_values])    # 픽셀값 쓰기

            else:
                print(f"Sticker not detected in {file_name}. Skipping...")

# 사용 예시
image_folder = r'C:\Users\kang9\Desktop\coding_and_study\acin\semiconductor_vision\sticker_detection\wafer_img'
output_folder = r'C:\Users\kang9\Desktop\coding_and_study\acin\semiconductor_vision\sticker_detection\result_data_fixed'
lower_bound = np.array([7,120,160])
upper_bound = np.array([15,140,180])
margin = 10

detect_stickers_in_folder_with_fixed_corners(image_folder, lower_bound, upper_bound, margin, output_folder)
