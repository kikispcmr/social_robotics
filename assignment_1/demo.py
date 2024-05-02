from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep 
from autobahn.wamp.request import Subscription
import re
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"]
    }],
    realm="rie.6633488cc887f6d074f02eeb",
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
    ("What is the biggest tropical rainforest in the world?", "Amazon"),
    ("What continent has the smallest population?", "Antartica"),
    ("What is the smallest continent in the world?", "Australia"),
    ] 

change_flow = [
    ("Do you want to continue or change the game up?", True)
]

@inlineCallbacks
def smart_question_binary(session, question):
    yield sleep(1)
    answer = yield session.call("rie.dialogue.ask", question=question[0], answers={"true": ["true", "yes", "ja", "tru"], "false": ["false", "no", "nej", "fls"]})
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
def smart_question_branching(session):
    yield sleep(1)
    answer = yield session.call("rie.dialogue.ask", question="Do you want to try something harder?", answers={"true": ["true",, "tru", "yes", "ye"], "false": ["false", "no", "na", "nej"]})
    yield sleep(1)
    data = yield session.call("rie.dialogue.stt.read", time=6000)
    print(answer, data)
    answ = None
    
    for frame in data:
        if (frame["data"]["body"]["final"]):
            print(frame)
            
    if (answer == "true"):
        text = "That's great! Let's go with some trivia."
        yield session.call("rie.dialogue.say", text=text)
        answ = True
    elif (answer == "false"):
        yield session.call("rie.dialogue.say", text="No problem, let's continue!")
        anws = False 
    else: 
        smart_question_branching(session)
        
    return answ

@inlineCallbacks
def on_keyword(frame, session):
    if "certainty" in frame["data"]["body"] and frame["data"]["body"]["certainty"] > 0.45:
        yield session.call("rie.dialogue.say", text="Great, let us begin! Answer the following questions with either True or False.")
    
@inlineCallbacks
def keyword(session, statement, keywords): 
    # keyword question, not sure about this one as i have not tested
    ans = None
    cert = None
    final = None
    yield session.call("rie.dialogue.say", text=statement)
    yield sleep(0.5)
    data = yield session.call("rie.dialogue.stt.read", time=6000)
    for frame in data:
        if frame["data"]["body"]["final"]:
            print(frame)
            ans = frame["data"]["body"]["text"]
            cert = frame["data"]["body"]["certainty"]
            final = frame["data"]["body"]["final"]
            
        
    yield session.call("rie.dialogue.keyword.add", keywords=keywords)
    yield session.subscribe(on_keyword, "rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.clear")
    yield session.call("rie.dialogue.keyword.close")    
    return ans, cert, final

def regex(session, yes_pattern, no_pattern, reply):
    if re.search(yes_pattern, reply):
        # Trivia questions
        yield session.call("rie.dialogue.say", text="Let's start with some trivia!")
        print("START TRIVIA QUESTIONS")
    elif re.search(no_pattern, reply):
        # Continue with normal questions
        yield session.call("rie.dialogue.say", text="Alright, let's continue!")
        print("CONTINUE")
    else:
        # For times it throws a random event from the api
        yield sleep(1)
        yield session.call("rie.dialogue.say", text="I'm going to assume you want to keep on playing! We are having so much fun!")
            
@inlineCallbacks
def main(session, details):
    yes_pattern = r'(?i)\b(yes)\b'
    no_pattern = r'(?i)\b(no)\b'
      
    session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.vision.face.find")
    session.call("rie.vision.face.track") 
    
    #yield sleep(3)
    ### Start of Dialogue flow
    first_key = ["start", "yes", "ja", "go", "forward", "play"]
    reply, cert, final = yield keyword(session, "Say start when you're ready to play!", first_key)
    if final:
        yield session.call("rie.dialogue.say", text="Let's gooo")
        print("We starts")
        
        
    yield smart_question_binary(session, statements[0])
    yield smart_question_binary(session, statements[1])
    yield smart_question_binary(session, statements[2])
    
    answ = yield smart_question_branching(session)
    
    if answ:
        yield smart_question_binary(session, trivia[0])
        yield smart_question_binary(session, trivia[1])
        yield smart_question_binary(session, trivia[2])
    else: 
        yield smart_question_binary(session, statements[3])
        yield smart_question_binary(session, statements[4])
        yield session.call("rie.dialogue.say", text="Let's change things up.")
        yield smart_question_binary(session, statements[3])
        yield smart_question_binary(session, statements[4])
    
    
    ### Shall we start with trivia questions?
    #yield smart_question(session, statements[0])
    second_key = ["like", "I", "question", "one", "last", "about"]
    text = "Which question was your favourite one? Mine was question uhm... I forgot. Ahahaha."
    reply, cert, final = yield keyword(session, text, second_key)
    if final:
        yield session.call("rie.dialogue.say", text="That's a good one! I love it.")
        
        
    yield session.call("rie.dialogue.say", text="You reached the end! Great job. I hope you learnt something new about the world around you!")
        

    #print("!!!", reply, type(reply))
    #while reply == None or cert == 0.0:
    #    reply, cert = yield keyword(session, "We didn't quite get that. Repeat that please!", second_key)
    

        
    #yield smart_question(session, statements[1])

    
    
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