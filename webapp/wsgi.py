from app import create_app
import logging

application = create_app()


logging.basicConfig(format='%(levelname)s:%(filename)s:%(lineno)d %(message)s', level=logging.DEBUG)
