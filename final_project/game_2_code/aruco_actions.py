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
    def __init__(self, session):
        self.session = session

    @inlineCallbacks
    def wait_for_correct_card(self, session, correct_card_id):
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
        print("Card detected:", frame["data"])

    @inlineCallbacks
    def aruco_question(self, questions: Tuple[str, int, str], pos_action = None, neg_action = None):
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



