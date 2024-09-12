import cv2
import numpy as np
import os
from PIL import Image

from .func import apply_margin, detect_stickers, load_and_preprocess_image, create_mask, find_corners, find_largest_contour, draw_corners_and_edges

####### 이미지 전처리 부분
# 원본 꼭짓점으로 정의된 영역 내의 이미지를 반환하는 함수
def crop_original_region(image, corners):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [corners], 255)
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    x_min, y_min = np.min(corners, axis=0)
    x_max, y_max = np.max(corners, axis=0)
    
    return masked_image[y_min:y_max, x_min:x_max]

# 마진이 적용된 꼭짓점으로 정의된 영역 내의 이미지를 반환하는 함수
def crop_margined_region(image, corners, margin):
    adjusted_corners = apply_margin(corners, margin)
    
    # 이미지 경계를 벗어나지 않도록 좌표 조정
    adjusted_corners[:, 0] = np.clip(adjusted_corners[:, 0], 0, image.shape[1] - 1)
    adjusted_corners[:, 1] = np.clip(adjusted_corners[:, 1], 0, image.shape[0] - 1)
    
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [adjusted_corners], 255)
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    x_min, y_min = np.min(adjusted_corners, axis=0)
    x_max, y_max = np.max(adjusted_corners, axis=0)
    
    cropped_image = masked_image[y_min:y_max, x_min:x_max]
    
    # 검은색 영역을 원본 이미지의 내용으로 복구
    # black_mask = (cropped_image == 0).all(axis=-1).astype(np.uint8) * 255
    # inpainted_image = cv2.inpaint(cropped_image, black_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # return inpainted_image
    
    # 원본 이미지에서 잘라낸 영역 복사하여 검은색 부분 채우기
    original_cropped = image[y_min:y_max, x_min:x_max]
    non_black_pixels = cropped_image != 0
    cropped_image[~non_black_pixels] = original_cropped[~non_black_pixels]
    
    return cropped_image

# 네 꼭짓점 반환 함수
def get_contours(hsv_image, lower_bound, upper_bound):
    # 마스크 생성 및 가장 큰 외곽선 찾기
    mask = create_mask(hsv_image, lower_bound, upper_bound)
    max_contour = find_largest_contour(mask)

    if max_contour is None:
        print("외곽선을 찾을 수 없습니다. HSV 값을 조정해 주세요")
        return None, None
    
    return find_corners(max_contour)

def get_cropped_sticker_images(image_path, lower_bound, upper_bound, margin, contours=None):
    """
    스티커를 감지하고 원본 및 마진이 적용된 크롭 이미지를 반환하는 함수
    """
    # detect_stickers 함수 호출
    contour_image = detect_stickers(image_path, lower_bound, upper_bound, margin)
    
    if contour_image is None:
        print("스티커를 감지할 수 없습니다. HSV 값을 조정해주세요")
        return None, None

    # 원본 이미지 로드
    image_cv, hsv_image = load_and_preprocess_image(image_path)

    if contours is None:
        # 네 꼭짓점 찾기
        original_corners = get_contours(hsv_image, lower_bound, upper_bound)
    else :
        original_corners = contours
    
    # 원본 꼭짓점 영역 크롭
    original_crop = crop_original_region(image_cv, original_corners)
    
    # 마진 적용된 꼭짓점 영역 크롭
    margined_crop = crop_margined_region(image_cv, original_corners, margin)
    
    return original_crop, margined_crop


####### 이미지 탐지 방식 부분
# dynamic
def dynamic_detected_images(captured_files, lower_bound, upper_bound, margin, detected_folder, file_prefix="detected"):
    pass

# Fixed
def fixed_detected_images(captured_image, lower_bound, upper_bound, margin):
    
    # (살구색) 스티커 HSV값 설정, 마진값 설정
    
    
    # 탐지 체크 용도
    contour_image = detect_stickers(captured_image, lower_bound, upper_bound, margin)

    if contour_image is None :
        print("컨투어 이미지 탐지 안됌")
        return False
        
    # 고정 방식
    
    # 원본 이미지 로드
    image_cv, hsv_image = load_and_preprocess_image(captured_image)
    
    # 첫번째 사진 컨투어 찾기
    contours = get_contours(hsv_image, lower_bound, upper_bound)
    
    # 찾은 컨투어로 이미지 크롭 
    original_crop, margined_crop = get_cropped_sticker_images(captured_image, lower_bound, upper_bound, margin, contours=contours)
    
    print("고정 방식 완료!")
    
    return contours, margined_crop
    

