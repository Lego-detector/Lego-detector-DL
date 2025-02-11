from io import BytesIO
import logging
from typing import List
from PIL import Image
import torch

from ultralytics import YOLO
from ultralytics.engine.results import Results

from entity import BoundingBox

from .adapter import AbstractObjectDetection


class ObjectDetection(AbstractObjectDetection):
    def __init__(self, model_path: str):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self._load_model(model_path)
        self.model.to(self.device)
        logging.info(f'Current Device: {self.model.device.__str__()}')

    def _load_model(self, path):
        logging.info('Loading model from pt file ...')

        model = YOLO(path)

        logging.info('Model Loaded ...')

        logging.info('Fusing model ...')

        model.fuse()

        logging.info('Loading model process complete')

        return model

    def preprocess(self, inp) -> Image:
        img_io = BytesIO(inp)

        img = Image.open(img_io)

        return img

    def inference(self, source) -> Results:
        return self.model.predict(
            source,
            stream=False,
            iou=0.7
        )[0]


    def postprocess(self, inp: Results):
        results = []
        for box in inp.boxes:
            bbox = BoundingBox(
                int(box.cls),
                float(box.conf),
                box.xywh.tolist()
            ).to_tuple()

            results.append(bbox)
            
        return results
