from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import game_1 # mathias
from game_2_code.game_2 import start_game # kyriakos
from game_3_code import game_3 # vic

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
    }],
    realm="rie.666aab97961f249628fc26eb",
)

@inlineCallbacks
def ask_game_choice(session):
    yield session.call("rie.dialogue.say", text="Which game would you like to play? Please say 'Game 1', 'Game 2', or 'Game 3'.")
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question="Which game would you like to play?",
        answers={
            "game 1": ["game 1", "one", "game one", "first game"],
            "game 2": ["game 2", "two", "game two", "second game"],
            "game 3": ["game 3", "three", "game three", "third game"],
        },
    )
    yield sleep(1)
    _ = yield session.call("rie.dialogue.stt.read", time=6000)
    return answer

@inlineCallbacks
def vic_code(session, details):
    print("Here")
    # start by looking at the face
    yield session.call("rie.vision.face.find")
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    
    # introduction
    yield session.call("rie.dialogue.say", text="Hello! I'm your friendly robot. My name is Alpha Mini.")
    yield sleep(1)
    yield session.call("rie.dialogue.say", text="I can help you learn about geography through fun games.")
    yield sleep(1)
    yield session.call("rie.dialogue.say", text="Did you know that the Amazon Rainforest is the largest tropical rainforest in the world? It spans across nine countries!")
    yield sleep(2)
    yield session.call("rie.dialogue.say", text="Now, let's have some fun together!")
    
    # ask user to choose a game
    answer = yield ask_game_choice(session)
    
    if answer == "game 1":
        yield session.call("rie.dialogue.say", text="Starting Game 1")
        yield game_1.start_game(session)
    elif answer == "game 2":
        yield session.call("rie.dialogue.say", text="Starting Game 2")
        yield game_2.start_game(session)
    elif answer == "game 3":
        yield session.call("rie.dialogue.say", text="Starting Game 3")
        yield game_3.start_game(session)
    else:
        yield session.call("rie.dialogue.say", text="I didn't understand that. Please say 'Game 1', 'Game 2', or 'Game 3'.")

@inlineCallbacks
def main(session, details):
    print("Starting the game")
    yield vic_code(session, details)
    session.leave()


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
