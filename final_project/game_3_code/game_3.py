# Individual Part for Victoria 
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
import random
from typing import Generator, Any
from .game_3_info import encouragement_sentences, positive_feedback_sentences, flag_cards, questions, score_feedback
from shared_code.drive import DriveSystem 
from typing import Generator, Any
from shared_code.emotion_mapping import emotion_cards
from shared_code.robot_actions import RobotActions
from game_3_code.game_3_info import encouragement_sentences, positive_feedback_sentences, flag_cards, questions, score_feedback


def get_feedback_message(score):
    """
    Returns a personalized feedback message based on the player's score.

    This function takes the player's score as input and returns a corresponding feedback message
    from the `score_feedback` dictionary. If the score does not fall within any predefined range,
    a default encouragement message is returned as fall back.

    Args:
        score (int): The player's score.

    Returns:
        str: A feedback message corresponding to the player's score.
    """
    for score_range, message in score_feedback.items():
        if score_range[0] <= score <= score_range[1]:
            return message
    return "Great effort! Keep learning and improving."

@inlineCallbacks
def smart_question_binary(session, question):
    """
    Ask a binary (True/False) question to the user and provides feedback based on the user's answer.
    
    Args:
        session: The session object for interacting with the robot.
        question: A tuple containing the question, correct answer (True/False), and additional explanation.
        
    Returns:
        bool: True if the user answered correctly, False otherwise.
    """
    correct = False
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={
            "true": ["true", "yes", "ja", "tru"],
            "false": ["false", "no", "nej", "fls"],
        },
    )
    yield sleep(1)
    _ = yield session.call("rie.dialogue.stt.read", time=6000)

    if (answer == "true" and question[1]) or (answer == "false" and not question[1]):
        # Nod yes
        session.call(
            "rom.actuator.motor.write",
            frames=[
                {"time": 400, "data": {"body.head.pitch": 0.15}},
                {"time": 1200, "data": {"body.head.pitch": -0.15}},
                {"time": 2000, "data": {"body.head.pitch": 0.15}},
                {"time": 2400, "data": {"body.head.pitch": 0.0}},
            ],
            force=True,
        )
        correct = True
        text = f"That is correct. {random.choice(positive_feedback_sentences)}" + question[2]
        yield session.call("rie.dialogue.say", text=text)
    elif (answer == "true" and not question[1]) or (answer == "false" and question[1]):
        yield session.call("rie.dialogue.say", text=f"That is incorrect. {random.choice(encouragement_sentences)}")

    return correct


@inlineCallbacks
def touched(frame):
    """
    Callback function for handling touch events on the robot's head.
    
    Args:
        frame: The data frame containing touch sensor information.
    """
    if ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
        print("touched") 


class CardUsage:
    """
    A class for handling the usage of Aruco cards in the game.
    """

    def __init__(self, session):
        """
        Initializes the CardUsage object.
        
        Args:
            session: The session object for interacting with the robot.
        """
        self.session = session
        

    @inlineCallbacks
    def ask_flag_card_question(self):
        """
        Asks questions about the national flags of different countries using Aruco cards.
        """
        self.session.call("rie.vision.card.stream")
        
        for card_id, (country, fact) in flag_cards.items():
            correct = False
            attempts = 0
            max_attempts = 2  # set a max number of attempts per question
            question = f"What does the national flag of {country} look like?"

            while not correct:
                if attempts > 0 and attempts < 2:  # ask the question, if not first attempt, provide feedback
                    yield self.session.call("rie.dialogue.say", text="Try one more time. " + question)
                elif attempts > 1:
                    yield self.session.call("rie.dialogue.say", text=f"I'll give you a hint! The national flag of {country} has {fact}..." + question)
                else:
                    yield self.session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_flag(card_id)

                if correct and card_id is 5:
                    yield self.session.call("rie.dialogue.say", text=f"Correct! That is the national flag of {country}. {random.choice(positive_feedback_sentences)}")
                elif correct:
                    yield self.session.call("rie.dialogue.say", text=f"Correct! That is the national flag of {country}. {random.choice(positive_feedback_sentences)} Let's try another country !")
                else:
                    yield self.session.call("rie.dialogue.say", text=f"That's not the correct flag! {random.choice(encouragement_sentences)}")

                attempts += 1

    
    @inlineCallbacks
    def wait_for_correct_flag(self, correct_card_id):
        """
        Wait for the user to show the correct Aruco card corresponding to the given card ID.
        
        Args:
            correct_card_id: The ID of the correct Aruco card.
            
        Returns:
            bool: True if the user showed the correct card, False otherwise.
        """
        card_detected = None
        card_detected = yield self.detect_card()
        return card_detected == correct_card_id

    @inlineCallbacks
    def detect_card(self):
        """
        Detects the Aruco card shown by the user.
        
        Returns:
            int: The ID of the detected Aruco card.
        """
        self.session.call("rie.vision.card.stream")

        # detect the shown card
        card_detected = yield self.session.call("rie.vision.card.read")
        print("card detected : ", card_detected[0]['data']['body'][0][5])
        card_detected = card_detected[0]['data']['body'][0][5]

        return card_detected



