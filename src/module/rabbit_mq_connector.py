import functools
import logging
import threading
import time
import pika
from pika.channel import Channel

from common.constant import QueueName

class RabbitMQConnector():
    _instance = None
    __connection: pika.SelectConnection = None
    __channel: Channel = None
    __ready_event = threading.Event()

    def __new__(cls, host, port, user, pwd):
        if (cls._instance is not None):
            logging.info('Has already connect to redis stack')

            return cls._instance

        cls._instance = super().__new__(cls)
        cls._instance.__connect(host, port, user, pwd)

        while(not cls._instance.__ready_event.wait(1)): pass

        return cls._instance
    
    def get_channel(self) -> Channel:
        return self.__channel
    
    def get_connection(self) -> pika.SelectConnection:
        return self.__connection
    
    def close(self):
        try:
            if self.__channel and self.__channel.is_open:
                self.__channel.close()

            if self.__connection:
                if self.__connection.is_open:
                    self.__connection.close()
                
                if self.__connection.ioloop.is_running():
                    self.__connection.ioloop.stop() 

            logging.info("RabbitMQ connection closed successfully.")

        except pika.exceptions.ConnectionWrongStateError:
            logging.warning("Connection already closed. No action needed.")
        
        except Exception as e:
            logging.error(f"Error while closing RabbitMQ connection: {e}")

    def __connect(self, host, port, user, pwd) -> pika.SelectConnection:
        def start_ioloop():
            reconnect_attempts = 1

            while (True):
                try:
                    logging.info(f"Connecting to RabbitMQ (Attempt {reconnect_attempts})...")
                    self.__connection = pika.SelectConnection(
                        pika.ConnectionParameters(
                            host,
                            port,
                            credentials=pika.PlainCredentials(user, pwd),
                        ),
                        on_open_callback=self.__on_connection_open,
                        on_close_callback=functools.partial(self.__on_connection_closed, host, port, user, pwd)
                    )

                    logging.info("RabbitMQ connection established. Starting event loop...")
                    self.__connection.ioloop.start()
                    break  # Exit loop when connected successfully

                except pika.exceptions.AMQPConnectionError as e:
                    reconnect_attempts += 1
                    wait_time = min(2 ** reconnect_attempts, 60)

                    logging.error(f"RabbitMQ connection failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        thread = threading.Thread(target=start_ioloop, daemon=True)
        thread.start()

    def __on_connection_open(cls, connection: pika.SelectConnection):
        cls._instance.__connection = connection
        cls._instance.__connection.channel(
            on_open_callback=cls._instance.__on_channel_open
        )

    def __on_channel_open(cls, channel: Channel):
        cls._instance.__channel = channel

        cls._instance.__channel.queue_declare(
            queue=QueueName.INFERENCE_SESSION, 
            durable=True, 
        )

        cls._instance.__channel.queue_declare(
            queue=QueueName.INFERENCE_RESPONSE, 
            durable=True, 
        )

        cls.__ready_event.set()

    def __on_connection_closed(
        cls, 
        host, 
        port, 
        user, 
        pwd, 
        connection: pika.SelectConnection, 
        reason
    ):
        logging.warning(f"RabbitMQ connection lost: {reason}. Reconnecting...")
        cls._instance.__connect(host, port, user, pwd)