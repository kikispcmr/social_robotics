from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6633488cc887f6d074f02eeb",
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
def smart_question_binary(session, question):
    """
    Asks a binary (True/False) question to the user and provides feedback based on the user's answer.

    Args:
        session (autobahn.twisted.component.Component): The WAMP session object.
        question (tuple): A tuple containing the question text, the correct answer (True or False), and a trivia reply.

    Returns:
        None
    """
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
    _ = yield session.call("rie.dialogue.stt.read", time=6000)

    if (answer == "true" and question[1]) or (answer == "false" and not question[1]):
        # Nod yes
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


def smart_question_multiple(session, question):
    """
    Asks a multiple-choice question to the user and provides feedback based on the user's answer.

    Args:
        session (autobahn.twisted.component.Component): The WAMP session object.
        question (tuple): A tuple containing the question text, a list of correct answers, and a trivia reply.

    Returns:
        None
    """
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={"true": ["true", "yes", "ja"], "false": ["false", "no", "nej"]},
    )
    yield sleep(1)
    _ = yield session.call("rie.dialogue.stt.read", time=6000)

    if answer in question[1]:
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
    elif answer not in question[1]:
        yield session.call("rie.dialogue.say", text="That is incorrect.")


@inlineCallbacks
def smart_question_branching(session):
    """
    Asks the user if they want to try something harder and branches the flow based on the user's answer.

    Args:
        session (autobahn.twisted.component.Component): The WAMP session object.

    Returns:
        bool: True if the user wants to try something harder, False otherwise.
    """
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question="Do you want to try something harder?",
        answers={
            "true": ["true", "tru", "yes", "ye"],
            "false": ["false", "no", "na", "nej"],
        },
    )
    yield sleep(1)
    _ = yield session.call("rie.dialogue.stt.read", time=6000)
    answ = None

    # If true we do a different set of questions, if false continue, otherwise ask again
    if answer == "true":
        text = "That's great! Let's go with some trivia."
        yield session.call("rie.dialogue.say", text=text)
        answ = True
    elif answer == "false":
        yield session.call("rie.dialogue.say", text="No problem, let's continue!")
        answ = False
    else:
        smart_question_branching(session)

    return answ


# Handles keyword input
@inlineCallbacks
def on_keyword(frame, session):
    """
    Callback function for the keyword event.

    Args:
        frame (dict): The frame containing the detected keyword and its certainty.
        session (autobahn.twisted.component.Component): The WAMP session object.

    Returns:
        None
    """
    if (
        "certainty" in frame["data"]["body"]
        and frame["data"]["body"]["certainty"] > 0.45
    ):
        yield session.call(
            "rie.dialogue.say",
            text="Great, let us begin! Answer the following questions with either True or False.",
        )


# Run keyword question by the robot
@inlineCallbacks
def keyword(session, statement, keywords):
    """
    Asks the user a statement and waits for a keyword response.

    Args:
        session (autobahn.twisted.component.Component): The WAMP session object.
        statement (str): The statement to present to the user.
        keywords (list): A list of keywords to listen for.

    Returns:
        tuple: A tuple containing the user's response, the certainty of the response, and a boolean indicating if the response is final.
    """
    ans = None
    cert = None
    final = None
    yield session.call("rie.dialogue.say", text=statement)
    yield sleep(0.5)
    data = yield session.call("rie.dialogue.stt.read", time=6000)
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


@inlineCallbacks
def main(session, _):
    """
    The main function that runs the dialogue flow.

    Args:
        session (autobahn.twisted.component.Component): The WAMP session object.
        _ (Any): An unused argument required by the autobahn library.

    Returns:
        None
    """
    session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.vision.face.find")
    session.call("rie.vision.face.track")

    # Start of Dialogue flow
    first_key = ["start", "yes", "ja", "go", "forward", "play"]
    _, _, final = yield keyword(
        session, "Say start when you're ready to play!", first_key
    )

    if final:
        yield session.call("rie.dialogue.say", text="Let's go!")

    # Basic question track with additional trivia replies
    yield smart_question_binary(session, questions[0])
    yield smart_question_binary(session, questions[1])
    yield smart_question_binary(session, questions[2])

    # Branching question: If true then do trivia questions otherwise continue regular questions
    answ = yield smart_question_branching(session)

    if answ:
        yield smart_question_binary(session, trivia[0])
        yield smart_question_binary(session, trivia[1])
        yield smart_question_binary(session, trivia[2])
    else:
        # We do two more questions
        yield smart_question_binary(session, questions[3])
        yield smart_question_binary(session, questions[4])

        yield session.call("rie.dialogue.say", text="Let's change things up.")
        # Then we do the trivia question regardless
        yield smart_question_binary(session, trivia[0])
        yield smart_question_binary(session, trivia[1])
        yield smart_question_binary(session, trivia[2])
        yield smart_question_binary(session, trivia[3])
        yield smart_question_binary(session, trivia[4])

    # Ask what were the user's favourite exercise was
    second_key = ["like", "I", "question", "one", "last", "about"]
    text = "Which question was your favourite one? Mine was question uhm... I forgot. Ahahaha."
    _, _, final = yield keyword(session, text, second_key)

    if final:
        yield session.call("rie.dialogue.say", text="That's a good one! I love it.")

    yield session.call("rie.dialogue.say", text="You reached the end! Great job.")

    # Cute final animations
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
