from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep
from game_1_code.game_1_dialogue import animal_questions, continent_cards, correct_responses, incorrect_responses, incorrect_responses_true_false, correct_responses_true_false, true_false_cards, false_statements
from shared_code.robot_actions import RobotActions
import random

#class for the mini animal game
class AnimalGame:
    def __init__(self, session):
        self.session = session
        self.robot_actions = RobotActions(session)
        self.game_running = False  # Safety flag to prevent multiple game starts
        self.score = 0

    #function to check the card and return whether a correct continent was shown
    @inlineCallbacks
    def check_card(self, frame, expected_location):
        card_id = yield self.detect_card(frame)
        if card_id in continent_cards and continent_cards[card_id] == expected_location:
            returnValue((True, card_id))
        returnValue((False, card_id))

    #function to check whether the correct true or false card was shown
    @inlineCallbacks
    def check_true_false_card(self, frame, value):
        card_id = yield self.detect_card(frame)
        if card_id in true_false_cards and true_false_cards[card_id] == value:
            returnValue((True, card_id))
        returnValue((False, card_id))

    #function to detect the card
    @inlineCallbacks
    def detect_card(self, frame):
        self.session.call("rie.vision.card.stream")
        # detect the shown card
        card_detected = yield self.session.call("rie.vision.card.read")
        print("card detected: ", card_detected[0]['data']['body'][0][5])
        card_id = card_detected[0]['data']['body'][0][5]
        return card_id

    # Ask where an animal lives
    @inlineCallbacks
    def ask_question(self, animal, location, hint):
        question = f"Where do {animal}s live?"
        yield self.session.call("rie.dialogue.say", text=question)
        yield sleep(1)

        # start the card detection stream
        yield self.session.call("rie.vision.card.stream")
        correct = False
        attempts = 0
        max_attempts = 2
        card_id = None
        while not correct and attempts < max_attempts:
            # Listen for the card input
            frame = yield self.session.call("rie.vision.card.read", time=6000)
            correct, card_id = yield self.check_card(frame, location)
            if correct:
                yield self.robot_actions.move_positive()  # happy movement when correct
                yield self.session.call("rie.dialogue.say", text=random.choice(correct_responses).format(animal=animal, location=location))
                yield self.session.call("rie.dialogue.say", text=f"{animal_questions[animal][1]}")  # provide the fact
                self.score += 1
                return
            attempts += 1
            if attempts < max_attempts:
                if attempts == 1:
                    yield self.session.call("rie.dialogue.say", text=f"That's not the right answer. You showed {continent_cards[card_id]}. Try again! Here's a hint: {hint}")
                else:
                    yield self.session.call("rie.dialogue.say", text=random.choice(incorrect_responses))
                    yield self.session.call("rie.dialogue.say", text=f"{animal_questions[animal][1]}")  # provide the fact
            else:
                yield self.robot_actions.move_negative()  # sad movement when incorrect after max attempts
                yield self.session.call("rie.dialogue.say", text=f"The correct answer is {location}, where {animal}s live.")
                yield self.session.call("rie.dialogue.say", text=f"{animal_questions[animal][1]}")  # provide the fact

    # Ask the true or false question
    @inlineCallbacks
    def ask_true_false_question(self, statement, is_true):
        yield self.session.call("rie.dialogue.say", text=statement)
        correct = False
        attempts = 0
        max_attempts = 2 # define max attempts the user can try to 2. After the attempts are over, move on to next question (the user should know the answer after first response, but it is good to repeat for memory)

        while not correct and attempts < max_attempts:
            frame = yield self.session.call("rie.vision.card.read", time=6000)
            correct, card_id = yield self.check_true_false_card(frame, is_true)
            if correct:
                yield self.robot_actions.move_positive()
                yield self.session.call("rie.dialogue.say", text=random.choice(correct_responses_true_false))
                self.score += 1  
                break
            else:
                attempts += 1
                yield self.robot_actions.move_negative()
                yield self.session.call("rie.dialogue.say", text=random.choice(incorrect_responses_true_false) if attempts < max_attempts else f"The correct answer was {'True' if is_true else 'False'}.")
        yield self.session.call("rie.dialogue.say", text="Let's move to the next question!")

    
    # when touched, this runs
    @inlineCallbacks
    def touched(self, frame):
        print("Touch detected!")
        if self.game_running is False and ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
            print("Head touch detected!")
            self.game_running = True
            yield self.session.call("rom.actuator.audio.stream", url="https://audio.jukehost.co.uk/tD16h2ar3hk2Hh1u7FYaX7pzJ0Iu5NFG", sync=False)
            sleep(1)
            yield self.session.call("rom.actuator.audio.stop")
            yield self.session.call("rie.dialogue.say", text="Great, let's get started!")
            yield self.run_game()

    # running the game, which consists of two main phases - the continent questions and the true-false questions
    @inlineCallbacks
    def run_game(self):
        yield self.start_animal_game()
        # Start the true/false game after the animal game
        yield self.start_true_false_game()
        yield self.session.leave()

    # start of the animal game
    @inlineCallbacks
    def start_animal_game(self):
        animal_items = list(animal_questions.items())
        random.shuffle(animal_items)  # shuffle the questions to randomize the order

        for animal, (location, fact, hint) in animal_items:
            yield self.ask_question(animal, location, hint)

        yield self.session.call("rie.dialogue.say", text="You have completed the first part of the game. Great job! Now you know more about where these animals live and some interesting facts about them.")
        yield sleep(1)
        yield self.session.call("rie.dialogue.say", text="Remember, learning about animals helps us understand the world better and why it's important to protect their habitats.")

    # this starts the second, more difficult part of the animal game with the true and false statements.
    @inlineCallbacks
    def start_true_false_game(self):
        yield self.session.call("rie.dialogue.say", text="Now, let's test whether you noticed the facts I told you with some true or false questions.")
        animal_items = list(animal_questions.items())
        random.shuffle(animal_items)
        for animal, (location, fact, hint) in animal_items:
            false_fact, false_hint = false_statements[animal]
            statements = [
                (f"A fact about {location}: {fact}", True),
                (f"A hint about {location}: {hint}", True),
                (f"A fact about {location}: {false_fact}", False),
                (f"A hint about {location}: {false_hint}", False)
            ]
            random.shuffle(statements)
            for statement, is_true in statements:
                yield self.ask_true_false_question(statement, is_true)
        yield self.session.call("rie.dialogue.say", text="Great job on completing the true/false challenge! Keep learning and exploring!")
        # provide feedback based on the total correct answers
        yield self.session.call("rie.dialogue.say", text=f"You answered {self.score} questions correctly!")
        if self.score > len(animal_questions):
            yield self.session.call("rie.dialogue.say", text="Amazing! You really know your stuff!")
        elif self.score > len(animal_questions) // 2:
            yield self.session.call("rie.dialogue.say", text="Good job! You have a good understanding!")
        else:
            yield self.session.call("rie.dialogue.say", text="Don't worry! Keep practicing and you'll get better!")
        

    #start game 1
    @inlineCallbacks
    def start_game(self):
        yield self.session.call("rie.dialogue.say", text="Hello there! I'm excited to take you on an adventure to learn about some amazing animals and where they live.")
        yield sleep(1)
        yield self.robot_actions.wave_arm()
        yield self.session.call("rie.dialogue.say", text="We'll explore different continents and discover fascinating facts about each animal. Touch my head to get started!")
        yield sleep(2)
        yield self.session.subscribe(self.touched, "rom.sensor.touch.stream")
