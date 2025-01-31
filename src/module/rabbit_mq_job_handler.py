import json
import logging
from common.constant import QueueName
from entity import Job, InferenceResponse
from .adapter import AbstractJobHandler
from common.config import ENV
from pika.adapters.blocking_connection import BlockingChannel


class RabbitMQJobHandler(AbstractJobHandler):
    def __init__(self, channel: BlockingChannel):
        self.__channel = channel
        self.__queue = self.__channel.consume(QueueName.INFERENCE_SESSION, inactivity_timeout=1)     

    def get_job(self) -> Job:
        try:
            # declare if need
            self.__channel.queue_declare(QueueName.INFERENCE_SESSION)

            deliver_info, _, msg = self.__queue.__next__()

            if (msg is None):
                return None

            val: dict = json.loads(msg)
            uid = val.get('uid')
            image = val.get('image')

            return Job(uid, image, deliver_info.delivery_tag)
        except Exception as err:
            logging.error(err)
            return

    def mark_job_as_done(self, job_result: InferenceResponse):
        response = json.dumps({
                'uid': job_result.uid,
                'status': job_result.status,
                'results': job_result.results
            })
        
        try:
            self.__channel.queue_declare(QueueName.INFERENCE_RESPONSE)
            self.__channel.basic_publish(
                '',
                QueueName.INFERENCE_RESPONSE,
                response
            )

            self.__channel.basic_ack(job_result.delivery_tag)

        except Exception as err:
            logging.error(err)
            return