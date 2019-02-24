import os


class Config:
    SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')


def configure_app(app):
    app.config.from_object(Config)
