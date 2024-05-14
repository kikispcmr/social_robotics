import re
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.request import Subscription
from Dialogue import Dialogue
from twisted.internet.defer import inlineCallbacks

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.66434106c887f6d074f07e38",
)

@inlineCallbacks
def main(session, details):


    yield session.call("rie.dialogue.say", text="hello!")

    # Define and execute the skiing movement sequence correctly
    yield session.call("rom.actuator.motor.write",
        frames=[{"time": 1200, "data": {"legs.right.upper.pitch": -1.75}},
            {"time": 1200, "data": {"arms.left.upper.pitch": -2.6}},
            {"time": 1200, "data": {"legs.right.upper.pitch": 1.75}},
            {"time": 1200, "data": {"legs.left.upper.pitch": 1.75}}],
            force=True)

    yield session.call("rie.dialogue.say", text="Skiing movement complete!")

    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    yield session.call("rie.dialogue.say", text="Goodbye!")

    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
