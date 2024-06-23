from twisted.internet.defer import inlineCallbacks
from typing import Tuple
# aruco id mapping - 4 cards
animals_cards = {
    1: ("Giraffe", "Africa"),
    2: ("Panda", "Asia"),
    3: ("Kangaroo", "Australia"),
    4: ("Penguin", "Antarctica"),
}


class ArucoActions:
    """
    A class for handling Aruco card detection and asking questions related to the detected cards.

    Attributes:
        session (object): A session object for interacting with the RIE system.

    Methods:
        wait_for_correct_card(session, correct_card_id):
            Waits for the correct Aruco card to be detected.

        on_card(frame):
            Callback function for handling detected Aruco cards.

        aruco_question(questions, pos_action=None, neg_action=None):
            Asks a question related to an Aruco card and performs actions based on the answer.
    """
    def __init__(self, session):
        """
        Initializes the ArucoActions class.

        Args:
            session (object): A session object for interacting with the RIE system.
        """
        self.session = session

    @inlineCallbacks
    def wait_for_correct_card(self, session, correct_card_id):
        """
        Waits for the correct Aruco card to be detected.

        Args:
            session (object): A session object for interacting with the RIE system.
            correct_card_id (int): The ID of the correct Aruco card.

        Returns:
            bool: True if the correct card is detected, False otherwise.
        """
        print("entered")
        # if we have the correct card
        card_detected = yield session.call("rie.vision.card.read")

        print("card detected : ", card_detected[0]["data"]["body"][0][5])
        print("Correct card id: ", correct_card_id)
        yield session.subscribe(self.on_card, "rie.vision.card.stream")
        yield session.call("rie.vision.card.stream")

        if (
            card_detected[0]["data"]["body"][0][5] == correct_card_id
        ):  
            return True

        print(card_detected[0]["data"]["body"][0][5])

        return False

    def on_card(self, frame):
        """
        Callback function for handling detected Aruco cards.

        Args:
            frame (dict): A dictionary containing information about the detected Aruco card.
        """
        print("Card detected:", frame["data"])

    @inlineCallbacks
    def aruco_question(self, questions: Tuple[str, int, str], pos_action = None, neg_action = None):
        """
        Asks a question related to an Aruco card and performs actions based on the answer.

        Args:
            questions (Tuple[str, int, str]): A tuple containing the question text, the correct card ID, and the response text for a correct answer.
            pos_action (callable, optional): A function to be called if the answer is correct.
            neg_action (callable, optional): A function to be called if the answer is incorrect.

        Returns:
            int: 1 if the answer is correct, 0 otherwise.
        """
        anw = 0
        yield self.session.call("rie.dialogue.say", text=questions[0]) 
        correct_card = yield self.wait_for_correct_card(self.session, questions[1])
        if correct_card:
            yield self.session.call("rie.dialogue.say", text=questions[2])
            anw = 1
            if pos_action is not None:
               yield pos_action
        else:
            yield self.session.call("rie.dialogue.say", text="That is incorrect. Sorry! Let's try another question")
            if neg_action is not None:
                yield neg_action
        return anw



