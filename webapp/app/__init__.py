from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from app.config import configure_app
from app.twodegrees import two_degrees
import json


def create_app(custom_config=None):
    app = Flask('slackbot')

    configure_app(app)

    if custom_config is not None:
        app.config.from_object(custom_config)

    bot_api = SlackClient(app.config.get('SLACK_BOT_TOKEN'))

    @app.route('/', methods=['GET'])
    def hello():
        return 'Hello there!'

    @app.route('/slack/events', methods=['GET', 'POST'])
    def what():
        data = request.data.decode('utf-8')
        event_data = json.loads(data)
        print("INFO: callback: " + event_data['event']['type'])
        app.logger.info('raw data: ' + data)
        return Response(), 200

    slack_events_adapter = SlackEventAdapter(app.config.get('SLACK_SIGNING_SECRET'), endpoint='/slack/event',
                                             server=app)

    @slack_events_adapter.on('message')
    async def message_channels(event_data):
        print("INFO: callback: " + event_data['event']['type'])
        two_degrees(bot_api)(event_data)

    @slack_events_adapter.on('error')
    def error_handler(err):
        app.logger.error('slack api error: ' + str(err))

    print("Starting slackbot app")
    return app
