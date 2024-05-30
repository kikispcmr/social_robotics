from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

# define the mapping of Aruco card IDs to animals and their locations - example
animals_cards = {
    1: ("Giraffe", "Africa"),
    2: ("Panda", "Asia"),
    3: ("Kangaroo", "Australia"),
    4: ("Penguin", "Antarctica")
}

@inlineCallbacks
def on_card(frame, session, expected_card_id):
    # check if the correct card is shown
    for card in frame["data"]["body"]:
        if card[5] == expected_card_id:
            yield session.call("rie.dialogue.say", text=f"Correct! This card represents a {animals_cards[expected_card_id][0]}.")
            return True
    return False

@inlineCallbacks
def ask_question(session, animal, card_id):
    question = f"Where do {animal}s live?"
    yield session.call("rie.dialogue.say", text=question)
    yield sleep(1)

    # start card detection stream
    yield session.call("rie.vision.card.stream")
    correct = False
    attempts = 0
    max_attempts = 3  # Set a max number of attempts per question

    while not correct and attempts < max_attempts:
        # Listen for the card input
        frame = yield session.call("rie.vision.card.read", time=6000)
        correct = yield on_card(frame, session, card_id)
        if not correct:
            attempts += 1
            if attempts < max_attempts:
                yield session.call("rie.dialogue.say", text="That's not the right card. Try again!")
            else:
                yield session.call("rie.dialogue.say", text=f"The correct answer is {animals_cards[card_id][1]}, where {animal}s live.")

@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="You have started Game 1. Enjoy!")
    yield sleep(1)
    
    for card_id, (animal, location) in animals_cards.items():
        yield ask_question(session, animal, card_id)
    
    yield session.call("rie.dialogue.say", text="You have completed the game. Great job!")
    session.leave()
