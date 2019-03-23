import app.wumpus.db as db
import app.wumpus.ui as ui
import random
from datetime import datetime


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
        game = db.find_game(session, user_id)
        if game.state is None:
            new_game(session, user_id)

        message = ""
        if action_id == 'wumpus_show_instructions':
            message = instructions

        message += get_hazards_and_location(game)
        return ui.choice(message, ui.Option("Shoot", "wumpus_shoot"), ui.Option("Move", "wumpus_move"))


def new_game(session, user_id):
    game = db.Game(user_id=user_id, start_time=datetime.now(), arrows=5)
    game.wumpus_location = random_cave()
    game.bats = [db.Bat(location=random_cave()), db.Bat(location=random_cave())]
    game.pits = [db.Pit(location=random_cave()), db.Pit(location=random_cave())]
    while True:
        game.player_location = random_cave()
        if game.player_location != game.wumpus_location:
            break
    session.add(game)


def get_hazards_and_location(game):
    wumpus_nearby = False
    pit_nearby = False
    bats_nearby = False
    for x in tunnel_connections[game.player_location]:
        wumpus_nearby |= game.wumpus_location == x
        for p in game.pits:
            pit_nearby |= p.location == x
        for b in game.bats:
            bats_nearby |= b.location == x
    messages = "You are in room %d" % game.player_location
    if wumpus_nearby:
        messages += "\nI smell a wumpus!"
    if pit_nearby:
        messages += "\nI feel a draft"
    if bats_nearby:
        messages += "\nBats nearby!"
    return messages


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

instructions = """
WELCOME TO 'HUNT THE WUMPUS'

THE WUMPUS LIVES IN A CAVE OF 20 ROOMS: EACH ROOM HAS 3 TUNNELS LEADING TO OTHER
ROOMS. (LOOK AT A DODECAHEDRON TO SEE HOW THIS WORKS. IF YOU DON'T KNOW WHAT A
DODECAHEDRON IS, ASK SOMEONE)

***
HAZARDS:

BOTTOMLESS PITS - TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
IF YOU GO THERE: YOU FALL INTO THE PIT (& LOSE!)

SUPER BATS  - TWO OTHER ROOMS HAVE SUPER BATS. IF YOU GO THERE, A BAT GRABS YOU
AND TAKES YOU TO SOME OTHER ROOM AT RANDOM. (WHICH MIGHT BE TROUBLESOME)

WUMPUS:

THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER FEET AND IS TOO BIG FOR
A BAT TO LIFT). USUALLY HE IS ASLEEP. TWO THINGS WAKE HIM UP: YOUR ENTERING HIS
ROOM OR YOUR SHOOTING AN ARROW.

IF THE WUMPUS WAKES, HE MOVES (P=0.75) ONE ROOM OR STAYS STILL (P=0.25). AFTER
THAT, IF HE IS WHERE YOU ARE, HE EATS YOU UP (& YOU LOSE!)

YOU:

EACH TURN YOU MAY MOVE OR SHOOT A CROOKED ARROW 
MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.

EACH ARROW CAN GO FROM 1 TO 5 ROOMS: YOU AIM BY TELLING THE COMPUTER THE ROOMS
YOU WANT THE ARROW TO GO TO. IF THE ARROW CAN'T GO THAT WAY (IE NO TUNNEL) IT
MOVES AT RANDOM TO THE NEXT ROOM.

IF THE ARROW HITS THE WUMPUS: YOU WIN.

IF THE ARROW HITS YOU: YOU LOSE.

WARNINGS:

WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OP HAZARD, THE COMPUTER SAYS:

WUMPUS - 'I SMELL A WUMPUS'

BAT - 'BATS NEARBY'

PIT - 'I FEEL A DRAFT'

"""
