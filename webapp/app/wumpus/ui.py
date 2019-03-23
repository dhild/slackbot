class Option:
    def __init__(self, text, value):
        self.text = text
        self.value = value


def choice(message, *args):
    elements = []
    for opt in args:
        elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": opt.text,
                "emoji": False
            },
            "value": opt.value
        })
    return {
        "text": message,
        "blocks": [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        }, {
            "type": "actions",
            "block_id": "actionblock",
            "elements": elements
        }]
    }