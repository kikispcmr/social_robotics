#from aruco_actions import DialogueCard
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
#from dialogue_actions import DialogueBranches
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000
wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
	}],
	realm="rie.664f05bdf26645d6dd2bfb28",
)

# aruco id mapping - 12 cards
emotion_cards = {
    0: ("serenity", 1, "emotion1"),
    1: ("joy", 2, "emotion1"),
    2: ("ecstasy", 3, "emotion1"),
    3: ("pensiveness", -1, "emotion1"),
    4: ("sadness", -2, "emotion1"),
    5: ("grief", -3, "emotion1"),
    6: ("annoyance",-1, "emotion2"),
    7: ("anger",-2, "emotion2"),
    8: ("rage",-3, "emotion2"),
    9: ("apprehension",1, "emotion2"),
    10: ("fear",2, "emotion2"),
    11: ("terror",3, "emotion2")
}

negative_emotions = {"sadness", "grief", "annoyance", "anger", "rage", "apprehension", "fear", "terror"}

positive_emotions = {"serenity", "joy", "ecstasy"}

@inlineCallbacks
def detect_emotion(self, session):
    session.call("rie.vision.card.stream")
    card_detected = yield session.call("rie.vision.card.read")
    card_id = card_detected[0]['data']['body'][0][5]
    print("card detected : ", card_id)

    yield session.subscribe(self.on_card, "rie.vision.card.stream")
    yield session.call("rie.vision.card.stream")

    detected_emotion = emotion_cards.get(card_id, "Unknown emotion")
    print(f"Detected emotion: {detected_emotion}")

    return detected_emotion


@inlineCallbacks
def main(session, details):
    robot_actions = RobotActions(session)
    yield robot_actions.move_negative()
    yield robot_actions.move_neutral()
    yield robot_actions.move_positive()

    """
    detected_emotion = yield detect_emotion(session)
    if detected_emotion in negative_emotions:
        yield robot_actions.move_sad()
    elif detected_emotion in positive_emotions:
        yield robot_actions.move_happy()
    """
    session.leave()


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
