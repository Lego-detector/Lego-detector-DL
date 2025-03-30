class BoundingBox():
    UNKNOWN_CLASS = 0

    def __init__(self, class_id: int, conf: float, xywh):
        self.class_id = class_id

        if (0.4 <= conf < 0.5):
            self.conf = self.UNKNOWN_CLASS
        else:
            self.conf = conf

        self.xywh = xywh

    def to_dict(self) -> tuple:
        return {
            "classId": self.class_id,
            "conf": self.conf,
            "xywh": self.xywh
        }

        