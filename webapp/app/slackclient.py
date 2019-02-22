import os


class SlackConfig:
    SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN')
    SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')


class SlackAPI:
    def __init__(self, config):
        self.config = config
        self.verification_token = config.get('SLACK_VERIFICATION_TOKEN')
        self.app_token = config.get('SLACK_APP_TOKEN')
        self.bot_token = config.get('SLACK_BOT_TOKEN')

        from slackclient import SlackClient
        self.app_client = SlackClient(self.app_token)
        self.bot_client = SlackClient(self.bot_token)

    def is_valid_request(self, req):
        json = req.get_json()
        return json['token'] == self.config.get('SLACK_VERIFICATION_TOKEN')
