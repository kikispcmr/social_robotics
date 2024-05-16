import re

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.request import Subscription
from Dialogue import Dialogue
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks

TIMEOUT_TIME = 6000
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6639d599c887f6d074f04f49",
)


@inlineCallbacks
def main(session, details):
    session.subscribe(touched, "rom.sensor.touch.stream")
    yield assigment2_stuff(session)
    session.leave()


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
