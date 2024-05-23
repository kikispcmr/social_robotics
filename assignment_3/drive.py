

class DriveSystem():

    def __init__(self):
        self.drive_meter = 0.5

        # Decay the perception meter intensity
        self.perception_meter = {
            "emotion1": 0,  
                "emotion2" : 0, 
    }

        self.response_meters = {
            "postive": 0,
            "neutral" : 0, 
            "negative" : 0

        }

    def percieve_positive(self):




