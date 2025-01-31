from typing import List, Any


class BoundingBox():
    def __init__(self, class_name: int, conf: float, xywh: List[Any]):
        self.class_name = class_name
        self.conf = conf
        self.xywh = xywh

    def to_tuple(self) -> tuple:
        return (
            self.class_name,
            self.conf,
            self.xywh
        )

        