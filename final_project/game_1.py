from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="You have started Game 1. Enjoy!")
    # Game 1 logic here
    session.leave()
