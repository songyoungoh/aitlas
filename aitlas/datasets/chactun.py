import csv
import os
import numpy as np

from ..base import BaseDataset
from ..utils import image_loader, image_invert
from .schemas import SegmentationDatasetSchema


#Aguada
#Building
#Platform

CLASSES_TO_IDX = {"Aguada": 0, "Building": 1, "Platform": 2}

class ChactunDataset(BaseDataset):

    schema = SegmentationDatasetSchema

    def __init__(self, config):
        # now call the constructor to validate the schema and split the data
        BaseDataset.__init__(self, config)
        self.images = []
        self.masks = []
        self.class_values = []

        self.load_dataset(self.config.root)

    def __getitem__(self, index):
        image = image_loader(self.images[index])

        mask = np.zeros(shape=(len(self.masks[index]), image.shape[0], image.shape[1]), dtype=np.float)
        for i, path in enumerate(self.masks[index]):
            mask[i] = image_invert(path, True)

        image, mask = self.transform({"image": image, "mask": mask})
        return image, mask

    def __len__(self):
        return len(self.images)

    def load_dataset(self, root_dir):
        self.class_values = CLASSES_TO_IDX.values()

        if not self.class_values:
            raise ValueError(
                "You need to implement the classes to index mapping for the dataset"
            )

        masks_for_image = []
        for root, _, fnames in sorted(os.walk(root_dir)):
            for i, fname in enumerate(sorted(fnames)):
                path = os.path.join(root_dir, fname)
                if i % 4 == 0:
                    self.images.append(path)
                    masks_for_image = []
                else:
                    masks_for_image.append(path)
                    if i % 4 == 3:
                        self.masks.append(masks_for_image)

    def labels(self):
        return list(CLASSES_TO_IDX.keys())

