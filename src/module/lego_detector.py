import time
from entity import InferenceResponse
from .adapter import AbstractJobHandler, AbstractObjectDetection


class LegoDetector():
    def __init__(
        self,
        object_dectection: AbstractObjectDetection,
        job_handler: AbstractJobHandler,
    ):
        self.object_dectection = object_dectection
        self.job_handler = job_handler

    def run(self):
        while (True):
            job = self.job_handler.get_job()

            if job is None:
                continue

            preprocess_img = self.object_dectection.preprocess(job.image)
            output = self.object_dectection.inference(preprocess_img)
            results = self.object_dectection.postprocess(output)
            
            response = InferenceResponse(
                uid=job.uid,
                results=results
            )

            self.job_handler.mark_job_as_done(response)
