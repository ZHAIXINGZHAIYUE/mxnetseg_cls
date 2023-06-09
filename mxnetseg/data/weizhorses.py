# coding=utf-8

import os
from PIL import Image
from gluoncv.data.segbase import SegmentationDataset
from mxnetseg.utils import DATASETS, dataset_dir


@DATASETS.add_component
class WeizmannHorses(SegmentationDataset):
    """
    Weizmann horses for binary segmentation.
    Reference:
        E. Borenstein and S. Ullman. Class-specific, top-down segmentation.
    """

    NUM_CLASS = 2

    def __init__(self, root=None, split='train', mode=None, transform=None, **kwargs):
        root = root if root is not None else os.path.join(dataset_dir(), 'WeizHorses')
        super(WeizmannHorses, self).__init__(root, split, mode, transform, **kwargs)
        _img_dir = os.path.join(root, 'horse')
        _mask_dir = os.path.join(root, 'mask')
        if split == 'train':
            _split_f = os.path.join(root, 'train.txt')
        elif split == 'val':
            _split_f = os.path.join(root, 'val.txt')
        else:
            raise RuntimeError(f'Unknown dataset split: {split}')

        self.images = []
        self.masks = []
        with open(_split_f, 'r') as lines:
            for line in lines:
                _img = os.path.join(_img_dir, line.strip())
                assert os.path.isfile(_img)
                self.images.append(_img)
                _mask = os.path.join(_mask_dir, line.strip())
                assert os.path.isfile(_mask)
                self.masks.append(_mask)
        assert len(self.images) == len(self.masks)

    def __getitem__(self, item):
        img = Image.open(self.images[item]).convert('RGB')
        if self.mode == 'test':
            img = self._img_transform(img)
            if self.transform is not None:
                img = self.transform(img)
            return img, os.path.basename(self.images[item])
        mask = Image.open(self.masks[item])
        if self.mode == 'train':
            img, mask = self._sync_transform(img, mask)
        elif self.mode == 'val':
            img, mask = self._val_sync_transform(img, mask)
        else:
            assert self.mode == 'testval'
            img, mask = self._img_transform(img), self._mask_transform(mask)
        if self.transform is not None:
            img = self.transform(img)
        return img, mask

    @property
    def classes(self):
        return 'background', 'horse'

    def __len__(self):
        return len(self.images)
