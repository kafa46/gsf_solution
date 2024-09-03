import numpy as np
import os, sys
# from datasets.base_dataset import BaseADDataset
from torch.utils.data import Dataset
from PIL import Image
from torchvision.transforms import (
    Compose,
    Resize,
    RandomRotation,
    ToTensor,
    Normalize,
)
from datasets.cutmix import CutMix
import random


class MVTecDataset(Dataset):

    def __init__(self, args, train: bool = True):
        super().__init__()
        self.args = args
        self.train = train
        self.classname = self.args.classname
        self.know_class = self.args.know_class
        self.pollution_rate = self.args.cont_rate # outlier contamination rate in train data
        self.split = 'train' if train else 'test'
        if self.args.test_threshold == 0 and self.args.test_rate == 0:
            self.test_threshold = self.args.nAnomaly
        else:
            self.test_threshold = self.args.test_threshold
        self.root = os.path.join(self.args.dataset_root, self.classname)
        self.transform = self.transform_train() if self.train else self.transform_test()
        self.transform_pseudo = self.transform_pseudo()

        normal_files = os.listdir(os.path.join(self.root, self.split, 'good'))
        normal_data = [
            f'{self.split}/good/{x}' for x in normal_files if self.check_ext(x)
        ]
        if self.train is True:
            self.nPollution = int(
                (len(normal_data)/(1-self.pollution_rate)) * self.pollution_rate
            )
            if self.test_threshold==0 and self.args.test_rate>0:
                normal_rate = int((len(normal_data)/(1-self.args.test_rate)) * self.args.test_rate)
                self.test_threshold = normal_rate + self.args.nAnomaly
            self.ood_data = self.get_ood_data()

        outlier_data, pollution_data = self.split_outlier()
        outlier_data.sort()

        normal_data = normal_data + pollution_data

        normal_label = np.zeros(len(normal_data)).tolist()
        outlier_label = np.ones(len(outlier_data)).tolist()

        self.images = normal_data + outlier_data
        self.labels = np.array(normal_label + outlier_label)
        self.normal_idx = np.argwhere(self.labels == 0).flatten()
        self.outlier_idx = np.argwhere(self.labels == 1).flatten()

    def check_ext(self, f_name: str) -> bool:
        '''validate file extension (ex: example.png)'''
        return (
            f_name.endswith('png') or
            f_name.endswith('PNG') or
            f_name.endswith('jpg') or
            f_name.endswith('npy')
        )
    
    def get_ood_data(self):
        '''Extract Out-of-Distribution data
        i.e., extract all normal data from dataset.
        Ref: https://hoya012.github.io/blog/anomaly-detection-overview-2/
        현재 보유하고 있는 In-distribution 데이터 셋을 이용하여 
        multi-class classification network를 학습시킨 뒤, 
        test 단계에서 In-distribution test set은 정확하게 예측하고 
        Out-of-distribution 데이터 셋은 걸러내는 것
        '''
        ood_data = list()
        if self.args.outlier_root is None:
            return None
        dataset_classes = os.listdir(self.args.outlier_root) # 비정상 데이터 폴더명
        for cl in dataset_classes:
            if cl == self.args.classname:
                continue
            cl_root = os.path.join(self.args.outlier_root, cl, 'train', 'good')
            ood_file = os.listdir(cl_root)
            ood_data = [
                os.path.join(cl_root, f) for f in ood_file if self.check_ext(f)
            ]
        return ood_data

    def split_outlier(self, dir_name: str = 'test'):
        '''Split anomalies under 'test' directory
        This func can handle hard setting using "args.know_class"
        - Args:
            - dir_name (str): target directory containing anomaly dataset
        '''
        outlier_data_dir = os.path.join(self.root, dir_name)
        outlier_classes = os.listdir(outlier_data_dir) # ex. carpet/test: hole, thread, ...
        
        # Handling hard-setting
        if self.know_class in outlier_classes:
            print("Know outlier class for hard setting: " + self.know_class)
            outlier_data = []
            know_class_data = []
            for class_name in outlier_classes:
                if class_name == 'good': continue
                outlier_file = os.listdir(os.path.join(outlier_data_dir, class_name))
                for file in outlier_file:
                    if self.check_ext(file):
                        if class_name == self.know_class:
                            know_class_data.append(f'{dir_name}/{class_name}/{file}')
                        else:
                            outlier_data.append(f'{dir_name}/{class_name}/{file}')
            np.random.RandomState(self.args.ramdn_seed).shuffle(know_class_data)
            know_outlier = know_class_data[0:self.args.nAnomaly]
            unknow_outlier = outlier_data
            if self.train:
                return know_outlier, list()
            return unknow_outlier, list()
        
        # Handling normal-setting
        for class_name in outlier_classes:
            if class_name == 'good': continue
            outlier_file = os.listdir(os.path.join(outlier_data_dir, class_name))
            outlier_data = [
                f'{dir_name}/{class_name}/{f}'for f in outlier_file if self.check_ext(f)
            ]

        np.random.RandomState(self.args.ramdn_seed).shuffle(outlier_data)
        if self.train:
            anomaly = self.args.nAnomaly
            pollution = self.nPollution
            return (
                outlier_data[0:anomaly], 
                outlier_data[anomaly:anomaly + pollution]
            )
        return outlier_data[self.test_threshold:], list()

    def load_image(self, path: str) -> Image:
        if path.endswith('npy'):
            img = np.load(path).astype(np.uint8)
            img = img[:, :, :3]
            return Image.fromarray(img)
        return Image.open(path).convert('RGB')

    def transform_train(self):
        composed_transforms = Compose([
            Resize((self.args.img_size, self.args.img_size)),
            RandomRotation(180),
            ToTensor(),
            Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        return composed_transforms

    def transform_pseudo(self):
        composed_transforms = Compose([
            Resize((self.args.img_size,self.args.img_size)),
            CutMix(),
            RandomRotation(180),
            ToTensor(),
            Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        return composed_transforms

    def transform_test(self):
        composed_transforms = Compose([
            Resize((self.args.img_size, self.args.img_size)),
            ToTensor(),
            Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        return composed_transforms

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        rnd = random.randint(0, 1)
        # Train mode
        if index in self.normal_idx and rnd == 0 and self.train:
            if self.ood_data is None:
                index = random.choice(self.normal_idx)
                image = self.load_image(os.path.join(self.root, self.images[index]))
                transform = self.transform_pseudo
            else:
                image = self.load_image(random.choice(self.ood_data))
                transform = self.transform
            label = 2
        # Test mode
        else:
            image = self.load_image(os.path.join(self.root, self.images[index]))
            transform = self.transform
            label = self.labels[index]
        sample = {'image': transform(image), 'label': label}
        return sample
