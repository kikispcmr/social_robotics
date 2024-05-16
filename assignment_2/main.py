from aruco_actions import DialogueCard
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from dialogue_actions import DialogueBranches
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6639d599c887f6d074f04f49",
)

questions = [
    (
        "Africa is the second largest continent in the world by land area.",
        True,
        "That is correct! Africa is the second largest continent in the world by land area.",
    ),
    (
        "Skiing originated as a mode of transportation in the Alps during the 19th century.",
        False,
        "That is correct! Skiing originated in northern Europe and Asia thousands of years ago as a means of transportation. The oldest known skis were found in Russia and date back to around 6000 to 5000 BC",
        True,
    ),
]


def dialogue_section(session, action_manager, dialogue_manager):

    for question in questions:
        dialogue_manager.smart_question_multiple(questions, action_manager.skiing_motion))


@inlineCallbacks
def main(session, details):
    action_manager = RobotActions(session)
    card_manager = DialogueCard()
    dialogue_manager = DialogueBranches(session)
    session.subscribe(action_manager.touched, "rom.sensor.touch.stream")

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

    # GAME SECTION

    dialogue_section(session, action_manager, dialogue_manager)

    ## END OF DIALOGUE GAME SECTION

    card_detected = yield session.call("rie.vision.card.read")
    print(card_detected[0])
    yield session.call(
        "rie.dialogue.say",
        text="Let's try something different.. Answer my questions using the aruco cards infront of me !",
    )

    # ask the geography card question
    yield card_manager.ask_geographical_card_question(
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


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
