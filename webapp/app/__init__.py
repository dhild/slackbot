from flask import Flask, request, Response, jsonify
from app.slackclient import SlackAPI
import os

app = Flask('slackbot')
slack_api = SlackAPI()
verification_token = os.environ.get('SLACK_VERIFICATION_TOKEN')


@app.route('/', methods=['GET'])
def hello():
    return 'Hello world!'


@app.route('/slack/event', methods=['POST'])
def slack_event():
    if not slack_api.is_valid_request(request):
        return Response(), 401
    req = request.get_json()
    if req['type'] == 'url_verification':
        return jsonify(challenge=req['challenge'])
    return Response(), 200
