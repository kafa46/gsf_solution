import torch.nn as nn
from torchvision import models
from torchvision.models.resnet import ResNet18_Weights


class FeatureRESNET18(nn.Module):
    def __init__(self):
        super(FeatureRESNET18, self).__init__()
        # self.net = models.resnet18(pretrained=True)
        # Modified code as follow due to UserWarning
        #   UserWarning: The parameter 'pretrained' is deprecated since 0.13 
        #       and may be removed in the future, please use 'weights' instead.
        #   UserWarning: Arguments other than a weight enum or `None` for 'weights' 
        #       are deprecated since 0.13 and may be removed in the future. 
        #       The current behavior is equivalent to passing
        #       `weights=ResNet18_Weights.IMAGENET1K_V1`. 
        #       You can also use `weights=ResNet18_Weights.DEFAULT` 
        #       to get the most up-to-date weights.
        self.net = models.resnet18(weights=ResNet18_Weights.DEFAULT)

    def forward(self, x):
        x = self.net.conv1(x)
        x = self.net.bn1(x)
        x = self.net.relu(x)
        x = self.net.maxpool(x)
        x = self.net.layer1(x)
        x = self.net.layer2(x)
        x = self.net.layer3(x)
        x = self.net.layer4(x)
        return x

