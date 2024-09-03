import argparse
import torch
import numpy as np
import train

from PIL import Image
from torchvision.transforms import (
    Compose, 
    Resize, 
    ToTensor, 
    Normalize,
)
from modeling.net import DRA

def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model_fn', type=str, required=True, 
        help='model file path, required'
    )
    parser.add_argument(
        '--input_data', type=str, required=True,
        help='input data file path, required'
    )
    parser.add_argument(
        '--no-cuda', action='store_true', default=False, 
        help='disables CUDA training, default: False'
    )
    args = parser.parse_args()
    args.cuda = not args.no_cuda and torch.cuda.is_available()
    return args


class DRAInference():
    def __init__(self, model_fn) -> None:
        check_point = torch.load(model_fn)
        self.input_data = args.input_data
        self.args = check_point['args']
        print(self.args)
        self.model = DRA(self.args, backbone=self.args.backbone)
        self.model.load_state_dict(check_point['model_state_dict'])
        self.mean, self.std = check_point['mean_std']
        
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
            # image = image.type(torch.FloatTensor)
        elif isinstance(input_data, np.array):
            image = torch.Tensor(input_data)
        
        if torch.cuda.is_available():
            image = image.cuda()
        
        if self.args.total_heads == 4:
            try:
                ref_image = next(self.trainer.ref)['image']
            except StopIteration:
                self.ref = iter(self.trainer.ref_loader)
                ref_image = next(self.ref)['image']
            # print(f'image.shape: {image.shape}')
            image = image.unsqueeze(dim=0)
            # print(f'image.shape: {image.shape}')
            # print(f'ref_image.shape: {ref_image.shape}')
            ref_image = ref_image.cuda()
            image = torch.cat([ref_image, image], dim=0)
            # print(f'cat image.shape: {image.shape}')
             
        
        with torch.no_grad():
            class_pred = [np.array([]) for _ in range(self.args.total_heads)]
            total_target = np.array([])
            # print(f'class_pred: {class_pred}')
            # print(f'total_target: {total_target}')
            
            outputs = self.model(image, label=None)
            # print(f'outputs: {outputs}')
            for i in range(self.args.total_heads):
                if i == 0:
                    data = -1 * outputs[i].data.cpu().numpy()
                else:
                    data = outputs[i].data.cpu().numpy()
                class_pred[i] = np.append(class_pred[i], data)
            print(f'class_pred: {class_pred}')
        
        # compute anomaly_score
        anomaly_score = sum([i.item() for i in class_pred])
        z_score = (anomaly_score - self.mean)/self.std
        print(f'self.mean: {self.mean}')
        print(f'self.std: {self.std}')
        print(f'anomaly_score: {anomaly_score}')
        print(f'z_score: {z_score}')
        # if anomaly_score >= self.mean + 3*self.st:
        if z_score >= 3.0:
            print('Abnomal')
        else:
            print('Normal')
            

if __name__=='__main__':
    args = arg_parser()
    di = DRAInference(args.model_fn)
    di.inference(args.input_data)
    

            