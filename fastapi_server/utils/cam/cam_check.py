import cv2

def find_available_cameras():
    index = 0  # 카메라 인덱스 시작
    available_cameras = []

    while True:
        camera = cv2.VideoCapture(index)
        if not camera.isOpened():  # 카메라가 열리지 않으면 연결되지 않음
            print("등록된 카메라 없음")
            break
        available_cameras.append(index)  # 사용 가능한 카메라 인덱스 추가
        camera.release()  # 카메라 자원 해제
        index += 1  # 다음 카메라 인덱스로 넘어감

    return available_cameras


