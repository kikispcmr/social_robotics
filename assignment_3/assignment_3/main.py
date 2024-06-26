from autobahn.twisted.component import Component, run
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks 
from drive import DriveSystem 
from typing import Generator, Any
from emotion_mapping import emotion_cards

# Constant Variables 
TIMEOUT_TIME = 6000
CARD_SESSION_TIME = 10

# Global Variables :( 
still_seconds = CARD_SESSION_TIME

wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
	}],
	realm="rie.665853e0f26645d6dd2c2e92",
)

@inlineCallbacks
def detect_emotion(session: Component) -> Any: 
    global still_seconds

    detected_emotion = None 
    session.call("rie.vision.card.stream")
    
    card_detected = yield session.call("rie.vision.card.read", time = 1000)
    # Okay so we try to get the card id from the detected card
    try:
        card_id = card_detected[0]['data']['body'][0][5]
        yield session.call("rie.vision.card.stream")

        detected_emotion = emotion_cards.get(card_id, "Unknown emotion")
        still_seconds = CARD_SESSION_TIME
    except:
        pass
    return detected_emotion


@inlineCallbacks
def main(session: Component, details: Any) -> Generator:
    global still_seconds

    robot_actions = RobotActions(session)
    drive_system = DriveSystem()
    outcome, outcome_intensity = None, None

    # We keep the loop going until it has no input for like 5 seconds
    # Basic loop checking for incomming detected emotions 
    while(True):
        detected_emotion = yield detect_emotion(session)
        drive_system.print_meters()
        if detected_emotion != None:
            # First argument is the detected emotion category, then the detected emotion intensity
            drive_system.percieve_emotions(detected_emotion[2], detected_emotion[1])
        outcome, outcome_intensity = drive_system.update_all_meters()

        # If the loop timeout is 0, then we get the highest response bar 
        if still_seconds == 0:
            outcome, outcome_intensity = drive_system.emotion_selector()
            break
        # Else if a threashold of a response bar is reached, we stop now 
        elif outcome is not None:
            print("Outcome: ", outcome, "Intensity: ", outcome_intensity)
            break
        # Also if an emotion threshold is reached, break
        print("still seconds: ", still_seconds)
        still_seconds -= 1
    
    # If the outcome is anything but None, it will perform the required action
    if outcome == "neutral":
        yield robot_actions.move_neutral() 
    elif outcome == "positive":
        yield robot_actions.move_positive(outcome_intensity/2)
    elif outcome == "negative":
        yield robot_actions.move_negative(outcome_intensity/2)

    # Ask if you want to continue the conversation ..
    answers = {"yes": ["yeah", "yes", "ye", "okay"], "no": ["no", "nah", "nope"]} 
    answer = yield session.call("rie.dialogue.ask", question="Would you like to continue the conversation?", answers=answers)

    if answer == "yes": 
        yield session.call("rie.dialogue.say", text="Yay ! Show me an emotion !") 
    elif answer == "no": 
        session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
        yield session.call("rie.dialogue.say", text="Okay! Have a nice day ! Goodbye! ") 
        session.leave()
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly...")

    # Loop again
    main(session, details)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
