from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks 

wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
	}],
	realm="rie.665853e0f26645d6dd2c2e92",
)



@inlineCallbacks
def main(session, details):
    yield session.call(
        "rie.dialogue.say",
        text="Hello!",
    )
    session.leave()



wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
