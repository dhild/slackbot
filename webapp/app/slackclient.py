import os
from slackclient import SlackClient


class SlackAPI:
    def __init__(self):
        self.slack_token = os.environ.get('SLACK_APP_TOKEN')
        self.slack_client = SlackClient(self.slack_token)

    def process_event(self, form):
        if form['token'] == self.slack_token:
            if form['type'] == 'url_verification':
                return {'challenge': form['challenge']}, 200
        return None, 200
