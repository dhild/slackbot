import os
from slackclient import SlackClient


class SlackAPI:
    def __init__(self):
        self.verification_token = os.environ.get('SLACK_VERIFICATION_TOKEN')
        self.app_token = os.environ.get('SLACK_APP_TOKEN')
        self.bot_token = os.environ.get('SLACK_BOT_TOKEN')
        self.app_client = SlackClient(self.app_token)
        self.bot_client = SlackClient(self.bot_token)

    def is_valid_request(self, req):
        if req.get_json()['token'] == self.verification_token:
            return True
        return False
