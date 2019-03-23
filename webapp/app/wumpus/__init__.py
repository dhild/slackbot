import app.wumpus.db as db
import app.wumpus.ui as ui
import random


class Processor(object):
    def __init__(self, slack):
        self.slack = slack

    def event_handler(self, event_data):
        message = event_data["event"]
        if message.get("subtype") is None:
            text = message.get("text")
            if "hunt the wumpus" in text.lower():
                user_id = message.get("user")
                channel = message["channel"]
                response = hunt_the_wumpus(user_id, '')
                self.slack.api_call("chat.postMessage", channel=channel, **response)

    def interaction_handler(self, data):
        if data["type"] == "block_actions":
            channel = data["channel"]["id"]
            timestamp = data["message"]["ts"]
            user_id = data["user"]["id"]
            action_id = data["actions"][0]["action_id"]
            response = hunt_the_wumpus(user_id, action_id)
            if response is not None:
                self.slack.api_call("chat.update", channel=channel, ts=timestamp, **response)


def hunt_the_wumpus(user_id, action_id):
    with db.session_scope() as session:
        game = db.find_or_create_game(session, user_id)
        if game.state is None:
            setup_game(game)
            return ui.choice("Show Instructions?", ui.Option("Yes", "wumpus_show_instructions"),
                             ui.Option("No", "wumpus_skip_instructions"))

        if action_id == "wumpus_show_instructions":
            pass


def setup_game(game):
    while True:
        game.player_location = random_cave()
        game.wumpus_location = random_cave()
        if game.player_location != game.wumpus_location:
            break


def random_cave():
    return random.randint(1, 20)


# In traditional Hunt the Wumpus, the playing area is a dodecahedron. If you squash it, and label each of the vertices,
# you get a map of how to traverse the tunnels (edges) to each cave (vertex).
tunnel_connections = {
    1: [2, 3, 15],
    2: [1, 5, 18],
    3: [1, 4, 7],
    4: [3, 5, 6],
    5: [2, 4, 10],
    6: [4, 8, 9],
    7: [3, 8, 11],
    8: [6, 7, 12],
    9: [6, 10, 13],
    10: [5, 9, 14],
    11: [7, 15, 16],
    12: [8, 13, 16],
    13: [9, 12, 17],
    14: [10, 17, 18],
    15: [1, 11, 20],
    16: [11, 12, 19],
    17: [13, 14, 19],
    18: [2, 14, 20],
    19: [16, 17, 20],
    20: [15, 18, 19],
}
