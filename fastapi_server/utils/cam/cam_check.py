import cv2

class CameraManager:
    def __init__(self):
        self.cameras = [None for i in range(0,10)]  # 카메라 객체들을 저장할 리스트
        self.available_cameras = [] # 카메라가 사용 가능한지 확인
        self.cameras_use = [False for i in range(0,10)] # 카메라가 사용중인지 체크하는 용도
        self.current_using_index = 0

    def find_available_cameras(self):
        for index in range(0,10):
            camera = cv2.VideoCapture(index)
            if not camera.isOpened():
                print(f"카메라 {index}에 접근할 수 없습니다.")
            else :
                print(f"카메라 {index}에 접근 가능합니다.")
                self.available_cameras.append(index)
                camera.release()
        
        return self.available_cameras

    # 동적으로 카메라 인덱스에 맞춰 CameraStream 생성
    def add_camera_stream(self, camera_index):
        print("카메라 사용가능 객체 할당")
        self.cameras[camera_index] = CameraStream(camera_index)
        self.cameras_use[camera_index] = True
        self.current_using_index = camera_index
        return self.cameras[camera_index]   # 카메라 객체 생성 후 반환

        
    # 저장된 모든 카메라 객체 해제
    def release_all_cameras(self):
        for index, camera_status in enumerate(self.cameras_use):
            if camera_status == True:
                print(f"현재 인덱스: {index} 카메라 할당 해제")
                self.cameras[index].stop()
        
        self.available_cameras = []
        self.cameras = [None for i in range(0,10)]  # 카메라 리스트 초기화
        self.cameras_use = [False for i in range(0,10)] # 카메라가 사용중인지 체크하는 용도 초기화
        print("모든 카메라 자원 해제 완료")

class CameraStream:
    def __init__(self, camera_index):
        self.camera = cv2.VideoCapture(camera_index)
        self.frame = None

    def get_frame(self):
        # 카메라에서 직접 프레임을 읽어옴
        success, frame = self.camera.read()
        if success:            
            # PNG 형식으로 인코딩하여 반환
            ret, buffer = cv2.imencode('.png', frame)
            return buffer.tobytes()
        return None

    def save_frame(self, file_path='temp/captured_frame.png'):
        # 프레임을 읽어와서 파일로 저장
        success, frame = self.camera.read()
        if frame is not None :
            cv2.imwrite(file_path, frame)
            print("이미지 저장 완료")
        else:
            print(" 이미지 저장 불가 카메라에서 프레임을 읽어올수 없음 ")
    
    def generate_frames(self):
        while True:
            frame = self.get_frame()
            if frame is None:
                continue
            yield (b'--frame\r\n'
                    b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

    def stop(self):
        # 카메라 자원 해제
        self.camera.release()
        

# 카메라 매니저 객체 생성(싱글톤)
cam_manager = CameraManager()
