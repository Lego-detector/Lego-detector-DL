import json
import logging
import uuid
import pika
from pika.adapters.blocking_connection import BlockingChannel

from common.constant import QueueName

class RabbitMQConnector():
    _instance = None
    __client: BlockingChannel = None

    def __new__(cls, host, port, user, pwd):
        if (cls._instance is not None):
            logging.info('Has already connect to redis stack')

            return cls._instance

        cls._instance = super().__new__(cls)
        cls._instance.__client = cls._instance.__connect(
            host, 
            port, 
            user, 
            pwd
        )

        return cls._instance
    
    def get_client(self) -> BlockingChannel:
        return self.__client
    
    def close(self):
        self.__client.close()

    def __connect(self, host, port, user, pwd) -> BlockingChannel:
        config = pika.ConnectionParameters(
            host=host, 
            port=port,
            credentials=pika.PlainCredentials(user, pwd)
        )

        connection = pika.BlockingConnection(config)
        
        chan = connection.channel()

        chan.queue_declare(QueueName.INFERENCE_SESSION)
        chan.queue_declare(QueueName.INFERENCE_RESPONSE)

        return chan
