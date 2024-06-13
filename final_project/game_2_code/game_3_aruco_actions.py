from twisted.internet.defer import inlineCallbacks

# aruco id mapping - 4 cards
animals_cards = {
    1: ("Giraffe", "Africa"),
    2: ("Panda", "Asia"),
    3: ("Kangaroo", "Australia"),
    4: ("Penguin", "Antarctica"),
}


class ArucoActions:
    def __init__(self):
        pass

    @inlineCallbacks
    def wait_for_correct_card(self, session, correct_card_id):
        print("entered")
        # if we have the correct card
        card_detected = yield session.call("rie.vision.card.read")

        print("card detected : ", card_detected[0]["data"]["body"][0][5])
        yield session.subscribe(self.on_card, "rie.vision.card.stream")
        yield session.call("rie.vision.card.stream")

        if (
            card_detected[0]["data"]["body"][0][5] == correct_card_id
        ):  # check that the id is correct
            return True
        return False

    def on_card(self, frame):
        print("Card detected:", frame["data"])
