from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000

class DialogueActions:
    """
    This class contains methods for handling dialogue branches in a conversation.
    """

    def __init__(self, session):
        """
        Initialize the DialogueBranches class.

        Args:
            session: The current session.
        """
        self.session = session

    @inlineCallbacks
    def base_smart_question_flow(self, questions):
        """
        Ask a question and return the answer and data.

        Args:
            questions: A list of questions.

        Returns:
            A tuple containing the data and the answer.
        """
        answer = yield self.session.call(
            "rie.dialogue.ask",
            question=questions[0],
            answers={
                "true": ["true", "yes", "ja", "tru"],
                "false": ["false", "no", "nej", "fls"],
            },
        )
        data = yield self.session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)
        return data, answer

    @inlineCallbacks
    def target_smart_question_flow(self, questions):
        """
        Ask a question and return the answer and data.

        Args:
            questions: A list of questions.

        Returns:
            A tuple containing the data and the answer.
        """
        answer = yield self.session.call(
            "rie.dialogue.ask",
            question=questions[0],
            answers={
                "true": ["true", "yes", "ja", "tru"],
                "false": ["false", "no", "nej", "fls"],
            },
        )
        data = yield self.session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)
        if (answer == questions[1]):
            yield self.nod_and_say("That is correct." + questions[2])
        elif (answer != questions[1]):
            yield self.session.call("rie.dialogue.say", text="That is incorrect.")

    # NICE TO HAVE
    @inlineCallbacks
    def nod_and_say(self, text):
        """
        Make the robot nod and say a given text.

        Args:
            text: The text to say.
        """
        self.session.call(
            "rom.actuator.motor.write",
            frames=[
                {"time": 400, "data": {"body.head.pitch": 0.15}},
                {"time": 1200, "data": {"body.head.pitch": -0.15}},
                {"time": 2000, "data": {"body.head.pitch": 0.15}},
                {"time": 2400, "data": {"body.head.pitch": 0.0}},
            ],
            force=True,
        )
        yield self.session.call("rie.dialogue.say", text=text)

    def monologue(self, questions):
        """
        Make the robot say a given text.

        Args:
            text: The text to say.
        """
        for text in questions:
            yield self.session.call("rie.dialogue.say", text=text)

    # KEEP | THIS ONE IS IMPORTANT
    @inlineCallbacks
    def smart_question_binary(self, questions, score):
        """
        Ask a binary question and perform an action based on the answer.

        Args:
            questions: A list of questions.
            action: The action to perform.
        """
        print(questions)
        answer = yield self.base_smart_question_flow(questions)
        answer = answer[-1]
        print("THIS", answer)

        if (answer == "true" and questions[1]) or (answer == "false" and not questions[1]):
            yield self.nod_and_say("That is correct." + questions[2])
            score += 1
        elif (answer == "true" and not questions[1]) or (answer == "false" and questions[1]):
            yield self.session.call("rie.dialogue.say", text=questions[3])
            score = 0

        return score

    # KEEP 
    @inlineCallbacks
    def smart_question_branching(self, session, question):
        """
        Ask a question and branch the dialogue based on the answer.

        Args:
            session: The current session.
            question: The question to ask.

        Returns:
            The answer to the question.
        """
        answer = None
        answer = yield self.base_smart_question_flow([question])
        answer = answer[-1]

        if answer == "true":
            yield session.call("rie.dialogue.say", text="That's great! Let's go!")
            answer = True
        elif answer == "false":
            yield session.call("rie.dialogue.say", text="No problem, let's continue!")
            answer = False
        else:
            self.smart_question_branching(session, question)

        return answer

    @inlineCallbacks
    def on_keyword(self, frame, session):
        """
        Perform an action when a keyword is detected.

        Args:
            frame: The current frame.
            session: The current session.
        """
        if "certainty" in frame["data"]["body"] and frame["data"]["body"]["certainty"] > 0.45:
            yield session.call("rie.dialogue.say", text="Great, let us begin!")

    @inlineCallbacks
    def keyword(self, session, statement, keywords):
        """
        Add keywords to the dialogue and perform an action when a keyword is detected.

        Args:
            session: The current session.
            statement: The statement to say.
            keywords: The keywords to add.

        Returns:
            A list of frames.
        """
        yield session.call("rie.dialogue.say", text=statement)
        data = yield session.call("rie.dialogue.stt.read", time=TIMEOUT_TIME)
        frames = [(frame["data"]["body"]["text"], frame["data"]["body"]["certainty"], frame["data"]["body"]["final"]) for frame in data if frame["data"]["body"]["final"]]

        yield session.call("rie.dialogue.keyword.add", keywords=keywords)
        yield session.subscribe(self.on_keyword, "rie.dialogue.keyword.stream")
        yield session.call("rie.dialogue.keyword.stream")
        yield session.call("rie.dialogue.keyword.clear")
        yield session.call("rie.dialogue.keyword.close")
        return frames
