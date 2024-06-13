from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep
from game_1_code.game_1_dialogue import animal_questions, continent_cards, correct_responses, incorrect_responses
from shared_code.robot_actions import RobotActions
import random

class AnimalGame:
    def __init__(self, session):
        self.session = session
        self.game_running = False
        self.robot_actions = RobotActions(session)
        self.question_running = False  # To prevent multiple question flows

    @inlineCallbacks
    def check_card(self, frame, expected_location):
        card_id = yield self.detect_card(frame)
        if card_id in continent_cards and continent_cards[card_id] == expected_location:
            returnValue((True, card_id))
        returnValue((False, card_id))

    @inlineCallbacks
    def detect_card(self, frame):
        self.session.call("rie.vision.card.stream")
        print("entered")
        # detect the shown card
        card_detected = yield self.session.call("rie.vision.card.read")
        print("card detected: ", card_detected[0]['data']['body'][0][5])
        card_detected = card_detected[0]['data']['body'][0][5]
        return card_detected

    @inlineCallbacks
    def ask_question(self, animal, location, hint):
        if self.question_running:  # Prevent simultaneous question flows
            return
        self.question_running = True  # Mark question flow as running

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
                self.question_running = False  # Mark question flow as finished
                return
            attempts += 1
            if attempts < max_attempts:
                if attempts == 1:
                    yield self.session.call("rie.dialogue.say", text=f"That's not the right answer. You showed {continent_cards[card_id]}. Try again! Here's a hint: {hint}")
                else:
                    yield self.session.call("rie.dialogue.say", text=random.choice(incorrect_responses))
            else:
                yield self.robot_actions.move_negative()  # sad movement when incorrect after max attempts
                yield self.session.call("rie.dialogue.say", text=f"The correct answer is {location}, where {animal}s live.")

        self.question_running = False  # Mark question flow as finished

    @inlineCallbacks
    def start_game(self):
        if not self.game_running:
            yield self.session.call("rie.dialogue.say", text="Hello there! I'm excited to take you on an adventure to learn about some amazing animals and where they live.")
            yield sleep(1)
            yield self.robot_actions.wave_arm()
            yield self.session.call("rie.dialogue.say", text="We'll explore different continents and discover fascinating facts about each animal. Touch my head to get started!")
            yield sleep(2)
            yield self.session.subscribe(self.touched, "rom.sensor.touch.stream")

    @inlineCallbacks
    def touched(self, frame):
        print("Touch detected!")
        yield self.session.call("rom.sensor.touch.stream", unsubscribe=True)
        if not self.game_running and ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
            self.game_running = True
            print("Head touch detected!")
            yield self.session.call("rom.actuator.audio.stream", url="https://audio.jukehost.co.uk/tD16h2ar3hk2Hh1u7FYaX7pzJ0Iu5NFG", sync=False)
            sleep(1)
            yield self.session.call("rom.actuator.audio.stop")
            yield self.session.call("rie.dialogue.say", text="Great, let's get started!")
            yield self.run_game()

    @inlineCallbacks
    def run_game(self):
        animal_items = list(animal_questions.items())
        random.shuffle(animal_items)  # shuffle the questions to randomize the order

        for animal, (location, fact, hint) in animal_items:
            yield self.ask_question(animal, location, hint)

        yield self.session.call("rie.dialogue.say", text="You have completed the game. Great job! Now you know more about where these animals live and some interesting facts about them.")
        yield sleep(1)
        yield self.session.call("rie.dialogue.say", text="Remember, learning about animals helps us understand the world better and why it's important to protect their habitats. Until next time, keep exploring and learning!")
        yield self.session.leave()
        self.game_running = False
        self.question_running = False  # Reset question running status
