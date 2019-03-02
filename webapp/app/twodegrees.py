import spacy


class MessageProcessor:
    def __init__(self, slack):
        self.slack = slack
        self.find_person = PersonFinder()
        self.casual_reference = CasualReferencer()

    def process(self, event_data):
        message = event_data["event"]
        if message.get("subtype") is None:
            text = message.get("text")
            person = self.find_person(text)
            if person is None:
                return
            text = self.casual_reference(person)
            channel = message["channel"]
            self.slack.api_call("chat.postMessage", channel=channel, text=text)


class CasualReferencer:
    def __call__(self, *args, **kwargs):
        return "You know, I actually met %s at a party once" % args[0]


class PersonFinder:
    def __init__(self):
        self.nlp = spacy.load('en')

    def __call__(self, *args, **kwargs):
        doc = self.nlp(*args, **kwargs)
        for ent in doc.ents:
            print('Discovered %s: %s' % (ent.label_, ent.text))
            if ent.label_ == 'PERSON':
                return ent.text
