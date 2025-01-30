import json
from entity import Job, InferenceResponse
from .adapter import AbstractJobHandler
from common.config import ENV
from pika.adapters.blocking_connection import BlockingChannel
from collections import deque 


class RabbitMQJobHandler(AbstractJobHandler):
    inmemory_queue = deque()
    __queue_name = 'imgdata'

    def __init__(self, channel: BlockingChannel):
        self.__channel = channel
        self.__queue = self.__channel.consume(self.__queue_name)

    async def get_job(self) -> Job:
        try:
            # declare if need
            await self.__channel.queue_declare(self.__queue_name)

            deliver_info, _, msg = await self.__queue.__next__()

            if msg is None:
                return None

            val = json.loads(msg)
            uid = val['uid']
            image = val['image'].encode("latin1")

            return Job(uid, image, deliver_info.delivery_tag)
        except:
            return

    def mark_job_as_done(self, job_result: InferenceResponse):
        response = json.dumps({
                "uid": job_result.uid,
                "status": job_result.status,
                "results": job_result.results
            })
        
        try:
            
            self.__channel.queue_declare('inferrence_response')
            self.__channel.basic_publish(
                '',
                'inferrence_response',
                response
            )

            self.__channel.basic_ack(job_result.delivery_tag)

        except Exception as err:
            self.inmemory_queue.append(response)
            return
    
    # def push_inmemory_to_mq():
    #     self.__channel.queue_declare('inferrence_response')