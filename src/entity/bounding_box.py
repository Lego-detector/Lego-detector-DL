from typing import List, Any


class BoundingBox():
    def __init__(self, class_id: int, conf: float, xywh):
        self.class_id = class_id
        self.conf = conf
        self.xywh = xywh

    def to_dict(self) -> tuple:
        return {
            "classId": self.class_id,
            "conf": self.conf,
            "xywh": self.xywh
        }

        