import logging
import logging.config
from common.config import ENV

from module import (
    ObjectDetection, 
    LegoDetector, 
    RabbitMQConnector,
    RabbitMQJobHandler, 
)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    model_path = './model/yolov8n.pt'
    connector = RabbitMQConnector(
        ENV.MQ_HOST,
        ENV.MQ_PORT,
        ENV.MQ_USER,
        ENV.MQ_PWD,
    )

    mq_chan = connector.get_channel()
    mq_conn = connector.get_connection()

    queue = RabbitMQJobHandler(channel=mq_chan, connection=mq_conn)
    model = ObjectDetection(model_path)

    dl_runner = LegoDetector(model, queue)

    try:
        dl_runner.run()
    except Exception as err:
        ## some notification service here ##

        ###################################

        logging.fatal(err)
    finally:
        connector.close()
