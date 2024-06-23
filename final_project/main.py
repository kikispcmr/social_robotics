"""
This script initiates an educational geography game session with a robot that teaches children about geography through three fun minigames. 

The games include learning about animal habitats, human geography, and a geography challenge focused on national flags, trivia, and languages.

Authors: MATHIAS RANDRÜÜT, VICTORIA POLAKA, and KYRIAKOS HJIKAKOU

"""

from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from game_1_code.game_1 import AnimalGame # Mathias
from game_2_code import game_2 # Kyriakos
from game_3_code import game_3 # Victoria

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
    }],
    realm="rie.6671489d755a12a49504d05d",
)

@inlineCallbacks
def ask_game_choice(session):
    """
    Ask the user to choose a game and provides brief explanations for each game.

    Args:
        session: The session object for interacting with the robot.

    Returns:
        str: The chosen game.
    """
    yield session.call("rie.dialogue.say", text="We have three fun games to choose from!")
    yield sleep(1)
    
    yield session.call("rie.dialogue.say", text="Game 1 is an Animal Game where you will learn about different animals and their habitats.")
    yield sleep(1)
    
    yield session.call("rie.dialogue.say", text="Game 2 is a Human Geography game all about where people live on Earth and fun facts about that!")
    yield sleep(1)
    
    yield session.call("rie.dialogue.say", text="Game 3 is a Geography Challenge where you will test your knowledge of national flags, trivia, and languages from Europe.")
    yield sleep(1)
    
    yield session.call("rie.dialogue.say", text="Which game would you like to play? Please say 'Game 1', 'Game 2', or 'Game 3'.")
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question="Which game would you like to play?",
        answers={
            "game 1": ["game 1", "one", "game one", "first game"],
            "game 2": ["game 2", "two", "game two", "second game"],
            "game 3": ["game 3", "three", "game three", "third game"],
        },
    )
    yield sleep(1)
    _ = yield session.call("rie.dialogue.stt.read", time=6000)
    return answer

@inlineCallbacks
def main(session, details):
    """
    Main function to start the geography educational game.

    Args:
        session: The session object for interacting with the robot.
        details: Additional details for the session.
    """
    # Start by looking at the face
    yield session.call("rie.vision.face.find")
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    
    # Introduction
    yield session.call("rie.dialogue.say", text="Hello! I'm your friendly robot. My name is Alpha Mini.")
    yield sleep(1)
    yield session.call("rie.dialogue.say", text="I can help you learn about geography through fun games.")
    yield sleep(1)
    yield session.call("rie.dialogue.say", text="Did you know that the Amazon Rainforest is the largest tropical rainforest in the world? It spans across nine countries!")
    yield sleep(1)
    yield session.call("rie.dialogue.say", text="Now, let's have some fun together!")
    
    # Ask user to choose a game
    answer = yield ask_game_choice(session)
    
    if answer == "game 1":
        yield session.call("rie.dialogue.say", text="Starting Game 1")
        game_1 = AnimalGame(session)
        yield game_1.start_game()
    elif answer == "game 2":
        yield session.call("rie.dialogue.say", text="Starting Game 2")
        yield game_2.start_game(session)
    elif answer == "game 3":
        yield session.call("rie.dialogue.say", text="Starting Game 3")
        yield game_3.start_game(session)
    else:
        yield session.call("rie.dialogue.say", text="I didn't understand that. Please say 'Game 1', 'Game 2', or 'Game 3'.")
    session.leave()


wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
