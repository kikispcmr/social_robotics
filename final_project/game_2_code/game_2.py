from twisted.internet.defer import inlineCallbacks
from robot_actions import RobotActions
from touch_actions import TouchActions
from dialogue_actions import DialogueActions
from movements import mapping 


@inlineCallbacks 
def dialogue_section(session, dialogue_manager):
    # Intoduce the Human Geography game 
    # Dialogue should be:
    # Hey! Are you ready to learn about Human Geography?
    
    # [Wait for yes or no response]

    # If no, say "What a shame"
    # If yes, say "Great! Let's get started"

    # Continue: First let's talk about what is HUman Geography 
    # Geography is all of the things that are around us. On the Earth, in the Earth, and above the Earth.
    # Human Geograpgy is how we, as people interact with the Earth. How we change it and how it changes us.

    # So tell me, what is Human Geography, its how we interact with the ...? 

    # Wait for earth, if timeout, repeat the whole previous paragraph. 

    # If correct, say "Wow we have a good listener! Let's move on to the next question"
    # Introduce the Human Geography game
    yield dialogue_manager.nod_and_say("Hey! Are you ready to learn about Human Geography?")

    # Wait for yes or no response
    questions = ["", True, "", False]
    _, answer = yield dialogue_manager.base_smart_question_flow(questions)

    # If no, say "What a shame"
    if answer == "false":
        yield dialogue_manager.nod_and_say("What a shame")
    # If yes, say "Great! Let's get started"
    elif answer == "true":
        yield dialogue_manager.nod_and_say("Great! Let's get started")

    # Continue: First let's talk about what is Human Geography
    yield dialogue_manager.nod_and_say("First let's talk about what is Human Geography. Geography is all of the things that are around us. On the Earth, in the Earth, and above the Earth. Human Geography is how we, as people interact with the Earth. How we change it and how it changes us.")

    # So tell me, what is Human Geography, its how we interact with the ...?
    question = ["So tell me, what is Human Geography, its how we interact with the ...?", ["earth"], "Wow we have a good listener! Let's move on to the next question", False]
    yield dialogue_manager.smart_question_multiple(question)

    # Wait for "earth", if timeout, repeat the whole previous paragraph.
    while True:
        data, answer = yield dialogue_manager.base_smart_question_flow([""])
        if answer == "earth":
            break
        else:
            yield dialogue_manager.nod_and_say("First let's talk about what is Human Geography. Geography is all of the things that are around us. On the Earth, in the Earth, and above the Earth. Human Geography is how we, as people interact with the Earth. How we change it and how it changes us.")

    # If correct, say "Wow we have a good listener! Let's move on to the next question"
    yield dialogue_manager.nod_and_say("Wow we have a good listener! Let's move on to the next question")

def touch_section(session, dialogue_manager, touch_manager):
    # --- End of the introduction
    # A big part of human geography is all about cities. Let's look at the NEtherlands! 
    # You should be very familiar with the Netherlands. Imagine the middle of my head in Amsterdam, where would Groningen be on my head?

    # Do BlocklyTouchHead annimation to show middle of the head 

    # [Then do a touch call to the back of the head of the robot]
    # If the answer is correct, say "Great! Let's move on to the next question."
    # If the answer is incorrect, say "That is incorrect. Let's try again."
    # If the answer is still incorrect, say "That is incorrect. The answer is the back of my head."
    # THen we continue, where would Eindhoven be on my head?
    # [Then do a touch call to the back of the head of the robot]
    # If the answer is correct, say "Great! Let's move on to the next question."
    # If the answer is incorrect, say "That is incorrect. Let's try again."
    # If the answer is still incorrect, say "That is incorrect. The answer is the back of my head."
    # Great Job let's move on!!! 

    #--- End of this section


    dialogue_manager.nod_and_say("A big part of human geography is all about cities. Let's look at the Netherlands!")

    # You should be very familiar with the Netherlands. Imagine the middle of my head in Amsterdam, where would Groningen be on my head?
    yield dialogue_manager.nod_and_say("You should be very familiar with the Netherlands. Imagine the middle of my head is Amsterdam, where would Groningen be on my head?")

    # Do BlocklyTouchHead animation to show middle of the head
    yield session.call("rom.actuator.motor.write", frames=[{"time": 0, "data": {"body.head.pitch": 0.0}}], force=True)

    # Then do a touch call to the back of the head of the robot
    touch_manager.touch("rear")

    # Check if the answer is correct
    correct_answer = False
    for _ in range(2):
        while not touch_manager.is_touched("body.head.rear"):
            yield sleep(0.1)

        if touch_manager.is_touched("body.head.rear"):
            correct_answer = True
            break

    if correct_answer:
        yield dialogue_manager.nod_and_say("Great! Let's move on to the next question.")
    else:
        yield dialogue_manager.nod_and_say("That is incorrect. The answer is the back of my head.")

    # Then we continue, where would Eindhoven be on my head?
    yield dialogue_manager.nod_and_say("Then we continue, where would Eindhoven be on my head?")

    # Then do a touch call to the back of the head of the robot
    touch_manager.touch("rear")

    # Check if the answer is correct
    correct_answer = False
    for _ in range(2):
        while not touch_manager.is_touched("body.head.rear"):
            yield sleep(0.1)

        if touch_manager.is_touched("body.head.rear"):
            correct_answer = True
            break

    if correct_answer:
        yield dialogue_manager.nod_and_say("Great! Let's move on to the next question.")
    else:
        yield dialogue_manager.nod_and_say("That is incorrect. The answer is the back of my head.")

    yield dialogue_manager.nod_and_say("Great job! Let's move on!!!")


@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="You have started Game 2. Have fun!")
    action_manager = RobotActions(session, mapping)
    touch_manager = TouchActions(session)
    dialogue_manager = DialogueActions(session)

    
    dialogue_section(session, dialogue_manager)

    # Okay since human geography is all about how we interact with the Earth. Pretend my head is a big . 
    # Idkkkkk think of questions. 
    # Robot demonstrates that touching its front head means yes 

    # End of that section: 
    # Okay, let's move on to the next section.
    # Let's play with some Aruco cards: 


    # End of Aruco cards section:


    # Feedback of game:
    yield action_manager.motion("positive")
    yield touch_manager.touch("front")
    yield touch_manager.touch("back")

    session.leave()




