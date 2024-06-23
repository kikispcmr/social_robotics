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
"""
A list of dictionaries representing a sad emotion animation sequence.

- "time": The time in milliseconds at which the animation frame should be executed.
- "data": A dictionary containing the joint positions for the robot's head and arms.

The animation sequence starts with the head and arms in a neutral position and then moves them
towards the face to simulate a sad expression.
"""
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
"""
A list of dictionaries representing a positive emotion animation sequence.

- "time": The time in milliseconds at which the animation frame should be executed.
- "data": A dictionary containing the joint positions for the robot's head and arms.

The animation sequences starts with the robot's arms in a neutral position and then moves them
into the air, swinging in a happy manner. 
"""

class RobotActions:
    """
    A class for performing robot actions and animations.

    Attributes:
        session (object): A session object for interacting with the robot.
        movements (dict): A dictionary mapping emotion names to animation sequences.
        pre_movements (dict): A dictionary mapping names to pre-built robot movements.

    Methods:
        motion(movement):
            Performs a specific animation sequence based on the provided emotion name.
        prebuilt_motion(movement):
            Performs a pre-built robot movement based on the provided name.
    """
    def __init__(self, session):
        """
        Initializes the RobotActions class.

        Args:
            session (object): A session object for interacting with the robot.
        """
        self.session = session
        self.movements = {
            "negative": sad_emotion,
            "positive" : positive_emotion,
        }

        self.pre_movements = {
            "neutral": "BlocklyStand",
            "disco": "BlocklyDiscoDance",
            "up" : "ArmsUp",
            "kiss" : "air_kiss_avatar"
        }
    
    # Perform a specific movement from the internal dictionary of pre-built movements 
    @inlineCallbacks
    def motion(self, movement: str):
        """
        Performs a specific animation sequence based on the provided emotion name.

        Args:
            movement (str): The name of the emotion for which to perform the animation sequence.
        """
        yield self.session.call("rom.actuator.motor.write", frames=self.movements[movement], force=True)

    @inlineCallbacks
    def prebuilt_motion(self, movement: str):
        """
        Performs a pre-built robot movement based on the provided name.

        Args:
            movement (str): The name of the pre-built movement to perform.
        """
        yield self.session.call("rom.optional.behavior.play", name=self.pre_movements[movement])

