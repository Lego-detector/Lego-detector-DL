import json
import logging
import uuid
import pika
from pika.adapters.blocking_connection import BlockingChannel

class RabbitMQConnector():
    _instance = None
    __client: BlockingChannel = None

    def __new__(cls, host, port, user, pwd):
        if cls._instance is not None:
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

    def __connect(self, host, port, user, pwd) -> BlockingChannel:
        config = pika.ConnectionParameters(
            host=host, 
            port=port,
            credentials=pika.PlainCredentials(user, pwd)
        )

        connection = pika.BlockingConnection(config)
        
        chan = connection.channel()

        chan.queue_declare('imgdata')

        for i in range(3):
            with open(f"./test_image/{i}.jpg", "rb") as img_file:
                img_str = img_file.read().decode("latin1")
                chan.basic_publish(
                    '',
                    routing_key='imgdata',
                    body=json.dumps({
                        "uid": uuid.uuid4().hex,
                        "image": img_str
                    }),
                )

        return chan
