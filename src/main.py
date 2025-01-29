import redis
from common import ENV

from module import (
    RedisConnector, 
    ObjectDetection, 
    LegoDetector, 
    RedisJobHandler
)

if __name__ == '__main__':
    model_path = './model/yolov8n.pt'
    redis_connector = RedisConnector(
        ENV.REDIS_HOST,
        ENV.REDIS_PORT,
        ENV.REDIS_USER,
        ENV.REDIS_PWD,
    )

    redis_client = redis_connector.get_client()

    queue = RedisJobHandler(store=redis_client)
    model = ObjectDetection(model_path)

    dl_runner = LegoDetector(model, queue)

    dl_runner.run()
