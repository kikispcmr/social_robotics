from aruco_actions import DialogueCard
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from robot_actions import RobotActions
from twisted.internet.defer import inlineCallbacks

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.664f05bdf26645d6dd2bfb28",
)

def main(session, details):
    action_manager = RobotActions(session)
    action_manager.motion("pos")
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])



