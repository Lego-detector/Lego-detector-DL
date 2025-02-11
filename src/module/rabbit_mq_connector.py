import json
import logging
import uuid
import pika
from pika.adapters.blocking_connection import BlockingChannel

from common.constant import QueueName

class RabbitMQConnector():
    _instance = None
    __connection: pika.BlockingConnection = None
    __channel: BlockingChannel = None

    def __new__(cls, host, port, user, pwd):
        if (cls._instance is not None):
            logging.info('Has already connect to redis stack')

            return cls._instance

        cls._instance = super().__new__(cls)
        cls._instance.__connection = cls._instance.__connect(
            host, 
            port, 
            user, 
            pwd
        )
        cls._instance.__channel = cls._instance.__connection.channel()

        return cls._instance
    
    def get_channel(self) -> BlockingChannel:
        return self.__channel
    
    def get_connection(self) -> pika.BlockingConnection:
        return self.__connection
    
    def close(self):
        self.__channel.close()
        self.__connection.close()

    def __connect(self, host, port, user, pwd) -> pika.BlockingConnection:
        config = pika.ConnectionParameters(
            host=host, 
            port=port,
            credentials=pika.PlainCredentials(user, pwd)
        )

        connection = pika.BlockingConnection(config)
        
        chan = connection.channel()

        chan.queue_declare(QueueName.INFERENCE_SESSION, durable=True)
        chan.queue_declare(QueueName.INFERENCE_RESPONSE, durable=True)

        return connection
