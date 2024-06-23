# Shared code

from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

# Defines the sequence of movements for a sad emotion.
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

# Defines the sequence of movements for a positive emotion.
positive_emotion = [
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
    """
    A class which helps with handling different robot actions, like movement and audio control.

    Attributes:
        session: The session object for communicating with the robot.
        movements: A dictionary mapping emotion types to their respective movement sequences.
    """
    def __init__(self, session):
        self.session = session
        self.movements = {
            "negative": sad_emotion,
            "positive" : positive_emotion,
        }


    @inlineCallbacks
    def motion(self, movement: str):
        """
        Perform a specific movement from the internal dictionary of pre-built movements.

        Args:
            movement (str): The type of movement to perform ('negative' or 'positive').
        """
        yield self.session.call("rom.actuator.motor.write", frames=self.movements[movement], force=True)



    @inlineCallbacks
    # Adjust intensity based on the intensity factor from the drive
    def intensity_volume(self, intensity):
        """
        Adjusts the volume based on the intensity factor.

        Args:
            intensity (float): The intensity factor to set the volume level.
        """
        loudness = round(intensity * 100)
        yield self.session.call("rom.actuator.audio.volume", volume = loudness)



    @inlineCallbacks
    def move_negative(self, intensity = -0.5):
        """
        Performs negative movement with associated audio.

        Args:
            intensity (float): The intensity factor for the movement and volume.
        """

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
        """
        Performs positive movement with associated audio.

        Args:
            intensity (float): The intensity factor for the movement and volume.
        """
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
        """
        Makes the robot be in a neutral standing position.
        """
        yield self.session.call("rom.optional.behavior.play", name="BlocklyStand")

 
    @inlineCallbacks
    def wave_arm(self):
        """
        Makes the robot wave it's arm.
        """
        yield self.session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
