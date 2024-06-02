from twisted.internet.defer import inlineCallbacks
#from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep

flag_cards = {
    1: ("Sweden", "idk"),
    2: ("Latvia", "idk"),
    3: ("Netherlands", "idk"),
    4: ("Cyprus", "idk"),
    5: ("Poland", "idk")     
    }


questions = [
    (
        "Africa is the second largest continent in the world by land area.",
        True,
        "Did you know there are giraffes in Africa!",
    ),
    (
        "The capital of Japan is Tokyo.",
        True,
        "Did you know Tokyo has 14 million people living in it! That's amazing isn't it.",
    ),
    (
        "The Amazon Rainforest is located in South America.",
        True,
        "The Amazon Rainforest is the largest tropical rainforest in the world, spanning across nine different countries!",
    ),
    (
        "Antarctica is the smallest continent on Earth.",
        False,
        "Australia, not Antarctica, is the smallest continent by land area, despite Antarctica having the smallest population due to its harsh environment.",
    ),
    (
        "Mount Everest is the tallest mountain in the world.",
        True,
        "While Mount Everest is the highest mountain above sea level at 8,848 meters, it is not the tallest mountain when measured from base to peak. Some mountains, such as Mauna Kea in Hawaii, are taller than Everest when considering their total height from base to peak.",
    ),
]

def touched(frame):
    if ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
        print("touched") 


class CardUsage:
    def __init__(self, session):
        self.session = session
        

    @inlineCallbacks
    def ask_flag_card_question(self):
        #session.call("rie.vision.card.stream")
        # we ask the question based on animal_cards mapping
        
        for card_id, (country, fact) in flag_cards.items():
            correct = False
            attempts = 0
            max_attempts = 2  # set a max number of attempts per question
            question = f"What does the national flag of {country} look like?"

            while not correct:
                if attempts > 0 and attempts < 2:  # ask the question, if not first attempt, provide feedback
                    yield self.session.call("rie.dialogue.say", text="Try one more time. " + question)
                elif attempts > 1:
                    yield self.session.call("rie.dialogue.say", text="The national flag of {country} has {fact}." + question)
                else:
                    yield self.session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_card(self.session, card_id)

                print("exited")
                if correct:
                    yield self.session.call("rie.dialogue.say", text=f"Correct! That is the national flag of {country}. Let's try another country !")
                else:
                    yield self.session.call("rie.dialogue.say", text="That's not the correct flag!")
                
                attempts += 1


    @inlineCallbacks
    def wait_for_correct_card(self, correct_card_id):
        print("entered")
        # detect the shown card
        card_detected = yield self.session.call("rie.vision.card.read")

        print("card detected : ", card_detected[0]['data']['body'][0][5])
        yield self.session.call("rie.vision.card.stream")
        
        if card_detected[0]['data']['body'][0][5] == correct_card_id: # check card is correct
            return True
        return False


class Levels:
    def __init__(self, session, score, card_usage):
        self.session = session
        self.score = score
        self.card_usage = card_usage
    
    @inlineCallbacks
    def easy(self):
        yield self.session.call("rie.dialogue.say", text="I will ask you a question and you should pick which aruco card is the correct answer!")
        yield self.card_usage.ask_flag_card_question(self.session)
        self.score = 3

    @inlineCallbacks
    def medium(self):
        # Medium Level
        for i in range(6):
            yield self.session.call("rie.dialogue.say", text="What is the largest country in the EU?")
            # Add logic to check the response
            # Update score based on the response

    @inlineCallbacks
    def hard(self):
        # Hard Level
        for i in range(5):
            yield self.session.call("rie.dialogue.say", text="Show me what country speaks like this?")
            # Play Sweden audio
            yield self.session.call("rom.actuator.audio.play", url="path_to_sweden_audio.mp3")
            # Add logic to check the response
            # Update score based on the response





# vics game individual part
@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="")
    score = 0
    aruco_card_usage = CardUsage(session)
    game_levels = Levels(session, score, aruco_card_usage)

    yield session.call("rie.dialogue.say", text="Guess all of the coutries national flags atleast once and score 3 points! Are you ready?")

    answers = {"yes": ["yeah", "yes", "ye", "okay"], "no": ["no", "nah", "nope"]} 
    answer = yield session.call("rie.dialogue.ask", question="Guess all of the coutries national flags atleast once and score 3 points! Are you ready?", answers=answers)

    if answer == "yes": 
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!") 
        yield game_levels.easy()
    elif answer == "no": 
        yield session.call("rie.dialogue.say", text="Okay! Then let me know when you want to begin by touching my head!") 
        # Touch subscribte
        session.subscribe(touched, "rom.sensor.touch.stream")
        yield session.call("rom.sensor.touch.stream")  # <- touch interaction
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!")
        yield game_levels.easy()
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly...")
    
    yield session.call("rie.dialogue.say", text="Well done! Now that you have correctly answered all of the flag questions, let's move on to some trivia!" +
                       "This time I will add points to your score for every correct answer!")

    yield session.call("rie.dialogue.say", text="Now that you collected so many points. Let's try something different. I will speak in a language and you will have to guess what language out of the countries infront of you am I speaking?"
                       + "I hope you paid attention to the beginning of our game about the different national flags")
    

    # Final feedback
    yield session.call("rie.dialogue.say", text=f"Your final score is {score} out of 10.")
    session.leave()

