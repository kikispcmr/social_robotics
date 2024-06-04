from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

class RobotActions:

    def __init__(self, session, mapping):
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

 
