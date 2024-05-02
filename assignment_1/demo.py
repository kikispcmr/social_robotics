from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep 
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"]
    }],
    realm="rie.66336d09c887f6d074f03073",
)

statements = [
    ("Africa is the second largest continent in the world by land area.", True, "Did you know there are giraffes in Africa!"),
    ("The capital of Japan is Tokyo.", True, "Did you know Tokyo has 14 million people living in it! That's amazing isn't it."),
    ("The Amazon Rainforest is located in South America.", True, "The Amazon Rainforest is the largest tropical rainforest in the world, spanning across nine different countries!"),
    ("Antarctica is the smallest continent on Earth.", False, "Australia, not Antarctica, is the smallest continent by land area, despite Antarctica having the smallest population due to its harsh environment."),
    ("Mount Everest is the tallest mountain in the world.", True, "While Mount Everest is the highest mountain above sea level at 8,848 meters, it is not the tallest mountain when measured from base to peak. Some mountains, such as Mauna Kea in Hawaii, are taller than Everest when considering their total height from base to peak."),
    ] 

trivia = [
    ("Where are there giraffes?", "Africa"),
    ("What is the capital of Japan?", "Tokyo"),
    ("What is the biggest tropical rainforest in the world?", "Amazon Rainforest"),
    ("What continent has the smallest population?", "Antartica"),
    ("What is the smallest continent in the world?", "Australia"),
    ] 

@inlineCallbacks
def smart_question(session, question):
    yield sleep(1)
    answer = yield session.call("rie.dialogue.ask", question=question[0], answers={"true": ["true", "yes"], "false": ["false", "no"]})
    yield sleep(1)
    data = yield session.call("rie.dialogue.stt.read", time=6000)
    print(answer, data)
    
    for frame in data:
        if (frame["data"]["body"]["final"]):
            print(frame)
    if (answer == "true" and question[1]) or (answer == "false" and not question[1]):
        # nod yes
        session.call("rom.actuator.motor.write",
        frames=[{"time": 400, "data": {"body.head.pitch": 0.15}},
        {"time": 1200, "data": {"body.head.pitch": -
        0.15}},
        {"time": 2000, "data": {"body.head.pitch": 0.15}},
        {"time": 2400, "data": {"body.head.pitch": 0.0}}],
        force=True) 
        text = "That is correct." + question[2]
        yield session.call("rie.dialogue.say", text=text)
    elif (answer == "true" and not question[1]) or (answer == "false" and question[1]):
        yield session.call("rie.dialogue.say", text="That is incorrect.")


@inlineCallbacks
def on_keyword(frame, session):
    if "certainty" in frame["data"]["body"] and frame["data"]["body"]["certainty"] > 0.45:
        yield session.call("rie.dialogue.say", text="Great, let us begin!")
    
@inlineCallbacks
def keyword(session): 
    # keyword question, not sure about this one as i have not tested
    yield session.call("rie.dialogue.say", text="Do you want to continue.")
    data = yield session.call("rie.dialogue.stt.read", time=6000)
    for frame in data:
        if frame["data"]["body"]["final"]:
            print(frame)

        
    yield session.call("rie.dialogue.keyword.add", keywords=["yes"])
    yield session.subscribe(on_keyword, "rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.clear")
    yield session.call("rie.dialogue.keyword.close")    
            
@inlineCallbacks
def main(session, details):
    session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.vision.face.find")
    session.call("rie.vision.face.track") 
    
    #yield sleep(3)
    ### Start of Dialogue flow
    yield smart_question(session, statements[0])
    yield keyword(session)
    yield smart_question(session, statements[1])

    
    
    # Keyword ask whether to ocntinue or flip
    
    # ---------------
    # starting with the smart true-false questions
    #ready_answer = yield session.call("rie.dialogue.ask", question="Are you ready to start?", answers={"yes": ["yes", "yeah"], "no": ["no", "nope"]})
    
    #if ready_answer != "yes":
    #    yield session.call("rie.dialogue.say", text="Alright, just start me again when you're ready.")
    #    session.leave()
    #    return
    #else:
    session.leave()

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])