'''
This module will send some image date to ad_server (anomaly detection server).
Only purpose of this module is to simulate sending
realtime images from monitoring camera.
'''

import os
import random
import time
import requests

PORT = '8877'
AD_SERVER_IP = f'http://127.0.0.1:{PORT}/monitor/' # should be same as ad_server
DATA_DIR = 'sample_dataset/carpet'
SEND_INTERVAL = 0.1 # unit: seconds

class ImageSender:
    '''Send images in SEND_INTERVAL'''
    def __init__(
        self,
        ad_server_ip: str = AD_SERVER_IP,
        data_dir: str = DATA_DIR,
        send_interval: int = SEND_INTERVAL
    ) -> None:
        self.ad_server_ip = ad_server_ip
        self.data_dir = data_dir
        self.send_interval = send_interval
        self.files = self.get_file_list()

    def get_file_list(self):
        sub_dirs = [d.path for d in os.scandir(self.data_dir)]
        files = []
        for sub_dir in sub_dirs:
            temp_files = os.listdir(sub_dir)
            temp_files = [os.path.join(sub_dir, f) for f in temp_files]
            files.extend(temp_files)
        return files

    def send_files(self):
        while True:
            time.sleep(self.send_interval)
            # select one image randomly from files
            rand_num = random.randint(0, len(self.files)-1)
            send_file = self.files[rand_num]
            classname = send_file.split('/')[-2]
            files = {'image': open(send_file, 'rb')}
            data = {'classname': classname}
            print(send_file)
            response = requests.post(
                self.ad_server_ip, 
                files=files,
                data=data,
            )
            

if __name__=='__main__':
    imgsend = ImageSender()
    imgsend.send_files()
