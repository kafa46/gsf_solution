# utils/cam_live.py
import cv2
import threading

class CameraStream:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        # 새로운 스레드에서 카메라 업데이트 시작
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # 카메라에서 프레임을 계속 읽어옴
        while not self.stopped:
            success, frame = self.camera.read()
            if success:
                # 스레드 안전성을 위해 lock을 걸고 프레임 저장
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        # 실시간 영상(이미지)을 반환 (lock을 사용하여 스레드 안전성 확보)
        with self.lock:
            if self.frame is not None:
                # PNG 형식으로 인코딩
                ret, buffer = cv2.imencode('.png', self.frame)
                return buffer.tobytes()
            return None

    def stop(self):
        self.stopped = True
        self.camera.release()

# 싱글톤으로 사용되는 카메라 스트림
camera_stream = CameraStream().start()