def fixed_detected_live():
    # 쓰레드 동기화 처리 해야됌(Lock)
    global save_start_flag
    while save_start_flag == True:
        if save_start_flag == False:
            print("동영상 저장 종료")
            break
        # 동영상 촬영 시작
        
    return 

def all_crop_draw(image_path, contours_list, margin_list, save_path):
    # 이미지 로드
    image_cv, _ = load_and_preprocess_image(image_path)
    
    # 각 컨투어에 대해 처리
    for contour, margin in zip(contours_list, margin_list):
        # 마진 적용
        adjusted_contour = apply_margin(contour, margin)
                
        # 마진이 적용된 컨투어 그리기 (초록색)
        draw_corners_and_edges(image_cv, adjusted_contour, color=(0, 255, 0), thickness=2)
    
    full_save_path = os.path.join(save_path, "all_crop.png")
    # 이미지 저장
    cv2.imwrite(full_save_path, image_cv)
    print(f"Image saved to: {full_save_path}")
        
# if __name__ == "__main__":
#     # 경로 설정
#     # 설정
#     output_folder = "../../data/input/captured_images"
#     dy_cropped_folder = "../../data/output/dy_cropped_stickers"
#     fx_cropped_folder = "../../data/output/fx_cropped_stickers"
        
#     # (살구색) 스티커 HSV값 설정, 마진값 설정
#     lower_bound = np.array([4,100,140])
#     upper_bound = np.array([20,130,170])
#     margin = 20
    
#     # 폴더 생성
#     if not os.path.exists(dy_cropped_folder):
#         os.makedirs(dy_cropped_folder, exist_ok=True)
#     elif not os.path.exists(fx_cropped_folder):
#         os.makedirs(fx_cropped_folder, exist_ok=True)

#     # 기존에 저장된 이미지 파일들의 경로를 리스트로 가져오기
#     captured_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".png")]
    
#     # 탐지 체크 용도
#     contour_image = detect_stickers(captured_files[0], lower_bound, upper_bound, margin)

#     if contour_image is None :
#         print("컨투어 이미지 탐지 안됌")
#         exit(0)

#     # 동적 방식
#     for file_path in captured_files:
#         file_name = os.path.basename(file_path)
#         file_name = str(file_name).replace("wafer_capture_", "")
        
#         """
#         스티커 디텍션 동작부분
#         """
#         original_crop, margined_crop = get_cropped_sticker_images(file_path, lower_bound, upper_bound, margin)
        
        
#         # 디텍션된 이미지 전체를 저장
#         if margined_crop is not None:
#             detected_image_path = os.path.join(dy_cropped_folder, f"dy_detected_{file_name}")
#             cv2.imwrite(detected_image_path, margined_crop) # margin 적용된 이미지 저장
#             print(f"Detected image saved to: {detected_image_path}")
#     print("동적 방식 완료!")
    
    
#     # 고정 방식
    
#     # 원본 이미지 로드
#     image_cv, hsv_image = load_and_preprocess_image(captured_files[0])
    
#     # 첫번째 사진 컨투어 찾기
#     contours = get_contours(hsv_image)
    
#     for file_path in captured_files:
#         file_name = os.path.basename(file_path)
#         file_name = str(file_name).replace("wafer_capture_", "")
        
#         """
#         스티커 디텍션 동작부분
#         """
        
#         original_crop, margined_crop = get_cropped_sticker_images(file_path, lower_bound, upper_bound, margin, contours=contours)
        
        
#         # 디텍션된 이미지 전체를 저장
#         if margined_crop is not None:
#             detected_image_path = os.path.join(fx_cropped_folder, f"fx_detected_{file_name}")
#             cv2.imwrite(detected_image_path, margined_crop)
#             print(f"Detected image saved to: {detected_image_path}")
            
#     print("고정 방식 완료!")
    
#     print("스티커 전처리 작업 완료!")