class Levels:
    """
    A class representing different levels of the game.
    """
    def __init__(self, session, score, card_usage):
        """
        Initializes the Levels object.
        
        Args:
            session: The session object for interacting with the robot.
            score: The initial score of the game.
            card_usage: An instance of the CardUsage class for handling Aruco cards.
        """
        self.session = session
        self.score = score
        self.card_usage = card_usage
    
    @inlineCallbacks
    def easy(self):
        """
        Implements the easy level of the game; guessing corresponding flags to countries.
        """
        yield self.session.call("rie.dialogue.say", text="I will ask you a question and you should pick which aruco card is the correct answer!")
        yield self.card_usage.ask_flag_card_question()
        self.score = 2

    @inlineCallbacks
    def medium(self):
        """
        Implements the medium level of the game; relevant geography trivia.
        """
        extra_attempt = 0
        for question in questions[:-1]:
            if (yield smart_question_binary(self.session, question)):
                self.score += 1
        
        if self.score < 4 and extra_attempt is 0:
            extra_attempt = 1
            yield self.session.call("rie.dialogue.say", text="Well done for trying so hard, you deserve a bonus question! Answer the following extra bonus question correctly for an additional point!")
            if (yield smart_question_binary(self.session, questions[-1])):  # Ask the last question separately for extra point if score low
                self.score += 1



    @inlineCallbacks
    def hard(self):
        """
        Implements the hard level of the game; guess corresponding flag of country to language.
        """
        yield self.session.call("rie.dialogue.say", text="Guess the next language I am speaking? Name the country and then match it to one of the flag cards in front of you! Let's start!")

        language_config = {
            "nl": {
                "text": "Hallo! Ik ben hier om je aardrijkskunde te leren! Welk land spreekt deze taal?",
                "expected_card": 3,
                "score": 1,
                "country": "Dutch"
            },
            "pl": {
                "text": "Cześć! Nazywam się Alpha Mini i jestem tutaj, aby nauczyć Cię geografii! W jakim kraju mówi się tym językiem?",
                "expected_card": 5,
                "score": 1,
                "country": "Polish"
            },
            "es": {
                "text": "Hola, ¡estoy aquí para enseñarte algo de geografía! ¿Qué país habla este idioma?",
                "expected_card": 18,
                "score": 1,
                "country": "Spanish"
            }
        }

        for lang, config in language_config.items():
            yield self.session.call("rie.dialogue.config.language", lang=lang)
            yield self.session.call("rie.dialogue.say", text=config["text"])
            detected_card = yield self.card_usage.detect_card()
            yield self.session.call("rie.dialogue.config.language", lang="en")
            if detected_card == config["expected_card"]:
                yield self.session.call("rie.dialogue.say", text=random.choice(positive_feedback_sentences))
                self.score += config["score"]
            else:
                yield self.session.call("rie.dialogue.say", text=f" That is incorrect. I spoke {config['country']}. {random.choice(encouragement_sentences)}")

        yield self.session.call("rie.dialogue.config.language", lang="en")

class EmpathyModule:
    """
    A class to handle emotion detection and empathy expression for the robot.

    This class encapsulates the logic for detecting emotions using Aruco cards,
    processing the detected emotions, and expressing appropriate empathetic responses
    based on the detected emotions.

    Attributes:
        session (Component): The session object for interacting with the robot.
        robot_actions (RobotActions): An instance of the RobotActions class for performing robot actions.
        drive_system (DriveSystem): An instance of the DriveSystem class for managing the robot's emotional state.
        outcome (str): The detected emotional outcome (neutral, positive, or negative).
        outcome_intensity (float): The intensity of the detected emotional outcome.
    """
    def __init__(self, session):
        """
        Initializes the EmpathyModule with the given session.

        Args:
            session (Component): The session object for interacting with the robot.
        """
        self.session = session
        self.robot_actions = RobotActions(session)
        self.drive_system = DriveSystem()
        self.outcome = None
        self.outcome_intensity = None

    @inlineCallbacks
    def detect_emotion(self):
        """
        Detects the emotion shown by the user using Aruco cards.

        This method streams the vision data, reads the detected Aruco card, and maps it to the corresponding emotion.

        Returns:
            str: The detected emotion or "Unknown emotion" if no emotion is detected.
        """
        global still_seconds

        detected_emotion = None
        self.session.call("rie.vision.card.stream")

        card_detected = yield self.session.call("rie.vision.card.read", time=1000)
        try:
            card_id = card_detected[0]['data']['body'][0][5]
            yield self.session.call("rie.vision.card.stream")

            detected_emotion = emotion_cards.get(card_id, "Unknown emotion")
            still_seconds = CARD_SESSION_TIME
        except:
            pass
        return detected_emotion


    @inlineCallbacks
    def process_emotion(self):
        """
        Processes the detected emotions and updates the robot's emotional state.

        This method continuously detects emotions for 5 seconds, updates the drive system with the perceived emotions,
        and determines the emotional outcome and its intensity.
        """
        global still_seconds

        while True:
            detected_emotion = yield self.detect_emotion()
            self.drive_system.print_meters()
            if detected_emotion is not None:
                self.drive_system.perceive_emotions(detected_emotion[2], detected_emotion[1])
            self.outcome, self.outcome_intensity = self.drive_system.update_all_meters()

            if still_seconds == 0:
                self.outcome, self.outcome_intensity = self.drive_system.emotion_selector()
                break
            elif self.outcome is not None:
                print("Outcome: ", self.outcome, "Intensity: ", self.outcome_intensity)
                break
            print("still seconds: ", still_seconds)
            still_seconds -= 1

    @inlineCallbacks
    def express_empathy(self):
        """
        Expresses the appropriate empathy response based on the detected emotional outcome.

        This method uses the robot actions to perform the corresponding movements (neutral, positive, or negative)
        and calls the dialogue method to express the empathetic response through speech.
        """
        if self.outcome == "neutral":
            yield self.robot_actions.move_neutral()
            yield self.session.call("rie.dialogue.say", text="I see.")
        elif self.outcome == "positive":
            yield self.robot_actions.move_positive(self.outcome_intensity / 2)
            yield self.session.call("rie.dialogue.say", text="Wow, you seem really pleased! I'm delighted that you're enjoying the game so much.")
        elif self.outcome == "negative":
            yield self.robot_actions.move_negative(self.outcome_intensity / 2)
            yield self.session.call("rie.dialogue.say", text="It sounds like you're a bit discouraged. I understand, learning new things isn't always easy. But I believe in you - let's break it down and try again together.")



