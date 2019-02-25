class TwoDegrees:
    def __init__(self, slack):
        self.slack = slack
        self.famous_people = [
            "paris hilton",
            "steve buscemi",
        ]
        self.places = [
            "on the ferry",
            "at the pub",
            "while touring Europe"
        ]

    def process(self, event_data):
        message = event_data["event"]
        if message.get("subtype") is None:
            text = message.get("text").lower()
            person = self.get_famous_person(text)
            if person is None:
                return
            place = self.get_location()
            channel = message["channel"]
            message = "I once met %s at %s" % person, place
            self.slack.api_call("chat.postMessage", channel=channel, text=message)

    def get_famous_person(self, text):
        for person in self.famous_people:
            if person in text:
                return person
        return None

    def get_location(self):
        return self.places[2]
