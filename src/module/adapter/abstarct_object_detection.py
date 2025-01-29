from abc import ABC, abstractmethod
from typing import List

from PIL import Image

from ultralytics.engine.results import Results


class AbstractObjectDetection(ABC):
    
    @abstractmethod
    def _load_model(self, path):
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, input) -> Image:
        raise NotImplementedError()

    @abstractmethod
    def inference(self, source) -> Results:
        raise NotImplementedError()

    @abstractmethod
    def postprocess(self, input):
        raise NotImplementedError()
        