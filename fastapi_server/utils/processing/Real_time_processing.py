import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from func import create_mask, find_largest_contour, create_polygon_mask, find_corners, extract_pixels, draw_corners_and_edges

class StickerDetectionApp:
    def __init__(self, root, video_source=1):
        self.root = root
        self.root.title("Sticker Detection")
        
        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 너비를 640으로 설정
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 높이를 480으로 설정
        
        self.canvas = tk.Canvas(root, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.label_status = tk.Label(root, text="Status: OK", font=("Helvetica", 14))
        self.label_status.pack()

        self.lower_bound = np.array([50, 138, 96])
        self.upper_bound = np.array([78, 168, 126])
        self.sticker_detected = False
        self.reference_pixels_hsv = None
        self.fixed_corners = None  # 고정된 네 꼭짓점을 저장하는 변수

        self.delay = 15
        self.update()

        self.root.mainloop()

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            if not self.sticker_detected:
                # 처음에 스티커를 탐지하여 네 꼭짓점 좌표를 고정
                contour_image, extracted_pixels_rgb, extracted_pixels_hsv = self.detect_stickers(frame)
                if extracted_pixels_hsv is not None:
                    self.reference_pixels_hsv = extracted_pixels_hsv
                    self.fixed_corners = find_corners(find_largest_contour(create_mask(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), self.lower_bound, self.upper_bound)))
                    self.sticker_detected = True
                    self.label_status.config(text="Status: OK", fg="green")  # 첫 탐지 후 OK 상태로 설정
            else:
                # 실시간으로 고정된 네 꼭짓점을 영상에 그리기
                if self.fixed_corners is not None:
                    draw_corners_and_edges(frame, self.fixed_corners, color=(255, 0, 0))
                
                # 실시간으로 영역 내 픽셀 변화 감지
                hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                poly_mask = create_polygon_mask(frame.shape, self.fixed_corners)
                _, current_pixels_hsv = extract_pixels(hsv_image, poly_mask)
                    
                if self.check_movement(self.reference_pixels_hsv, current_pixels_hsv):
                    self.label_status.config(text="Status: NG", fg="red")
                else:
                    self.label_status.config(text="Status: OK", fg="green")

            # Tkinter에 영상 표시
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.root.after(self.delay, self.update)

    def check_movement(self, reference_pixels_hsv, current_pixels_hsv, threshold=0.8, min_diff_threshold=30):
        """기준 HSV 픽셀값과 현재 HSV 픽셀값을 비교하여 움직임을 감지"""
        if reference_pixels_hsv is None or current_pixels_hsv is None:
            print("Movement check aborted: reference_pixels_hsv or current_pixels_hsv is None.")
            return False
        
        # 크기와 채널 수 확인
        if reference_pixels_hsv.shape != current_pixels_hsv.shape:
            print(f"Shape mismatch: reference_pixels_hsv {reference_pixels_hsv.shape}, current_pixels_hsv {current_pixels_hsv.shape}. NG detected due to shape mismatch.")
            return True  # NG로 간주
        
        # 두 배열의 차이를 계산하여 변화율 확인
        diff = cv2.absdiff(reference_pixels_hsv, current_pixels_hsv)
        diff[diff < min_diff_threshold] = 0  # 차이가 작은 부분은 무시
        non_zero_count = np.count_nonzero(diff)
        
        # 변화율이 일정 비율(30%) 이상일 경우 NG로 간주
        if non_zero_count / diff.size > threshold:
            print(f"NG detected: Change ratio ({non_zero_count / diff.size:.2f}) exceeded the threshold ({threshold}).")
            return True
        
        print("No significant movement detected. Returning False.")
        return False

    def detect_stickers(self, frame):
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = create_mask(hsv_image, self.lower_bound, self.upper_bound)
        max_contour = find_largest_contour(mask)
        if max_contour is None:
            return None, None, None

        original_corners = find_corners(max_contour)
        poly_mask = create_polygon_mask(frame.shape, original_corners)
        
        _, extracted_pixels_rgb = extract_pixels(frame, poly_mask)
        _, extracted_pixels_hsv = extract_pixels(hsv_image, poly_mask)
        
        contour_image = frame.copy()
        draw_corners_and_edges(contour_image, original_corners)
        
        return contour_image, extracted_pixels_rgb, extracted_pixels_hsv

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = StickerDetectionApp(root)
