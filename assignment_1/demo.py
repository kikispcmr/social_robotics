import re

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.request import Subscription
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 1
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6636524dc887f6d074f03f25",
)

# Questions: (Question asked: string, Question truth: boolean, Trivia Reply: string)
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
def smart_question_flow(session, question):
    yield sleep(1)

    print("WE ARE HERE")
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={
            "true": ["true", "yes", "ja", "tru"],
            "false": ["false", "no", "nej", "fls"],
        },
    )
    print("WE ARE HERE2", answer)
    yield sleep(1)
    data = yield session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)
    print(data, answer)
    return data, answer


@inlineCallbacks
def smart_question_binary(session, question):
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={
            "true": ["true", "yes", "ja", "tru"],
            "false": ["false", "no", "nej", "fls"],
        },
    )
    yield sleep(1)
    data = yield session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)

    if (answer == "true" and question[1]) or (answer == "false" and not question[1]):
        # nod yes
        session.call(
            "rom.actuator.motor.write",
            frames=[
                {"time": 400, "data": {"body.head.pitch": 0.15}},
                {"time": 1200, "data": {"body.head.pitch": -0.15}},
                {"time": 2000, "data": {"body.head.pitch": 0.15}},
                {"time": 2400, "data": {"body.head.pitch": 0.0}},
            ],
            force=True,
        )
        text = "That is correct." + question[2]
        yield session.call("rie.dialogue.say", text=text)
    elif (answer == "true" and not question[1]) or (answer == "false" and question[1]):
        yield session.call("rie.dialogue.say", text="That is incorrect.")


@inlineCallbacks
def smart_question_multiple(session, question):
    _, answer = smart_question_flow(session, question)
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={"true": ["true", "yes", "ja"], "false": ["false", "no", "nej"]},
    )
    yield sleep(1)
    yield session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)

    if answer in question[1]:
        session.call(
            "rom.actuator.motor.write",
            frames=[
                {"time": 400, "data": {"body.head.pitch": 0.15}},
                {"time": 1200, "data": {"body.head.pitch": -0.15}},
                {"time": 2000, "data": {"body.head.pitch": 0.15}},
                {"time": 2400, "data": {"body.head.pitch": 0.0}},
            ],
            force=True,
        )
        text = "That is correct." + question[2]
        yield session.call("rie.dialogue.say", text=text)
    elif answer not in question[1]:
        yield session.call("rie.dialogue.say", text="That is incorrect.")


@inlineCallbacks
def smart_question_branching(session, question):
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={
            "true": ["true", "tru", "yes", "ye"],
            "false": ["false", "no", "na", "nej"],
        },
    )
    yield sleep(1)
    data = yield session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)

    answ = None

    for frame in data:
        if frame["data"]["body"]["final"]:
            print(frame)

    if answer == "true":
        text = "That's great! Let's go with some trivia."
        yield session.call("rie.dialogue.say", text=text)
        answ = True
    elif answer == "false":
        yield session.call("rie.dialogue.say", text="No problem, let's continue!")
        anws = False
    else:
        smart_question_branching(session, question)

    return answ


@inlineCallbacks
def on_keyword(frame, session):
    if (
        "certainty" in frame["data"]["body"]
        and frame["data"]["body"]["certainty"] > 0.45
    ):
        yield session.call(
            "rie.dialogue.say",
            text="Great, let us begin! Answer the following questions with either True or False.",
        )


@inlineCallbacks
def keyword(session, statement, keywords):
    ans = None
    cert = None
    final = None
    yield session.call("rie.dialogue.say", text=statement)
    yield sleep(0.5)
    data = yield session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)
    for frame in data:
        if frame["data"]["body"]["final"]:
            print(frame)
            ans = frame["data"]["body"]["text"]
            cert = frame["data"]["body"]["certainty"]
            final = frame["data"]["body"]["final"]

    yield session.call("rie.dialogue.keyword.add", keywords=keywords)
    yield session.subscribe(on_keyword, "rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.clear")
    yield session.call("rie.dialogue.keyword.close")
    return ans, cert, final


def regex(session, yes_pattern, no_pattern, reply):
    if re.search(yes_pattern, reply):
        # Trivia questions
        yield session.call("rie.dialogue.say", text="Let's start with some trivia!")
        print("START TRIVIA QUESTIONS")
    elif re.search(no_pattern, reply):
        # Continue with normal questions
        yield session.call("rie.dialogue.say", text="Alright, let's continue!")
        print("CONTINUE")
    else:
        # For times it throws a random event from the api
        yield sleep(1)
        yield session.call(
            "rie.dialogue.say",
            text="I'm going to assume you want to keep on playing! We are having so much fun!",
        )


@inlineCallbacks
def main(session, details):
    session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.vision.face.find")
    session.call("rie.vision.face.track")

    first_key = ["start", "yes", "ja", "go", "forward", "play"]
    reply, cert, final = yield keyword(
        session, "Say start when you're ready to play!", first_key
    )

    if final:
        yield session.call("rie.dialogue.say", text="Let's gooo")
        print("We starts")

    yield smart_question_binary(session, questions[0])
    yield smart_question_binary(session, questions[1])
    yield smart_question_binary(session, questions[2])

    answ = yield smart_question_branching(
        session, ["Do you want to try something harder?"]
    )

    if answ:
        yield smart_question_binary(session, trivia[0])
        yield smart_question_binary(session, trivia[1])
        yield smart_question_binary(session, trivia[2])
    else:
        yield smart_question_binary(session, questions[3])
        yield smart_question_binary(session, questions[4])

        yield session.call("rie.dialogue.say", text="Let's change things up.")

        yield smart_question_binary(session, trivia[3])
        yield smart_question_binary(session, trivia[4])

    ### Shall we start with trivia questions?
    second_key = ["like", "I", "question", "one", "last", "about"]
    text = "Which question was your favourite one? Mine was question uhm... I forgot. Ahahaha."
    reply, cert, final = yield keyword(session, text, second_key)
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
