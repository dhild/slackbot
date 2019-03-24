import logging
import random


class Game(object):
    lose_message = "Ha ha ha - you lose!"
    win_message = "Hee hee hee - the Wumpus'll getcha next time!!"

    def __init__(self, username, player_location, wumpus_location, bat_locations, pit_locations, arrows):
        self.username = username
        self.player_location = player_location
        self.wumpus_location = wumpus_location
        self.bat_locations = bat_locations
        self.pit_locations = pit_locations
        self.arrows = arrows
        self.messages = []
        self._continue_messages()

        class GameLoggerAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                return '[%s] %s' % (self.extra['username'], msg), kwargs

        self.logger = GameLoggerAdapter(logging.getLogger(__name__), {'username': username})

    def _continue_messages(self):
        for x in tunnel_connections[self.player_location]:
            if x == self.wumpus_location:
                self.messages.append("You smell a Wumpus!")
            if x in self.pit_locations:
                self.messages.append("You feel a draft")
            if x in self.bat_locations:
                self.messages.append("You can hear bats nearby!")
        self.messages.append("You are in room %d" % self.player_location)
        self.messages.append("Tunnels lead to %d, %d, %d" % (
            tunnel_connections[self.player_location][0], tunnel_connections[self.player_location][1],
            tunnel_connections[self.player_location][2]))

    def should_continue(self):
        return Game.lose_message not in self.messages and Game.win_message not in self.messages

    def move(self, target):
        self.logger.debug("Moving player to %d" % target)
        self.player_location = target
        for p in self.bat_locations:
            if p == target:
                self.logger.debug("Player encountered a bat at %d" % target)
                self.messages.append("A bat has snatched you up and dropped you in a random cave!")
                self.player_location = random_cave()

        for p in self.pit_locations:
            if p == target:
                self.logger.debug("Player fell into a pit at %d" % target)
                self.messages.append("YYYIIIIEEEE... You fell into a pit!")
                self.messages.append(Game.lose_message)
                return

        if self.player_location == self.wumpus_location:
            self.messages.append("....oops! Bumped a Wumpus!")
            self.move_wumpus()

    def shoot(self, target):
        self.logger.debug("Shooting at %d" % target)
        if target == self.wumpus_location:
            self.messages.append("Aha! You got the wumpus!")
            self.messages.append(Game.win_message)
            return
        self.messages.append("Missed!")

        self.arrows -= 1
        if self.arrows == 0:
            self.messages.append("You are out of arrows!")
            self.messages.append(Game.lose_message)
            return

        self.move_wumpus()

    def move_wumpus(self):
        choice = random.randint(0, 3)
        if choice < 3:
            self.wumpus_location = tunnel_connections[self.wumpus_location][choice]
            self.logger.debug("Wumpus moved to cave %d" % self.wumpus_location)
        else:
            self.logger.debug("Wumpus stayed put")

        if self.player_location == self.wumpus_location:
            self.logger.debug("Player got eaten by the wumpus %d" % self.player_location)
            self.messages.append("Tsk tsk tsk - Wumpus got you!")
            self.messages.append(Game.lose_message)

    def adjoining_caves(self):
        return tunnel_connections[self.player_location]


def new_game(username):
    caves = list(range(1, 20))
    return Game(username=username, player_location=random_cave(caves), wumpus_location=random_cave(caves),
                bat_locations=[random_cave(caves), random_cave(caves)],
                pit_locations=[random_cave(caves), random_cave(caves)], arrows=5)


def random_cave(caves=None):
    if caves is None:
        return random_cave(list(range(1, 20)))
    cave = random.choice(caves)
    caves.remove(cave)
    return cave


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
