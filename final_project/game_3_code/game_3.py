from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
import random
from .game_3_drive import DriveSystem 
from typing import Generator, Any
from .game_3_emotion_mapping import emotion_cards
from .game_3_robot_actions import RobotActions
from .game_3_info import encouragement_sentences, positive_feedback_sentences, flag_cards, questions, score_feedback

def get_feedback_message(score):
    for score_range, message in score_feedback.items():
        if score_range[0] <= score <= score_range[1]:
            return message
    return "Great effort! Keep learning and improving."


def smart_question_binary(session, question):
    """
    Asks a binary (True/False) question to the user and provides feedback based on the user's answer.
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



def touched(frame):
    if ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
        print("touched") 


class CardUsage:
    def __init__(self, session):
        self.session = session
        

    @inlineCallbacks
    def ask_flag_card_question(self):
        #session.call("rie.vision.card.stream")
        
        for card_id, (country, fact) in flag_cards.items():
            correct = False
            attempts = 0
            max_attempts = 2  # set a max number of attempts per question
            question = f"What does the national flag of {country} look like?"

            while not correct:
                if attempts > 0 and attempts < 2:  # ask the question, if not first attempt, provide feedback
                    yield self.session.call("rie.dialogue.say", text="Try one more time. " + question)
                elif attempts > 1:
                    yield self.session.call("rie.dialogue.say", text="I'll give you a hint! The national flag of {country} has {fact}." + question)
                else:
                    yield self.session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_flag(self.session, card_id)

                print("exited")
                if correct:
                    yield self.session.call("rie.dialogue.say", text=f"Correct! That is the national flag of {country}. {random.choice(positive_feedback_sentences)} Let's try another country !")
                else:
                    yield self.session.call("rie.dialogue.say", text=f"That's not the correct flag! {random.choice(encouragement_sentences)}")

                attempts += 1

    
    @inlineCallbacks
    def wait_for_correct_flag(self, correct_card_id):
        card_detected = yield self.detect_card()
        yield self.session.call("rie.vision.card.stream")
        return card_detected == correct_card_id

    
    def detect_card(self):
        print("entered")
        # detect the shown card
        card_detected = yield self.session.call("rie.vision.card.read")
        print("card detected : ", card_detected[0]['data']['body'][0][5])
        card_detected = card_detected[0]['data']['body'][0][5]

        return card_detected



class Levels:
    def __init__(self, session, score, card_usage):
        self.session = session
        self.score = score
        self.card_usage = card_usage
    
    @inlineCallbacks
    def easy(self):
        yield self.session.call("rie.dialogue.say", text="I will ask you a question and you should pick which aruco card is the correct answer!")
        yield self.card_usage.ask_flag_card_question(self.session)
        self.score = 2

    @inlineCallbacks
    def medium(self):
        for question in questions[:-1]:
            if (yield smart_question_binary(self.session, question)):
                self.score += 1
        
        if self.score < 4:
            yield self.session.call("rie.dialogue.say", text="You are doing so well, you deserve a bonus question! Answer the following extra bonus question correctly for an additional point!")
            if (yield smart_question_binary(self.session, questions[-1])):  # Ask the last question separately
                self.score += 1



    @inlineCallbacks
    def hard(self):
        # Hard Level
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
            "sv": {
                "text": "Hej, jag är här för att lära dig lite geografi! Vilket land talar detta språk?",
                "expected_card": 1,
                "score": 1,
                "country": "Swedish"
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
                yield self.session.call("rie.dialogue.say", text=f" That is incorrect. I spoke {config["country"]}. {random.choice(encouragement_sentences)}")

        yield self.session.call("rie.dialogue.config.language", lang="en")

class EmpathyModule:
    def __init__(self, session):
        self.session = session
        self.robot_actions = RobotActions(session)
        self.drive_system = DriveSystem()
        self.outcome = None
        self.outcome_intensity = None

    @inlineCallbacks
    def detect_emotion(self):
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


# vics game individual part
@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="Let's start the mini game challenge! In this game, I will test your knowledge of national flags, trivia, and languages from Europe.")
    score = 0
    aruco_card_usage = CardUsage(session)
    game_levels = Levels(session, score, aruco_card_usage)

    yield sleep(2)
    # Easy difficulty part
    yield session.call("rie.dialogue.say", text="Let's start with something simple. Your task is to identify the national flags of different countries using the Aruco cards infront of you. Guess all of the coutries national flags atleast once and score 2 points!")
    answers = {"yes": ["yeah", "yes", "ye", "okay", "ofcourse"], "no": ["no", "nah", "nope", "never"]} 
    answer = yield session.call("rie.dialogue.ask", question="Are you ready?", answers=answers)

    if answer == "yes": 
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!") 
        yield game_levels.easy()
    elif answer == "no": 
        yield session.call("rie.dialogue.say", text="No worries! Just let me know when you're ready by touching my head.") 
        # Touch subscribe
        session.subscribe(touched, "rom.sensor.touch.stream")
        yield session.call("rom.sensor.touch.stream")  # <- touch interaction
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!")
        yield game_levels.easy()
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly.")
    
    # Medium difficulty part
    yield session.call("rie.dialogue.say", text="Well done! Now that you've identified the flags, let's move on to some trivia questions. This time I will add points to your score for every correct answer!")
    yield game_levels.medium()

    # Hard difficulty part
    yield session.call("rie.dialogue.say", text="Fantastic job so far! Now, let's try something different. I'll speak in a language, and you have to guess which country it is from by showing me the countries corresponding flag."
                       + "Let's see how well you paid attention to the beginning of the game")
    yield game_levels.hard()

     # Final feedback
    final_score = game_levels.score
    feedback_message = get_feedback_message(final_score)
    session.call("rom.optional.behavior.play", name="BlocklyApplause")
    yield session.call("rie.dialogue.say", text=f"You have completed the challenge! Well done! Your final score is {final_score} out of 10. {feedback_message}")
    yield sleep(2)

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
        yield session.call("rie.dialogue.say", text="That's a shame! Goodbye!") 
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly.")
    
    

