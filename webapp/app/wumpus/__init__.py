import app.wumpus.db as db
import logging

logger = logging.getLogger(__name__)


class Processor(object):
    def __init__(self, slack):
        self.slack = slack

    def event_handler(self, event_data):
        message = event_data["event"]
        if message.get("subtype") is None:
            text = message.get("text")
            if "wumpus" in text.lower():
                user_id = message.get("user")
                channel = message["channel"]
                logger.info("Starting to hunt the wumpus for user '%s' in channel '%s'" % (user_id, channel))
                response = hunt_the_wumpus(user_id)
                if response is not None:
                    self.slack.api_call("chat.postMessage", channel=channel, **response)

    def interaction_handler(self, payload):
        if payload["type"] == "block_actions":
            channel = payload["channel"]["id"]
            timestamp = payload["message"]["ts"]
            user_id = payload["user"]["id"]
            action_id = payload["actions"][0]["action_id"]
            if not action_id.startswith("wumpus_"):
                logger.error("Unknown action id: " + action_id)
                return

            action_value = payload["actions"][0]["value"]

            logger.info(
                "Hunting the wumpus with user '%s', action '%s', value '%s'" % (user_id, action_id, action_value))
            response = hunt_the_wumpus(user_id, action_id, action_value)
            if response is not None:
                logger.debug("Updating message with: %s" % response)
                self.slack.api_call("chat.update", channel=channel, ts=timestamp, **response)


def hunt_the_wumpus(user_id, action_id="", action_value=None):
    with db.session_scope() as session:
        game = db.find_game(session, user_id)
        logger.debug("Game for '%s' has: player=%d, wumpus=%d, arrows=%d" % (
            user_id, game.player_location, game.wumpus_location, game.arrows))

        if action_id.startswith("wumpus_move_"):
            target = int(action_value)
            game.move(target)

        if action_id.startswith("wumpus_shoot_"):
            target = int(action_value)
            game.shoot(target)

        db.save_game(session, game)

        show_instructions = action_id == "wumpus_show_instructions"
        show_instructions &= game.should_continue()
        return create_payload(game, show_instructions)


def create_payload(game, show_instructions):
    header = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://www.atariarchives.org/bcc1/showpage.php?page=247|*Hunt the Wumpus!*>"
        }
    }
    blocks = [header]

    if show_instructions:
        header["accessory"] = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Hide Instructions",
                "emoji": False
            },
            "action_id": "wumpus_hide_instructions",
            "value": "dummy"
        }
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": instructions
            }
        })
    else:
        header["accessory"] = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Show Instructions",
                "emoji": False
            },
            "action_id": "wumpus_show_instructions",
            "value": "dummy"
        }

    for m in game.messages:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                # Give the text that Preformatted styling:
                "text": "```\n" + m + "\n```"
            }
        })

    if game.should_continue():
        moves = []
        shoots = []
        for x in game.adjoining_caves():
            moves.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Move to %d" % x,
                    "emoji": False
                },
                "action_id": "wumpus_move_%d" % x,
                "value": "%d" % x
            })
            shoots.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Shoot at %d" % x,
                    "emoji": False
                },
                "action_id": "wumpus_shoot_%d" % x,
                "value": "%d" % x
            })
        blocks.append({
            "type": "actions",
            "block_id": "move_options",
            "elements": moves
        })
        blocks.append({
            "type": "actions",
            "block_id": "shoot_options",
            "elements": shoots
        })

    return {
        "text": "Hunt the wumpus is not available in your region :troll:",
        "blocks": blocks
    }


instructions = """
```
WELCOME TO 'HUNT THE WUMPUS'

THE WUMPUS LIVES IN A CAVE OF 20 ROOMS: EACH ROOM HAS 3 TUNNELS LEADING TO OTHER ROOMS. (LOOK AT A DODECAHEDRON TO SEE \
HOW THIS WORKS. IF YOU DON'T KNOW WHAT A DODECAHEDRON IS, ASK SOMEONE)

***
HAZARDS:

BOTTOMLESS PITS - TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
IF YOU GO THERE: YOU FALL INTO THE PIT (& LOSE!)

SUPER BATS  - TWO OTHER ROOMS HAVE SUPER BATS. IF YOU GO THERE, A BAT GRABS YOU AND TAKES YOU TO SOME OTHER ROOM AT \
RANDOM. (WHICH MIGHT BE TROUBLESOME)

WUMPUS:

THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER FEET AND IS TOO BIG FOR A BAT TO LIFT). USUALLY HE IS ASLEEP. \
TWO THINGS WAKE HIM UP: YOUR ENTERING HIS ROOM OR YOUR SHOOTING AN ARROW.

IF THE WUMPUS WAKES, HE MOVES (P=0.75) ONE ROOM OR STAYS STILL (P=0.25). AFTER THAT, IF HE IS WHERE YOU ARE, HE EATS \
YOU UP (& YOU LOSE!)

YOU:

EACH TURN YOU MAY MOVE OR SHOOT A CROOKED ARROW 
MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.

EACH ARROW CAN GO FROM 1 TO 5 ROOMS: YOU AIM BY TELLING THE COMPUTER THE ROOMS YOU WANT THE ARROW TO GO TO. IF THE \
ARROW CAN'T GO THAT WAY (IE NO TUNNEL) IT MOVES AT RANDOM TO THE NEXT ROOM.

IF THE ARROW HITS THE WUMPUS: YOU WIN.

IF THE ARROW HITS YOU: YOU LOSE.

WARNINGS:

WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OP HAZARD, THE COMPUTER SAYS:

WUMPUS - 'I SMELL A WUMPUS'

BAT - 'BATS NEARBY'

PIT - 'I FEEL A DRAFT'
```
"""
