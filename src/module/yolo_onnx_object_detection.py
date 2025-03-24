import logging
from typing import List, Tuple
from matplotlib import pyplot as plt
import numpy as np
import onnxruntime as onnx
from PIL import Image
from io import BytesIO

import torch

from entity import BoundingBox

from ultralytics.models.yolo.detect import DetectionPredictor
from ultralytics.utils import ops

from .yolo_object_detection import YoloObjectDetection

class YoloOnnxObjectDetection(YoloObjectDetection):
    def __init__(self, model_path: str,):
        logging.info('Testing model')
        self.img_processor: DetectionPredictor = super()._load_model(model_path).predictor

        self.EPs = onnx.get_available_providers()
        self.model = self._load_model(model_path)

        logging.info(f'Current Device: {self.model.get_providers()}')

    def _load_model(self, path: str) -> onnx.InferenceSession:
        logging.info('Loading model to ONNX runtime')

        session = onnx.InferenceSession(path, providers=self.EPs)

        logging.info('Model Loaded...')

        return session

    def preprocess(self, input) -> np.ndarray:
        ori_img = super().preprocess(input)
        processed_img = self.img_processor.preprocess([ ori_img ]).numpy()

        return processed_img, ori_img

    def inference(self, source) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        preprocess_img, _ = source

        input_name = self.model.get_inputs()[0].name
        output_name = self.model.get_outputs()[0].name

        # Run inference
        result = self.model.run([output_name], {input_name: preprocess_img})

        return result[0], *source

    def postprocess(self, input) -> List[dict]:
        preds, preprocess_img, ori_img = input
        tensor_pred = torch.from_numpy(preds)
        results = ops.non_max_suppression(
            tensor_pred, 
            iou_thres=0.7
        )

        boxes = self.img_processor.construct_results(results, preprocess_img, [ ori_img ])[0]

        return super().postprocess(boxes)
