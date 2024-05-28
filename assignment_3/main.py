from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks 
from drive import DriveSystem, emotion_poles 
from typing import Generator, List, Any
from drive_test import print_meters 
TIMEOUT_TIME = 6000
wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
	}],
	realm="rie.665584dcf26645d6dd2c1d8c",
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

still_seconds = 15

@inlineCallbacks
def detect_emotion(session: Component, drive) -> Any: 
    global still_seconds

    detected_emotion = None 
    session.call("rie.vision.card.stream")
    
    card_detected = yield session.call("rie.vision.card.read", time = 1000)
    # Okay so we try to get the card id from the detected card
    try:
        card_id = card_detected[0]['data']['body'][0][5]
        yield session.call("rie.vision.card.stream")

        detected_emotion = emotion_cards.get(card_id, "Unknown emotion")
        still_seconds = 15
        print(f"Detected emotion: {detected_emotion}")
        
    except:
        print("No card detected")
     
    print_meters(drive)
    return detected_emotion


@inlineCallbacks
def main(session: Component, details: Any) -> Generator:
    global still_seconds
    robot_actions = RobotActions(session)
    drive_system = DriveSystem()
    outcome = None
    #yield robot_actions.move_negative()
    #yield robot_actions.move_neutral()
    #yield robot_actions.move_positive()
    print("started")


    # We keep the loop going until it has no input for like 5 seconds
    # Basic loop checking for incomming detected emotions 
    while(True):
        detected_emotion = yield detect_emotion(session, drive_system)

        #drive_system.percieve_emotions(detected_emotion[2], detected_emotion[1]) 

        # Assume we have detected an emotion. What's next is to pass this to the perceptive system 
        # and let it update the perception meter
        if detected_emotion != None:
            # First argument is the detected emotion category, then the detected emotion intensity
            drive_system.percieve_emotions(detected_emotion[2], detected_emotion[1])
        outcome = drive_system.update_all_meters()

        # If the loop timeout is 0, then we get the highest response bar 
        if still_seconds == 0:
            outcome = drive_system.emotion_selector()
            break
        # Else if a threashold of a response bar is reached, we stop now 
        elif outcome is not None:
            break
        # Also if an emotion threshold is reached, break
        # TODO: do that here 
        #yield sleep(1)
        print("still seconds: ", still_seconds)
        still_seconds -= 1
    
    if outcome == "neutral":
        robot_actions.move_neutral() # TODO: add intensity_factor for the movement from outcome
    elif outcome == "positive":
        robot_actions.move_positive()
    elif outcome == "negative":
        robot_actions.move_negative()
    session.leave()




wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
