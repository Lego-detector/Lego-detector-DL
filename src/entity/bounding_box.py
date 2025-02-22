from typing import List, Any


class BoundingBox():
    def __init__(self, class_name: int, conf: float, xywh):
        self.class_name = class_name
        self.conf = conf
        self.xywh = xywh

    def to_dict(self) -> tuple:
        return {
            "className": self.class_name,
            "conf": self.conf,
            "xywh": self.xywh
        }

        