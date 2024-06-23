from twisted.internet.defer import inlineCallbacks
from .robot_actions import RobotActions
from .dialogue_actions import DialogueActions
from .aruco_actions import ArucoActions
from .questions import aruco, dialogue, questions, intro, harder_questions, capital_aruco, capital_section_intro


@inlineCallbacks 
def dialogue_section(session, dialogue_manager, robot_actions):
    """
    A section of the game that involves dialogue and robotic actions.

    Args:
        session (obj): The current game session.
        dialogue_manager (obj): The manager responsible for handling dialogue.
        robot_actions (obj): The manager responsible for controlling robotic actions.

    Returns:
        None
    """
    total_score = 0
    for statement in intro:
       yield dialogue_manager.nod_and_say(statement)
    for question in questions:
        yield dialogue_manager.target_smart_question_flow(question)
       
    robot_actions.motion("positive")
    robot_actions.prebuilt_motion("disco")

    yield dialogue_manager.nod_and_say("Great! We'll be trying harder questions now, try to get as many of them right as you can!")
    for question in harder_questions:
        if total_score >= 2:
            reply = yield dialogue_manager.smart_question_branching(session, "Would you like to try something harder?")
            if reply:
                yield robot_actions.motion("positive") 
                break 
            else: 
                yield robot_actions.motion("negative")
                yield dialogue_manager.nod_and_say("That's okay! Let's try another question.")

# Add fun facts at the end of each reply 
@inlineCallbacks
def capital_section(session, dialogue_manager, aruco_manager, robot_actions):
    """
    A section of the game that involves capital-themed questions and robotic actions.

    Args:
        session (obj): The current game session.
        dialogue_manager (obj): The manager responsible for handling dialogue.
        aruco_manager (obj): The manager responsible for handling ARUCO questions.
        robot_actions (obj): The manager responsible for controlling robotic actions.

    Returns:
        None
    """
    for statement in capital_section_intro:
       yield session.call("rom.optional.behavior.play", name="speakingAct1")
       yield dialogue_manager.nod_and_say(statement)


    yield aruco_manager.aruco_question(capital_aruco[0], robot_actions.motion("up"), robot_actions.motion("negative"))
    yield aruco_manager.aruco_question(capital_aruco[1], robot_actions.prebuilt_motion("BlocklyBow"), robot_actions.motion("negative"))
    yield aruco_manager.aruco_question(capital_aruco[2], robot_actions.prebuilt_motion("BlocklyBow"), robot_actions.motion("negative"))



@inlineCallbacks 
def aruco_section(session, dialogue_manager, aruco_manager, questions, robot_actions):
    """
    A section of the game that involves ARUCO questions and robotic actions.

    Args:
        session (obj): The current game session.
        dialogue_manager (obj): The manager responsible for handling dialogue.
        aruco_manager (obj): The manager responsible for handling ARUCO questions.
        questions (list): A list of ARUCO questions.
        robot_actions (obj): The manager responsible for controlling robotic actions.

    Returns:
        None
    """
    for statement in dialogue:
       yield session.call("rom.optional.behavior.play", name="speakingAct4")
       yield dialogue_manager.nod_and_say(statement)

    streak_counter = 0
    ans = yield aruco_manager.aruco_question(questions[0])
    streak_counter = streak_counter + 1 if ans else 0
    ans = yield aruco_manager.aruco_question(questions[1])
    streak_counter = streak_counter + 1 if ans else 0
    if streak_counter >= 2:
        yield dialogue_manager.smart_question_branching(session, "Would you like to try something harder?")
    else:
        ans = yield aruco_manager.aruco_question(questions[2], robot_actions.prebuilt_motion("disco"), robot_actions.motion("negative"))

@inlineCallbacks
def start_game(session):
    """
    The entry point of the game.

    Args:
        session (obj): The current game session.

    Returns:
        None
    """
    # Game starts here
    yield session.call("rie.dialogue.say", text="You have started Game 2. Have fun!")
    action_manager = RobotActions(session)
    dialogue_manager = DialogueActions(session)
    aruco_manager = ArucoActions(session)
    
    # SECTION 1 AND 2
    yield session.call("rie.vision.face.find")
    yield session.call("rom.optional.behavior.play", name="Stand/Waiting/LookHand_2")
    yield dialogue_section(session, dialogue_manager, action_manager)
    
    yield session.call("rie.vision.face.find")
    yield session.call("rom.optional.behavior.play", name="BlocklyApplause")
    
    # SECTION 3
    yield capital_section(session, dialogue_manager, aruco_manager, action_manager)

    # SECTION 4
    yield session.call("rie.vision.face.find")
    yield aruco_section(session, dialogue_manager, aruco_manager, aruco, action_manager)


    yield session.call("rie.vision.face.find")
    yield session.call("rie.dialogue.say", text="Amazing job, you did great! Time to move to the next game.")





