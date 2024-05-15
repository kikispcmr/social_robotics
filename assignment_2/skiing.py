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
    
    #test1
    # Define and execute the skiing movement sequence correctly. For some reason, part of the time legs not moving.
    yield session.call("rom.actuator.motor.write",
        frames=[{"time": 1200, "data": {"legs.right.upper.pitch": -1.75}},
            {"time": 1200, "data": {"arms.left.upper.pitch": -2.6}},
            {"time": 1200, "data": {"legs.right.upper.pitch": 1.75}},
            {"time": 1200, "data": {"legs.left.upper.pitch": 1.75}}],
            force=True)
    
    #test2
    yield session.call("rom.actuator.motor.write",
        frames=[
            # starting position
            {"time": 1000, "data": {"legs.right.upper.pitch": 0.5, "legs.left.upper.pitch": 0.5, "arms.right.upper.pitch": -0.5, "arms.left.upper.pitch": -0.5}},
            
            # right ski push
            {"time": 2000, "data": {"legs.right.upper.pitch": -0.5, "arms.left.upper.pitch": -1.0}},
            
            # return to middle
            {"time": 3000, "data": {"legs.right.upper.pitch": 0.5, "legs.left.upper.pitch": 0.5, "arms.right.upper.pitch": -0.5, "arms.left.upper.pitch": -0.5}},
            
            # left ski push
            {"time": 4000, "data": {"legs.left.upper.pitch": -0.5, "arms.right.upper.pitch": -1.0}},
            
            # return to starting position
            {"time": 5000, "data": {"legs.right.upper.pitch": 0.5, "legs.left.upper.pitch": 0.5, "arms.right.upper.pitch": -0.5, "arms.left.upper.pitch": -0.5}}
        ],
        force=True)


    yield session.call("rie.dialogue.say", text="Skiing movement complete!")

    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    yield session.call("rie.dialogue.say", text="Goodbye!")

    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
