from flask import Flask, request, make_response
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from app.config import configure_app
import app.twodegrees
import app.wumpus
import queue
import threading
from time import time
import json


def create_app(custom_config=None):
    app = Flask('slackbot')
    worker = WorkerThread()

    configure_app(app)

    if custom_config is not None:
        app.config.from_object(custom_config)

    bot_api = SlackClient(app.config.get('SLACK_BOT_TOKEN'))
    two_degrees = twodegrees.MessageProcessor(bot_api)
    wumpus_hunter = wumpus.Processor(bot_api)

    @app.route('/', methods=['GET'])
    def hello():
        return 'Hello there!'

    slack_events_adapter = SlackEventAdapter(app.config.get('SLACK_SIGNING_SECRET'), server=app)

    @slack_events_adapter.on('message')
    def message_channels(event_data):
        worker.enqueue(event_data, two_degrees.process)
        worker.enqueue(event_data, wumpus_hunter.event_handler)

    @slack_events_adapter.on('error')
    def error_handler(err):
        app.logger.error('slack api error: ' + str(err))

    @app.route('/slack/interaction', methods=['POST'])
    def interaction_handler():
        # Each request comes with request timestamp and request signature
        # emit an error if the timestamp is out of range
        req_timestamp = request.headers.get('X-Slack-Request-Timestamp')
        if abs(time() - int(req_timestamp)) > 60 * 5:
            app.logger.error('interaction handler: Invalid request timestamp')
            return make_response("", 403)

        # Verify the request signature using the app's signing secret
        # emit an error if the signature can't be verified
        req_signature = request.headers.get('X-Slack-Signature')
        if not slack_events_adapter.server.verify_signature(req_timestamp, req_signature):
            app.logger.error('interaction handler: Invalid request signature')
            return make_response("", 403)

        # Parse the request payload into JSON
        payload = json.loads(request.form['payload'])
        worker.enqueue(payload, wumpus_hunter.interaction_handler)

        return make_response("", 200)

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
