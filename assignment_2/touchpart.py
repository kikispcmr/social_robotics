from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

TIMEOUT_TIME = 6000


def touched(frame):
    if ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
        #yield call("rie.dialogue.say", text="Ouch! Please don't touch me!")
        print("touch") 

# aruco id mapping - 4 cards
animals_cards = {
    1: ("Giraffe", "Africa"),
    2: ("Panda", "Asia"),
    3: ("Kangaroo", "Australia"),
    4: ("Penguin", "Antarctica")
}

class Dialogue_card:
    def __init__(self):
        pass

    @inlineCallbacks
    def ask_geographical_card_question(self, session):
        session.call("rie.vision.card.stream")
        # we ask the question based on animal_cards mapping
        for card_id, (animal, location) in animals_cards.items():
            correct = False
            attempts = 0
            max_attempts = 1  # set a max number of attempts per question
            question = f"Where do {animal}s live?"

            while not correct and attempts < max_attempts:
                if attempts > 0:  # ask the question, if not first attempt, provide feedback
                    yield session.call("rie.dialogue.say", text="Try one more time. " + question)
                else:
                    yield session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_card(session, card_id)

                if correct:
                    yield session.call("rie.dialogue.say", text=f"Correct! {animal}s live in {location}.")
                else:
                    yield session.call("rie.dialogue.say", text="That's not the right card.")
                
                attempts += 1

            if not correct:
                yield session.call("rie.dialogue.say", text=f"The correct answer is {location} where {animal}s live.")


    @inlineCallbacks
    def wait_for_correct_card(self, session, correct_card_id):
        # if we have the correct card
        card_detected = yield session.call("rie.vision.card.read")
        if card_detected[0] == correct_card_id: # check that the id is correct
            return True
        return False

    def on_card(self, frame):
        print("Card detected:", frame["data"])



@inlineCallbacks
def main(session, details):

    '''    # Touch subscribte
    session.subscribe(touched, "rom.sensor.touch.stream")

    # Start by seeking for participants
    yield session.call("rie.vision.face.find")
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm") # <- predefined behaviour with no target word
    yield session.call("rie.dialogue.say", text="Oh hey there! Would you like to play a game with me? If so touch my head so I know you're ready!")
    yield session.call("rom.sensor.touch.stream") # <- touch interaction
    yield session.call("rie.dialogue.say", text="Awesome! Let's begin the game!! Answer True or False to the following statements.")
    

    # First question
    question = "Africa is the second largest continent in the world by land area."
    answers = {"true": ["True", "tru", "yes"], "false": ["False", "fls", "no", "fals"]}
    answer = yield session.call("rie.dialogue.ask", question=question, answers=answers)
    
    yield sleep(1)
    if answer == "true": # correct answer
        print("true")
        yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm") # <- predefined behaviour with target word "True"
        yield session.call("rie.dialogue.say", text="That is correct! Did you know there are giraffes in Africa!")
    elif answer == "false":
        yield session.call("rie.dialogue.say", text="That is incorrect!")
    else:
        yield session.call("rie.dialogue.say", text="Sorry, but I didn't hear you properly.")
    '''

    print("skiing now")
    # Skiing motion self-defined
    yield session.call("rom.actuator.motor.write", # <- self-defined gesture for concept skiing
        frames=[
            # starting position
            {"time": 1000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
            
            # right ski push
            {"time": 2000, "data": {"body.legs.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -1.0}},
            
            # return to middle
            {"time": 3000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
            
            # left ski push
            {"time": 4000, "data": {"body.legs.left.upper.pitch": -0.5, "body.arms.right.upper.pitch": -1.0}},
            
            # return to starting position
            {"time": 5000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}}
        ],
        force=True)
    
    print("question time")

    # Second question
    question = "Skiing originated as a mode of transportation in the Alps during the 19th century."
    answers = {"true": ["True", "tru", "yes"], "false": ["False", "fls", "no", "fals", "falz"]}
    answer = yield session.call("rie.dialogue.ask", question=question, answers=answers)

    yield sleep(1)
    if answer == "true":
        session.call("rom.optional.behaviour.play", name="BlocklyApplause") # <- predefined behaviour with target word "True"
        yield session.call("rie.dialogue.say", text="That is incorrect!")
    elif answer == "false": #correct answer
        yield session.call("rie.dialogue.say", text="That is correct! Skiing originated in northern Europe and Asia thousands of years ago as a means of transportation. The oldest known skis were found in Russia and date back to around 6000 to 5000 BC")
    else:
        yield session.call("rie.dialogue.say", text="Sorry, but I didn't hear you properly.")


    yield session.call("rie.dialogue.say", text="Let's try something different.. Answer my questions using the aruco cards infront of me !")

    dialogue_manager = Dialogue_card()
    yield session.subscribe(dialogue_manager.on_card, "rie.vision.card.stream")
    #yield session.subscribe(dialogue_manager.ask_geographical_card_question, "rie.vision.card.stream")
    # ask the geography card qquestion
    yield dialogue_manager.ask_geographical_card_question(session) # <- aruco cards interaction

    
    session.call("rom.optional.behavior.play", name="BlocklyRobotDance")
    yield session.call(
        "rie.dialogue.say",
        text="You reached the end! Great job. I hope you learnt something new about the world around you!",
    )

    session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    yield session.call("rie.dialogue.say", text="Goodbye!")






    session.leave()




# Create wamp connection
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6645d117f26645d6dd2bcaf7",
)


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])