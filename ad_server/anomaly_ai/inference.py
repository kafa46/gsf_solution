import argparse
import torch
import numpy as np
# import train
from anomaly_ai import train
from PIL import Image
from torchvision.transforms import (
    Compose,
    Resize,
    ToTensor,
    Normalize,
)
from config import ARGS
from anomaly_ai.modeling.net import DRA

class DRAInference():
    def __init__(self, model_fn) -> None:
        check_point = torch.load(model_fn)
        # self.input_data = args.input_data
        self.args = check_point['args']
        print(self.args)
        self.model = DRA(self.args, backbone=self.args.backbone)
        self.model.load_state_dict(check_point['model_state_dict'])
        self.mean, self.std = check_point['mean_std']
        
        # Adjust args for inference
        self.args.dataset_root = ARGS['dataset_root']
        self.args.classname = ARGS['classname']
        self.threshold = ARGS['z-score_threshold-low']
        
        if torch.cuda.is_available():
            self.model.to('cuda')
        self.trainer = train.Trainer(self.args)
        self.transform = self.transform_test()

    def transform_test(self) -> Compose:
        '''Define image transform'''
        composed_transforms = Compose([
            Resize((self.args.img_size, self.args.img_size)),
            ToTensor(),
            Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        return composed_transforms

    def load_img_from_file(self, path: str) -> Compose:
        if 'npy' in path[-3:]:
            img = np.load(path).astype(np.uint8)
            img = img[:, :, :3]
            return Image.fromarray(img)
        else:
            img = Image.open(path).convert('RGB')
        data = self.transform(img)
        return data


    def inference(self, input_data: str|torch.Tensor) -> int:
        '''DRA prediction
        - Args:
            - input_data: path for input data or bytearray
        - Return: int (predicted label)
        '''
        self.model.eval()
        if isinstance(input_data, str):
            image = self.load_img_from_file(input_data)
        elif isinstance(input_data, Image.Image):
            image = self.transform(input_data)

        if torch.cuda.is_available():
            image = image.cuda()

        if self.args.total_heads == 4:
            try:
                ref_image = next(self.trainer.ref)['image']
            except StopIteration:
                self.ref = iter(self.trainer.ref_loader)
                ref_image = next(self.ref)['image']
            image = image.unsqueeze(dim=0)
            ref_image = ref_image.cuda()
            image = torch.cat([ref_image, image], dim=0)

        with torch.no_grad():
            class_pred = [np.array([]) for _ in range(self.args.total_heads)]
            outputs = self.model(image, label=None)
            for i in range(self.args.total_heads):
                if i == 0:
                    data = -1 * outputs[i].data.cpu().numpy()
                else:
                    data = outputs[i].data.cpu().numpy()
                class_pred[i] = np.append(class_pred[i], data)
            # print(f'class_pred: {class_pred}')
        # compute anomaly_score
        anomaly_score = sum([i.item() for i in class_pred])
        z_score = (anomaly_score - self.mean)/self.std
        if z_score < 0:
            z_score *= -1.0
        
        anomaly_status = True if z_score >= self.threshold else False
        # True: 비정상, False: 정상
        
        return {
            'anomaly_score': anomaly_score,
            'is_anomaly': anomaly_status,
            'z_score': z_score,
            'threshold': self.threshold,
        }

