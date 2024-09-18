import cv2
import numpy as np

### 웨이퍼 탐지하는 함수 

# 이미지 읽기
image = cv2.imread('/home/kangsan/semiconductor_vision/sticker_detection/image/input_img/img1.jpg')
if image is None:
    print("이미지를 읽을 수 없습니다. 경로를 확인하세요.")
else:
    cv2.namedWindow('원본 이미지', cv2.WINDOW_NORMAL)
    cv2.imshow('원본 이미지', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.namedWindow('그레이스케일 이미지', cv2.WINDOW_NORMAL)
    cv2.imshow('그레이스케일 이미지', gray_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray_image)
    print(f"최대 밝기 위치: {maxLoc}, 최대 밝기 값: {maxVal}")

    
    threshold = 60  
    mask = cv2.inRange(gray_image, maxVal - threshold, maxVal)

    result_image = image.copy()
    result_image[mask > 0] = [0, 255, 255] 

    # 최고 밝기 위치에 원을 그리기
    brightest_point = maxLoc
    cv2.circle(result_image, brightest_point, 30, (0, 0, 255), -1)  # 빨간색 원으로 표시

    cv2.namedWindow('제일 밝은 부분', cv2.WINDOW_NORMAL)
    cv2.imshow('제일 밝은 부분', result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
