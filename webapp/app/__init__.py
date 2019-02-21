from flask import Flask, request, Response
from flask.json import dumps
from app.slackclient import SlackAPI

app = Flask('slackbot')
slack_api = SlackAPI()


@app.route('/', methods=['GET'])
def hello():
    return 'Hello world!'


@app.route('/slack/event', methods=['POST'])
def slack_event():
    resp, code = slack_api.process_event(request.get_json())
    if resp is not None:
        resp = dumps(resp)
    return Response(response=resp, status=code, content_type="application/json")
