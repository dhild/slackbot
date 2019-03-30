from app import create_app
import os
import logging

application = create_app()

log_level = logging.ERROR
if "LOG_LEVEL" in os.environ:
    log_level = os.environ["LOG_LEVEL"]

logging.basicConfig(format='%(levelname)s:%(filename)s:%(lineno)d %(message)s', level=log_level)
