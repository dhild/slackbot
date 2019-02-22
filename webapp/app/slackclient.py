def _default_config():
    import os
    return {
        'SLACK_VERIFICATION_TOKEN': os.environ.get('SLACK_VERIFICATION_TOKEN'),
        'SLACK_APP_TOKEN': os.environ.get('SLACK_APP_TOKEN'),
        'SLACK_BOT_TOKEN': os.environ.get('SLACK_BOT_TOKEN'),
    }


default_config = _default_config()


class SlackAPI:
    def __init__(self, config):
        self.verification_token = config.get('SLACK_VERIFICATION_TOKEN')
        self.app_token = config.get('SLACK_APP_TOKEN')
        self.bot_token = config.get('SLACK_BOT_TOKEN')

        from slackclient import SlackClient
        self.app_client = SlackClient(self.app_token)
        self.bot_client = SlackClient(self.bot_token)

    def is_valid_request(self, req):
        if req.get_json()['token'] == self.verification_token:
            return True
        return False
