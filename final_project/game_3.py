from twisted.internet.defer import inlineCallbacks

@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="You have started Game 3. Good luck!")
    # Game 3 logic here
    session.leave()
