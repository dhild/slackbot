import spacy
import random
from string import Template

intros = ["Get this...", "Believe it or not,", "Fun fact,", "You know,"]
locations = ["DC", "Seattle", "LA", "Florida", "Miami", "Las Vegas"]
places = ["bar", "restaurant", "club", "museum", "party"]
events = ["my brother's wedding", "a conference", "a Bat Mitzvah", "my brother's bachelor party"]
drinks = ["beers", "cocktails", "wine", "milkshakes"]
people = ["Jay-Z", "Mike Myers", "Buckethead", "Nick Carter", "John Singleton", "Meghan Markle", "Neil Degrasse Tyson"]
bands = ["Led Zeppelin", "Primus"]
experiences = ["went to school together", "attended the same temple"]

templates = [
    Template('$intro last time I was in $location, I bumped into $name at a $place'),
    Template('$intro I had $drink with $name at $event in $location'),
    Template('$intro $name and I $experience growing up'),
    Template('$intro I once hung out with $name and $person backstage at $band show')
]


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
        t = random.choice(templates)
        return t.substitute(
            name=args[0],
            intro=random.choice(intros),
            location=random.choice(locations),
            place=random.choice(places),
            event=random.choice(events),
            drink=random.choice(drinks),
            person=random.choice(people),
            band=random.choice(bands),
            experience=random.choice(experiences))


class PersonFinder:
    def __init__(self):
        self.nlp = spacy.load('en')

    def __call__(self, *args, **kwargs):
        doc = self.nlp(*args, **kwargs)
        for ent in doc.ents:
            print('Discovered %s: %s' % (ent.label_, ent.text))
            if ent.label_ == 'PERSON':
                return ent.text
