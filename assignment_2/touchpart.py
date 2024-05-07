from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

def touched(frame, session):
    if ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
        #yield call("rie.dialogue.say", text="Ouch! Please don't touch me!")
        touch_speak(session)
        print("touch") 

def touch_speak():
    yield session.call("rie.dialogue.say", text="Ouch! Please don't touch me!")

@inlineCallbacks
def main(session, details):

    # Touch part
    session.subscribe(touched, "rom.sensor.touch.stream")
    #session.call("rom.sensor.touch.stream") 
    session.call("rom.sensor.touch.stream")
    #Start by seeking for participants
    session.call("rie.dialogue.say", text="HELLLLLLLLLLLLLLLLLLLLLOOOOOOOOOOo")
    yield session.call("rie.vision.face.find")
    session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    yield session.call("rie.dialogue.say", text="Oh hey! Would you like to play a game?")
    session.call("rie.vision.face.track")



    session.leave()




# Create wamp connection
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6639d599c887f6d074f04f49",
)


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])