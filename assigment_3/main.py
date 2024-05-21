from aruco_actions import DialogueCard
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from dialogue_actions import DialogueBranches
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6645d299f26645d6dd2bcb28",
)

# aruco id mapping - 12 cards
emotion_cards = {
    0: ("serenity"),
    1: ("joy"),
    2: ("ecstasy"),
    3: ("pensiveness"),
    4: ("sadness"),
    5: ("grief"),
    6: ("annoyance"),
    7: ("anger"),
    8: ("rage"),
    9: ("apprehension"),
    10: ("fear"),
    11: ("terror")
}



@inlineCallbacks
def main(session, details):

    session.leave()


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
