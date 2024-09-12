class GlobalState:
    def __init__(self):
        self.contours_list = []
        self.margin_list = []
        self.save_flag = False
        

# 전역 인스턴스 생성 (최대한 빠르게 하려고...만듬)
global_state_instance = GlobalState()