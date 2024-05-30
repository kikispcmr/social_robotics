from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="You have started Game 2. Have fun!")
    session.leave()
