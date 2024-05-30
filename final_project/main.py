from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
import game_1
import game_2
import game_3

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
    }],
    realm="rie.665853e0f26645d6dd2c2e92",
)

@inlineCallbacks
def on_keyword(frame, session):
    if "certainty" in frame["data"]["body"] and frame["data"]["body"]["certainty"] > 0.45:
        keyword = frame["data"]["body"]["text"].lower()
        if "game 1" in keyword:
            yield session.call("rie.dialogue.say", text="Starting Game 1")
            game_1.start_game(session)
        elif "game 2" in keyword:
            yield session.call("rie.dialogue.say", text="Starting Game 2")
            game_2.start_game(session)
        elif "game 3" in keyword:
            yield session.call("rie.dialogue.say", text="Starting Game 3")
            game_3.start_game(session)
        else:
            yield session.call("rie.dialogue.say", text="I didn't understand that. Please say 'Game 1', 'Game 2', or 'Game 3'.")

@inlineCallbacks
def main(session, details):
    yield session.call("rie.dialogue.say", text="Hello! I'm your friendly robot.")
    yield session.call("rie.dialogue.say", text="Which game would you like to play? Please say 'Game 1', 'Game 2', or 'Game 3'.")
    yield session.call("rie.dialogue.keyword.add", keywords=["game 1", "game 2", "game 3"])
    yield session.subscribe(on_keyword, "rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.stream")

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
