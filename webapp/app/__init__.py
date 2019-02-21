from flask import Flask
from app.utils.slack import SlackAPI

app = Flask('slackbot')


@app.route('/')
def hello():
    return 'Hello world!'
