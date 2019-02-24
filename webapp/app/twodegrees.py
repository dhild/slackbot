from flask import current_app


def two_degrees(slack):
    def process(event_data):
        current_app.logger.error("message processing!")
        message = event_data["event"]
        if message.get("subtype") is None and "hi" in message.get("text"):
            channel = message["channel"]
            message = "Hello <@%s>! :tada:" % message["user"]
            slack.api_call("chat.postMessage", channel=channel, text=message)
    return process
