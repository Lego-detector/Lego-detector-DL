import redis
from redis.client import Redis
from redis.retry import Retry
from redis.exceptions import (
    ConnectionError, 
    TimeoutError, 
)
from redis.backoff import ConstantBackoff
import logging

############################################


############################################

class RedisConnector():
    _instance = None
    __redis_client: Redis = None

    def __new__(cls, host, port, user, pwd, max_connections=None):
        if cls._instance is not None:
            logging.info('Has already connect to redis stack')

            return cls._instance

        cls._instance = super().__new__(cls)
        cls._instance.__connect(host, port, user, pwd, max_connections)

        return cls._instance
    
    def get_client(self) -> Redis:
        return self.__redis_client

    def __connect(self, host, port, user, pwd, max_connections=None) -> Redis:
        pool = redis.ConnectionPool(
            host=host,
            port=port,
            # username=user,  # Replace with your Redis username
            # password=pwd,  # Replace with your Redis password
            decode_responses=True,     # Automatically decode strings from bytes
            max_connections=max_connections,         # Optional: Max connections in the pool
        )
    
        self.__redis_client = redis.StrictRedis(
            db=0,
            connection_pool=pool,
            retry_on_timeout=True, 
            health_check_interval=10,
            retry=Retry(ConstantBackoff(10), -1),
            retry_on_error=[
                ConnectionError, TimeoutError
            ],
        )

        logging.info(f"Redis store connected")
        
        return self.__redis_client
