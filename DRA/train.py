from copy import deepcopy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import argparse
import os

from dataloaders.dataloader import initDataloader
from modeling.net import DRA
from tqdm import tqdm
from sklearn.metrics import average_precision_score, roc_auc_score
from modeling.layers import build_criterion
import random

import matplotlib.pyplot as plt

WEIGHT_DIR = './weights'


def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=48, 
                        help="batch size used in SGD")
    parser.add_argument("--steps_per_epoch", type=int, default=20, 
                        help="the number of batches per epoch")
    parser.add_argument("--epochs", type=int, default=20, 
                        help="the number of epochs")
    parser.add_argument("--cont_rate", type=float, default=0.0, 
                        help="the outlier contamination rate in the training data")
    parser.add_argument("--test_threshold", type=int, default=0,
                        help="the outlier contamination rate in the training data")
    parser.add_argument("--test_rate", type=float, default=0.0,
                        help="the outlier contamination rate in the training data")
    parser.add_argument("--dataset", type=str, default='mvtecad', 
                        help="a list of data set names")
    parser.add_argument("--ramdn_seed", type=int, default=42, 
                        help="the random seed number")
    parser.add_argument('--workers', type=int, default=4, metavar='N', 
                        help='dataloader threads')
    parser.add_argument('--no-cuda', action='store_true', default=False, 
                        help='disables CUDA training')
    parser.add_argument('--savename', type=str, default='model.pkl', 
                        help="save modeling")
    parser.add_argument('--dataset_root', type=str, default='./data/mvtec_anomaly_detection', 
                        help="dataset root")
    parser.add_argument('--experiment_dir', type=str, default='./experiment/experiment_14', 
                        help="dataset root")
    parser.add_argument('--classname', type=str, default='capsule', 
                        help="dataset class")
    parser.add_argument('--img_size', type=int, default=448, help="dataset root")
    parser.add_argument("--nAnomaly", type=int, default=10, 
                        help="the number of anomaly data in training set")
    parser.add_argument("--n_scales", type=int, default=2, 
                        help="number of scales at which features are extracted")
    parser.add_argument('--backbone', type=str, default='resnet18', help="backbone")
    parser.add_argument('--criterion', type=str, default='deviation', help="loss")
    parser.add_argument("--topk", type=float, default=0.1, help="topk in MIL")
    parser.add_argument('--know_class', type=str, default=None, 
                        help="set the know class for hard setting")
    parser.add_argument('--pretrain_dir', type=str, default=None, 
                        help="root of pretrain weight")
    parser.add_argument("--total_heads", type=int, default=4, 
                        help="number of head in training")
    parser.add_argument("--nRef", type=int, default=5, 
                        help="number of reference set")
    parser.add_argument('--outlier_root', type=str, default=None, help="OOD dataset root")
    args = parser.parse_args()
    args.cuda = not args.no_cuda and torch.cuda.is_available()
    return args

