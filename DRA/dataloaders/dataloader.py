from torch.utils.data import DataLoader
from dataloaders.utlis import worker_init_fn_seed, BalancedBatchSampler
from datasets.mvtecad import MVTecDataset


class initDataloader():

    @staticmethod
    def build(args, **kwargs):
        if args.dataset == "mvtecad":
            train_set = MVTecDataset(args, train=True)
            test_set = MVTecDataset(args, train=False)
            
            # Create train_loader object
            train_loader = DataLoader(
                train_set,
                worker_init_fn = worker_init_fn_seed,
                batch_sampler = BalancedBatchSampler(args, train_set),
                **kwargs
            )
            
            # Create test_loader object
            test_loader = DataLoader(
                test_set,
                batch_size=args.batch_size,
                shuffle=False,
                worker_init_fn= worker_init_fn_seed,
                **kwargs
            )
            return train_loader, test_loader
        else:
            raise NotImplementedError