from twisted.internet.defer import inlineCallbacks

class TouchActions:
    """
    A class for handling touch sensor actions on a robot.

    Attributes:
        session (object): A session object for interacting with the robot.
        touch_mapping (dict): A dictionary mapping touch sensor names to their corresponding sensor IDs.

    Methods:
        is_touched(frame, target):
            Checks if the specified touch sensor is touched based on the received sensor data frame.
        touch(target):
            Subscribes to the touch sensor stream for the specified target sensor.
    """

    def __init__(self, session):
        """
        Initializes the TouchActions class.

        Args:
            session (object): A session object for interacting with the robot.
        """
        self.session = session
        self.touch_mapping = {
            "front": "body.head.front",
            "middle": "body.head.middle",
            "rear": "body.head.rear",
        }

    @inlineCallbacks
    def is_touched(self, frame, target):
        """
        Checks if the specified touch sensor is touched based on the received sensor data frame.

        Args:
            frame (dict): A dictionary containing the sensor data frame.
            target (str): The name of the touch sensor to check.

        Returns:
            bool: True if the specified touch sensor is touched, False otherwise.
        """
        if(target in frame["data"]):
            return True
        return False

    @inlineCallbacks
    def touch(self, target : str):
        """
        Subscribes to the touch sensor stream for the specified target sensor.

        Args:
            target (str): The name of the touch sensor to subscribe to.
        """
        self.session.subscribe(self.is_touched, "rom.sensor.touch.stream", self.touch_mapping[target])



