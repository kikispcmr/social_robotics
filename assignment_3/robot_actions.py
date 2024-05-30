from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

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
            "body.arms.left.upper.pitch": -2.6,
            "body.arms.right.upper.pitch": -2.6,
            "body.arms.left.lower.roll": -1.75,
            "body.arms.right.lower.roll": -1.75,
        },
    },
    {
        "time": 2000,
        "data": {
            "body.head.pitch": 0.175,
            "body.arms.left.upper.pitch": -1.0,
            "body.arms.right.upper.pitch": -1.0,
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
            "body.head.pitch": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0,
        },
    }
]

positive_emotion = [
    # starting position
        {
            "time": 400,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 0,
                "body.arms.left.lower.roll": 0
            },
        },
        {
            "time": 1000,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 0.0,
                "body.arms.left.lower.roll": 0.0
            },
        },
        {
            "time": 1400,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 1.0,
                "body.arms.left.lower.roll": -1.0
            },
        },
        {
            "time": 1800,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": -1.0,
                "body.arms.left.lower.roll": 1.0
            },
        },
        {
            "time": 2200,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 1.0,
                "body.arms.left.lower.roll": -1.0
            },
        },
                {
            "time": 2600,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": -1.0,
                "body.arms.left.lower.roll": 1.0
            },
        },
        {
            "time": 3000,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 0.0,
                "body.arms.left.lower.roll": 0.0
            },
        },
        {
            "time": 3400,
            "data": {
                "body.arms.right.upper.pitch": 0,
                "body.arms.left.upper.pitch": 0,
                "body.arms.right.lower.roll": 0.0,
                "body.arms.left.lower.roll": 0.0
            },
        }
   ]

class RobotActions:

    def __init__(self, session):
        self.session = session
        self.movements = {
            "negative": sad_emotion,
            "positive" : positive_emotion,
        }
    
    # Perform a specific movement from the internal dictionary of pre-built movements 
    @inlineCallbacks
    def motion(self, movement: str):
        yield self.session.call("rom.actuator.motor.write", frames=self.movements[movement], force=True)

    @inlineCallbacks
    # Adjust intensity based on the intensity factor from the drive
    def intensity_volume(self, intensity):
        loudness = round(intensity * 100)
        yield self.session.call("rom.actuator.audio.volume", volume = loudness)

    @inlineCallbacks
    def move_negative(self, intensity = -0.5):

        self.intensity_volume(intensity)
        # start audio stream
        yield self.session.call("rom.actuator.audio.stream",
            url="https://audio.jukehost.co.uk/SVmmjrrjwLIlNx6wu2yVy5skfTOZpxhg",
            sync=False
        )
        
        # do the movement
        yield self.motion("negative")
        
        # stop the audio
        yield sleep(5)  # keep playing audio for 5 secs
        yield self.session.call("rom.actuator.audio.stop")



    @inlineCallbacks
    def move_positive(self, intensity = -0.5):
        self.intensity_volume(intensity)
        # start audio stream
        yield self.session.call("rom.actuator.audio.stream",
            url="https://audio.jukehost.co.uk/lezvtSmppReALoBM2qHEly1ZICpNKs6t",
            sync=False
        )

        yield self.motion("positive")

        # stop audio
        yield sleep(1)
        yield self.session.call("rom.actuator.audio.stop")


    @inlineCallbacks
    def move_neutral(self):
        # simply stands
        yield self.session.call("rom.optional.behavior.play", name="BlocklyStand")

 
