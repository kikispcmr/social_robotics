from twisted.internet.defer import inlineCallbacks
from shared_code.robot_actions import RobotActions
from movements import mapping 
@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="You have started Game 2. Have fun!")
    action_manager = RobotActions(session, mapping)

    yield action_manager.motion("positive")

    session.leave()



