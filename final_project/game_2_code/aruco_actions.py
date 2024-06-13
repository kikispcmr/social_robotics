
from twisted.internet.defer import inlineCallbacks


class ArucoActions:

    def __init__(self, session):
        self.session = session
    @inlineCallbacks
    def wait_for_correct_card(self, session, correct_card_id):
        print("entered")
        # if we have the correct card
        card_detected = yield session.call("rie.vision.card.read")

        print("card detected : ", card_detected[0]['data']['body'][0][5])
        yield session.subscribe(self.on_card, "rie.vision.card.stream")
        yield session.call("rie.vision.card.stream")
        
        if card_detected[0]['data']['body'][0][5] == correct_card_id: # check that the id is correct
            return True
        return False

    @inlineCallbacks
    def on_card(self, frame):
        print("Card detected:", frame["data"])

        for card_id, (animal, location) in animals_cards.items():
            correct = False
            attempts = 0
            max_attempts = 2  # set a max number of attempts per question
            question = f"Where do {animal}s live?"

            while not correct and attempts < max_attempts:
                if attempts > 0:  # ask the question, if not first attempt, provide feedback
                    yield session.call("rie.dialogue.say", text="Try one more time. " + question)
                else:
                    yield session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_card(session, card_id)

                print("exited")
                if correct:
                    yield session.call("rie.dialogue.say", text=f"Correct! {animal}s live in {location}.")
                else:
                    yield session.call("rie.dialogue.say", text="That's not the right card.")
                
                attempts += 1

            if not correct:
                yield session.call("rie.dialogue.say", text=f"The correct answer is {location} where {animal}s live.")

