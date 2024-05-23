#from aruco_actions import DialogueCard
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
#from dialogue_actions import DialogueBranches
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks 
from drive import DriveSystem, emotion_poles, decay_loop
from typing import Generator, List
TIMEOUT_TIME = 6000
wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
	}],
	realm="rie.664eed4af26645d6dd2bfa31",
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

still_seconds = 5
@inlineCallbacks
def detect_emotion(session):
    global still_seconds

    detected_emotion = None 
    session.call("rie.vision.card.stream")
    
    card_detected = yield session.call("rie.vision.card.read", time = 100)

    try:
        card_id = card_detected[0]['data']['body'][0][5]
        yield session.call("rie.vision.card.stream")

        detected_emotion = emotion_cards.get(card_id, "Unknown emotion")
        still_seconds = 5
        print(f"Detected emotion: {detected_emotion}")
    except:
        print("No card detected")
            
        #print("card detected : ", card_id)

    #yield session.subscribe(on_card, "rie.vision.card.stream")


    return detected_emotion


@inlineCallbacks
def main(session, details):
    global still_seconds
    robot_actions = RobotActions(session)
    drive_system = DriveSystem()
    #yield robot_actions.move_negative()
    #yield robot_actions.move_neutral()
    #yield robot_actions.move_positive()
    print("started")


    # We keep the loop going until it has no input for like 5 seconds
    while(True):
        detected_emotion = yield detect_emotion(session)

        #drive_system.percieve_emotions(detected_emotion[2], detected_emotion[1]) 
        if still_seconds == 0:
            break
        # Also if an emotion threshold is reached, break
        # TODO: do that here 
        yield sleep(1)
        print("still seconds: ", still_seconds)
        still_seconds -= 1
        """
    if detected_emotion in negative_emotions:
        
        yield robot_actions.move_negative()
    elif detected_emotion in positive_emotions:
        yield robot_actions.move_positive()
    """
    session.leave()


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
