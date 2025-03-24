import sys
import logging
import logging.config
import threading
import time
from common.config import ENV

from module import (
    YoloOnnxObjectDetection, 
    YoloObjectDetection,
    LegoDetector, 
    RabbitMQConnector,
    RabbitMQJobHandler, 
)

if __name__ == '__main__':
    # Log setting
    try:
        sys.tracebacklimit = 0

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # MQ setup
        connector = RabbitMQConnector(
            ENV.MQ_HOST,
            ENV.MQ_PORT,
            ENV.MQ_USER,
            ENV.MQ_PWD,
        )

        jobHandler = RabbitMQJobHandler(connector)

        # DL setup
        model_path = './model/yolov8n.pt'
        model = YoloObjectDetection(model_path)

        dl_runner = LegoDetector(model, jobHandler)

        dl_runner.run()
    except Exception as err:
        ## some notification service here ##

        ###################################

        logging.fatal(err)
        raise err
    except KeyboardInterrupt:
        logging.info('end')
    finally:
        connector.close()
