import re

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.request import Subscription
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000


class Dialogue:
    def __init__(self):
        pass

    @inlineCallbacks
    def base_smart_question_flow(self, session, questions):
        yield sleep(1)

        print("WE ARE HERE")
        answer = yield session.call(
            "rie.dialogue.ask",
            question=questions[0],
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
    def smart_question_binary(self, session, questions):
        _, answer = self.base_smart_question_flow(session, questions)

        if (answer == "true" and questions[1]) or (
            answer == "false" and not questions[1]
        ):
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
            text = "That is correct." + questions[2]
            yield session.call("rie.dialogue.say", text=text)
        elif (answer == "true" and not questions[1]) or (
            answer == "false" and questions[1]
        ):
            yield session.call("rie.dialogue.say", text="That is incorrect.")

    @inlineCallbacks
    def smart_question_multiple(self, session, question):
        _, answer = self.base_smart_question_flow(session, question)
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
    def smart_question_branching(self, session, question):
        answ = None
        data, answer = self.base_smart_question_flow(session, question)
        for frame in data:
            if frame["data"]["body"]["final"]:
                print(frame)

        if answer == "true":
            text = "That's great! Let's go with some trivia."
            yield session.call("rie.dialogue.say", text=text)
            answ = True
        elif answer == "false":
            yield session.call("rie.dialogue.say", text="No problem, let's continue!")
            answ = False
        else:
            self.smart_question_branching(session, question)

        return answ

    @inlineCallbacks
    def on_keyword(self, frame, session):
        if (
            "certainty" in frame["data"]["body"]
            and frame["data"]["body"]["certainty"] > 0.45
        ):
            yield session.call(
                "rie.dialogue.say",
                text="Great, let us begin!",
            )

    @inlineCallbacks
    def keyword(self, session, statement, keywords):
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
        yield session.subscribe(self.on_keyword, "rie.dialogue.keyword.stream")
        yield session.call("rie.dialogue.keyword.stream")
        yield session.call("rie.dialogue.keyword.clear")
        yield session.call("rie.dialogue.keyword.close")
        return ans, cert, final
