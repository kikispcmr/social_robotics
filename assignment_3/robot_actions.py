from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep


positive_movement = [
    # starting position
        {
            "time": 400,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
            },
        },
        {
            "time": 1000,
            "data": {
                "body.arms.right.lower.roll": -1.0,
                "body.arms.left.lower.roll": 1.0,
            },
        },
        """{
            "time": 2000,
            "data": {
                "body.arms.right.upper.pitch": 1.0,
                "body.arms.left.upper.pitch": -1.0,
            },
        },
        # return to starting position
        {
            "time": 2400,
            "data": {
                "body.arms.right.upper.pitch": -0.5,
                "body.arms.left.upper.pitch": -0.5,
            },
        },"""
   ]


sad_emotion = [
    {
        "time": 400,
        "data": {
            "body.head.pitch": -0.175,
            "body.arms.left.upper.pitch": -1.0,
            "body.arms.right.upper.pitch": -1.0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0,
        },
    },
    {
        "time": 1400,
        "data": {
            "body.head.pitch": 0.175,
            "body.arms.left.upper.pitch": -1.5,
            "body.arms.right.upper.pitch": -1.5,
            "body.arms.left.lower.roll": -1.75,
            "body.arms.right.lower.roll": -1.75,
        },
    },
    {
        "time": 2000,
        "data": {
            "body.head.pitch": 0.175,
            "body.arms.left.upper.pitch": -1.5,
            "body.arms.right.upper.pitch": -1.5,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0,
        },
    },
    {
        "time": 2400,
        "data": {
            "body.head.pitch": 0.0,
            "body.arms.left.upper.pitch": -1.0,
            "body.arms.right.upper.pitch": -1.0,
            "body.arms.left.lower.roll": 2.0,
            "body.arms.right.lower.roll": 2.0,
        },
    },
    {
        "time": 3000,
        "data": {
            "body.head.pitch": 0,
            "body.arms.left.upper.pitch": 0,
            "body.arms.right.upper.pitch": 0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0,
        },
    }
]

# happy sound option :P https://audio.jukehost.co.uk/lezvtSmppReALoBM2qHEly1ZICpNKs6t

class RobotActions:

    def __init__(self, session):
        self.session = session
        self.movements = {
            "sad": sad_emotion,
        }

    def touched(self, frame):
        if (
            "body.head.front" in frame["data"]
            or "body.head.middle" in frame["data"]
            or "body.head.rear" in frame["data"]
        ):
            # yield call("rie.dialogue.say", text="Ouch! Please don't touch me!")
            print("touch")

    @inlineCallbacks
    # Perform a specific movement from the internal dictionary of pre-built movements (made by us)
    def motion(self, movement: str):
        yield self.session.call("rom.actuator.motor.write", frames=self.movements[movement], force=True)

    @inlineCallbacks
    def move_sad(self):
        # start audio stream
        yield self.session.call("rom.actuator.audio.stream",
            url="https://audio.jukehost.co.uk/SVmmjrrjwLIlNx6wu2yVy5skfTOZpxhg",
            sync=False
        )
        print("Audio started")
        
        # do the movement
        yield self.motion("sad")
        print("Sad movement completed")
        
        # stop the audio
        yield sleep(5)  # keep playing audio for 5 secs
        yield self.session.call("rom.actuator.audio.stop")
        print("Audio stopped")
