sad_emotion = [
    # starting position
        {
            "time": 400,
            "data": {
                "body.head.pitch": -0.175,
            },
        },  
        {
            "time": 400,
            "data": {
                "body.head.pitch": 0.175,
            },
        }
    ]


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

    # Perform a specific movement from the internal dictionary of pre-built movements (made by us)
    def motion(self, movement: str):
        yield self.session.call("rom.actuator.motor.write", frames=self.movements[movement], force=True)
