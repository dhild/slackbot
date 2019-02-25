from flask import Flask
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from app.config import configure_app
from app.twodegrees import TwoDegrees
import queue
import threading


def create_app(custom_config=None):
    app = Flask('slackbot')
    worker = WorkerThread()

    configure_app(app)

    if custom_config is not None:
        app.config.from_object(custom_config)

    bot_api = SlackClient(app.config.get('SLACK_BOT_TOKEN'))
    two_degrees = TwoDegrees(bot_api)

    @app.route('/', methods=['GET'])
    def hello():
        return 'Hello there!'

    slack_events_adapter = SlackEventAdapter(app.config.get('SLACK_SIGNING_SECRET'), server=app)

    @slack_events_adapter.on('message')
    def message_channels(event_data):
        worker.enqueue(event_data, two_degrees.process)

    @slack_events_adapter.on('error')
    def error_handler(err):
        app.logger.error('slack api error: ' + str(err))

    print("Starting slackbot app")
    worker.start()
    return app


class WorkerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.setDaemon(True)
        self.queue = queue.Queue()

    def run(self):
        while True:
            (event_data, processor) = self.queue.get()
            try:
                processor(event_data)
            except Exception as err:
                print("Worker Exception caught:", err)
            self.queue.task_done()

    def enqueue(self, event_data, processor):
        self.queue.put((event_data, processor))
