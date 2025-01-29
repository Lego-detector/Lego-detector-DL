import json
from redis import Redis

from entity import Job, InferenceResponse, InferenceStatus
from .adapter import AbstractJobHandler
from common import ENV

class RedisJobHandler(AbstractJobHandler):
    __queue = ['imgdata']

    def __init__(self, store: Redis):
        self.__store: Redis = store
    
    def get_job(self) -> Job:
        try:
            timeout = 3 if ENV.DEBUG_MODE else None
            job = self.__store.blpop(self.__queue, timeout=timeout)
            
            if job is None:
                return None
            
            _, val = job
            val = json.loads(val)
            uid = val['uid']
            image = bytes.fromhex(val['image'])

            return Job(uid, image)
        except Exception as err:
            return 
    
    def mark_job_as_done(self, job_result: InferenceResponse):
        try:
            print(job_result.results)
            self.__store.set(
                f'inferrence:{job_result.uid}',
                json.dumps({
                    "status": InferenceStatus.COMPLETED,
                    "results": job_result.results
                })
            )
        except Exception as err:
            return