class Trainer(object):
    def __init__(self, args):
        self.args = args
        # Define Dataloader
        kwargs = {'num_workers': args.workers}
        self.train_loader, self.test_loader= initDataloader.build(args, **kwargs)
        if self.args.total_heads == 4:
            temp_args = args
            temp_args.batch_size = self.args.nRef
            temp_args.nAnomaly = 0
            self.ref_loader, _ = initDataloader.build(temp_args, **kwargs)
            self.ref = iter(self.ref_loader)
        self.best_loss = np.inf
        self.best_model = None
        self.model = DRA(args, backbone=self.args.backbone)

        if self.args.pretrain_dir != None:
            self.model.load_state_dict(torch.load(self.args.pretrain_dir))
            print('Load pretrain weight from: ' + self.args.pretrain_dir)

        self.criterion = build_criterion(args.criterion)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0002, weight_decay=1e-5)
        self.scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)

    def generate_labels(self, target: int, eval=False):
        # targets = []
        if eval:
            targets = [target==0, target, target, target]
            # targets.append(target==0)
            # targets.append(target)
            # targets.append(target)
            # targets.append(target)
            return targets
        else:
            temp_t = target != 0
            targets = [
                target == 0,
                temp_t[target != 2],
                temp_t[target != 1],
                target != 0
            ]
            # targets.append(target == 0)
            # targets.append(temp_t[target != 2])
            # targets.append(temp_t[target != 1])
            # targets.append(target != 0)
        return targets

    def training(self):
        # self.scheduler.step() -> comment out! move this statement after optimizer.step() 
        for epoch in range(self.args.epochs):
            train_loss = 0.0
            class_loss = [0.0 for _ in range(self.args.total_heads)]
            # Perform train with mini-batch
            self.model.train()
            tbar = tqdm(self.train_loader)
            for idx, sample in enumerate(tbar):
                image, label = sample['image'], sample['label']
                if self.args.cuda:
                    image, label = image.cuda(), label.cuda()
                if self.args.total_heads == 4:
                    try:
                        ref_image = next(self.ref)['image']
                    except StopIteration:
                        self.ref = iter(self.ref_loader)
                        ref_image = next(self.ref)['image']
                    ref_image = ref_image.cuda()
                    image = torch.cat([ref_image, image], dim=0)
                outputs = self.model(image, label)
                labels = self.generate_labels(label)
                losses = list()
                for i in range(self.args.total_heads):
                    if self.args.criterion == 'CE':
                        prob = F.softmax(outputs[i], dim=1)
                        losses.append(self.criterion(prob, labels[i].long()).view(-1, 1))
                    else:
                        losses.append(self.criterion(outputs[i], labels[i].float()).view(-1, 1))
                loss = torch.cat(losses)
                loss = torch.sum(loss)
                self.optimizer.zero_grad()
                loss.backward()

                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                # Moved from above due to the warning 
                #   UserWarning: Detected call of `lr_scheduler.step()` before `optimizer.step()`. 
                #   In PyTorch 1.1.0 and later, you should call them in the opposite order: `optimizer.step()` before `lr_scheduler.step()`.  
                #   Failure to do this will result in PyTorch skipping the first value of the learning rate schedule. 
                #   See more details at https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate
                self.scheduler.step() 
                # Compute total loss in epoch
                train_loss += loss.item()
                for i in range(self.args.total_heads):
                    class_loss[i] += losses[i].item()
                train_loss_updated = train_loss / (idx + 1)
                # tbar.set_description(f'Epoch:{epoch+1:2d}/{args.epochs}, Train loss: {train_loss / (idx + 1):.3f}')
                tbar.set_description(
                    f'Epoch:{epoch+1:2d}/{args.epochs}, Train loss: {train_loss_updated:.3f}'
                )
            # Evaluation & check best model
            self.model.eval()
            tbar = tqdm(self.test_loader, desc='\rTest loss:')
            test_loss = 0.0
            all_outputs = []
            all_labels = []
            for i, sample in enumerate(tbar):
                image, label = sample['image'], sample['label']
                all_labels.append(label)
                if self.args.cuda:
                    image, label = image.cuda(), label.cuda()
                if self.args.total_heads == 4:
                    try:
                        ref_image = next(self.ref)['image']
                    except StopIteration:
                        self.ref = iter(self.ref_loader)
                        ref_image = next(self.ref)['image']
                    ref_image = ref_image.cuda()
                    image = torch.cat([ref_image, image], dim=0)
                with torch.no_grad():
                    outputs = self.model(image, label)
                    all_outputs.append(outputs)
                    labels = self.generate_labels(label, eval=True)
                    losses = list()
                    for i in range(self.args.total_heads):
                        if self.args.criterion == 'CE':
                            prob = F.softmax(outputs[i], dim=1)
                            losses.append(self.criterion(prob, labels[i].long()))
                        else:
                            losses.append(self.criterion(outputs[i], labels[i].float()))
                    loss = losses[0]
                    for i in range(1, self.args.total_heads):
                        loss += losses[i]
                test_loss += loss.item()
                test_loss_averaged = test_loss / (i + 1)
                tbar.set_description(f'Test loss: {test_loss_averaged:.3f}')                
            # Check best model
            if test_loss_averaged < self.best_loss:
                print(f'Best model is detected! with eval loss: {test_loss_averaged:.3f} -> save this model')
                self.best_loss = test_loss_averaged
                self.best_model = deepcopy(self.model)
        # End of epochs
        # Save best model
        save_fn = f'{self.args.dataset}-{self.args.backbone}.model'
        save_path = os.path.join(self.args.experiment_dir, save_fn)
        mean, std = self.get_mean_stdev(all_labels, all_outputs)
        
        torch.save(
            {
                'model_state_dict': self.best_model.state_dict(),
                'args': self.args,
                'mean_std': (mean, std)
            }, 
            save_path
        )
        print(f'Best model saved -> {save_fn}')
                
    def normalization(self, data):
        return data

    def get_mean_stdev(self, all_labels: list, all_outputs: list) -> tuple[float, float]:
        '''Compute mean and stdev from given data array
        This func only consider normal samples
        '''
        # Select only normal samples
        all_labels = np.array(all_labels)
        # print(f'\nall_labels: {all_labels}')
        # print(f'all_labels.shape: {all_labels.shape}')
        # print(f'type(all_labels): {type(all_labels)}')
        # print(f'type(all_labels[0]): {type(all_labels[0])}')
        # print(f'all_labels[0].shape: {all_labels[0].shape}')
        normal_indices = np.where(all_labels[0]==0)[0] # label 값이 0인 인덱스 추출
        # print(f'\nnormal_indices: {normal_indices}')
        # print(f'normal_indices.shape: {normal_indices.shape}')
        
        class_pred = [np.array([]) for _ in range(self.args.total_heads)]
        for outputs in all_outputs:
            for i in range(self.args.total_heads):
                if i == 0:
                    pred_value = -1 * outputs[i].data.cpu().numpy()
                else:
                    pred_value = outputs[i].data.cpu().numpy()
                class_pred[i] = np.append(class_pred[i], pred_value)
        total_pred = class_pred[0]
        for i in range(1, self.args.total_heads):
            total_pred = total_pred + class_pred[i]
        total_pred = np.array(total_pred)
        # print(f'\ntotal_pred: {total_pred}')
        # print(f'total_pred.shape: {total_pred.shape}')
        # Extract pred_values only from normal samples
        anomaly_socres_normal_samples = np.take(total_pred, normal_indices)
        # print(f'\nanomaly_socres_normal_samples: {anomaly_socres_normal_samples}')
        # print(f'anomaly_socres_normal_samples.shape: {anomaly_socres_normal_samples.shape}')
        mean = np.mean(anomaly_socres_normal_samples)
        std = np.std(anomaly_socres_normal_samples)
        # print(f'\n(mean, std): {(mean, std)}')
        return (mean, std)
        
        # # Compute anomaly_score for each sample
        # anomaly_socres = []
        # for output in outputs:
        #     anomaly_socres.append(self.get_anomaly_score(output))
        # anomaly_socres = np.array(anomaly_socres)
        # anomaly_socres_normal_samples = np.take(anomaly_socres, normal_indices)
        # # print(f'labels.shape: {labels.shape}')
        # # Compute mean & stdev
        

    def get_anomaly_score(self, output: list) -> float:
        scores = []
        for i in range(self.args.total_heads):
            pred_value = -1.0*output[i].cpu() if i==0 else output[i].cpu()
            scores.append(pred_value)
        anomaly_score = sum(scores)
        return anomaly_score
        

    def eval(self):
        self.model.eval()
        test_loss = 0.0
        class_pred = [np.array([]) for _ in range(self.args.total_heads)]
        tbar = tqdm(self.test_loader, desc='\r')
        for i, sample in enumerate(tbar):
            image, label = sample['image'], sample['label']
            if self.args.cuda:
                image, label = image.cuda(), label.cuda()
            if self.args.total_heads == 4:
                try:
                    ref_image = next(self.ref)['image']
                except StopIteration:
                    self.ref = iter(self.ref_loader)
                    ref_image = next(self.ref)['image']
                ref_image = ref_image.cuda()
                image = torch.cat([ref_image, image], dim=0)
            with torch.no_grad():
                outputs = self.model(image, label)
                labels = self.generate_labels(label, eval=True)
                losses = []
                for i in range(self.args.total_heads):
                    if self.args.criterion == 'CE':
                        prob = F.softmax(outputs[i], dim=1)
                        losses.append(self.criterion(prob, labels[i].long()))
                    else:
                        losses.append(self.criterion(outputs[i], labels[i].float()))
                loss = losses[0]
                for i in range(1, self.args.total_heads):
                    loss += losses[i]
            test_loss += loss.item()
            tbar.set_description('Test loss: %.3f' % (test_loss / (i + 1)))
            for i in range(self.args.total_heads):
                if i == 0:
                    pred_value = -1 * outputs[i].data.cpu().numpy()
                else:
                    pred_value = outputs[i].data.cpu().numpy()
                class_pred[i] = np.append(class_pred[i], pred_value)
            total_labels = np.array([])
            total_labels = np.append(total_labels, label.cpu().numpy())

        total_pred = self.normalization(class_pred[0])
        for i in range(1, self.args.total_heads):
            total_pred = total_pred + self.normalization(class_pred[i])

        with open(self.args.experiment_dir + '/result.txt', mode='a+', encoding="utf-8") as w:
            for label, score in zip(total_labels, total_pred):
                w.write(str(label) + '   ' + str(score) + "\n")

        total_roc, total_pr = aucPerformance(labels=total_labels, predicts=total_pred)
        print(f'(total_label, total_pred): {list(zip(total_labels, total_pred))}')

        normal_mask = total_labels == 0
        outlier_mask = total_labels == 1
        plt.clf()
        plt.bar(
            np.arange(total_pred.size)[normal_mask], 
            total_pred[normal_mask], 
            color='green'
        )
        plt.bar(
            np.arange(total_pred.size)[outlier_mask], 
            total_pred[outlier_mask], 
            color='red'
        )
        plt.ylabel("Anomaly score")
        plt.savefig(args.experiment_dir + "/vis.png")
        return total_roc, total_pr

    def save_weights(self, filename):
        torch.save(self.model.state_dict(), os.path.join(args.experiment_dir, filename))

    def load_weights(self, filename):
        path = os.path.join(WEIGHT_DIR, filename)
        self.model.load_state_dict(torch.load(path))

    def init_network_weights_from_pretraining(self):

        net_dict = self.model.state_dict()
        ae_net_dict = self.ae_model.state_dict()

        ae_net_dict = {k: v for k, v in ae_net_dict.items() if k in net_dict}
        net_dict.update(ae_net_dict)
        self.model.load_state_dict(net_dict)


def aucPerformance(labels, predicts, prt=True):
    roc_auc = roc_auc_score(y_true=labels, y_score=predicts)
    ap = average_precision_score(y_true=labels, y_score=predicts)
    if prt:
        print(f"ROC-AUC: {roc_auc:.4f}, AVE_PRECISION: {ap:.4f}")
    return roc_auc, ap


if __name__ == '__main__':
    args = arg_parser()
    trainer = Trainer(args)
    argsDict = args.__dict__
    if not os.path.exists(args.experiment_dir):
        os.makedirs(args.experiment_dir)
    with open(args.experiment_dir + '/config.tsv', 'w') as f:
        for eachArg, value in argsDict.items():
            f.writelines(f'{eachArg}\t{value}\n')
            # f.writelines(eachArg + ' : ' + str(value) + '\n')
        
    print('Total Epoches:', trainer.args.epochs)
    trainer.model = trainer.model.to('cuda')
    trainer.criterion = trainer.criterion.to('cuda')
    # for epoch in range(0, trainer.args.epochs):
    #     trainer.training(epoch)
    trainer.training()
    # trainer.eval()
    trainer.save_weights(args.savename)

