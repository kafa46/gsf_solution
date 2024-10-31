import cv2
import numpy as np
from PIL import Image

### 스티커 디텍션하는 본 동작 메인 함수 
#

# 디텍션한 부분 이미지만 반환하는 함수
def crop_detected_region(image, corners):
    """
    네 꼭짓점으로 정의된 영역을 크롭하여 반환하는 함수.
    
    :param image: 원본 이미지 (numpy 배열)
    :param corners: 탐지된 네 꼭짓점 좌표 (numpy 배열)
    :return: 크롭된 이미지 영역 (numpy 배열)
    """
    
    # 다각형 마스크 생성
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [corners], 255)

    # 마스크를 사용하여 이미지에서 다각형 영역만 추출
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    # 네 꼭짓점의 최소/최대 좌표를 기준으로 크롭할 사각형 영역 계산
    x_min = np.min(corners[:, 0])
    x_max = np.max(corners[:, 0])
    y_min = np.min(corners[:, 1])
    y_max = np.max(corners[:, 1])

    # 이미지 크롭
    cropped_image = masked_image[y_min:y_max, x_min:x_max]
    
    return cropped_image

def load_and_preprocess_image(image_path, resize_dim=(800, 800)):
    """이미지를 불러오고, 크기 조정 후, BGR과 HSV로 변환"""
    image = Image.open(image_path)
    image = image.resize(resize_dim, Image.LANCZOS)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    hsv_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)
    return image_cv, hsv_image

def create_mask(hsv_image, lower_bound, upper_bound):
    """HSV 이미지에서 특정 색상 범위에 해당하는 마스크 생성"""
    return cv2.inRange(hsv_image, lower_bound, upper_bound)

def find_largest_contour(mask):
    """마스크에서 가장 큰 외곽선 찾기"""
    # RETR_EXTERNAL: 가장 외곽의 외곽선만 검출
    # CHAIN_APPROX_SIMPLE: 외곽선의 수평, 수직, 대각선 부분을 압축하여 끝점만 저장
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        return max(contours, key=cv2.contourArea)
    else:
        return None

def find_corners(contour):
    """외곽선에서 네 꼭짓점 찾기"""
    top_left = min(contour, key=lambda point: point[0][0] + point[0][1])[0]
    top_right = max(contour, key=lambda point: point[0][0] - point[0][1])[0]
    bottom_left = min(contour, key=lambda point: point[0][0] - point[0][1])[0]
    bottom_right = max(contour, key=lambda point: point[0][0] + point[0][1])[0]
    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)

def apply_margin(corners, margin):
    """네 꼭짓점에 마진을 적용"""
    return np.array([
        (corners[0][0] - margin, corners[0][1] - margin),  # top_left
        (corners[1][0] + margin, corners[1][1] - margin),  # top_right
        (corners[2][0] + margin, corners[2][1] + margin),  # bottom_right
        (corners[3][0] - margin, corners[3][1] + margin)   # bottom_left
    ], dtype=np.int32)

def create_polygon_mask(image_shape, corners):
    """다각형 마스크 생성"""
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [corners], 255)
    return mask


def draw_corners_and_edges(image, corners, color=(255, 0, 100), thickness=2):
    """이미지에 네 꼭짓점과 이를 잇는 선 그리기"""
    for i in range(4):
        cv2.line(image, tuple(corners[i]), tuple(corners[(i + 1) % 4]), color, thickness)
    # for corner in corners:
    #     cv2.circle(image, tuple(corner), 2, (0, 0, 255), -1)


def detect_stickers(image_path, lower_bound, upper_bound, margin, crop=False):
    # 이미지 로드 및 전처리
    image_cv, hsv_image = load_and_preprocess_image(image_path)
    
    # 마스크 생성
    mask = create_mask(hsv_image, lower_bound, upper_bound)
    
    # 가장 큰 외곽선 찾기
    max_contour = find_largest_contour(mask)
    
    if max_contour is None:
        print("Contour not found")
        return None, None, None

    # 네 꼭짓점 찾기
    original_corners = find_corners(max_contour)
    
    # 마진 적용 후 선분 그리기
    adjusted_corners = apply_margin(original_corners, margin)
    contour_image = image_cv.copy()
    draw_corners_and_edges(contour_image, original_corners)
    draw_corners_and_edges(contour_image, adjusted_corners, color=(0, 255, 0))
    
    if crop:
        # 크롭된 이미지를 반환
        cropped_image = crop_detected_region(image_cv, adjusted_corners)
        return cropped_image
    else:
        # 선분이 그려진 전체 이미지를 반환
        return contour_image


# # 사용 예시
# image_path = r'C:\Users\kang9\Desktop\coding_and_study\acin\semiconductor_vision\sticker_detection\wafer_img\wafer_00m00s_001.jpg'
# lower_bound = np.array([7,120,160])
# upper_bound = np.array([15,140,180])
# margin = 10

# contour_image, extracted_pixels_rgb, extracted_pixels_hsv = detect_stickers(image_path, lower_bound, upper_bound, margin)

# # print(extracted_pixels_hsv)

# # 결과 이미지 
# cv2.imshow("detect image", contour_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # RGB 영역 시각화
# cv2.imshow("Extracted RGB Pixels", extracted_pixels_rgb)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # HSV 영역 시각화 (HSV를 다시 RGB로 변환하여 시각화)
# if extracted_pixels_hsv is not None and extracted_pixels_hsv.shape[-1] == 3:  # 채널 수 확인
#     extracted_pixels_hsv_rgb = cv2.cvtColor(extracted_pixels_hsv, cv2.COLOR_HSV2BGR)
#     cv2.imshow("Extracted HSV Pixels (as RGB)", extracted_pixels_hsv_rgb)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# else:
#     print("extracted_pixels_hsv does not have 3 channels.")
