from twisted.internet.defer import inlineCallbacks

# aruco id mapping - 4 cards
animals_cards = {
    1: ("Giraffe", "Africa"),
    2: ("Panda", "Asia"),
    3: ("Kangaroo", "Australia"),
    4: ("Penguin", "Antarctica"),
}


class Dialogue_card:
    def __init__(self):
        pass

    @inlineCallbacks
    def ask_geographical_card_question(self, session):
        session.call("rie.vision.card.stream")

        # We ask the question based on animal_cards mapping
        for card_id, (animal, location) in animals_cards.items():
            correct = False
            attempts = 0
            max_attempts = 1  # set a max number of attempts per question
            question = f"Where do {animal}s live?"

            while not correct and attempts < max_attempts:
                # ask the question, if not first attempt, provide feedback

                if attempts > 0:
                    yield session.call(
                        "rie.dialogue.say", text="Try one more time. " + question
                    )
                else:
                    yield session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_card(session, card_id)

                if correct:
                    yield session.call(
                        "rie.dialogue.say",
                        text=f"Correct! {animal}s live in {location}.",
                    )
                else:
                    yield session.call(
                        "rie.dialogue.say", text="That's not the right card."
                    )

                attempts += 1
            if not correct:
                yield session.call(
                    "rie.dialogue.say",
                    text=f"The correct answer is {location} where {animal}s live.",
                )

    @inlineCallbacks
    def wait_for_correct_card(self, session, correct_card_id):
        print("entered")
        # if we have the correct card
        card_detected = yield session.call("rie.vision.card.read")

        print(card_detected[0])
        yield session.subscribe(self.on_card, "rie.vision.card.stream")
        yield session.call("rie.vision.card.stream")

        if card_detected[0] == correct_card_id:  # check that the id is correct
            return True
        return False

    def on_card(self, frame):
        print("Card detected:", frame["data"])
