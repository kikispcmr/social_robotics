



class TouchActions:

    def __init__(self, session):
        self.session = session
        self.touch_mapping = {
            "front": "body.head.front",
            "middle": "body.head.middle",
            "rear": "body.head.rear",
        }

    def touch(self, target : str):
        self.session.subscribe(self.is_touched, "rom.sensor.touch.stream", self.touch_mapping[target])

    def is_touched(self, frame, target):
        if(target in frame["data"]):
            return True
        return False

