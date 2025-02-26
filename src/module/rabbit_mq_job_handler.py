import json
import logging
import threading

from collections.abc import Callable

import pika
from common.constant import QueueName
from entity import Job, InferenceResponse
from .adapter import AbstractJobHandler
from common.config import ENV
from pika.channel import Channel


class RabbitMQJobHandler(AbstractJobHandler):
    def __init__(self, channel: Channel, connection: pika.SelectConnection):
        self.__connection = connection
        self.__channel: Channel = channel
        self.__get_job_callback = None
        self.__is_callback_ready = threading.Event()

        self.__setup_consumer()

    def register_job_callback(self, callback: Callable[[Job], None]):
        self.__get_job_callback = callback
        self.__is_callback_ready.set()

    def mark_job_as_done(self, job_result: InferenceResponse) -> bool:
        success_flag = threading.Event()
        response = json.dumps({
                'uid': job_result.uid,
                'status': job_result.status,
                'results': job_result.results
            })
        
        def publish_callback():
            try:
                if self.__channel and not self.__channel.is_closed:
                    self.__channel.basic_publish(
                        exchange="",
                        routing_key=QueueName.INFERENCE_RESPONSE,
                        body=response,
                        properties=pika.BasicProperties(delivery_mode=2),
                    )
                    self.__channel.basic_ack(job_result.delivery_tag)
                    success_flag.set()
                else:
                    success_flag.clear()
                    logging.error("Channel is closed. Cannot publish message.")
            except Exception as err:
                logging.error(f"Failed to mark job as done for Job._id: {job_result.uid}, Error: {err}")

        self.__connection.ioloop.call_later(0, publish_callback)
        success_flag.wait()
        
        return success_flag.is_set()
        
    def __setup_consumer(self):
        if not self.__channel or self.__channel.is_closed:
            logging.error("Channel is not available!")
            return

        self.__channel.queue_declare(queue=QueueName.INFERENCE_SESSION, durable=True)
        self.__channel.queue_declare(queue=QueueName.INFERENCE_RESPONSE, durable=True)

        self.__channel.basic_consume(
            queue=QueueName.INFERENCE_SESSION,
            on_message_callback=self.__get_job,
            auto_ack=False,
        )

    def __get_job(self, ch: Channel, method, properties, body) -> None:
        try:
            # declare if need
            self.__channel.queue_declare(queue=QueueName.INFERENCE_SESSION, durable=True)

            val: dict = json.loads(body)
            uid = val.get('uid')
            image = val.get('image').encode('latin-1')
            job = Job(uid, image, method.delivery_tag)

            self.__is_callback_ready.wait()

            if (self.__get_job_callback):
                self.__get_job_callback(job)

        except Exception as err:
            logging.error(f"Error processing job: {err}")
            ch.basic_nack(method.delivery_tag, requeue=True)