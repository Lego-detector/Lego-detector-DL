import queue
import threading
import logging
from entity import InferenceResponse, Job
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
        try:
            halt_event = threading.Event()
            jobChan = queue.Queue()
            responseChan = queue.Queue()
            workers = self.__run_mq_worker(halt_event, jobChan, responseChan)

            # run object detection on main thread
            self.__inference_worker(jobChan, responseChan, halt_event)

        except KeyboardInterrupt as err:
            halt_event.set()  # send halt signal

            for worker in workers:
                worker.join()

        finally:
            logging.info('Exiting process.')

    def __job_handler_worker(
        self, 
        jobChan: queue.Queue, 
        halt_event: threading.Event
    ):
        while (not halt_event.is_set()):
            if (jobChan.full()):
                continue

            job = self.job_handler.get_job()

            if (job is None):
                continue

            jobChan.put(job)

    def __inference_worker(
        self, 
        jobChan: queue.Queue, 
        responseChan: queue.Queue, 
        halt_event: threading.Event
    ):
        while (not halt_event.is_set() or not jobChan.empty()):
            try:
                job: Job = jobChan.get(timeout=1)
            except queue.Empty:
                continue 

            if (job is None):
                continue

            preprocess_img = self.object_dectection.preprocess(job.image)
            output = self.object_dectection.inference(preprocess_img)
            results = self.object_dectection.postprocess(output)

            response = InferenceResponse(
                uid=job.uid,
                results=results,
                delivery_tag=job.delivery_tag
            )

            responseChan.put(response)

    def __mark_done_worker(
        self, 
        responseChan: queue.Queue, 
        halt_event: threading.Event
    ):
        while (not halt_event.is_set() or not responseChan.empty()):
            try:
                response: InferenceResponse = responseChan.get(timeout=1)
            except queue.Empty:
                continue 

            if (response is None):
                continue

            self.job_handler.mark_job_as_done(response)
            logging.info(f'mark done (uid: {response.uid}, tag: {response.delivery_tag})')

    def __run_mq_worker(self, halt_event, jobChan: threading.Event, responseChan: threading.Event):
        workers = []
        tasks = [
            {'worker': self.__job_handler_worker, 'args': (jobChan, )},
            {'worker': self.__mark_done_worker, 'args': (responseChan, )}
        ]

        for t in tasks:
            worker = threading.Thread(target=t.get('worker'), args=(*t.get('args'), halt_event))
            workers.append(worker)
            worker.start()

        return workers