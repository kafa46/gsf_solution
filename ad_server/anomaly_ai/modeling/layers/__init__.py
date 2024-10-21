import torch
from anomaly_ai.modeling.layers.deviation_loss import DeviationLoss
from anomaly_ai.modeling.layers.binary_focal_loss import BinaryFocalLoss

def build_criterion(criterion):
    if criterion == "deviation":
        print("Loss : Deviation")
        return DeviationLoss()
    elif criterion == "BCE":
        print("Loss : Binary Cross Entropy")
        return torch.nn.BCEWithLogitsLoss()
    elif criterion == "focal":
        print("Loss : Focal")
        return BinaryFocalLoss()
    elif criterion == "CE":
        print("Loss : CE")
        return torch.nn.CrossEntropyLoss()
    else:
        raise NotImplementedError