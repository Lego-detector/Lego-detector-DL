import functools
import json
import logging
import time

import pika
from common.constant import QueueName
from entity import Job, InferenceResponse
from .adapter import AbstractJobHandler
from common.config import ENV
from pika.adapters.blocking_connection import BlockingChannel


class RabbitMQJobHandler(AbstractJobHandler):
    def __init__(self, channel: BlockingChannel, connection: pika.BlockingConnection):
        self.__channel = channel
        self.__connection = connection

        self.__queue = self.__channel.consume(queue=QueueName.INFERENCE_SESSION, inactivity_timeout=1)   

    def get_job(self) -> Job:
        try:
            # declare if need
            self.__channel.queue_declare(queue=QueueName.INFERENCE_SESSION, durable=True)
            
            try:
                deliver_info, _, msg = self.__queue.__next__()
            except IndexError:
                return

            if (msg is None):
                return None

            val: dict = json.loads(msg)
            uid = val.get('uid')
            image = val.get('image').encode('latin-1')

            return Job(uid, image, deliver_info.delivery_tag)
        except Exception as err:
            print('job hanlder', err)
            time.sleep(3)
            return

    def mark_job_as_done(self, job_result: InferenceResponse):
        response = json.dumps({
                'uid': job_result.uid,
                'status': job_result.status,
                'results': job_result.results
            })
        
        try:
            self.__channel.queue_declare(queue=QueueName.INFERENCE_RESPONSE, durable=True)

            cb = functools.partial(
                self.__callback_publish, 
                self.__channel, 
                response, 
                job_result
            )
            
            self.__connection.add_callback_threadsafe(cb)

        except Exception as err:
            print('job markdone', err)
            time.sleep(3)
            return
        
    def __callback_publish(self, ch, response, job):
        self.__channel.basic_publish(
                exchange='',
                routing_key=QueueName.INFERENCE_RESPONSE,
                body=response,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )

        self.__channel.basic_ack(job.delivery_tag)