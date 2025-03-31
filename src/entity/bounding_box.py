class BoundingBox():
    UNKNOWN_CLASS = 136

    def __init__(self, class_id: int, conf: float, xywh):
        if (conf < 0.5):
            self.class_id = self.UNKNOWN_CLASS
        else:
            self.class_id = class_id

        self.conf = conf
        self.xywh = xywh

    def to_dict(self) -> tuple:
        return {
            "classId": self.class_id,
            "conf": self.conf,
            "xywh": self.xywh
        }

        