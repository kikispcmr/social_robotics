import re

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.request import Subscription
from Dialogue import Dialogue
from twisted.internet.defer import inlineCallbacks

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.66434106c887f6d074f07e38",
)

questions = [
    (
        "Africa is the second largest continent in the world by land area.",
        True,
        "Did you know there are giraffes in Africa!",
    ),
    (
        "The capital of Japan is Tokyo.",
        True,
        "Did you know Tokyo has 14 million people living in it! That's amazing isn't it.",
    ),
    (
        "The Amazon Rainforest is located in South America.",
        True,
        "The Amazon Rainforest is the largest tropical rainforest in the world, spanning across nine different countries!",
    ),
    (
        "Antarctica is the smallest continent on Earth.",
        False,
        "Australia, not Antarctica, is the smallest continent by land area, despite Antarctica having the smallest population due to its harsh environment.",
    ),
    (
        "Mount Everest is the tallest mountain in the world.",
        True,
        "While Mount Everest is the highest mountain above sea level at 8,848 meters, it is not the tallest mountain when measured from base to peak. Some mountains, such as Mauna Kea in Hawaii, are taller than Everest when considering their total height from base to peak.",
    ),
]

# Trivia (Question: string, Correct Answer: string)
trivia = [
    ("Where are there giraffes?", "Africa"),
    ("What is the capital of Japan?", "Tokyo"),
    ("What is the biggest tropical rainforest in the world?", "Amazon"),
    ("What continent has the smallest population?", "Antartica"),
    ("What is the smallest continent in the world?", "Australia"),
]


change_flow = [("Do you want to continue or change the game up?", True)]


@inlineCallbacks
def main(session, details):
    dialogue_manager = Dialogue()

    session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.vision.face.find")
    session.call("rie.vision.face.track")

    first_key = ["start", "yes", "ja", "go", "forward", "play"]

    reply, _, final = yield dialogue_manager.keyword(
        session, "Say start when you're ready", first_key
    )
    if final:
        yield session.call("rie.dialogue.say", text="Let's gooo")
        print("We starts")

    yield dialogue_manager.smart_question_binary(session, questions[0])
    yield dialogue_manager.smart_question_binary(session, questions[1])
    yield dialogue_manager.smart_question_binary(session, questions[2])

    answ = yield dialogue_manager.smart_question_branching(
        session, ["Do you want to try something harder?"]
    )

    if answ:
        yield dialogue_manager.smart_question_binary(session, trivia[0])
        yield dialogue_manager.smart_question_binary(session, trivia[1])
        yield dialogue_manager.smart_question_binary(session, trivia[2])
    else:
        yield dialogue_manager.smart_question_binary(session, questions[3])
        yield dialogue_manager.smart_question_binary(session, questions[4])

        yield session.call("rie.dialogue.say", text="Let's change things up.")

        yield dialogue_manager.smart_question_binary(session, trivia[3])
        yield dialogue_manager.smart_question_binary(session, trivia[4])

    ### Shall we start with trivia questions?
    second_key = ["like", "I", "question", "one", "last", "about"]
    text = "Which question was your favourite one? Mine was question uhm... I forgot. Ahahaha."
    reply, cert, final = yield dialogue_manager.keyword(session, text, second_key)
    if final:
        yield session.call("rie.dialogue.say", text="That's a good one! I love it.")

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