# Constant Variables 
TIMEOUT_TIME = 6000
CARD_SESSION_TIME = 10

# GLobal Variables
still_seconds = CARD_SESSION_TIME


# Victorias Individual part of the projec5
@inlineCallbacks
def start_game(session):
    """
    Starts the mini game challenge.
    
    Args:
        session: The session object for interacting with the robot.
    """
    yield session.call("rie.dialogue.say", text="Let's start the mini game challenge! In this game, I will test your knowledge of national flags, trivia, and languages from Europe.")
    score = 0
    aruco_card_usage = CardUsage(session)
    game_levels = Levels(session, score, aruco_card_usage)
    
    yield sleep(1)

    # Easy difficulty part
    yield session.call("rie.dialogue.say", text="Let's start with something simple. Your task is to identify the national flags of different countries using the Aruco cards infront of you. Guess all of the coutries national flags atleast once and score 2 points!")
    answers = {"yes": ["yeah", "yes", "ye", "okay", "ofcourse"], "no": ["no", "nah", "nope", "never"]} 
    answer = yield session.call("rie.dialogue.ask", question="Are you ready?", answers=answers)
    
    if answer == "yes": 
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!") 
        yield game_levels.easy()
    elif answer == "no": 
        session.call("rom.optional.behavior.play", name="BlocklyTouchHead")
        yield session.call("rie.dialogue.say", text="No worries! Just let me know when you're ready by touching my head.") 
        session.subscribe(touched, "rom.sensor.touch.stream")
        yield session.call("rom.sensor.touch.stream")  # <- touch interaction
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!")
        yield game_levels.easy()
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly.")
    
    # Medium difficulty part
    session.call("rom.optional.behavior.play", name="BlocklyApplause")
    yield session.call("rie.dialogue.say", text="Well done! Now that you've identified the flags, let's move on to some trivia questions. This time I will add points to your score for every correct answer!")
    yield game_levels.medium()
    

    # Hard difficulty part
    session.call("rom.optional.behavior.play", name="BlocklyApplause")
    yield session.call("rie.dialogue.say", text="Fantastic job so far! Now, let's try something different. I'll speak in a language, and you have to guess which country it is from by showing me the countries corresponding flag. Let's see how well you paid attention to the beginning of the game")
    yield game_levels.hard()
    
     # Final feedback
    final_score = game_levels.score
    feedback_message = get_feedback_message(final_score)
    session.call("rom.optional.behavior.play", name="BlocklyApplause")
    yield session.call("rie.dialogue.say", text=f"You have completed the challenge! Well done! Your final score is {final_score} out of 10. {feedback_message}")
    yield sleep(1)

    yield session.call("rie.dialogue.say", text="How do you feel now that you have completed the challenge?")

    empathy_module = EmpathyModule(session)
    yield empathy_module.process_emotion()
    yield empathy_module.express_empathy()


    answer = yield session.call("rie.dialogue.ask", question="You did very good for your first time doing this challenge. Would you like to play again and beat your high-score?", answers=answers)

    if answer == "yes": 
        yield session.call("rie.dialogue.say", text="Awesome! Let's play again!!")
        session.call("rom.optional.behavior.play", name="BlocklyRobotDance")
        start_game(session)
    elif answer == "no": 
        session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
        yield session.call("rie.dialogue.say", text="That's a shame!")
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly.")
    
    

