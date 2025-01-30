import redis
from common.config import ENV
import asyncio

from module import (
    ObjectDetection, 
    LegoDetector, 
    RabbitMQConnector,
    RabbitMQJobHandler, 
)

if __name__ == '__main__':
    model_path = './model/yolov8n.pt'
    connector = RabbitMQConnector(
        ENV.MQ_HOST,
        ENV.MQ_PORT,
        ENV.MQ_USER,
        ENV.MQ_PWD,
    )

    client = connector.get_client()

    queue = RabbitMQJobHandler(channel=client)
    model = ObjectDetection(model_path)

    dl_runner = LegoDetector(model, queue)

    dl_runner.run()
