from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000


@inlineCallbacks
def main(session, details):
    # Touch subscribte
    session.subscribe(touched, "rom.sensor.touch.stream")

    # Start by seeking for participants
    yield session.call("rie.vision.face.find")
    yield session.call(
        "rom.optional.behavior.play", name="BlocklyWaveRightArm"
    )  # <- predefined behaviour with no target word
    yield session.call(
        "rie.dialogue.say",
        text="Oh hey there! Would you like to play a game with me? If so touch my head so I know you're ready!",
    )
    yield session.call("rom.sensor.touch.stream")  # <- touch interaction
    yield session.call(
        "rie.dialogue.say",
        text="Awesome! Let's begin the game!! Answer True or False to the following statements.",
    )

    # First question
    question = "Africa is the second largest continent in the world by land area."
    answers = {"true": ["True", "tru", "yes"], "false": ["False", "fls", "no", "fals"]}
    answer = yield session.call("rie.dialogue.ask", question=question, answers=answers)

    yield sleep(1)
    if answer == "true":  # correct answer
        print("true")
        yield session.call(
            "rom.optional.behavior.play", name="BlocklyWaveRightArm"
        )  # <- predefined behaviour with target word "True"
        yield session.call(
            "rie.dialogue.say",
            text="That is correct! Did you know there are giraffes in Africa!",
        )
    elif answer == "false":
        yield session.call("rie.dialogue.say", text="That is incorrect!")
    else:
        yield session.call(
            "rie.dialogue.say", text="Sorry, but I didn't hear you properly."
        )

    # Second question
    # Skiin I guess

    question = "Skiing originated as a mode of transportation in the Alps during the 19th century."
    answers = {
        "true": ["True", "tru", "yes"],
        "false": ["False", "fls", "no", "fals", "falz"],
    }
    answer = yield session.call("rie.dialogue.ask", question=question, answers=answers)

    yield sleep(1)
    if answer == "true":
        session.call(
            "rom.optional.behaviour.play", name="BlocklyApplause"
        )  # <- predefined behaviour with target word "True"
        yield session.call("rie.dialogue.say", text="That is incorrect!")
    elif answer == "false":  # correct answer
        yield session.call(
            "rie.dialogue.say",
            text="That is correct! Skiing originated in northern Europe and Asia thousands of years ago as a means of transportation. The oldest known skis were found in Russia and date back to around 6000 to 5000 BC",
        )
    else:
        yield session.call(
            "rie.dialogue.say", text="Sorry, but I didn't hear you properly."
        )

    card_detected = yield session.call("rie.vision.card.read")
    print(card_detected[0])
    yield session.call(
        "rie.dialogue.say",
        text="Let's try something different.. Answer my questions using the aruco cards infront of me !",
    )

    dialogue_manager = Dialogue_card()
    # yield session.subscribe(dialogue_manager.on_card, "rie.vision.card.stream")
    # yield session.subscribe(dialogue_manager.ask_geographical_card_question, "rie.vision.card.stream")
    # ask the geography card question
    yield dialogue_manager.ask_geographical_card_question(
        session
    )  # <- aruco cards interaction

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
