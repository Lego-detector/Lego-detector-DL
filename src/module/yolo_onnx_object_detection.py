import logging
from typing import List
from matplotlib import pyplot as plt
import torchvision
from module.adapter import AbstractObjectDetection
import numpy as np
import onnxruntime as onnx
from PIL import Image, ImageFile
from io import BytesIO

import torch

from entity import BoundingBox


class YoloOnnxObjectDetection(AbstractObjectDetection):
    def __init__(self, model_path: str,):
        logging.info('Testing model')
        self.img_size = 640
        self.EPs = onnx.get_available_providers()
        self.model = self._load_model(model_path)

        logging.info(f'Current Device: {self.model.get_providers()}')

    def _load_model(self, path: str) -> onnx.InferenceSession:
        logging.info('Loading model to ONNX runtime')

        session = onnx.InferenceSession(path, providers=self.EPs)

        logging.info('Model Loaded...')

        return session

    def preprocess(self, input) -> np.ndarray:
        img_io = BytesIO(input)
        img = Image.open(img_io)
        img = self.__letterbox_image(img)
        
        img_array = np.array(img, dtype=np.float32) / 255.0
        img.close()

        im = np.stack([ img_array ])
        im = im.transpose((0, 3, 1, 2))  # BGR to RGB, BHWC to BCHW, (n, 3, h, w)
        im = np.ascontiguousarray(im)  # contiguous

        return im

    def inference(self, source) -> np.ndarray:
        input_name = self.model.get_inputs()[0].name

        # Run inference
        result = self.model.run(None, {input_name: source})

        return torch.from_numpy(result[0])

    def postprocess(self, input: torch.Tensor) -> List[dict]:
        results = []
        tensor = input.squeeze(0)  # Now it's (300, 6)

        conf = tensor[:, 4] #(300, )
        bboxes = tensor[:, :4]  # Shape: (300, 4)
        xywhn = self.__xxyy_to_xywhn(bboxes)

        sel_indices = torchvision.ops.nms(bboxes, conf, 0.4)

        for index in sel_indices:
            box = tensor[int(index)]

            if (box[4] < 0.4):
                continue


            bbox = BoundingBox(
                class_id=int(box[5]),
                conf=float(box[4]),
                xywh=xywhn[index].tolist()
            ).to_dict()

            results.append(bbox)

        return results
    
    def __xxyy_to_xywhn(self, xxyy: torch.Tensor) -> torch.Tensor:
        x1, y1, x2, y2 = xxyy[:, 0], xxyy[:, 1], xxyy[:, 2], xxyy[:, 3]
        xc = ((x1 + x2) / 2) / self.img_size  # Normalize xc
        yc = ((y1 + y2) / 2) / self.img_size  # Normalize yc
        w = (x2 - x1) / self.img_size  # Normalize w
        h = (y2 - y1) / self.img_size  # Normalize h

        return torch.stack([xc, yc, w, h], dim=1)
    
    def __letterbox_image(self, image: ImageFile):
        iw, ih = image.size
        w = h = self.img_size
        scale = min(w/iw, h/ih)
        nw = int(iw*scale)
        nh = int(ih*scale)

        image = image.resize((nw, nh), Image.BICUBIC)
        new_image = Image.new('RGB', (w, h))
        new_image.paste(image, ((w - nw)//2, (h - nh)//2))
    
        return new_image
