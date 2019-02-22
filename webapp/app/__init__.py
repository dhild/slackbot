from flask import Flask, request, Response, jsonify
from app.slackclient import SlackAPI


def create_app():
    app = Flask('slackbot')

    from app.slackclient import default_config
    app.config.from_object(default_config)

    slack = SlackAPI(app.config)

    @app.route('/', methods=['GET'])
    def hello():
        return 'Hello world!'

    @app.route('/slack/event', methods=['POST'])
    def slack_event():
        if not slack.is_valid_request(request):
            return Response(), 401
        req = request.get_json()
        if req['type'] == 'url_verification':
            return jsonify(challenge=req['challenge'])
        return Response(), 200

    return app
