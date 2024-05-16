import re
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.request import Subscription
from Dialogue import Dialogue
from twisted.internet.defer import inlineCallbacks

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6645d117f26645d6dd2bcaf7",
)

@inlineCallbacks
def main(session, details):


    yield session.call("rie.dialogue.say", text="hello!")
    
    # nod yes
    session.call(
        "rom.actuator.motor.write",
        frames=[
            {"time": 400, "data": {"body.head.pitch": 0.15}},
            {"time": 1200, "data": {"body.head.pitch": -0.15}},
            {"time": 2000, "data": {"body.head.pitch": 0.15}},
            {"time": 2400, "data": {"body.head.pitch": 0.0}},
        ],
        force=True,
    )

    #test1
    # Define and execute the skiing movement sequence correctly. For some reason, part of the time legs not moving.
    yield session.call("rom.actuator.motor.write",
        frames=[{"time": 400, "data": {"body.legs.right.upper.pitch": -1.75}},
            {"time": 1200, "data": {"body.arms.left.upper.pitch": -2.6}},
            #{"time": 2000, "data": {"body.legs.right.upper.pitch": 1.75}},
            #{"time": 2400, "data": {"body.legs.left.upper.pitch": 1.75}}
            ],
            force=True)
    
    #test2
    yield session.call("rom.actuator.motor.write",
        frames=[
            # starting position
            {"time": 1000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
            
            # right ski push
            {"time": 2000, "data": {"body.legs.right.upper.pitch": -0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5,"body.arms.left.upper.pitch": -1.0}},
            
            # return to middle
            {"time": 3000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
            
            # left ski push
            {"time": 4000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": -0.5, "body.arms.right.upper.pitch": -1.0, "body.arms.left.upper.pitch": -0.5}},
            
            # return to starting position
            {"time": 5000, "data": {"body.legs.right.upper.pitch": 0.5, "body.legs.left.upper.pitch": 0.5, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}}
        ],
        force=True)


    yield session.call("rie.dialogue.say", text="Skiing movement complete!")

    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    yield session.call("rie.dialogue.say", text="Goodbye!")

    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
