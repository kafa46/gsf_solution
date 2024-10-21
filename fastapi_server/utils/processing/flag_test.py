import threading
import time

# 전역 변수로 flag 선언
flag = True
lock = threading.Lock()

def thread1_function():
    global flag
    while True:
        with lock:
            if not flag:
                print("쓰레드 1 종료")
                break
        
        # 작업 수행
        print("쓰레드 1 실행 중...")
        time.sleep(1)

# 쓰레드 1 생성 및 시작
thread1 = threading.Thread(target=thread1_function)
thread1.start()

# 5초 후 flag를 False로 변경하여 쓰레드 종료
time.sleep(5)
with lock:
    flag = False

# 쓰레드가 종료될 때까지 기다림
thread1.join()
print("메인 프로그램 종료")